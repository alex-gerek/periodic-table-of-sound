"""Meter test: tracks whose right answer is 3, not a power of two.

Three independent cues for how many pulses make a bar, none of them told the meter:
1. Drums: comb score of the drum onset envelope at 2, 3 and 4 pulses.
2. Bass: the same on the bass stem (in a waltz the bass plays beat 1 only).
3. Harmony: the period of chord changes in the pitched stems, searched freely over 1-8 s,
   expressed in pulses.
Six pulses is a multiple of both 2 and 3, so it is left out of the comparison of cues 1 and 2.

Also, for 6/8: is each pulse divided into 3 or into 2? Comb score of the drum envelope at
1/3 and 1/2 of the pulse.

Writes results.md and results.json next to this file.
"""
import glob
import json
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from pts import periodicity as P          # noqa: E402
from pts.zscale import z_of               # noqa: E402

MDIR = os.path.join(ROOT, "data", "material", "meters")
NOT_PITCHED = ("Drums", "Percussion", "Bass", "Vocals")


def load_sum(paths):
    mix, sr = None, None
    for p in paths:
        x, sr = sf.read(p, always_2d=True)
        x = P.mono(x)
        mix = x if mix is None else mix[:len(x)] + x[:len(mix)]
    return mix, sr


def combs(env, fs, tau, mults):
    r = P.autocorr(env, int((max(mults) * 4 + 1) * tau * fs) + 4)
    out = {}
    for n in mults:
        k = int(round(n * tau * fs))
        out[n] = P.comb_score(r, k, 4) if k >= 2 else None
    return out


def measure(folder):
    files = sorted(glob.glob(os.path.join(folder, "*.wav")))
    drums, sr = load_sum([f for f in files if "Drums" in os.path.basename(f)])
    env, fs = P.onset_envelope(drums, sr)
    pulse = P.envelope_periodicity(env, fs, 0.25, 2.0)
    res = {"pulse_tau": pulse.tau, "pulse_bpm": 60 / pulse.tau, "pulse_candidates": pulse.candidates,
           "drums": combs(env, fs, pulse.tau, (2, 3, 4)),
           "subdivision": combs(env, fs, pulse.tau, (1 / 3, 1 / 2))}
    bass_files = [f for f in files if "Bass" in os.path.basename(f)]
    if bass_files:
        bass, _ = load_sum(bass_files)
        benv, bfs = P.onset_envelope(bass, sr)
        res["bass"] = combs(benv, bfs, pulse.tau, (2, 3, 4))
    pitched, _ = load_sum([f for f in files if not any(s in os.path.basename(f) for s in NOT_PITCHED)])
    hc, hfs = P.harmonic_change(pitched, sr)
    h = P.envelope_periodicity(hc, hfs, 1.0, 8.0)
    res.update({"harm_tau": h.tau, "harm_strength": h.strength, "harm_candidates": h.candidates})
    if h.tau:
        res.update({"harm_in_pulses": h.tau / pulse.tau, "harm_dz": z_of(h.tau) - z_of(pulse.tau)})
    return res


def winner(d):
    d = {k: v for k, v in d.items() if v is not None}
    return max(d, key=d.get) if d else None


def main():
    res = {}
    for folder in sorted(glob.glob(os.path.join(MDIR, "meter_*"))):
        if glob.glob(os.path.join(folder, "*.wav")):
            res[os.path.basename(folder)] = measure(folder)
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump({k: {kk: (vv if not isinstance(vv, dict) else {str(a): b for a, b in vv.items()}) for kk, vv in v.items()}
                   for k, v in res.items()}, f, indent=1, default=float)
    fmt = lambda d: " / ".join(f"{d[n]:.2f}" if d.get(n) is not None else "–" for n in (2, 3, 4))
    L = ["# Meter test: measured", "",
         "Comb scores at 2 / 3 / 4 pulses (higher = the pattern repeats more strongly with that period).", "",
         "| Track | Pulse | Drums 2/3/4 | Drums say | Bass 2/3/4 | Bass says | Chord changes | In pulses | ΔZ | r |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for name, m in res.items():
        b = m.get("bass", {})
        h = (f"{m['harm_tau']:.3f} s | {m['harm_in_pulses']:.2f} | {m['harm_dz']:.3f} | {m['harm_strength']:.2f}"
             if m.get("harm_tau") else "not found | | | ")
        L.append(f"| {name} | {m['pulse_bpm']:.1f} BPM | {fmt(m['drums'])} | {winner(m['drums'])} | "
                 f"{fmt(b) if b else '–'} | {winner(b) if b else '–'} | {h} |")
    L += ["", "Division of the pulse (drums): comb at 1/3 and 1/2 of the pulse.", "",
          "| Track | 1/3 pulse | 1/2 pulse |", "|---|---|---|"]
    for name, m in res.items():
        s = m["subdivision"]
        L.append(f"| {name} | {s[1 / 3]:.2f} | {s[1 / 2]:.2f} |")
    with open(os.path.join(HERE, "results.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
