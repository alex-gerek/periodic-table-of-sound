"""Tempo series: one Suno prompt in 4/4, only the tempo changed.

For each track:
- Pulse: periodicity of the drum stem's onset envelope, searched over 0.25 - 2 s.
- Harmonic rhythm: periodicity of the harmonic-change curve of the pitched stems
  (everything except drums, percussion, bass and vocals), searched freely over 1 - 8 s.
  No row border is used in either search.
- Bar: 4 pulses (the prompt asked for 4/4). Its Z tells which row the bar falls into.
- dZ = Z(harmonic rhythm) - Z(pulse) must be log2 of a whole number if the metric levels
  nest, whatever the tempo.

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
from pts.zscale import z_of, period_of    # noqa: E402

T = os.path.join(ROOT, "data", "material", "tempo_series")
NOT_PITCHED = ("Drums", "Percussion", "Bass", "Vocals")


def load_sum(paths):
    mix, sr = None, None
    for p in paths:
        x, sr = sf.read(p, always_2d=True)
        x = P.mono(x)
        mix = x if mix is None else mix[:len(x)] + x[:len(mix)]
    return mix, sr


def measure(folder):
    files = sorted(glob.glob(os.path.join(folder, "*.wav")))
    drums, sr = load_sum([f for f in files if "Drums" in f])
    env, fs = P.onset_envelope(drums, sr)
    pulse = P.envelope_periodicity(env, fs, 0.25, 2.0)
    r = P.autocorr(env, int(3 * fs))
    levels = {}
    for n in (0.5, 1, 2, 4):
        k = int(round(n * pulse.tau * fs))
        if 2 <= k < len(r) - 2:
            levels[n] = {"bpm": 60 / (n * pulse.tau), "comb": P.comb_score(r, k, 4)}
    pitched, _ = load_sum([f for f in files if not any(s in os.path.basename(f) for s in NOT_PITCHED)])
    hc, hfs = P.harmonic_change(pitched, sr)
    harm = P.envelope_periodicity(hc, hfs, 1.0, 8.0)
    out = {"duration_s": len(drums) / sr, "pulse_tau": pulse.tau, "pulse_bpm": 60 / pulse.tau,
           "pulse_z": z_of(pulse.tau), "pulse_strength": pulse.strength, "drum_levels": levels,
           "bar_tau": 4 * pulse.tau, "bar_z": z_of(4 * pulse.tau), "bar_row": period_of(z_of(4 * pulse.tau)),
           "harm_tau": harm.tau, "harm_strength": harm.strength, "harm_candidates": harm.candidates,
           "pulse_confirmed": pulse.confirmed, "pulse_significance": pulse.evidence.get("significance"),
           "harm_confirmed": harm.confirmed, "harm_significance": harm.evidence.get("significance"),
           "pulse_confirmation": pulse.evidence.get("reason"), "harm_confirmation": harm.evidence.get("reason")}
    if harm.tau:
        out.update({"harm_z": z_of(harm.tau), "harm_in_pulses": harm.tau / pulse.tau,
                    "dz": z_of(harm.tau) - z_of(pulse.tau)})
    return out


def main():
    res = {}
    for folder in sorted(glob.glob(os.path.join(T, "tempo_*"))):
        if not glob.glob(os.path.join(folder, "*.wav")):
            continue
        name = os.path.basename(folder)
        res[name] = measure(folder)
        print(name, {k: v for k, v in res[name].items() if k not in ("harm_candidates", "drum_levels")}, flush=True)
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=float)
    L = ["# Tempo series: measured", "",
         "A period the confirmation test rejected (issue #7) is shown in italics as a *candidate*, with the reason; it is not a measurement.", "",
         "| Track | Pulse found | Z | 4/4 bar = 4 pulses | Z of the bar | Row of the bar | Harmonic rhythm | In pulses | ΔZ to the pulse | r | Harmonic rhythm confirmed |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, m in res.items():
        if not m.get("harm_tau"):
            hr = "not found | | | | –"
        elif m.get("harm_confirmed") is False:
            hr = (f"*candidate {m['harm_tau']:.3f} s* | *{m['harm_in_pulses']:.2f}* | *{m['dz']:.3f}* | *{m['harm_strength']:.2f}* | "
                  f"no: {m.get('harm_confirmation')}")
        else:
            hr = (f"{m['harm_tau']:.3f} s | {m['harm_in_pulses']:.2f} | {m['dz']:.3f} | {m['harm_strength']:.2f} | "
                  f"{P.verdict(m.get('harm_confirmed'))}, {m['harm_significance']:.0f} σ")
        pulse = f"{m['pulse_bpm']:.1f} BPM ({m['pulse_tau']:.4f} s)"
        if m.get("pulse_confirmed") is False:
            pulse = f"*candidate {pulse}, not confirmed*"
        L.append(f"| {name} | {pulse} | {m['pulse_z']:.2f} | {m['bar_tau']:.3f} s | "
                 f"{m['bar_z']:.2f} | {m['bar_row']} | {hr} |")
    L += ["", "Drum-pattern strength (comb score) at fractions and multiples of the pulse found:", "",
          "| Track | ½ pulse | 1 pulse | 2 pulses | 4 pulses |", "|---|---|---|---|---|"]
    for name, m in res.items():
        lv = m["drum_levels"]
        cell = lambda n: f"{lv[n]['comb']:.2f} ({lv[n]['bpm']:.0f} BPM)" if n in lv else "–"
        L.append(f"| {name} | {cell(0.5)} | {cell(1)} | {cell(2)} | {cell(4)} |")
    with open(os.path.join(HERE, "results.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
