"""Score the frozen ladder on the live recordings against the tapped labels (step 2026-11-22-live-001).

  PTS_TAPPING_DIR=<folder> python score_live.py

Run once, after all labels are in. The ladder runs on each tapped excerpt and, as a secondary
result, on the whole recording from its music start; the room-only start of the folk festival
recording is an extra negative.
"""
import json
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(HERE))
from pts import ladder as L          # noqa: E402
from runlog import run_folder        # noqa: E402

LIVE = os.path.join(ROOT, "data", "material", "live")
DROP_FIRST, MIN_INTERVALS, AGREE, MAX_CV = 4, 12, 0.04, 0.15
CONTROLS = ("276887__christopherbrooks__violin-improv.wav", "486407__martineerok__ottoman-taksim-music-soundcheck.wav")
ROOM = ("391806__martineerok__folkfestival-indoors.wav", 0.0, 19.0)


def pass_period(p):
    if not p or p.get("no_steady_beat"):
        return None
    d = np.diff(p["taps_s"][DROP_FIRST:])
    if len(d) < 2:
        return None
    m = np.median(d)
    d = d[(d >= 0.6 * m) & (d <= 1.6 * m)]
    if len(d) < MIN_INTERVALS or d.std() / d.mean() > MAX_CV:
        return None
    return float(np.median(d))


def spread(a):
    a = np.asarray(a, dtype=float)
    return a.std() / a.mean()


def pass_cycle(p):
    """A repeating uneven cycle in a pass that is not even (added on 2026-11-25, before any tap)."""
    if not p or p.get("no_steady_beat"):
        return None
    d = np.diff(p["taps_s"][DROP_FIRST:])
    if len(d) < 12:
        return None
    m0 = np.median(d)
    d = d[(d >= 0.3 * m0) & (d <= 3 * m0)]
    for k in range(2, 6):
        for ph in range(k):
            n = (len(d) - ph) // k
            if n < 6:
                continue
            block = d[ph:ph + n * k].reshape(n, k)
            steps = np.median(block, axis=0)
            if (spread(block.sum(axis=1)) <= 0.08 and all(spread(block[:, i]) <= 0.15 for i in range(k))
                    and steps.max() >= 1.25 * steps.min()):
                return {"k": k, "cycle_s": float(np.median(block.sum(axis=1))), "steps_s": [float(v) for v in steps]}
    return None


def label(passes):
    if any(p.get("no_steady_beat") for p in passes.values()):
        return {"status": "none"}
    per = [x for x in (pass_period(passes[k]) for k in sorted(passes)) if x]
    cyc = [c for c in (None if pass_period(passes[k]) else pass_cycle(passes[k]) for k in sorted(passes)) if c]
    for i, a in enumerate(cyc):
        for b in cyc[i + 1:]:
            if a["k"] == b["k"] and max(a["cycle_s"], b["cycle_s"]) / min(a["cycle_s"], b["cycle_s"]) - 1 <= AGREE:
                return {"status": "uneven", "k": a["k"], "cycle_s": (a["cycle_s"] + b["cycle_s"]) / 2, "steps_s": a["steps_s"]}
    pairs = [(a, b) for i, a in enumerate(per) for b in per[i + 1:]]
    for a, b in pairs:
        if max(a, b) / min(a, b) - 1 <= AGREE:
            return {"status": "verified", "beats_s": [(a + b) / 2], "passes_s": per}
    for a, b in pairs:
        if abs(max(a, b) / min(a, b) / 2 - 1) <= AGREE:
            return {"status": "ambiguous", "beats_s": sorted([a, b]), "passes_s": per}
    return {"status": "incomplete", "passes_s": per}


def mono(x):
    return x.mean(axis=1) if x.ndim == 2 else x


def bpm(levels):
    return [round(60 / v["tau"], 1) for v in levels]


def up_factor(levels, i):
    return int(round(levels[i + 1]["tau"] / levels[i]["tau"])) if i is not None and i + 1 < len(levels) else None


def main():
    data = os.environ["PTS_TAPPING_DIR"]
    taps = json.load(open(os.path.join(data, "taps.json"), encoding="utf-8"))
    key = json.load(open(os.path.join(data, "key.json"), encoding="utf-8"))["tracks"]
    with run_folder(__file__, "live") as run:
        rows = []
        for k in key:
            lab = label(taps.get(k["id"], {}))
            x, sr = sf.read(os.path.join(data, "audio", k["id"] + ".wav"))
            ex = L.ladder(mono(x), sr)
            full, fsr = sf.read(os.path.join(LIVE, k["name"]))
            whole = L.ladder(mono(full)[int(k["music_start_s"] * fsr):], fsr)
            row = {"id": k["id"], "name": k["name"], "label": lab, "excerpt_bpm": bpm(ex), "whole_bpm": bpm(whole),
                   "control": k["name"] in CONTROLS}
            if lab["status"] == "uneven":                 # reported apart from H1: does the ladder hold the cycle?
                row["excerpt_holds_cycle"] = L.on_ladder(ex, lab["cycle_s"]) is not None
                row["whole_holds_cycle"] = L.on_ladder(whole, lab["cycle_s"]) is not None
            for tag, lv in (("excerpt", ex), ("whole", whole)):
                if lab["status"] in ("verified", "ambiguous"):
                    hits = [L.on_ladder(lv, b) for b in lab["beats_s"]]
                    i = next((h for h in hits if h is not None), None)
                    row[tag + "_on_ladder"] = i is not None
                    row[tag + "_up"] = up_factor(lv, i)
                row[tag + "_empty"] = not lv
            rows.append(row)
            print(json.dumps(row), flush=True)
        y, sr = sf.read(os.path.join(LIVE, ROOM[0]))
        room = L.ladder(mono(y)[int(ROOM[1] * sr):int(ROOM[2] * sr)], sr)
        ver = [r for r in rows if r["label"]["status"] in ("verified", "ambiguous")]
        res = {"rows": rows, "room_only_bpm": bpm(room),
               "labels": {s: sum(r["label"]["status"] == s for r in rows) for s in ("verified", "ambiguous", "uneven", "none", "incomplete")},
               "uneven": {r["name"]: {"cycle_s": r["label"]["cycle_s"], "steps_s": r["label"]["steps_s"],
                                      "excerpt_holds_cycle": r["excerpt_holds_cycle"]} for r in rows if r["label"]["status"] == "uneven"},
               "H1_excerpt": f"{sum(r['excerpt_on_ladder'] for r in ver)}/{len(ver)}",
               "H1_whole": f"{sum(r['whole_on_ladder'] for r in ver)}/{len(ver)}",
               "H2_controls_empty": {r["name"]: r["excerpt_empty"] for r in rows if r["control"]},
               "H2_room_only_empty": not room}
        print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))
        json.dump(res, open(os.path.join(run.path, "results.json"), "w", encoding="utf-8"), indent=1, default=float)


if __name__ == "__main__":
    main()
