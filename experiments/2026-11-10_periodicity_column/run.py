"""Measure the Periodicity column of the table on the ground-truth stems.

For every element: measured tau, its Z, the row it falls into, and whether that row is
the one the second edition predicted. Then internal consistency checks (the periods of
one track must nest as whole-number ratios) and the time-compression test on real drums.

Nothing here was tuned on these stems: every parameter was fixed by the synthetic tests
in tests/test_periodicity.py, so all three tracks are held-out data for this step.

Usage: python run.py   (writes results.json and results.md next to this file)
"""
import json
import os
import sys
import time

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from pts import periodicity as P                      # noqa: E402
from pts.zscale import z_of, period_of, period_bounds, PERIODS  # noqa: E402

TRACKS = {
    "GRAVITY": os.path.join(ROOT, "data", "stems", "gravity"),
    "Metro": os.environ.get("PTS_METRO_STEMS", os.path.join(ROOT, "data", "stems", "metro")),
    "Pure voltage": os.path.join(ROOT, "data", "stems", "pure_voltage"),
}
# element symbol -> row predicted by the second edition
PREDICTED = {"F0 bass": 2, "F0 vocal": 2, "Vb": 3, "Sd": 3, "Pu": 4, "Sc": 4, "Me": 5, "Lp": 6, "Rp": 7}
VB_MIN_R = 0.3
NAMES = {"F0 bass": "Pitch (bass)", "F0 vocal": "Pitch (lead vocal)", "Vb": "Vibrato", "Sd": "Subdivision",
         "Pu": "Pulse", "Sc": "Sidechain pump", "Me": "Meter", "Lp": "Loop", "Rp": "Repetition"}
SOURCE = {"F0 bass": "Bass stem, waveform", "F0 vocal": "Lead vocal stem, waveform",
          "Vb": "Lead vocal, pitch track", "Sd": "Drums, onset envelope", "Pu": "Drums, onset envelope",
          "Sc": "Bass stem, level track", "Me": "Drums, onset envelope", "Lp": "Mix, spectral frames",
          "Rp": "Mix, spectral frames"}


def load(folder, key):
    name = next(f for f in os.listdir(folder) if f.lower().endswith(".wav") and key.lower() in f.lower())
    x, sr = sf.read(os.path.join(folder, name), always_2d=True)
    return P.mono(x), sr


def load_mix(folder):
    mix, sr = None, None
    for f in sorted(os.listdir(folder)):
        if f.lower().endswith(".wav"):
            x, sr = sf.read(os.path.join(folder, f), always_2d=True)
            x = P.mono(x)
            mix = x if mix is None else mix[:len(x)] + x[:len(mix)]
    return mix, sr


def entry(tau, strength=None, lo=None, hi=None, extra=None):
    if tau is None:
        return {"tau": None}
    z = z_of(tau)
    e = {"tau": tau, "z": z, "row": period_of(z), "strength": strength}
    if lo is not None:
        e.update({"tau_p10": lo, "tau_p90": hi, "z_p10": z_of(lo), "z_p90": z_of(hi)})
    if extra:
        e.update(extra)
    return e


def per_entry(p):
    extra = {"candidates": p.candidates}
    if p.confirmed is not None:                   # confirmation test (issue #7)
        extra.update({"confirmed": p.confirmed, "significance": p.evidence.get("significance"),
                      "confirmation": p.evidence.get("reason")})
    return entry(p.tau, p.strength, extra=extra)


