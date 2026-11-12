"""Summarise a grid run and a scaling run of the envelope study (issue #21).

  python analyze.py <grid run folder> <scaling run folder>

Writes summary.md into the grid run folder and prints it. The pass criteria are the ones fixed
in the research journal before the runs (step 2026-11-12-level-001).
"""
import collections
import json
import os
import sys

import numpy as np

TIME_MED, TIME_P95, SHAPE_MAX, FALSE_DB, LIN_TOL, SCALE_TOL = 0.10, 0.20, 0.05, 1.0, 0.1, 0.05


def q(v, p):
    v = [x for x in v if x is not None and np.isfinite(x)]
    return float(np.percentile(v, p)) if v else float("nan")


def load(folder):
    return json.load(open(os.path.join(folder, "cases.json")))


def cell_pass(cs):
    te = [abs(c["time_err"]) if c["time_err"] is not None else np.inf for c in cs]
    se = [c["shape_err"] if c["shape_err"] is not None else np.inf for c in cs]
    return (np.median(te) <= TIME_MED and np.percentile(te, 95) <= TIME_P95 and np.median(se) <= SHAPE_MAX), np.median(te), np.percentile(te, 95), np.median(se)


def main():
    gdir, sdir = sys.argv[1], sys.argv[2]
    G = [c for c in load(gdir)]
    ev = [c for c in G if c["shape"] != "constant"]
    const = [c for c in G if c["shape"] == "constant"]
    L = ["# Envelope validation: summary", "", f"Grid run `{os.path.basename(gdir)}`, scaling run `{os.path.basename(sdir)}`.",
         "A cell passes when, over its shapes and seeds, the median |time error| ≤ 10%, the 95th percentile ≤ 20%, and the median shape error ≤ 0.05.", ""]

    # 1. clean tonal carriers: the valid region in cycles
    for m in ("analytic", "rms"):
        L += [f"## 1. Clean tonal carriers, {m}: pass map (rows: true time T, columns: window w)", "",
              "Each cell: passing carriers out of 8 (sine and harmonic at 55, 220, 880, 3520 Hz), SNR ∞.", "",
              "| T \\ w | " + " | ".join(f"{w * 1e3:g} ms" for w in sorted({c['w'] for c in ev})) + " |", "|---|" + "---|" * len({c['w'] for c in ev})]
        for T in sorted({c["T"] for c in ev}):
            row = []
            for w in sorted({c["w"] for c in ev}):
                n = 0
                for kind in ("sine", "harmonic"):
                    for f0 in (55, 220, 880, 3520):
                        cs = [c for c in ev if c["method"] == m and c["T"] == T and c["w"] == w and c["carrier"] == kind and c["f0"] == f0 and not np.isfinite(c["snr"])]
                        n += cell_pass(cs)[0]
                row.append(str(n))
            L.append(f"| {T * 1e3:g} ms | " + " | ".join(row) + " |")
        L.append("")

    # 2. the rule in dimensionless form: w/T and cycles of the carrier
    L += ["## 2. Where it works, in dimensionless terms (tonal carriers, SNR ∞)", "",
          "Share of passing cells by the window/time ratio w/T and the carrier cycles inside the window w·f0.", "",
          "| method | w/T ≤ 0.1, w·f0 ≥ 2 | w/T ≤ 0.25, w·f0 ≥ 2 | w/T ≤ 0.25, w·f0 < 2 | w/T 0.25–0.5 | w/T > 0.5 |", "|---|---|---|---|---|---|"]
    for m in ("analytic", "rms"):
        bins = collections.defaultdict(list)
        cells = collections.defaultdict(list)
        for c in ev:
            if c["method"] == m and c["carrier"] != "noise" and not np.isfinite(c["snr"]):
                cells[(c["T"], c["w"], c["carrier"], c["f0"])].append(c)
        for (T, w, kind, f0), cs in cells.items():
            r, cyc = w / T, w * f0
            ok = cell_pass(cs)[0]
            if r <= 0.1 and cyc >= 2: bins[0].append(ok)
            if r <= 0.25 and cyc >= 2: bins[1].append(ok)
            if r <= 0.25 and cyc < 2: bins[2].append(ok)
            if 0.25 < r <= 0.5: bins[3].append(ok)
            if r > 0.5: bins[4].append(ok)
        L.append(f"| {m} | " + " | ".join(f"{100 * np.mean(bins[i]):.0f}% ({len(bins[i])})" if bins[i] else "–" for i in range(5)) + " |")
    L.append("")

    # 3. pitch: the shortest readable time per carrier (best window, analytic and rms)
    L += ["## 3. Pitch: the shortest time read within the criteria (SNR ∞, best window)", "",
          "| Carrier | f0 | analytic | rms | T·f0 at the limit (analytic) |", "|---|---|---|---|---|"]
    for kind, f0 in [("sine", f) for f in (55, 220, 880, 3520)] + [("harmonic", f) for f in (55, 220, 880, 3520)] + [("noise", 0)]:
        lim = {}
        for m in ("analytic", "rms"):
            best = None
            for T in sorted({c["T"] for c in ev}):
                if any(cell_pass([c for c in ev if c["method"] == m and c["T"] == T and c["w"] == w and c["carrier"] == kind and c["f0"] == f0 and not np.isfinite(c["snr"])])[0]
                       for w in sorted({c["w"] for c in ev})):
                    best = T
                    break
            lim[m] = best
        tf = "–" if lim["analytic"] is None or not f0 else f"{lim['analytic'] * f0:.1f}"
        L.append(f"| {kind} | {f0 or '–'} | {'none' if lim['analytic'] is None else f'{lim['analytic'] * 1e3:g} ms'} | "
                 f"{'none' if lim['rms'] is None else f'{lim['rms'] * 1e3:g} ms'} | {tf} |")
    L.append("")

    # 4. noise: additive SNR and the noise carrier
    L += ["## 4. Noise: median |time error| at the best window per cell, analytic", "",
          "| Carrier | T | SNR ∞ | 20 dB | 10 dB |", "|---|---|---|---|---|"]
    for kind, f0 in (("sine", 880), ("harmonic", 220), ("noise", 0)):
        for T in (0.005, 0.02, 0.05, 0.2):
            row = []
            for snr in (np.inf, 20.0, 10.0):
                best = min((cell_pass([c for c in ev if c["method"] == "analytic" and c["T"] == T and c["w"] == w and c["carrier"] == kind and c["f0"] == f0 and
                                       (c["snr"] == snr or (not np.isfinite(snr) and not np.isfinite(c["snr"])))])[1] for w in sorted({c["w"] for c in ev})))
                row.append(f"{100 * best:.1f}%")
            L.append(f"| {kind} {f0 or ''} | {T * 1e3:g} ms | " + " | ".join(row) + " |")
    L.append("")

    # 5. constant level and linearity
    L += ["## 5. Constant level: false change (median dB) and linearity (doubling the amplitude)", "",
          "| Carrier | method | w | false change, SNR ∞ | 20 dB | 10 dB | linearity, worst deviation from 6.02 dB |", "|---|---|---|---|---|---|---|"]
    for kind, f0 in (("sine", 55), ("sine", 880), ("harmonic", 55), ("harmonic", 880), ("noise", 0)):
        for m in ("analytic", "rms"):
            for w in (0.002, 0.005, 0.02):
                cs = [c for c in const if c["carrier"] == kind and c["f0"] == f0 and c["method"] == m and c["w"] == w]
                fc = [np.median([c["false_change_db"] for c in cs if (c["snr"] == s or (not np.isfinite(s) and not np.isfinite(c["snr"])))]) for s in (np.inf, 20.0, 10.0)]
                lin = max(abs(c["linearity_db"] - 6.0206) for c in cs)
                L.append(f"| {kind} {f0 or ''} | {m} | {w * 1e3:g} ms | {fc[0]:.2f} | {fc[1]:.2f} | {fc[2]:.2f} | {lin:.3f} dB |")
    L.append("")

    # 6. time scaling
    S = load(sdir)
    L += ["## 6. Tape-speed scaling: measured time ratio against k", "",
          "Ratio error = (T_k / T_1) / k − 1. ΔZ should equal log₂ k. Window scaled with k, or kept fixed.", "",
          "| Carrier | window | k | median |ratio error| | worst | median |ΔZ − log₂ k| | rows that changed |", "|---|---|---|---|---|---|---|"]
    for kind in ("sine", "harmonic", "noise"):
        for wmode in ("scaled", "fixed"):
            for k in (1 / 8, 1 / 4, 1 / 2, 2, 4):
                cs = [c for c in S if c["carrier"] == kind and c["window"] == wmode and c["k"] == k and c["method"] == "analytic"]
                re = [abs(c["ratio_err"]) for c in cs if c["ratio_err"] is not None]
                dz = [abs(c["dz"] - c["dz_expected"]) for c in cs if c["dz"] is not None]
                rows = sum(1 for c in cs if c["row0"] is not None and c["rowk"] is not None and c["row0"] != c["rowk"])
                miss = sum(1 for c in cs if c["ratio_err"] is None)
                L.append(f"| {kind} | {wmode} | {k:g} | {100 * np.median(re):.2f}% | {100 * max(re):.1f}% | {np.median(dz):.3f} | {rows} of {len(cs)}" + (f", {miss} unreadable" if miss else "") + " |")
    md = "\n".join(L) + "\n"
    open(os.path.join(gdir, "summary.md"), "w", encoding="utf-8").write(md)
    print(md)


if __name__ == "__main__":
    main()
