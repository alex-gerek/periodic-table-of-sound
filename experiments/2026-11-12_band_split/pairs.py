"""Controlled pairs for the band-split experiment (issue #15).

One seed fixes everything except the positions of the events: the grid step, the timbres
of kick, snare and hat, the jitter and the noise. Each seed then gives every combination of

  kick   every beat | beats 1 and 3 | 1 and 3 and the "and" of 3 | beat 1 only
  snare  none | beats 2 and 4 | every beat
  hats   every 1/2 beat | every 1/4 beat
  accent none | on beat 1

written twice: with the beat B = T (slow grid) and with the beat B = T/2 (the same pattern in a
grid twice as fast). Four beats per bar. The label is the beat the pattern was written in.
Nothing assumes that the kick marks the beat: the label comes from the grid, and in some
combinations the two grids give the same sound, which is then counted as ambiguous.
"""
import itertools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experiments", "2026-11-12_beat_level"))
import bench as B  # noqa: E402

SR = B.SR
KICKS = ("every", "1_3", "1_3_and3", "1")
SNARES = ("none", "2_4", "every")
HATS = (2, 4)
ACCENTS = (0, 1)
COMBOS = list(itertools.product(KICKS, SNARES, HATS, ACCENTS))
# Level of the hats after the first one in each beat. 0.8 marks the beat in the hats as well;
# 1.0 (the control, PTS_HAT_ACCENT=1.0) gives every hat the same level.
HAT_ACCENT = float(os.environ.get("PTS_HAT_ACCENT", "0.8"))
# Rate balance (PTS_HAT_BALANCE=1): with the beat T/2, hats are 1 or 2 per beat instead of 2 or 4,
# so their physical step (T/2 or T/4) is the same under both labels and cannot give the label away.
HAT_BALANCE = os.environ.get("PTS_HAT_BALANCE") == "1"


def base(seed):
    rng = np.random.default_rng(seed)
    return {"T": rng.uniform(0.5, 1.0), "kick": B._kick(rng), "snare": B._snare(rng), "hat": B._hat(rng),
            "hat_level": rng.uniform(0.2, 0.5), "accent": rng.uniform(1.2, 1.5), "jitter": rng.uniform(0.0, 0.01),
            "snr": rng.uniform(10, 25), "dur": 30.0, "noise_seed": int(rng.integers(1 << 30))}


def render(b, combo, beat):
    """One combination with the given beat (b['T'] or b['T'] / 2). Returns the signal."""
    kick_pos, snare_pos, hats, accent = combo
    if HAT_BALANCE and beat < b["T"] * 0.75:
        hats //= 2
    rng = np.random.default_rng(b["noise_seed"])          # the same jitter and noise draw for every combination
    x = np.zeros(int(b["dur"] * SR) + SR)
    j = lambda: rng.normal(0, b["jitter"])
    for i in range(int(b["dur"] / beat)):
        t, pos = i * beat, i % 4
        a = b["accent"] if (accent and pos == 0) else 1.0
        if kick_pos == "every" or (kick_pos in ("1_3", "1_3_and3") and pos in (0, 2)) or (kick_pos == "1" and pos == 0):
            B._place(x, t + j(), b["kick"], a)
        if kick_pos == "1_3_and3" and pos == 2:
            B._place(x, t + beat / 2 + j(), b["kick"], 0.6)
        if snare_pos == "every" or (snare_pos == "2_4" and pos in (1, 3)):
            B._place(x, t + j(), b["snare"], 0.8 * a)
        for q in range(hats):
            B._place(x, t + q * beat / hats + j(), b["hat"], b["hat_level"] * (1.0 if q == 0 else HAT_ACCENT))
    x = x[: int(b["dur"] * SR)]
    p = np.mean(x ** 2) + 1e-12
    return x + rng.standard_normal(len(x)) * np.sqrt(p / 10 ** (b["snr"] / 10))


def signals(seeds):
    """(signal, slow step T, label 'T' or 'T/2', combo, seed) for every combination and both grids."""
    for s in seeds:
        b = base(s)
        for combo in COMBOS:
            for label, beat in (("T", b["T"]), ("T/2", b["T"] / 2)):
                yield render(b, combo, beat), b["T"], label, combo, s
