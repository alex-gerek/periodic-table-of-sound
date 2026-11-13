"""Score the frozen pulse rules against the tapped beat labels (journal step 2026-11-13-tapping-001).

  PTS_TAPPING_DIR=<folder> PTS_METRO_STEMS=<folder> python score.py

Reads taps.json (raw taps) and key.json (the blinding key) from PTS_TAPPING_DIR and derives each
label with the pre-registered protocol (the same rule as tap.html). It then runs the frozen old
rule, candidate v1 and candidate v2 once on each track's full drum stem, and writes the report
into a fresh run folder (experiments/runlog.py).
"""
import glob
import json
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experiments", "2026-11-12_beat_level"))
from runlog import run_folder          # noqa: E402
import bench as B                      # noqa: E402
import rule_v2 as V                    # noqa: E402

DROP_FIRST, MIN_INTERVALS, AGREE = 4, 12, 0.04
RULES = {"old": B.rule_old, "v1": B.rule_new, "v2": V.rule_new_v2}


def pass_period(p):
    if not p or p.get("no_steady_beat"):
        return None
    t = p["taps_s"][DROP_FIRST:]
    d = np.diff(t)
    if len(d) < 2:
        return None
    m = np.median(d)
    d = d[(d >= 0.6 * m) & (d <= 1.6 * m)]
    return float(np.median(d)) if len(d) >= MIN_INTERVALS else None


def label(passes):
    """verified (beat), ambiguous (two levels), none, or incomplete."""
    if any(p.get("no_steady_beat") for p in passes.values()):
        return {"status": "none"}
    per = [x for x in (pass_period(passes[k]) for k in sorted(passes)) if x]
    pairs = [(a, b) for i, a in enumerate(per) for b in per[i + 1:]]
    for a, b in pairs:
        if max(a, b) / min(a, b) - 1 <= AGREE:
            return {"status": "verified", "beats_s": [(a + b) / 2], "passes_s": per}
    for a, b in pairs:
        if abs(max(a, b) / min(a, b) / 2 - 1) <= AGREE:
            return {"status": "ambiguous", "beats_s": sorted([a, b]), "passes_s": per}
    return {"status": "incomplete", "passes_s": per}


def drum_stem(name):
    if name == "metro":
        folder = os.environ.get("PTS_METRO_STEMS")
    else:
        hits = [f for f in glob.glob(os.path.join(ROOT, "data", "**", name), recursive=True) if os.path.isdir(f)]
        folder = hits[0] if hits else None
    if not folder:
        return None, None
    x = None
    for p in sorted(glob.glob(os.path.join(folder, "*.wav"))):
        if "drums" in os.path.basename(p).lower():
            y, sr = sf.read(p, always_2d=True)
            y = B.P.mono(y)
            x = y if x is None else x[:len(y)] + y[:len(x)]
    return x, sr


def best(found, beats):
    cls = [B.classify(found, b) for b in beats]
    return min(cls, key=lambda c: B.CLASSES.index(c[0]))


def main():
    data = os.environ["PTS_TAPPING_DIR"]
    taps = json.load(open(os.path.join(data, "taps.json"), encoding="utf-8"))
    key = {t["id"]: t for t in json.load(open(os.path.join(data, "key.json"), encoding="utf-8"))["tracks"]}
    with run_folder(__file__, "score") as run:
        rows = []
        for tid in sorted(key):
            lab = label(taps.get(tid, {}))
            row = {"id": tid, "track": key[tid]["name"], "label": lab}
            if lab["status"] in ("verified", "ambiguous"):
                x, sr = drum_stem(key[tid]["name"])
                for r, fn in RULES.items():
                    found = fn(x, sr) if x is not None else None
                    c, q = best(found, lab["beats_s"]) if found else ("none", None)
                    row[r] = {"found_s": found, "class": c, "ratio": q}
            rows.append(row)
            print(tid, key[tid]["name"], lab["status"], {r: row[r]["class"] for r in RULES if r in row}, flush=True)
        L = ["# Beat level on real recordings, against tapped labels", "",
             f"Run `{run.meta['run_id']}`. Labels from two blinded tapping passes per track (journal step 2026-11-13-tapping-001).", "",
             "| Label | Tracks |", "|---|---|"]
        for st in ("verified", "ambiguous", "none", "incomplete"):
            L.append(f"| {st} | {sum(r['label']['status'] == st for r in rows)} |")
        for group in ("verified", "ambiguous"):
            sel = [r for r in rows if r["label"]["status"] == group]
            if not sel:
                continue
            L += ["", f"## {group.capitalize()} tracks", "", "| Rule | " + " | ".join(B.CLASSES) + " |", "|---|" + "---|" * len(B.CLASSES)]
            for rn in RULES:
                L.append(f"| {rn} | " + " | ".join(str(sum(r[rn]["class"] == c for r in sel)) for c in B.CLASSES) + " |")
            L += ["", "| Track | Tapped beat | old | v1 | v2 |", "|---|---|---|---|---|"]
            for r in sel:
                tb = " or ".join(f"{60 / b:.1f} BPM" for b in r["label"]["beats_s"])
                cell = lambda rn: f"{r[rn]['class']} ({60 / r[rn]['found_s']:.1f} BPM)" if r[rn]["found_s"] else r[rn]["class"]
                L.append(f"| {r['track']} | {tb} | {cell('old')} | {cell('v1')} | {cell('v2')} |")
        md = "\n".join(L) + "\n"
        json.dump(rows, open(os.path.join(run.path, "scores.json"), "w", encoding="utf-8"), indent=1, default=float)
        open(os.path.join(run.path, "report.md"), "w", encoding="utf-8").write(md)
        print(md)


if __name__ == "__main__":
    main()
