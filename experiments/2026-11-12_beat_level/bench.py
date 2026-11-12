"""Beat-level benchmark (issue #15): signals with a known beat, a metric that tells the
beat apart from its subdivision and its multiples, and the rules being compared.

Every synthetic signal marks each beat with a strong event (kick or snare) and fills the
subdivisions with weak events (hats). The beat is therefore the level of the strong
events, which is the usual musical meaning of the pulse. Bars are marked by an accent.

Sets:
  dev     seeds 0-199 of the new generator, plus the 120 positives of the confirmation
          experiment (click trains and grooves, already investigated). Used for development.
  final   seeds 50000-50199 of the new generator. Run once, with `python run.py final`,
          after the rule is fixed. Never used for tuning.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from pts import periodicity as P  # noqa: E402

SR = 22050
TAU_LO, TAU_HI = 0.25, 2.0
TOL = 0.03          # relative tolerance for a level
PRECISION = 0.10    # right level, but off by more than TOL and at most this

DEV_SEEDS = range(0, 200)
FINAL_SEEDS = range(50000, 50200)

# ---------------------------------------------------------------- metric

CLASSES = ("exact", "precision", "subdivision", "multiple", "other", "none")


def classify(found, beat):
    """exact / precision / subdivision / multiple / other / none, and the ratio found/beat."""
    if found is None:
        return "none", None
    q = found / beat
    if abs(q - 1) <= TOL:
        return "exact", q
    if abs(q - 1) <= PRECISION:
        return "precision", q
    for k in (2, 3, 4):
        if abs(q * k - 1) <= TOL:
            return "subdivision", q
    for k in range(2, 9):
        if abs(q / k - 1) <= TOL:
            return "multiple", q
    return "other", q


# ---------------------------------------------------------------- generator

def _kick(rng):
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    f0, f1 = rng.uniform(40, 60), rng.uniform(60, 120)
    return np.sin(2 * np.pi * (f0 + f1 * np.exp(-t / 0.03)) * t) * np.exp(-t / rng.uniform(0.06, 0.15))


def _snare(rng):
    n = int(0.2 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * rng.uniform(170, 230) * t) * np.exp(-t / 0.04)
    noise = np.convolve(rng.standard_normal(n), [1, -0.6], "same") * np.exp(-t / rng.uniform(0.04, 0.09))
    return 0.6 * body + 0.5 * noise


def _hat(rng):
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    w = rng.standard_normal(n)
    w = np.diff(np.diff(w, prepend=0), prepend=0)          # tilt towards the highs
    return w / (np.abs(w).max() + 1e-9) * np.exp(-t / rng.uniform(0.01, 0.03))


def _place(x, t, b, amp):
    i = int(round(t * SR))
    if 0 <= i < len(x):
        seg = x[i:i + len(b)]
        seg += amp * b[:len(seg)]


PATTERNS = ("four", "backbeat", "oompah", "boombap")


def groove(seed):
    """A drum loop with a known beat. Returns (signal, beat_s, description)."""
    rng = np.random.default_rng(seed)
    compound = rng.random() < 0.2
    if compound:                                  # 6/8, 9/8, 12/8: the beat is a dotted quarter
        nb, sub = int(rng.choice([2, 3, 4])), 3
        bpm = rng.uniform(40, 110)
    else:
        nb = int(rng.choice([2, 3, 4, 5, 6, 7]))
        sub = int(rng.choice([2, 2, 3, 4]))
        bpm = rng.uniform(60, 200)
    beat = 60.0 / bpm
    if beat / sub < 0.06:                          # hats faster than 60 ms are not played
        sub = 2 if beat / 2 >= 0.06 else 1
    pattern = str(rng.choice(PATTERNS))
    swing = rng.uniform(0.5, 0.62) if sub == 2 and rng.random() < 0.3 else 0.5
    jitter = float(rng.choice([0.0, 0.005, 0.012, 0.02]))
    accent = rng.uniform(1.15, 1.6)
    hat_level = rng.uniform(0.15, 0.6)
    snr = float(rng.choice([30.0, 15.0, 6.0, 0.0]))
    dur = rng.uniform(20, 40)
    k, s, h = _kick(rng), _snare(rng), _hat(rng)
    x = np.zeros(int(dur * SR) + SR)
    j = lambda: rng.normal(0, jitter) if jitter else 0.0
    for i in range(int(dur / beat)):
        t, pos = i * beat, i % nb
        amp = accent if pos == 0 else 1.0
        if pattern == "four":
            _place(x, t + j(), k, amp)
            if nb >= 4 and pos % 2 == 1:
                _place(x, t + j(), s, 0.7)
        elif pattern == "backbeat":
            _place(x, t + j(), k if pos % 2 == 0 else s, amp)
        elif pattern == "oompah":
            _place(x, t + j(), k if pos == 0 else s, amp if pos == 0 else 0.6)
        else:                                       # boombap: snare on even beats, kick on odd beats and on some off-beats
            _place(x, t + j(), k if pos % 2 == 0 else s, amp)
            if pos % 2 == 0 and sub >= 2 and rng.random() < 0.5:
                _place(x, t + beat / sub * (sub - 1) + j(), k, 0.55)
        for q in range(sub):
            off = (q / sub) if not (sub == 2 and q == 1) else swing
            _place(x, t + off * beat + j(), h, hat_level * (1.0 if q == 0 else 0.8))
    x = x[: int(dur * SR)]
    p = np.mean(x ** 2) + 1e-12
    x = x + rng.standard_normal(len(x)) * np.sqrt(p / 10 ** (snr / 10))
    desc = {"seed": seed, "bpm": bpm, "beats_per_bar": nb, "subdivision": sub, "compound": compound,
            "pattern": pattern, "swing": swing, "jitter_s": jitter, "snr_db": snr, "duration_s": dur}
    return x, beat, desc


def investigated():
    """The 120 positives of the confirmation experiment, regenerated exactly."""
    sys.path.insert(0, os.path.join(ROOT, "experiments", "2026-11-12_periodicity_confirmation"))
    import run as C                              # noqa: E402
    out = []
    for split, seeds, gen in (("train", range(60), C.click_train), ("test", range(1000, 1060), C.groove)):
        for s in seeds:
            rng = np.random.default_rng(s)
            dur = rng.uniform(20, 40)
            C.NEGATIVES[list(C.NEGATIVES)[s % len(C.NEGATIVES)]](rng, dur)
            x, beat = gen(rng, dur)
            out.append((x, beat, {"seed": s, "family": gen.__name__, "split": split}))
    return out


# ---------------------------------------------------------------- rules

def rule_old(x, sr):
    """The rule in pts today: comb score on integer lags, the shortest peak within 0.9 of the best."""
    env, fs = P.onset_envelope(x, sr)
    return P.envelope_periodicity(env, fs, TAU_LO, TAU_HI).tau


# The candidate rule, fixed on the dev set (issue #15). Not in pts yet: whether it replaces
# the old rule is decided after the final check.
STRONG_FMAX = 2500.0   # strong events: kick and snare bodies; hats and cymbals sit above
CONSISTENCY = 0.5      # a level's comb must reach this share of the best comb (plateau 0.4-0.6 on dev)
LOCAL_MAX = 0.05       # a peak counts only if it is the highest within +-5% of its lag


def strong_envelope(x, sr):
    """Onset envelope of the strong events only: 6 log bands from 40 Hz to STRONG_FMAX."""
    Pw, fs = P.stft_power(x, sr, 1024, 0.005)
    L = 10 ** (P.log_bands(Pw, sr, 1024, 6, 40.0, STRONG_FMAX) / 10 * 0.3)
    return np.maximum(np.diff(L, axis=0, prepend=L[:1]), 0.0).sum(axis=1), fs


def _subpeak(r, p):
    a, b, c = r[p - 1], r[p], r[p + 1]
    den = a - 2 * b + c
    return p + (float(np.clip(0.5 * (a - c) / den, -0.5, 0.5)) if den < 0 else 0.0)


def refine(r, lag, n=4, tol=0.03):
    """The period read from its first n multiples (least squares), not from one peak."""
    num = den = 0.0
    for m in range(1, n + 1):
        c = m * lag
        w = max(1.0, tol * c)
        lo, hi = max(1, int(np.floor(c - w))), int(np.ceil(c + w))
        if hi + 1 >= len(r):
            break
        q = lo + int(np.argmax(r[lo:hi + 1]))
        q = _subpeak(r, q) if 1 <= q < len(r) - 1 else q
        num += m * q
        den += m * m
    return num / den if den else lag


def _at(r, c):
    i = int(round(c))
    return float(r[max(1, i - 1):i + 2].max())


def comb_at(r, T):
    """Mean correlation at the first four multiples of a fractional lag T."""
    v = [_at(r, m * T) for m in range(1, 5) if m * T + 2 < len(r)]
    return float(np.mean(v)) if v else 0.0


def rule_new(x, sr):
    """The shortest level of the strong events that repeats at its multiples and is confirmed.

    1. Onset envelope of the strong events only (below STRONG_FMAX).
    2. Peaks of its autocorrelation in [TAU_LO, TAU_HI) that are local maxima within +-5%.
    3. Each peak's period is refined from its first four multiples.
    4. Going from the shortest: the first period whose comb reaches CONSISTENCY of the best
       comb and that passes confirm_period() is the beat. If none does, the old rule's
       candidate is returned (it is then not confirmed).
    """
    env, fs = strong_envelope(x, sr)
    r = P.autocorr(env, int(4 * TAU_HI * fs) + 2)
    lo, hi = int(np.floor(TAU_LO * fs)), min(len(r) - 2, int(np.ceil(TAU_HI * fs)))
    if hi <= lo:
        return None
    k = np.arange(lo, hi + 1)
    pk = k[(r[k] > r[k - 1]) & (r[k] >= r[k + 1]) & (r[k] > 0)]
    pk = [p for p in pk if r[p] >= r[max(1, int(p * (1 - LOCAL_MAX))):int(p * (1 + LOCAL_MAX)) + 2].max()]
    cand = [refine(r, _subpeak(r, p)) for p in pk]
    if not cand:
        return None
    combs = np.array([comb_at(r, T) for T in cand])
    best = combs.max()
    for T, c in zip(cand, combs):
        if c >= CONSISTENCY * best and                 P.confirm_period(env, fs, P.Periodicity(T / fs, c), TAU_LO, P.autocorr).confirmed:
            return T / fs
    return P.envelope_periodicity(env, fs, TAU_LO, TAU_HI).tau


RULES = {"old": rule_old, "new": rule_new}