def measure(folder):
    res = {}
    bass, sr = load(folder, "bass")
    vocal, _ = load(folder, "lead vocal")
    drums, _ = load(folder, "drums")
    mix, _ = load_mix(folder)

    b = P.pitch(bass, sr, 30, 300)
    res["F0 bass"] = entry(b["tau"], None, b["tau_p10"], b["tau_p90"], {"voiced_share": b["voiced_share"]})
    v = P.pitch(vocal, sr, 70, 1000)
    res["F0 vocal"] = entry(v["tau"], None, v["tau_p10"], v["tau_p90"], {"voiced_share": v["voiced_share"]})
    vb, runs = P.vibrato(vocal, sr)
    # r >= 0.3 is the floor calibrated in vibrato_injection.py: 15 cents written into a
    # real vocal gives r = 0.33, the same vocal without vibrato r <= 0.09
    res["Vb"] = per_entry(vb) if vb.strength >= VB_MIN_R else {"tau": None, "best_r": vb.strength}
    res["Vb"]["voiced_runs"] = runs

    env, fs = P.onset_envelope(drums, sr)
    res["Sd"] = per_entry(P.envelope_periodicity(env, fs, *period_bounds(3)))
    res["Pu"] = per_entry(P.envelope_periodicity(env, fs, *period_bounds(4)))
    res["Me"] = per_entry(P.envelope_periodicity(env, fs, *period_bounds(5)))

    lv, lfs = P.level_track(bass, sr)
    res["Sc"] = per_entry(P.envelope_periodicity(lv, lfs, *period_bounds(4)))

    F, ffs = P.frame_features(mix, sr)
    res["Lp"] = per_entry(P.feature_periodicity(F, ffs, *period_bounds(6)))
    dur = len(mix) / sr
    res["Rp"] = per_entry(P.feature_periodicity(F, ffs, period_bounds(7)[0], dur / 2))

    # free search: the same tools with the lag range NOT taken from the predicted row.
    # Only elements whose definition does not already contain a time range can be tested
    # this way; for Pulse, Subdivision, Meter and Pitch the row follows from the definition.
    vbf, _ = P.vibrato(vocal, sr, tau_lo=0.03, tau_hi=1.0)
    res["free"] = {
        "Vb": per_entry(vbf),
        "Sc": per_entry(P.envelope_periodicity(lv, lfs, 0.05, 4.0)),
        "Lp": per_entry(P.feature_periodicity(F, ffs, 1.0, 64.0)),
    }

    # time-compression test on real drums: 32x faster, the waveform detector must find
    # an envelope period divided by 32, i.e. the same column 5 octaves lower
    seg = drums[int(30 * sr): int(62 * sr)]
    y = P.compress_time(seg, 32)
    pc = P.pitch(y, sr, 30, 1000)
    env_s, fs_s = P.onset_envelope(seg, sr)
    r = P.autocorr(env_s, int(2.5 * fs_s))
    if pc:
        target = pc["tau"] * 32
        k = int(round(target * fs_s))
        res["compression"] = {"pitch_hz": 1 / pc["tau"], "tau_x32": target, "z_compressed": z_of(pc["tau"]),
                              "z_original": z_of(target), "env_autocorr_at_tau_x32": float(r[k - 1:k + 2].max()),
                              "pulse_multiple": target / res["Pu"]["tau"] if res["Pu"]["tau"] else None}
    res["duration_s"] = dur
    return res


def usable(e):
    """A period counts as measured if it was found and not rejected by the confirmation."""
    return e.get("tau") is not None and e.get("confirmed") is not False


def consistency(res):
    def ratio(a, b):
        return res[a]["tau"] / res[b]["tau"] if usable(res[a]) and usable(res[b]) else None
    out = {}
    for a, b in (("Pu", "Sd"), ("Me", "Pu"), ("Lp", "Me"), ("Sc", "Pu")):
        q = ratio(a, b)
        out[f"{a}/{b}"] = {"ratio": q, "nearest_integer": None if q is None else round(q),
                           "error": None if q is None else abs(q - round(q)) / round(q) if round(q) else None}
    return out


FREE_RANGE = {"Vb": "30 ms – 1 s of the pitch track", "Sc": "50 ms – 4 s of the level track",
              "Lp": "1 – 64 s of the spectral frames"}


def fmt_t(t):
    return "–" if t is None else (f"{t * 1e3:.2f} ms" if t < 1 else f"{t:.2f} s")


