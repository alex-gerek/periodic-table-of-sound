"""Natural vibrato in real recordings.

Method (single-voice): the waveform pitch tracker of pts/periodicity.py, octave-error
cleaning, then for every held note (a voiced run of at least 0.6 s) the note is removed
with a 0.5 s running median and the remaining swing is autocorrelated between 0.1 and
0.35 s (about 3 to 10 Hz). Depth = sqrt(2) * standard deviation in cents.

Held notes are cut into 1 s windows (step 0.5 s), because vibrato is local in time.
A window counts as vibrato when r >= 0.5, depth >= 8 cents and the rate is 4 to 8.5 Hz.
The same gate is used for every recording. It is checked against two controls:
- the piano (a piano cannot play vibrato): the share it lets through is the false-alarm level;
- the piano with 15 cents at 5.5 Hz written in: the detector must find it.

The tracker needs one voice. Recordings with accompaniment (the cello with orchestra, the
violin with piano) are run too, but their numbers mostly measure tracker failure; see README.

Writes results.md and results.json next to this file.
"""
import json
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "experiments", "2026-11-10_periodicity_column"))
from pts import periodicity as P          # noqa: E402
from pts.zscale import z_of, period_of    # noqa: E402
from vibrato_injection import add_vibrato  # noqa: E402

M = os.path.join(ROOT, "data", "material")
# label, file, fmin, fmax, kind
RECS = [
    ("Soprano, Suno (lead vocal stem)", "vibrato/vibrato_soprano_01/0 Lead Vocals.wav", 150, 1400, "solo"),
    ("Baritone, Suno (lead vocal stem)", "vibrato/vibrato_baritone_01/0 Lead Vocals.wav", 70, 700, "solo"),
    ("Violin, Bach Partita 3 (Telmanyi, historic, solo)", "arias/violin_bach-partita3_telmanyi.mp3", 180, 2000, "solo"),
    ("Violin, Salut d'amour (Salvador, with piano)", "arias/violin_salut-d-amour_elgar_salvador.mp3", 180, 2000, "mix"),
    ("Cello, The Swan (with orchestra)", "arias/cello_swan_saint-saens_seattle-youth-so.mp3", 60, 1000, "mix"),
    ("Piano, Moonlight Adagio (control)", "arias/piano_moonlight-adagio_beethoven_control.mp3", 60, 1000, "control"),
]
GATE = {"r": 0.5, "depth": 8.0, "rate_lo": 4.0, "rate_hi": 8.5}
FS = 100.0


def held_notes(x, sr, fmin, fmax, min_run_s=0.6, detrend_s=0.5, win_s=1.0, step_s=0.5):
    """Vibrato is local in time: a held note can start straight and swing only at its end.

    Each held note is cut into windows of win_s (step step_s). In each window the note is
    removed with a running median and the swing is autocorrelated. Notes shorter than one
    window are analysed as a whole.
    """
    _, per = P.pitch_track(x, sr, fmin, fmax, frame_s=0.05, hop_s=0.01)
    cents = P.clean_cents(1200 * np.log2(1 / per / 440.0), FS)
    ok = np.isfinite(cents)
    k = int(detrend_s * FS) | 1
    W, H = int(win_s * FS), int(step_s * FS)
    wins, start = [], None
    for i, flag in enumerate(np.append(ok, False)):
        if flag and start is None:
            start = i
        elif not flag and start is not None:
            if (i - start) / FS >= min_run_s:
                c = cents[start:i]
                hp_all = c - P.running_median(c, k)
                spans = [(0, len(c))] if len(c) < W + k else [(a, a + W) for a in range(k // 2, len(c) - k // 2 - W + 1, H)]
                for a_, b_ in spans:
                    hp = hp_all[a_:b_] if len(c) >= W + k else hp_all[k // 2: len(c) - k // 2]
                    if len(hp) < 40:
                        continue
                    p = P.pick_period(P.autocorr(hp, 45), FS, 0.1, 0.35)
                    wins.append({"t": (start + a_) / FS, "dur": len(hp) / FS,
                                 "note_hz": float(440 * 2 ** (np.median(c[a_:b_]) / 1200)),
                                 "rate": None if p.tau is None else 1 / p.tau, "r": p.strength,
                                 "depth": float(np.sqrt(2) * hp.std())})
            start = None
    return wins, float(ok.mean())


def summary(notes):
    vib = [n for n in notes if n["rate"] and n["r"] >= GATE["r"] and n["depth"] >= GATE["depth"]
           and GATE["rate_lo"] <= n["rate"] <= GATE["rate_hi"]]
    tot = sum(n["dur"] for n in notes)
    s = {"held_notes": len(notes), "vibrato_notes": len(vib), "held_seconds": tot,
         "share": (sum(n["dur"] for n in vib) / tot) if tot else 0.0}
    if vib:
        rates = np.array([n["rate"] for n in vib]); depths = np.array([n["depth"] for n in vib])
        s.update({"rate_median": float(np.median(rates)), "rate_p10": float(np.percentile(rates, 10)),
                  "rate_p90": float(np.percentile(rates, 90)), "depth_median": float(np.median(depths)),
                  "depth_p10": float(np.percentile(depths, 10)), "depth_p90": float(np.percentile(depths, 90))})
        tau = 1 / s["rate_median"]
        s.update({"tau": tau, "z": z_of(tau), "row": period_of(z_of(tau))})
    return s


def line(label, s, kind):
    base = f"| {label} | {kind} | {s['held_seconds']:.0f} s | {100 * s['share']:.0f}% |"
    if s["vibrato_notes"]:
        return base + (f" {s['rate_median']:.2f} Hz ({s['rate_p10']:.2f}–{s['rate_p90']:.2f}) | ±{s['depth_median']:.0f} "
                       f"({s['depth_p10']:.0f}–{s['depth_p90']:.0f}) | {s['z']:.2f} | {s['row']} |")
    return base + " – | – | – | – |"


def main():
    res = {}
    for label, rel, fmin, fmax, kind in RECS:
        x, sr = sf.read(os.path.join(M, rel), always_2d=True)
        x = P.mono(x)
        notes, voiced = held_notes(x, sr, fmin, fmax)
        s = summary(notes)
        s.update({"kind": kind, "voiced_share": voiced, "duration_s": len(x) / sr})
        if kind == "control":
            s["with_15c"] = summary(held_notes(add_vibrato(x, sr, 15, 5.5), sr, fmin, fmax)[0])
        res[label] = s
        print(label, {k: v for k, v in s.items() if k != "with_15c"}, flush=True)
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump({"gate": GATE, "results": res}, f, indent=1)
    L = ["# Natural vibrato in real recordings", "",
         f"Gate for a vibrato note (the same for every recording): r ≥ {GATE['r']}, depth ≥ {GATE['depth']:.0f} cents, rate {GATE['rate_lo']}–{GATE['rate_hi']} Hz. A held note is a voiced run of at least 0.6 s; it is cut into 1 s windows (step 0.5 s) and each window is judged on its own.", "",
         "| Recording | Kind | Held-note time | Share of it with vibrato | Rate, median (10–90%) | Depth in cents, median (10–90%) | Z of the period | Row |",
         "|---|---|---|---|---|---|---|---|"]
    for label, s in res.items():
        L.append(line(label, s, s["kind"]))
        if "with_15c" in s:
            L.append(line("↳ same piano + 15 cents at 5.5 Hz written in", s["with_15c"], "control"))
    with open(os.path.join(HERE, "results.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
