"""Old rule, candidate v1 and candidate v2 (issue #15).

  python run_v2.py dev      development data: seeds 0-199, the 120 investigated examples, and
                            seeds 50000-50199 (the first final set, looked at after its run)
  python run_v2.py final2   the second held-out set: a new generator (holdout_b.py), seeds
                            70000-70199; run once, after v2 and the generator were frozen

Writes results_v2_<mode>.md and .json next to this file.
"""
import collections
import json
import os
import sys

import bench as B
import holdout_b as H
import rule_v2 as V

RULES = {"old": B.rule_old, "v1": B.rule_new, "v2": V.rule_new_v2}
ORDER = B.CLASSES


def label(d):
    if "family" in d:
        return f"investigated {d['family']} {d['seed']}"
    return f"seed {d['seed']}, {d['pattern']}, {d['beats_per_bar']} beats{' compound' if d['compound'] else ''}, subdivision {d['subdivision']}"


def report(title, rows):
    L = [f"# Beat level, old vs v1 vs v2: {title}", "", f"{len(rows)} signals.", "",
         "| Rule | " + " | ".join(ORDER) + " |", "|---|" + "---|" * len(ORDER)]
    for r in RULES:
        c = collections.Counter(x[r]["class"] for x in rows)
        L.append(f"| {r} | " + " | ".join(str(c[k]) for k in ORDER) + " |")
    for a, b in (("old", "v2"), ("v1", "v2")):
        better = [x for x in rows if x[a]["class"] != "exact" and x[b]["class"] == "exact"]
        worse = [x for x in rows if x[a]["class"] == "exact" and x[b]["class"] != "exact"]
        L += ["", f"## {a} → {b}: improved {len(better)}, worsened {len(worse)}", ""]
        if worse:
            L += ["| Worsened | Beat | " + a + " | " + b + " |", "|---|---|---|---|"]
            for x in worse:
                q = "–" if x[b]["ratio"] is None else f"{x[b]['ratio']:.3f}"
                L.append(f"| {label(x['desc'])} | {x['beat_s']:.4f} s | exact | {x[b]['class']} ({q}) |")
    by = collections.defaultdict(list)
    for x in rows:
        d = x["desc"]
        by[d.get("pattern", d.get("family"))].append(x)
    L += ["", "## By pattern (exact)", "", "| Pattern | Signals | old | v1 | v2 |", "|---|---|---|---|---|"]
    for g in sorted(by):
        L.append(f"| {g} | {len(by[g])} | " + " | ".join(str(sum(x[r]['class'] == 'exact' for x in by[g])) for r in RULES) + " |")
    errs = [x for x in rows if x["v2"]["class"] != "exact"]
    if errs:
        L += ["", "## Every error of v2", "", "| Signal | Beat | v2 | old |", "|---|---|---|---|"]
        for x in errs:
            q = "–" if x["v2"]["ratio"] is None else f"{x['v2']['ratio']:.3f}"
            qo = "–" if x["old"]["ratio"] is None else f"{x['old']['ratio']:.3f}"
            L.append(f"| {label(x['desc'])} | {x['beat_s']:.4f} s | {x['v2']['class']} ({q}) | {x['old']['class']} ({qo}) |")
    return "\n".join(L) + "\n"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
    if mode == "dev":
        sigs = [B.groove(s) for s in B.DEV_SEEDS] + B.investigated() + [B.groove(s) for s in B.FINAL_SEEDS]
        title = "development data"
    elif mode == "final2":
        sigs = [H.groove_b(s) for s in H.SEEDS]
        title = "second held-out set (new generator)"
    else:
        raise SystemExit(__doc__)
    rows = []
    for x, beat, d in sigs:
        row = {"desc": d, "beat_s": beat}
        for name, fn in RULES.items():
            found = fn(x, B.SR)
            c, q = B.classify(found, beat)
            row[name] = {"found_s": found, "class": c, "ratio": q}
        rows.append(row)
    md = report(title, rows)
    with open(os.path.join(B.HERE, f"results_v2_{mode}.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1, default=float)
    with open(os.path.join(B.HERE, f"results_v2_{mode}.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print(md)


if __name__ == "__main__":
    main()
