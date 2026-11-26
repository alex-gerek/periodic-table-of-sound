"""Seam features, frozen for protocol v2 (journal step 2026-11-26-seam-002, issue #34).

Five features of a mono mix, each a value every 0.25 s (NaN where its windows do not fit):
  envelope   change of the median log energy in 24 log bands over 4 s before and after
  floor      largest change over 8 bands of the 10th percentile of frame power over 6 s
  bandwidth  change of the median ratio of energy above 16 kHz to 8-16 kHz over 6 s
  level      change of the median total energy over 2 s
  click      median over 4-16 kHz of how far one short frame rises above both neighbours
Stage 1 statistic at a join: the largest value within +-2 s, against the same for windows centred
on every second of the track more than 10 s from any join and from the ends.

Do not change this file after the development sweep: the real ground truth is scored with it as is.
"""
import numpy as np

STEP_S = 0.25
NFFT, HOP = 2048, 512
NFFT_C, HOP_C = 512, 128
WIN_S = 2.0
EXCL_S = 10.0
FEATURES = ("envelope", "floor", "bandwidth", "level", "click")


def _frames_power(x, sr, nfft, hop):
    n = 1 + (len(x) - nfft) // hop
    idx = np.arange(nfft)[None, :] + hop * np.arange(n)[:, None]
    P = np.abs(np.fft.rfft(x[idx] * np.hanning(nfft), axis=1)) ** 2
    return P, np.fft.rfftfreq(nfft, 1.0 / sr), (np.arange(n) * hop + nfft / 2) / sr


def _bands(P, f, edges):
    return np.stack([P[:, (f >= lo) & (f < hi)].sum(axis=1) for lo, hi in zip(edges[:-1], edges[1:])], axis=1)


def _db(x):
    return 10.0 * np.log10(np.maximum(x, 1e-20))


def _change(series_t, values, centres, side_s, reducer, normalise):
    """|reducer(after) - reducer(before)| at each centre; values (frames, n) in dB."""
    out = np.full(len(centres), np.nan)
    for i, c in enumerate(centres):
        b = (series_t >= c - side_s) & (series_t < c)
        a = (series_t >= c) & (series_t < c + side_s)
        if b.sum() < 4 or a.sum() < 4 or c - side_s < series_t[0] or c + side_s > series_t[-1]:
            continue
        vb, va = reducer(values[b]), reducer(values[a])
        d = np.abs(va - vb)
        if normalise:
            dev = np.concatenate([np.abs(values[b] - np.median(values[b], axis=0)),
                                  np.abs(values[a] - np.median(values[a], axis=0))])
            d = d / (1.4826 * np.median(dev, axis=0) + 0.5)
            out[i] = float(np.mean(d))
        else:
            out[i] = float(np.max(d))
    return out


def features(x, sr):
    """Return (centres in s, {feature: values})."""
    P, f, t = _frames_power(x, sr, NFFT, HOP)
    centres = np.arange(0.0, len(x) / sr, STEP_S)
    env = _db(_bands(P, f, np.geomspace(50.0, 16000.0, 25)))
    flo = _db(_bands(P, f, np.geomspace(100.0, 16000.0, 9)))
    top = min(20000.0, 0.95 * sr / 2)
    hi = P[:, (f >= 16000.0) & (f < top)].sum(axis=1)
    mid = P[:, (f >= 8000.0) & (f < 16000.0)].sum(axis=1)
    bw = _db(hi / np.maximum(mid, 1e-20))[:, None]
    lev = _db(P[:, (f >= 50.0) & (f < 16000.0)].sum(axis=1))[:, None]
    out = {
        "envelope": _change(t, env, centres, 4.0, lambda v: np.median(v, axis=0), True),
        "floor": _change(t, flo, centres, 6.0, lambda v: np.percentile(v, 10, axis=0), False),
        "bandwidth": _change(t, bw, centres, 6.0, lambda v: np.median(v, axis=0), False),
        "level": _change(t, lev, centres, 2.0, lambda v: np.median(v, axis=0), False),
    }
    Pc, fc, tc = _frames_power(x, sr, NFFT_C, HOP_C)
    L = _db(Pc[:, (fc >= 4000.0) & (fc < 16000.0)])
    spike = np.full(len(tc), np.nan)
    spike[1:-1] = np.median(L[1:-1] - np.maximum(L[:-2], L[2:]), axis=1)
    click = np.full(len(centres), np.nan)
    pos = np.searchsorted(tc, centres)
    for i, p in enumerate(pos):                     # largest spike within +-STEP_S/2 of the centre
        lo, hi_ = np.searchsorted(tc, centres[i] - STEP_S / 2), np.searchsorted(tc, centres[i] + STEP_S / 2)
        seg = spike[lo:hi_]
        if seg.size and np.any(np.isfinite(seg)):
            click[i] = float(np.nanmax(seg))
    out["click"] = click
    return centres, out


def window_max(centres, values, at):
    sel = (centres >= at - WIN_S) & (centres <= at + WIN_S)
    v = values[sel]
    return float(np.nanmax(v)) if np.any(np.isfinite(v)) else np.nan


def join_pvalues(x, sr, joins):
    """Stage 1: conformal p of each join for each feature, against the same track's other places."""
    from pts.stats import conformal_p
    centres, feats = features(x, sr)
    dur = len(x) / sr
    grid = np.arange(np.ceil(EXCL_S), dur - EXCL_S, 1.0)
    grid = np.array([g for g in grid if all(abs(g - j) > EXCL_S for j in joins)])
    res = {}
    for name in FEATURES:
        v = feats[name]
        null = np.array([window_max(centres, v, g) for g in grid])
        null = null[np.isfinite(null)]
        res[name] = []
        for j in joins:
            s = window_max(centres, v, j)
            res[name].append({"join_s": float(j), "stat": s, "p": conformal_p(s, null) if np.isfinite(s) else 1.0,
                              "n_null": int(len(null))})
    return res


def binomial_tail(k, n, p=0.05):
    """P(X >= k) for X ~ Binomial(n, p)."""
    from math import comb
    return float(sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1)))


def holm(pvals, alpha=0.05):
    """Holm step-down: which hypotheses are rejected."""
    order = np.argsort(pvals)
    rejected = np.zeros(len(pvals), dtype=bool)
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (len(pvals) - rank):
            rejected[i] = True
        else:
            break
    return rejected
