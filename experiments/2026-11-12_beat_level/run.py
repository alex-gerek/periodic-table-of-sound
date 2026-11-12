"""Compare the old and the new pulse rule on the beat-level benchmark (issue #15).

  python run.py dev     development set: seeds 0-199 and the 120 investigated examples
  python run.py final   held-out set: seeds 50000-50199, run once after the rule was fixed
  python run.py real    real drum stems: the level each rule returns; scored only against
                        verified labels in labels.json (ambiguous labels are reported apart)

Writes results_<mode>.md and results_<mode>.json next to this file.
"""
import collections
import glob
import json
import os
import sys

import numpy as np
import soundfile as sf

import bench as B

HERE = B.HERE
ROOT = B.ROOT
ORDER = B.CLASSES


def run_set(signals):
    rows = []
    for x, beat, d in signals:
        row = {"desc": d, "beat_s": beat}
        for name, fn in B.RULES.items():
            found = fn(x, B.SR)
            c, q = B.classify(found, beat)
            row[name] = {"found_s": found, "class": c, "ratio": q}
        rows.append(row)
    return rows


def group_of(d):
    if "family" in d:
        return f"investigated: {d['family']}"
    if d["compound"]:
        return f"compound {d['beats_per_bar']}x3 eighths"
    return f"{d['beats_per_bar']} beats, hats in {d['subdivision']}s"


def report_synthetic(mode, rows):
    L = [f"# Beat level: {mode} set", "",
         f"{len(rows)} signals with a known beat. A level counts as *exact* within ±{100 * B.TOL:.0f}%, as a *precision* error "
         f"within ±{100 * B.PRECISION:.0f}%, as a *subdivision* at 1/2, 1/3 or 1/4 of the beat, and as a *multiple* at 2 to 8 beats.", "",
         "| Rule | " + " | ".join(ORDER) + " |", "|---|" + "---|" * len(ORDER)]
    for name in B.RULES:
        cnt = collections.Counter(r[name]["class"] for r in rows)
        L.append(f"| {name} | " + " | ".join(str(cnt[c]) for c in ORDER) + " |")
    L += ["", "## Old → new", "", "| Old \\ New | " + " | ".join(ORDER) + " |", "|---|" + "---|" * len(ORDER)]
    tr = collections.Counter((r["old"]["class"], r["new"]["class"]) for r in rows)
    for a in ORDER:
        if any(tr[(a, b)] for b in ORDER):
            L.append(f"| **{a}** | " + " | ".join(str(tr[(a, b)]) if tr[(a, b)] else "" for b in ORDER) + " |")
    worse = [r for r in rows if r["old"]["class"] == "exact" and r["new"]["class"] != "exact"]
    better = [r for r in rows if r["old"]["class"] != "exact" and r["new"]["class"] == "exact"]
    L += ["", f"**Improved:** {len(better)}. **Worsened:** {len(worse)}.", ""]
    if worse:
        L += ["### Worsened (exact before, not after)", "", "| Signal | Beat | Old | New |", "|---|---|---|---|"]
        for r in worse:
            d = r["desc"]
            L.append(f"| {group_of(d)}, seed {d['seed']}{', ' + d['pattern'] if 'pattern' in d else ''} | {r['beat_s']:.4f} s | "
                     f"{r['old']['ratio']:.3f} | {r['new']['class']} ({r['new']['ratio']:.3f}) |")
        L.append("")
    L += ["## By group", "", "| Group | Signals | Old exact | New exact | New errors |", "|---|---|---|---|---|"]
    groups = collections.defaultdict(list)
    for r in rows:
        groups[group_of(r["desc"])].append(r)
    for g in sorted(groups):
        rs = groups[g]
        errs = collections.Counter(r["new"]["class"] for r in rs if r["new"]["class"] != "exact")
        L.append(f"| {g} | {len(rs)} | {sum(r['old']['class'] == 'exact' for r in rs)} | {sum(r['new']['class'] == 'exact' for r in rs)} | "
                 + (", ".join(f"{k} {v}" for k, v in errs.items()) or "–") + " |")
    errs = [r for r in rows if r["new"]["class"] != "exact"]
    if errs:
        L += ["", "## Every error of the new rule", "", "| Signal | Beat | New | Old |", "|---|---|---|---|"]
        for r in errs:
            d = r["desc"]
            nq = "–" if r["new"]["ratio"] is None else f"{r['new']['ratio']:.3f}"
            L.append(f"| {group_of(d)}, seed {d['seed']}{', ' + d['pattern'] if 'pattern' in d else ''} | {r['beat_s']:.4f} s | "
                     f"{r['new']['class']} ({nq}) | {r['old']['class']} ({r['old']['ratio']:.3f}) |")
    return "\n".join(L) + "\n"


