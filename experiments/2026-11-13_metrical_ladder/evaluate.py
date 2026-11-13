"""Evaluate the metrical ladder (journal step 2026-11-13-ladder-001).

  python evaluate.py tune        dev grooves (seeds 0-199): choose Z_ACC
  python evaluate.py final       held-out grooves, second held-out set, negatives, run once
  PTS_TAPPING_DIR=... PTS_METRO_STEMS=... python evaluate.py tapped    the 12 tapped tracks, run once
"""
import collections
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experiments", "2026-11-12_beat_level"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "2026-11-12_periodicity_confirmation"))
from runlog import run_folder          # noqa: E402
import bench as B                      # noqa: E402
import holdout_b as H                  # noqa: E402
import ladder as L                     # noqa: E402

Z_GRID = (2.0, 3.0, 4.0, 5.0, 6.0, 8.0)


def _factor(a, b):
    """The step between two neighbouring levels, read from their periods (2, 3, ...)."""
    return int(round(b / a))


def first_up(levels, i):
    """Factor of the first level above level i (2, 3, or None)."""
    return _factor(levels[i]["tau"], levels[i + 1]["tau"]) if i is not None and i + 1 < len(levels) else None


def first_down(levels, i):
    """Factor of the first level below level i."""
    return _factor(levels[i - 1]["tau"], levels[i]["tau"]) if i is not None and i > 0 else None


def smallest_factor(n):
    return 2 if n % 2 == 0 else 3 if n % 3 == 0 else n


def score(rows):
    """rows: [(levels, beat, desc)] -> summary dict."""
    s = collections.Counter()
    sizes, meter = [], collections.Counter()
    for levels, beat, d in rows:
        s["n"] += 1
        if not levels:
            s["empty"] += 1
            continue
        s["seeded"] += 1
        sizes.append(len(levels))
        i = L.on_ladder(levels, beat)
        s["covered"] += i is not None
        nb, comp = d["beats_per_bar"], d["compound"]
        if not comp and nb in (2, 3, 4) and i is not None:
            want = 2 if nb in (2, 4) else 3
            got = first_up(levels, i)
            meter["scored"] += 1
            meter["right"] += got == want
            meter["baseline"] += want == 2
            meter[f"nb{nb}:{got}"] += 1
        elif i is not None:
            meter[f"other nb{nb}{'c' if comp else ''}:{first_up(levels, i)}"] += 1
        if i is not None and d["subdivision"] > 1:
            s["sub_scored"] += 1
            s["sub_right"] += first_down(levels, i) == smallest_factor(d["subdivision"])
    out = dict(s)
    out["coverage"] = s["covered"] / max(1, s["seeded"])
    out["median_size"] = float(np.median(sizes)) if sizes else 0.0
    out["meter_acc"] = meter["right"] / max(1, meter["scored"])
    out["meter_baseline"] = meter["baseline"] / max(1, meter["scored"])
    out["sub_acc"] = s["sub_right"] / max(1, s["sub_scored"])
    out["meter_detail"] = dict(sorted(meter.items()))
    return out


def run_set(sigs, z):
    return [(L.ladder(x, B.SR, z), beat, d) for x, beat, d in sigs]


def short(o):
    return (f"seeded {o.get('seeded', 0)}/{o['n']}  coverage {o['coverage']:.3f}  median size {o['median_size']:.1f}  "
            f"meter {o['meter_acc']:.3f} (baseline {o['meter_baseline']:.3f}, n {o['meter_detail'].get('scored', 0)})  "
            f"sub {o['sub_acc']:.3f}")


def main(mode):
    with run_folder(__file__, mode) as run:
        res = {}
        if mode == "tune":
            sigs = [B.groove(s) for s in B.DEV_SEEDS]
            for z in Z_GRID:
                res[z] = score(run_set(sigs, z))
                print(f"Z_ACC {z:>4}: {short(res[z])}", flush=True)
        elif mode == "final":
            import run as C                      # the confirmation experiment
            sets = {"final": [B.groove(s) for s in B.FINAL_SEEDS], "holdout_b": [H.groove_b(s) for s in H.SEEDS]}
            for name, sigs in sets.items():
                res[name] = score(run_set(sigs, L.Z_ACC))
                print(f"{name}: {short(res[name])}", flush=True)
            neg = collections.Counter()
            for s in list(range(60)) + list(range(1000, 1060)):
                rng = np.random.default_rng(s)
                dur = rng.uniform(20, 40)
                fam = list(C.NEGATIVES)[s % len(C.NEGATIVES)]
                lv = L.ladder(C.NEGATIVES[fam](rng, dur), C.SR)
                neg["n"] += 1
                neg["empty"] += not lv
                if lv:
                    neg[f"nonempty {fam}"] += 1
            res["negatives"] = dict(neg)
            print("negatives:", dict(neg), flush=True)
        elif mode == "tapped":
            sys.path.insert(0, os.path.join(ROOT, "experiments", "2026-11-13_beat_tapping"))
            import score as T                    # noqa: E402
            data = os.environ["PTS_TAPPING_DIR"]
            taps = json.load(open(os.path.join(data, "taps.json"), encoding="utf-8"))
            key = {t["id"]: t for t in json.load(open(os.path.join(data, "key.json"), encoding="utf-8"))["tracks"]}
            rows = []
            for tid in sorted(key):
                lab = T.label(taps.get(tid, {}))
                if lab["status"] != "verified":
                    continue
                x, sr = T.drum_stem(key[tid]["name"])
                lv = L.ladder(x, sr)
                beat = lab["beats_s"][0]
                i = L.on_ladder(lv, beat)
                rows.append({"track": key[tid]["name"], "tapped_bpm": 60 / beat, "on_ladder": i is not None,
                             "ladder_bpm": [round(60 / v["tau"], 1) for v in lv], "steps": [v["step"] for v in lv]})
                print(rows[-1], flush=True)
            res = {"tracks": rows, "covered": sum(r["on_ladder"] for r in rows), "n": len(rows),
                   "median_size": float(np.median([len(r["ladder_bpm"]) for r in rows]))}
            print(f"tapped: on the ladder {res['covered']}/{res['n']}, median size {res['median_size']}", flush=True)
        json.dump(res, open(os.path.join(run.path, "results.json"), "w", encoding="utf-8"), indent=1, default=str)


if __name__ == "__main__":
    main(sys.argv[1])
