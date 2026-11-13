"""The metrical ladder of a pulse (issue #29, journal step 2026-11-13-ladder-001).

Instead of one "beat", the ladder lists the related levels of a pulse: the fastest confirmed
level, the divisions and the groupings above it (by 2 or by 3), each with its evidence. Which
level a listener calls the beat is left open: listeners differ (half time, the bar of a waltz,
the dotted beat of 6/8), and the ladder holds all of them.

    from pts.ladder import ladder, on_ladder
    levels = ladder(x, sr)   # [{"tau": s, "step": k or None, "z": evidence, "role": seed | division | grouping}]

Frozen on 2026-11-13 after the held-out check: coverage 0.965 on both held-out groove sets,
12 of 12 tapped tracks, meter 0.888 and 0.955 against baselines 0.629 and 0.731, all 120
negatives empty. The copy in experiments/2026-11-13_metrical_ladder/ladder.py is the one that
was evaluated; tests/test_ladder.py checks that both give the same ladder.
"""
import numpy as np

from . import periodicity as P

SEED_LO, SEED_HI = 0.25, 2.0      # the old rule's search range
LEVEL_MIN, LEVEL_MAX = 0.06, 4.5  # the ladder's range in seconds
Z_ACC = 2.0                       # accent t threshold; chosen on the dev grooves only (run 20261113T063038Z-tune), frozen
DIV_SHARE = 0.25                  # a division's peak must reach this share of the level's peak in the same envelope
HIGH_FMIN = 2500.0                # divisions are also looked for in the events above this (hats, shakers)


def high_envelope(x, sr):
    """Onset envelope of the high events only: 4 log bands from HIGH_FMIN to 11 kHz.

    Quiet subdivisions (hats between the beats) hardly change the full-band autocorrelation,
    which the kick and the snare dominate, so they are looked for here as well.
    """
    Pw, fs = P.stft_power(x, sr, 1024, 0.005)
    B = 10 ** (P.log_bands(Pw, sr, 1024, 4, HIGH_FMIN, 11000.0) / 10 * 0.3)
    return np.maximum(np.diff(B, axis=0, prepend=B[:1]), 0.0).sum(axis=1), fs


ACCENT_BANDS = ((40.0, 150.0), (150.0, 2500.0), (2500.0, 11000.0))   # kick, snare body, hats


def band_envelopes(x, sr):
    """Onset envelopes of three bands (low, middle, high)."""
    Pw, fs = P.stft_power(x, sr, 1024, 0.005)
    out = []
    for lo, hi in ACCENT_BANDS:
        B = 10 ** (P.log_bands(Pw, sr, 1024, 3, lo, hi) / 10 * 0.3)
        out.append(np.maximum(np.diff(B, axis=0, prepend=B[:1]), 0.0).sum(axis=1))
    return out


def strengths(e, fs, tau):
    """Strength of each event of a level: the envelope maximum near each grid point."""
    lag = tau * fs
    m = int((len(e) - 1) // lag)
    if m < 8:
        return None
    grid = np.arange(m) * lag
    fold = [np.mean(e[np.round(grid + ph).astype(int).clip(0, len(e) - 1)]) for ph in range(int(lag))]
    phase = int(np.argmax(fold))
    w = max(1, int(0.1 * lag))
    centres = np.round(phase + grid).astype(int)
    return np.array([e[max(0, c - w):c + w + 1].max() if c - w < len(e) else 0.0 for c in centres])


def accent_t(feats, fs, tau, k):
    """Evidence that every k-th event of a level differs from the others (Welch t, best band and offset)."""
    best = 0.0
    for e in feats:
        s = strengths(e, fs, tau)
        if s is None:
            return 0.0
        s = s[: len(s) // k * k]
        idx = np.arange(len(s)) % k
        for c in range(k):
            a, b = s[idx == c], s[idx != c]
            if len(a) < 4:
                continue
            se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
            if se > 0:
                best = max(best, abs(a.mean() - b.mean()) / se)
    return float(best)


def _confirm(env, fs, tau):
    cand = P.Periodicity(tau, 0.0)
    return P.confirm_period(env, fs, cand, min(SEED_LO, 0.5 * tau), P.autocorr)


def _at(r, lag):
    """Position and height of the autocorrelation peak within 2% of a lag."""
    if lag * 1.02 >= len(r) - 1:
        return None, None
    return P._peak_near(r, lag)


def ladder(x, sr, z_acc=None):
    z_acc = Z_ACC if z_acc is None else z_acc
    x = P.mono(np.asarray(x, dtype=np.float64))
    env, fs = P.onset_envelope(x, sr)
    seed = P.envelope_periodicity(env, fs, SEED_LO, SEED_HI)
    if not seed.confirmed:
        return []
    n = len(env)
    r = P.autocorr(env, int(LEVEL_MAX * 1.05 * fs) + 2)
    levels = [{"tau": seed.tau, "step": None, "z": seed.evidence["significance"], "role": "seed"}]

    hi, _ = high_envelope(x, sr)
    tracks = [(e, P.autocorr(e, int(SEED_HI * 1.05 * fs) + 2)) for e in (env, hi)]
    l = seed.tau                                  # down: divisions by 2 or by 3, in the full or the high band
    while True:
        best = None
        for k in (2, 3):
            if l / k < LEVEL_MIN:
                continue
            for e, re in tracks:
                pos, val = _at(re, l / k * fs)
                _, top = _at(re, l * fs)
                if pos is None or top is None or top <= 0 or val < DIV_SHARE * top:
                    continue                      # a bump inside one event, not a level of its own
                c = _confirm(e, fs, pos / fs)
                if c.confirmed and (best is None or c.evidence["significance"] > best[2]):
                    best = (k, pos / fs, c.evidence["significance"])
        if best is None:
            break
        k, l, z = best
        levels.insert(0, {"tau": l, "step": k, "z": z, "role": "division"})

    feats = band_envelopes(x, sr)
    l = seed.tau                                  # up: groupings by 2 or by 3, from the accents
    while True:
        best = None
        for k in (2, 3):
            if k * l > LEVEL_MAX:
                continue
            z = accent_t(feats, fs, l, k)
            if z >= z_acc and _confirm(env, fs, k * l).confirmed and (best is None or z > best[2]):
                best = (k, k * l, z)
        if best is None:
            break
        k, l, z = best
        levels.append({"tau": l, "step": k, "z": z, "role": "grouping"})
    return levels


def on_ladder(levels, beat, tol=0.03):
    """Index of the level within tol of the beat, or None."""
    for i, lv in enumerate(levels):
        if abs(lv["tau"] / beat - 1) <= tol:
            return i
    return None
