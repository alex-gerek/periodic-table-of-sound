"""Apply the frozen region (region.py) and the pre-registered criteria to the held-out runs.

  python verdict.py <holdout grid run> <holdout scaling run>

Writes verdict.md into the grid run folder and prints it.
"""
import collections
import json
import os
import sys

import numpy as np

import region as R

TIME_MED, TIME_P95, SHAPE_MAX, FALSE_DB, LIN_TOL, SCALE_TOL = 0.10, 0.20, 0.05, 1.0, 0.1, 0.05


def summarise(cs):
    te = [abs(c["time_err"]) if c["time_err"] is not None else np.inf for c in cs]
    se = [c["shape_err"] if c["shape_err"] is not None else np.inf for c in cs]
    return {"pass": bool(np.median(te) <= TIME_MED and np.percentile(te, 95) <= TIME_P95 and np.median(se) <= SHAPE_MAX),
            "med": float(np.median(te)), "p95": float(np.percentile(te, 95)), "shape": float(np.median(se))}


def main():
    gdir, sdir = sys.argv[1], sys.argv[2]
    G = json.load(open(os.path.join(gdir, "cases.json")))
    S = json.load(open(os.path.join(sdir, "cases.json")))
    ev = [c for c in G if c["shape"] != "constant"]
    const = [c for c in G if c["shape"] == "constant"]
    L = ["# Envelope: verdict on the held-out runs", "",
         f"Grid `{os.path.basename(gdir)}`, scaling `{os.path.basename(sdir)}`. Region and criteria as frozen in commit `c578dc8`.", ""]
    rows = []
    for m in ("analytic", "rms"):
        cells = collections.defaultdict(list)
        for c in ev:
            if c["method"] == m:
                cells[(c["T"], c["w"], c["carrier"], c["f0"], c["snr"])].append(c)
        inside = {k: summarise(v) for k, v in cells.items() if R.inside(k[0], k[1], k[2], k[3], k[4])}
        outside = {k: summarise(v) for k, v in cells.items() if not R.inside(k[0], k[1], k[2], k[3], k[4])}
        allin = [c for k, v in cells.items() if R.inside(*k) for c in v]
        te = [abs(c["time_err"]) for c in allin if c["time_err"] is not None]
        se = [c["shape_err"] for c in allin if c["shape_err"] is not None]
        rows.append((m, inside, outside, te, se))
    L += ["## Inside the region", "", "| Estimator | Cells passing | Cases | Median |time error| | 95th percentile | Worst | Median shape error | Worst shape error |", "|---|---|---|---|---|---|---|---|"]
    for m, inside, outside, te, se in rows:
        L.append(f"| {m} | {sum(v['pass'] for v in inside.values())} of {len(inside)} | {len(te)} | {100 * np.median(te):.2f}% | {100 * np.percentile(te, 95):.2f}% | {100 * max(te):.1f}% | {np.median(se):.4f} | {max(se):.3f} |")
    for m, inside, outside, te, se in rows:
        bad = [k for k, v in inside.items() if not v["pass"]]
        if bad:
            L += ["", f"Failing region cells, {m} (T ms, w ms, carrier, f0, SNR): " + ", ".join(f"({k[0] * 1e3:g}, {k[1] * 1e3:g}, {k[2]}, {k[3]}, {k[4]:g}): median {100 * inside[k]['med']:.1f}%, p95 {100 * inside[k]['p95']:.1f}%, shape {inside[k]['shape']:.3f}" for k in bad)]
    L += ["", "## Outside the region (for the limits)", "", "| Estimator | Cells passing outside the region | of |", "|---|---|---|"]
    for m, inside, outside, te, se in rows:
        L.append(f"| {m} | {sum(v['pass'] for v in outside.values())} | {len(outside)} |")
    L += ["", "| Condition (analytic) | Cells | Passing |", "|---|---|---|"]
    m, inside, outside, te, se = rows[0]
    groups = collections.defaultdict(list)
    for k, v in outside.items():
        T, w, kind, f0, snr = k
        if np.isfinite(snr) and snr < 20: g = "SNR 10 dB"
        elif kind == "noise": g = "noise carrier, w < 10 ms or w > T/4"
        elif w > T / 4: g = "tonal, w > T/4"
        elif w * f0 < 2: g = "tonal, fewer than 2 carrier periods in the window"
        else: g = "tonal, noisy and w < T/50 or w < 2 ms"
        groups[g].append(v["pass"])
    for g, v in sorted(groups.items()):
        L.append(f"| {g} | {len(v)} | {sum(v)} ({100 * np.mean(v):.0f}%) |")
    # constant level and linearity
    L += ["", "## Constant level and linearity (inside the region)", "", "| Estimator | Tonal: worst false change | Noise carrier: worst false change | Worst linearity deviation from 6.02 dB |", "|---|---|---|---|"]
    for m in ("analytic", "rms"):
        ins = [c for c in const if c["method"] == m and R.inside_constant(c["w"], c["carrier"], c["f0"], c["snr"])]
        ft = [c["false_change_db"] for c in ins if c["carrier"] != "noise"]
        fn = [c["false_change_db"] for c in ins if c["carrier"] == "noise"]
        lin = max(abs(c["linearity_db"] - 6.0206) for c in const if c["method"] == m)
        L.append(f"| {m} | {max(ft):.2f} dB | {max(fn):.2f} dB | {lin:.4f} dB |")
    # scaling
    L += ["", "## Tape-speed scaling inside the region (analytic, window scaled with k)", "", "| Carrier | k | Cases | Median |ratio error| | Worst | Worst |ΔZ − log₂ k| | Row changed |", "|---|---|---|---|---|---|---|"]
    for kind in ("sine", "harmonic", "noise"):
        for k in (1 / 4, 1 / 2, 2, 4):
            cs = [c for c in S if c["carrier"] == kind and c["k"] == k]
            re = [abs(c["ratio_err"]) for c in cs if c["ratio_err"] is not None]
            dz = [abs(c["dz"] - c["dz_expected"]) for c in cs if c["dz"] is not None]
            miss = sum(c["ratio_err"] is None for c in cs)
            chg = sum(1 for c in cs if c["row0"] is not None and c["rowk"] is not None and c["row0"] != c["rowk"])
            L.append(f"| {kind} | {k:g} | {len(cs)}{f' ({miss} unreadable)' if miss else ''} | {100 * np.median(re):.2f}% | {100 * max(re):.2f}% | {max(dz):.3f} | {chg} |")
    allre = [abs(c["ratio_err"]) for c in S if c["ratio_err"] is not None]
    # verdict lines
    m, inside, outside, te, se = rows[0]
    ft = [c["false_change_db"] for c in const if c["method"] == "analytic" and R.inside_constant(c["w"], c["carrier"], c["f0"], c["snr"]) and c["carrier"] != "noise"]
    lin = max(abs(c["linearity_db"] - 6.0206) for c in const if c["method"] == "analytic")
    checks = [("time error, median ≤ 10% and 95th percentile ≤ 20% in every region cell", all(v["pass"] for v in inside.values())),
              ("shape error ≤ 0.05 (median, every region cell)", all(v["shape"] <= SHAPE_MAX for v in inside.values())),
              ("constant tonal level, false change < 1 dB", max(ft) < FALSE_DB),
              ("doubling the amplitude: 6.02 ± 0.1 dB", lin <= LIN_TOL),
              ("tape-speed factor within 5%", max(allre) <= SCALE_TOL)]
    L += ["", "## Criteria (fixed before the runs)", "", "| Criterion | Held-out result |", "|---|---|"]
    L += [f"| {n} | {'**met**' if ok else '**not met**'} |" for n, ok in checks]
    md = "\n".join(L) + "\n"
    open(os.path.join(gdir, "verdict.md"), "w", encoding="utf-8").write(md)
    print(md)


if __name__ == "__main__":
    main()