def real_tracks():
    folders = sorted(glob.glob(os.path.join(ROOT, "data", "stems", "*"))) + \
        sorted(glob.glob(os.path.join(ROOT, "data", "material", "tempo_series", "*"))) + \
        sorted(glob.glob(os.path.join(ROOT, "data", "material", "meters", "meter_*")))
    metro = os.environ.get("PTS_METRO_STEMS")
    if metro:
        folders.append(metro)
    for f in folders:
        w = [p for p in glob.glob(os.path.join(f, "*.wav")) if "drums" in os.path.basename(p).lower()]
        if not w:
            continue
        x = None
        for p in w:
            y, sr = sf.read(p, always_2d=True)
            y = B.P.mono(y)
            x = y if x is None else x[:len(y)] + y[:len(x)]
        yield ("metro" if f == metro else os.path.basename(f)), x, sr


def match(found, beats):
    """Against one or more acceptable beats (ambiguous tracks list several): the best class."""
    cls = [B.classify(found, b)[0] for b in beats]
    return min(cls, key=ORDER.index)


def report_real():
    labels = json.load(open(os.path.join(HERE, "labels.json"), encoding="utf-8"))
    rows = []
    for name, x, sr in real_tracks():
        row = {"track": name, "label": labels.get(name, {"status": "unverified"})}
        for rn, fn in B.RULES.items():
            row[rn] = fn(x, sr)
        rows.append(row)
    L = ["# Beat level: real drum stems", "",
         "The tempo written in a Suno prompt is not a label: a generation can differ from it. A track is scored only when its beat is **verified** in `labels.json`. **Ambiguous** tracks are listed apart. **Unverified** tracks show the level each rule returns and are not scored.", "",
         "| Track | Label | Old rule | New rule | Same level |", "|---|---|---|---|---|"]
    for r in rows:
        lb = r["label"]
        lab = lb["status"] + (f": {', '.join(f'{60 / b:.1f}' for b in lb['beats_s'])} BPM" if lb.get("beats_s") else "")
        same = abs(r["old"] / r["new"] - 1) <= B.TOL if r["old"] and r["new"] else False
        L.append(f"| {r['track']} | {lab} | {60 / r['old']:.1f} BPM | {60 / r['new']:.1f} BPM | {'yes' if same else '**no**'} |")
    for status in ("verified", "ambiguous"):
        sel = [r for r in rows if r["label"]["status"] == status]
        L += ["", f"**{status.capitalize()}:** " + (", ".join(
            f"{r['track']}: old {match(r['old'], r['label']['beats_s'])}, new {match(r['new'], r['label']['beats_s'])}"
            for r in sel) if sel else "none yet.")]
    return rows, "\n".join(L) + "\n"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
    if mode == "dev":
        rows = run_set([B.groove(s) for s in B.DEV_SEEDS] + B.investigated())
        md = report_synthetic("development", rows)
    elif mode == "final":
        rows = run_set([B.groove(s) for s in B.FINAL_SEEDS])
        md = report_synthetic("final (held out)", rows)
    elif mode == "real":
        rows, md = report_real()
    else:
        raise SystemExit(__doc__)
    with open(os.path.join(HERE, f"results_{mode}.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1, default=float)
    with open(os.path.join(HERE, f"results_{mode}.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print(md)


if __name__ == "__main__":
    main()