def report(all_res):
    L = ["# Periodicity column measured on the ground-truth stems", "",
         f"*Generated by `run.py` on {time.strftime('%Y-%m-%d %H:%M')}.*", "",
         "Each cell shows the measured τ, its Z and the row it falls into. ✓ means the row is the one the second edition predicted.",
         "A period the confirmation test rejected (issue #7) is shown in italics as a *candidate* with the reason, and it is not counted. Pitch and Vibrato have their own tests and are not passed through this one.", ""]
    head = "| Element | Source | Predicted row | " + " | ".join(all_res) + " |"
    L += [head, "|" + "---|" * (3 + len(all_res))]
    hits, total, rejected = 0, 0, 0
    for s, pred in PREDICTED.items():
        cells = []
        for name, res in all_res.items():
            e = res[s]
            if e["tau"] is None:
                cells.append("not found ✗")
                total += 1
                continue
            if e.get("confirmed") is False:
                rejected += 1
                cells.append(f"*candidate {fmt_t(e['tau'])}, Z {e['z']:.2f}, row {e['row']}: not confirmed, {e.get('confirmation')}*")
                continue
            ok = e["row"] == pred
            hits += ok
            total += 1
            rng = f" ({e['z_p10']:.1f}–{e['z_p90']:.1f})" if "z_p10" in e else ""
            sig = f", {e['significance']:.0f} σ" if e.get("confirmed") else ""
            cells.append(f"{fmt_t(e['tau'])}, Z {e['z']:.2f}{rng}, row {e['row']} {'✓' if ok else '✗'}{sig}")
        L.append(f"| {NAMES[s]} | {SOURCE[s]} | {pred}. {PERIODS[pred - 1]} | " + " | ".join(cells) + " |")
    L += ["", f"**{hits} of {total} measurements fall into their predicted row.** {rejected} candidates were not confirmed and are not counted. For Pitch, Subdivision, Pulse and Meter this is true by definition (see README); it is not evidence.", "",
          "The Metro lead vocal stem is nearly silent (voiced in under 0.1% of frames), so its vocal pitch and vibrato cells are not reliable.", "",
          "## Consistency: the periods of one track nest as whole numbers", "",
          "| Ratio | " + " | ".join(all_res) + " |", "|" + "---|" * (1 + len(all_res))]
    for key in ("Pu/Sd", "Me/Pu", "Lp/Me", "Sc/Pu"):
        row = []
        for res in all_res.values():
            c = res["consistency"][key]
            row.append("– (a period is missing or not confirmed)" if c["ratio"] is None else f"{c['ratio']:.3f} ≈ {c['nearest_integer']} (off {100 * c['error']:.1f}%)")
        L.append(f"| {key} | " + " | ".join(row) + " |")
    L += ["", "## Time-compression test on real drums", "",
          "32 seconds of the drum stem played 32 times faster. The pitch detector (a waveform tool) must find a period that, multiplied back by 32, is a period of the original onset envelope: the same column, exactly 5 rows of Z lower.", "",
          "| Track | Pitch of the compressed drums | × 32 | Z after → before | Envelope autocorrelation at that lag | In pulses of the original |",
          "|---|---|---|---|---|---|"]
    for name, res in all_res.items():
        c = res.get("compression")
        if not c:
            L.append(f"| {name} | not found | | | | |")
            continue
        q = c["pulse_multiple"]
        L.append(f"| {name} | {c['pitch_hz']:.1f} Hz | {fmt_t(c['tau_x32'])} | {c['z_compressed']:.2f} → {c['z_original']:.2f} | "
                 f"{c['env_autocorr_at_tau_x32']:.2f} | {'–' if q is None else f'{q:.3f} pulses'} |")
    L += ["", "## Free search: lag range not taken from the predicted row", "",
          "| Element | Searched | " + " | ".join(all_res) + " |", "|" + "---|" * (2 + len(all_res))]
    for s_, rng_ in FREE_RANGE.items():
        cells = []
        for res in all_res.values():
            e = res["free"][s_]
            if e["tau"] is None:
                cells.append("not found")
            elif e.get("confirmed") is False:
                cells.append(f"*candidate {fmt_t(e['tau'])}, Z {e['z']:.2f}, row {e['row']}: not confirmed*")
            else:
                cells.append(f"{fmt_t(e['tau'])}, Z {e['z']:.2f}, row {e['row']} {'✓' if e['row'] == PREDICTED[s_] else '✗'} (r = {e['strength']:.2f})")
        L.append(f"| {NAMES[s_]} | {rng_} | " + " | ".join(cells) + " |")
    return "\n".join(L) + "\n"


def main():
    all_res = {}
    for name, folder in TRACKS.items():
        t0 = time.time()
        res = measure(folder)
        res["consistency"] = consistency(res)
        all_res[name] = res
        print(f"{name}: {time.time() - t0:.0f} s", flush=True)
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump(all_res, f, indent=1, default=float)
    md = report(all_res)
    with open(os.path.join(HERE, "results.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print(md)


if __name__ == "__main__":
    main()
