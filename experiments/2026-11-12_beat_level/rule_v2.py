"""Candidate pulse rule, version 2 (issue #15).

Version 1 (`bench.rule_new`) stays unchanged, because the Ballroom adapter is pinned to it.
Version 2 adds one step, chosen on the development data (seeds 0-199, the 120 investigated
examples, and seeds 50000-50199, which were the first final set and have been looked at):

  A level that fails only the stability test (its significance, return and repetitions
  pass) is accepted when a whole multiple of it (2 to 8 times) is fully confirmed.

Why: in heavy noise (SNR 0 to 6 dB, 20 ms jitter) the beat is found, with a comb of 0.80 to
0.93 of the best and 6.0 to 6.4 sigma, but one half of the track reaches only 3.0 to 3.5
sigma against 3.54. Its multiple, 2 beats, collects more evidence and passes. A divisor of a
confirmed period is not a chance fluke in the way an isolated peak can be.
"""
import numpy as np

import bench as B

P = B.P
TOL = 0.03


def _levels(env, fs):
    r = P.autocorr(env, int(4 * B.TAU_HI * fs) + 2)
    lo, hi = int(np.floor(B.TAU_LO * fs)), min(len(r) - 2, int(np.ceil(B.TAU_HI * fs)))
    if hi <= lo:
        return []
    k = np.arange(lo, hi + 1)
    pk = k[(r[k] > r[k - 1]) & (r[k] >= r[k + 1]) & (r[k] > 0)]
    pk = [p for p in pk if r[p] >= r[max(1, int(p * (1 - B.LOCAL_MAX))):int(p * (1 + B.LOCAL_MAX)) + 2].max()]
    out = []
    for p in pk:
        T = B.refine(r, B._subpeak(r, p))
        c = B.comb_at(r, T)
        ev = P.confirm_period(env, fs, P.Periodicity(T / fs, c), B.TAU_LO, P.autocorr)
        e = ev.evidence
        strong = (e.get("significance", 0) >= P.Z_MIN and e.get("return", 0) >= P.Z_MIN
                  and e.get("repetitions", 0) >= P.MIN_REPS)
        out.append({"T": T, "comb": c, "confirmed": bool(ev.confirmed), "strong": bool(strong)})
    return out


def rule_new_v2(x, sr):
    """The shortest consistent level that is confirmed, or supported by a confirmed multiple."""
    env, fs = B.strong_envelope(x, sr)
    L = _levels(env, fs)
    if not L:
        return None
    best = max(l["comb"] for l in L)
    consistent = [l for l in L if l["comb"] >= B.CONSISTENCY * best]
    confirmed = [l for l in consistent if l["confirmed"]]
    for l in consistent:
        if l["confirmed"]:
            return l["T"] / fs
        if l["strong"] and any(abs(m["T"] / (q * l["T"]) - 1) <= TOL for m in confirmed for q in range(2, 9)):
            return l["T"] / fs
    return P.envelope_periodicity(env, fs, B.TAU_LO, B.TAU_HI).tau
