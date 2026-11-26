"""Calibrated decisions: exact intervals for rates, and p-values from a null set.

A threshold in sigma is a distance, not a probability. Whether "5 sigma" means one false
detection in a hundred or in a million depends on how well the noise model fits the
track. These tools state the error rate directly:

- `exact_interval` and `wilson_interval`: the uncertainty of a rate measured as k of n.
  "0 of 60 false detections" is compatible with a true rate of up to 6% (95%, exact).
- `conformal_p` and `conformal_threshold`: a finite-sample p-value and threshold against
  scores measured on null cases (cases known to contain no effect). If the tested case is
  exchangeable with the null cases (drawn the same way when there is no effect), then
  P(p <= alpha) <= alpha exactly, for any distribution of the scores. With N null scores
  the smallest possible p-value is 1 / (N + 1); a smaller alpha is reported as not
  attainable rather than extrapolated.
- `shuffle_pieces`: a null case made from the track itself. It is cut into pieces of
  random length and the pieces are put back in random order: the sounds and their local
  texture stay, any repetition at lags longer than the pieces is destroyed.

The calibration follows our own Blind Signal Discovery project (doi:10.5281/zenodo.24557479),
re-derived here with numpy only. Clopper and Pearson (1934), Wilson (1927) and the
conformal p-value (Vovk, Gammerman and Shafer, 2005) are published mathematics.
"""
from __future__ import annotations

import math

import numpy as np

# Two-sided 95%: the normal quantile used by the Wilson interval.
_Z95 = 1.959963984540054


def _beta_ppf(q: float, a: float, b: float) -> float:
    """Quantile of the Beta(a, b) distribution, by bisection on its CDF.

    The CDF is the regularized incomplete beta function, computed with its continued
    fraction (Numerical Recipes form, re-derived). 200 bisection steps reach machine
    precision on [0, 1].
    """
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _betainc(a, b, mid) < q:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _betacf(a: float, b: float, x: float) -> float:
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return h


def _betainc(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta function I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln_front = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                + a * math.log(x) + b * math.log1p(-x))
    front = math.exp(ln_front)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def _check_counts(k: int, n: int) -> None:
    if n < 0 or k < 0 or k > n or int(k) != k or int(n) != n:
        raise ValueError(f"need whole numbers 0 <= k <= n, got k={k}, n={n}")


def exact_interval(k: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Clopper-Pearson interval for a rate of k in n. Never narrower than the truth needs.

    With n = 0 nothing is known and the interval is (0, 1).
    """
    _check_counts(k, n)
    if n == 0:
        return (0.0, 1.0)
    alpha = 1.0 - confidence
    lo = 0.0 if k == 0 else _beta_ppf(alpha / 2.0, k, n - k + 1)
    hi = 1.0 if k == n else _beta_ppf(1.0 - alpha / 2.0, k + 1, n - k)
    return (lo, hi)


def wilson_interval(k: int, n: int) -> tuple[float, float]:
    """Wilson score interval (95%) for a rate of k in n: shorter than the exact one, approximate."""
    _check_counts(k, n)
    if n == 0:
        return (0.0, 1.0)
    z2 = _Z95 ** 2
    p = k / n
    den = 1.0 + z2 / n
    centre = (p + z2 / (2 * n)) / den
    half = (_Z95 / den) * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def rate_text(k: int, n: int) -> str:
    """'3 of 60 (5.0%, 95% CI 1.0 to 13.9%)': how every rate is written in a report."""
    lo, hi = exact_interval(k, n)
    share = f"{100.0 * k / n:.1f}%" if n else "n/a"
    return f"{k} of {n} ({share}, 95% CI {100 * lo:.1f} to {100 * hi:.1f}%)"


def conformal_p(score: float, null_scores) -> float:
    """p = (1 + number of null scores >= score) / (N + 1).

    A higher score means more evidence. A score that is not a number is no evidence (p = 1).
    """
    null = np.asarray(null_scores, dtype=np.float64).ravel()
    if not np.all(np.isfinite(null)):
        raise ValueError("null scores must be finite")
    if not np.isfinite(score):
        return 1.0
    return float((1 + np.count_nonzero(null >= score)) / (len(null) + 1))


def conformal_threshold(null_scores, alpha: float) -> float | None:
    """Smallest threshold t with P(score > t) <= alpha under the null, from N null scores.

    A score strictly above the returned value has conformal p <= alpha. Returns None when
    alpha is not attainable with N scores (1 / (N + 1) > alpha): with too few null cases
    no threshold can promise that rate, and the honest answer is to abstain.
    """
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must lie in (0, 1), got {alpha}")
    null = np.sort(np.asarray(null_scores, dtype=np.float64).ravel())
    n = len(null)
    if n == 0:
        return None
    # largest m with m / (n + 1) <= alpha: a score above the (n - m + 1)-th smallest
    # null score leaves at most m - 1 null scores >= it, so p <= m / (n + 1).
    m = int(math.floor(alpha * (n + 1)))
    while m > 0 and m / (n + 1.0) > alpha:
        m -= 1
    while m < n and (m + 1) / (n + 1.0) <= alpha:
        m += 1
    if m < 1:
        return None
    return float(null[n - m])


def shuffle_pieces(x, rng: np.random.Generator, lo: int, hi: int, fade: int = 0) -> np.ndarray:
    """Cut x (1-D, or 2-D with time on the first axis) into pieces of lo..hi samples, shuffled.

    Random piece lengths matter: pieces of one fixed length would put a join at a fixed
    interval and create the very repetition this null must not contain. An optional
    linear fade of `fade` samples at both ends of every piece hides the joins in audio.
    """
    x = np.asarray(x, dtype=np.float64)
    if not (1 <= lo <= hi):
        raise ValueError(f"need 1 <= lo <= hi, got lo={lo}, hi={hi}")
    pieces, i = [], 0
    ramp = np.linspace(0.0, 1.0, fade) if fade > 0 else None
    while i < len(x):
        c = int(rng.integers(lo, hi + 1))
        p = x[i:i + c].copy()
        if ramp is not None and len(p) > 2 * fade:
            shape = (fade,) + (1,) * (p.ndim - 1)
            p[:fade] *= ramp.reshape(shape)
            p[-fade:] *= ramp[::-1].reshape(shape)
        pieces.append(p)
        i += c
    order = rng.permutation(len(pieces))
    return np.concatenate([pieces[k] for k in order], axis=0)
