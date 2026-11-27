"""Ladder v2: each level confirmed by its calibrated surrogate p (journal step 2026-11-27-ladder-002).

Same search as pts/ladder.py (seed range, divisions, groupings, accent test, DIV_SHARE); only the
confirmation of a level differs:
  v1  confirm_period: significance >= 5 sigma, each half >= 5/sqrt(2), return >= 5, >= 4 repetitions
  v2  S = min(significance, return, sqrt(2) x weaker half) against K shuffles of the same envelope,
      p = (1 + #null >= S) / (K + 1) <= ALPHA, and >= 4 repetitions
Optional smoothing (arm v2b): the envelope is smoothed by a Gaussian of sd = sm x lag before S,
on the track and on each surrogate alike. For the seed the lag is the candidate the search picks.

    from ladder_v2 import ladder
    levels = ladder(x, sr, sm=0.0)
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from pts import ladder as L1          # noqa: E402
from pts import periodicity as P      # noqa: E402
from pts.stats import shuffle_pieces  # noqa: E402

K = 199
ALPHA = 0.01
SEED = 20261127
MIN_REPS = P.MIN_REPS
FROZEN_SM = 0.02          # chosen by the selection rule on run 20261127T151356Z-dev (arm v2b_0.02), frozen


def smooth(e, sd):
    """Gaussian smoothing with sd in samples (none below half a sample)."""
    if sd < 0.5:
        return e
    h = int(np.ceil(3 * sd))
    k = np.exp(-0.5 * (np.arange(-h, h + 1) / sd) ** 2)
    return np.convolve(e, k / k.sum(), mode="same")


def _s_at(track, fs, tau, tau_lo):
    c = P.confirm_period(track, fs, P.Periodicity(tau, 0.0), tau_lo, P.autocorr, z_min=0.0, min_reps=0.0)
    ev = c.evidence
    if "significance" not in ev:
        return 0.0, tau
    return float(min(ev["significance"], ev["return"], np.sqrt(2.0) * min(ev["significance_halves"]))), tau


def _s_search(track, fs, lo, hi, tau_lo):
    r = P.autocorr(track, int(P.N_MULT * hi * fs) + 2)
    cand = P.pick_period(r, fs, lo, hi, n_mult=P.N_MULT)
    if cand.tau is None:
        return 0.0, None
    return _s_at(track, fs, cand.tau, tau_lo)[0], cand.tau


def statistic(env, fs, sm, tau_lo, lag=None, search=None):
    """S of an envelope: at a fixed lag, or after the seed search in [lo, hi). Returns (S, tau)."""
    if lag is not None:
        return _s_at(smooth(env, sm * lag * fs), fs, lag, tau_lo)
    lo, hi = search
    if sm <= 0:
        return _s_search(env, fs, lo, hi, tau_lo)
    r = P.autocorr(env, int(P.N_MULT * hi * fs) + 2)
    cand = P.pick_period(r, fs, lo, hi, n_mult=P.N_MULT)
    if cand.tau is None:
        return 0.0, None
    return _s_at(smooth(env, sm * cand.tau * fs), fs, cand.tau, tau_lo)


def surrogate_test(env, fs, sm, tau_lo, rng, lag=None, search=None, full=False):
    """(passes, p, S, tau). Stops early once the test cannot pass, unless full=True (then p is exact)."""
    s_obs, tau = statistic(env, fs, sm, tau_lo, lag, search)
    if tau is None or not s_obs > 0:
        return False, 1.0, s_obs, tau
    if len(env) / (tau * fs) < MIN_REPS:
        return False, 1.0, s_obs, tau
    lo = max(1, int(round(tau_lo * fs / 3)))
    hi = max(lo, int(round(tau_lo * fs)))
    n_ge, limit = 0, int(np.floor(ALPHA * (K + 1))) - 1          # passes iff n_ge <= limit (1 for K = 199)
    for i in range(K):
        s, _ = statistic(shuffle_pieces(env, rng, lo, hi), fs, sm, tau_lo, lag, search)
        n_ge += s >= s_obs
        if n_ge > limit and not full:
            return False, None, s_obs, tau                     # p > ALPHA, not computed exactly
    p = (1 + n_ge) / (K + 1)
    return p <= ALPHA, p, s_obs, tau


def _confirm(env, fs, tau, sm, rng):
    ok, p, s, _ = surrogate_test(env, fs, sm, min(L1.SEED_LO, 0.5 * tau), rng, lag=tau)
    return ok, s, p


def ladder(x, sr, sm=FROZEN_SM, seed=SEED, z_acc=None):
    z_acc = L1.Z_ACC if z_acc is None else z_acc
    rng = np.random.default_rng(seed)
    x = P.mono(np.asarray(x, dtype=np.float64))
    env, fs = P.onset_envelope(x, sr)
    ok, p, s, tau = surrogate_test(env, fs, sm, L1.SEED_LO, rng, search=(L1.SEED_LO, L1.SEED_HI))
    if not ok:
        return []
    levels = [{"tau": tau, "step": None, "z": s, "p": p, "role": "seed"}]

    hi, _ = L1.high_envelope(x, sr)
    tracks = [(e, P.autocorr(e, int(L1.SEED_HI * 1.05 * fs) + 2)) for e in (env, hi)]
    l = tau
    while True:
        best = None
        for k in (2, 3):
            if l / k < L1.LEVEL_MIN:
                continue
            for e, re in tracks:
                pos, val = L1._at(re, l / k * fs)
                _, top = L1._at(re, l * fs)
                if pos is None or top is None or top <= 0 or val < L1.DIV_SHARE * top:
                    continue
                ok, s, p = _confirm(e, fs, pos / fs, sm, rng)
                if ok and (best is None or s > best[2]):
                    best = (k, pos / fs, s, p)
        if best is None:
            break
        k, l, s, p = best
        levels.insert(0, {"tau": l, "step": k, "z": s, "p": p, "role": "division"})

    feats = L1.band_envelopes(x, sr)
    l = tau
    while True:
        best = None
        for k in (2, 3):
            if k * l > L1.LEVEL_MAX:
                continue
            z = L1.accent_t(feats, fs, l, k)
            if z >= z_acc and (best is None or z > best[2]):
                ok, s, p = _confirm(env, fs, k * l, sm, rng)
                if ok:
                    best = (k, k * l, z, p)
        if best is None:
            break
        k, l, z, p = best
        levels.append({"tau": l, "step": k, "z": z, "p": p, "role": "grouping"})
    return levels
