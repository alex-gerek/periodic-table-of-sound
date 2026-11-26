"""Post-hoc diagnosis of run 20261126T130343Z-final (written AFTER its results were seen).

Two questions, both exploratory:
1. Were the bandwidth seams missed where the live window had almost nothing above 16 kHz
   to remove (MP3-sourced uploads, 78 rpm transfers)?
2. How high are the thresholds the live null sets (the 95th percentile of the window scores)?

Usage: python diagnose.py <results.json of the final run> [label]
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from runlog import run_folder  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("seam_run", os.path.join(HERE, "run.py"))
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def main():
    src = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else "diagnose"
    with run_folder(__file__, label) as run:
        res = json.load(open(src, encoding="utf-8"))
        paths = dict(R.live_recordings())
        cache, hf = {}, {}
        for w in res["live"]:
            if w["rec"] not in cache:
                cache[w["rec"]] = R.load_mono(paths[w["rec"]])
            x, sr = cache[w["rec"]]
            s = int(round(w["start_s"] * sr))
            F = R.block_features(x[s:s + R.WIN_S * sr], sr)
            hf[(w["rec"], w["start_s"])] = float(np.median(F[:, -1]))    # bandwidth ratio, dB
        bw = [s for s in res["seams"] if s["kind"] == "bandwidth" and not s["excluded"]]
        L = ["# Seam hunt: post-hoc diagnosis", "", f"Source: `{os.path.relpath(src, HERE)}`. Exploratory, written after the results.", "",
             "## 1. Bandwidth seams by the energy above 16 kHz before the join", "",
             "| Energy above 16 kHz against 8-16 kHz (window median) | Seams | Found by S_bw |", "|---|---|---|"]
        edges = (-200, -40, -30, -20, -10, 100)
        rows = []
        for lo, hi in zip(edges[:-1], edges[1:]):
            cs = [s for s in bw if lo <= hf[(s["rec"], s["start_s"])] < hi]
            f = sum(s["found_bw"] for s in cs)
            rows.append((lo, hi, len(cs), f))
            L.append(f"| {lo} to {hi} dB | {len(cs)} | {f} |")
        by_rec = {}
        for s in bw:
            by_rec.setdefault(s["rec"], []).append(hf[(s["rec"], s["start_s"])])
        L += ["", "| Recording | Median energy above 16 kHz (dB re 8-16 kHz) |", "|---|---|"]
        for r, v in sorted(by_rec.items(), key=lambda kv: np.median(kv[1])):
            L.append(f"| {r[:60]} | {np.median(v):.1f} |")
        q = {key: float(np.percentile([w[key] for w in res["live"]], 95)) for key in ("S_all", "S_bw")}
        seam_med = {k: {key: float(np.median([s[key] for s in res["seams"] if s["kind"] == k and not s["excluded"]]))
                        for key in ("S_all", "S_bw")} for k in R.SEAM_TYPES}
        L += ["", "## 2. Thresholds set by the live null", "",
              f"95th percentile of live window scores: S_all {q['S_all']:.1f}, S_bw {q['S_bw']:.1f}.", "",
              "| Seam | Median S_all with the seam | Median S_bw with the seam |", "|---|---|---|"]
        for k, v in seam_med.items():
            L.append(f"| {k} | {v['S_all']:.1f} | {v['S_bw']:.1f} |")
        out = {"hf_by_window": {f"{k[0]}@{k[1]}": v for k, v in hf.items()}, "bw_rows": rows, "q95": q, "seam_medians": seam_med}
        json.dump(out, open(os.path.join(run.path, "diagnosis.json"), "w", encoding="utf-8"), indent=1)
        open(os.path.join(run.path, "diagnosis.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
        print("\n".join(L))


if __name__ == "__main__":
    main()
