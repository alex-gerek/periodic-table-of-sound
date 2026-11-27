"""Held-out checks R, N and J for the frozen ladder v2 (journal step 2026-11-27-ladder-002). Run once.

  R  regression on sets seen once: final grooves (50000-50199), holdout_b (70000-70199),
     the negatives of 2026-11-12 (seeds 0-59 and 1000-1059), the 12 tapped tracks
  N  fresh negatives: seeds 3000-3119, the six families of 2026-11-12 in turn
  J  fresh jitter set: seeds 8000-8299, 40-120 BPM, jitter 3-6% (otherwise the dev click generator)
v1 (pts/ladder.py) runs beside v2 on every signal, for comparison only.
The live check L runs later, on a new tapped set, with its own script.

    PTS_TAPPING_DIR=<2026-11-13 tapping folder> PTS_METRO_STEMS=<Metro stems> python holdout.py final [workers]
"""
import collections
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
ROOT = os.path.dirname(EXP)
for p in (ROOT, EXP, HERE, os.path.join(EXP, "2026-11-12_beat_level"), os.path.join(EXP, "2026-11-12_periodicity_confirmation"),
          os.path.join(EXP, "2026-11-13_metrical_ladder"), os.path.join(EXP, "2026-11-13_beat_tapping")):
    sys.path.insert(0, p)
import dev_sweep as DS   # noqa: E402  (loader and live helpers; its generator constants)

ARMS = ("v1", "v2")
J_SEEDS = range(8000, 8300)
N_SEEDS = range(3000, 3120)
R_NEG_SEEDS = list(range(0, 60)) + list(range(1000, 1060))


def run_arm(arm, x, sr):
    if arm == "v1":
        from pts import ladder as L
        return L.ladder(x, sr)
    import ladder_v2 as V
    return V.ladder(x, sr)                     # frozen: sm = FROZEN_SM


def jitter_track(seed):
    """J: as the dev click generator, with tempo 40-120 BPM (log-uniform) and jitter 3-6% (uniform)."""
    rng = np.random.default_rng(seed)
    bpm = float(np.exp(rng.uniform(np.log(40), np.log(120))))
    jitter = float(rng.uniform(0.03, 0.06))
    drift = float(rng.uniform(-0.06, 0.06))
    accent = int(rng.integers(1, 4))
    snr = float(rng.uniform(10, 40))
    sr, dur = DS.CLICK_SR, DS.CLICK_DUR
    n = int(dur * sr)
    x = np.zeros(n)
    beat = 60.0 / bpm
    m = int(0.03 * sr)
    burst = rng.standard_normal(m) * np.exp(-np.arange(m) / (0.005 * sr))
    t, i = 0.2, 0
    while t < dur - 0.05:
        a = int(max(0.0, t + rng.normal(0, jitter * beat)) * sr)
        g = 2.0 if accent > 1 and i % accent == 0 else 1.0
        if a < n:
            seg = burst[: n - a]
            x[a:a + len(seg)] += g * seg
        t += beat / (1 + drift * (t / dur - 0.5))
        i += 1
    rms = np.sqrt(np.mean(x ** 2))
    x += rng.standard_normal(n) * rms * 10 ** (-snr / 20)
    return x, sr, beat, {"bpm": bpm, "jitter": jitter, "drift": drift, "accent": accent, "snr": snr}


def negative(seed):
    G = DS._load("conf12", os.path.join(EXP, "2026-11-12_periodicity_confirmation", "run.py"))
    rng = np.random.default_rng(seed)
    dur = rng.uniform(20, 40)
    fam = list(G.NEGATIVES)[seed % len(G.NEGATIVES)]
    return G.NEGATIVES[fam](rng, dur), G.SR, fam


def job(item):
    from pts import ladder as L
    kind, key = item
    if kind in ("final", "holdout_b"):
        import bench as B
        import holdout_b as H
        x, beat, d = B.groove(key) if kind == "final" else H.groove_b(key)
        return kind, key, {"beat": beat, "desc": d}, {a: [{"tau": v["tau"], "step": v["step"]} for v in run_arm(a, x, B.SR)] for a in ARMS}
    if kind in ("r_neg", "n_neg"):
        x, sr, fam = negative(key)
        return kind, key, {"family": fam}, {a: [round(60 / v["tau"], 1) for v in run_arm(a, x, sr)] for a in ARMS}
    if kind == "jitter":
        x, sr, beat, d = jitter_track(key)
        return kind, key, d, {a: L.on_ladder(run_arm(a, x, sr), beat) is not None for a in ARMS}
    if kind == "tapped":
        import score as T
        x, sr = T.drum_stem(key["name"])
        out = {}
        for a in ARMS:
            lv = run_arm(a, x, sr)
            out[a] = {"on": L.on_ladder(lv, key["beat"]) is not None, "bpm": [round(60 / v["tau"], 1) for v in lv]}
        return kind, key["name"], {"tapped_bpm": round(60 / key["beat"], 1)}, out
    raise ValueError(kind)


def tapped_items():
    import score as T
    data = os.environ["PTS_TAPPING_DIR"]
    taps = json.load(open(os.path.join(data, "taps.json"), encoding="utf-8"))
    key = {t["id"]: t for t in json.load(open(os.path.join(data, "key.json"), encoding="utf-8"))["tracks"]}
    out = []
    for tid in sorted(key):
        lab = T.label(taps.get(tid, {}))
        if lab["status"] == "verified":
            out.append(("tapped", {"name": key[tid]["name"], "beat": lab["beats_s"][0]}))
    return out


def main():
    from runlog import run_folder
    from pts.stats import rate_text
    E = DS._load("evaluate13", os.path.join(EXP, "2026-11-13_metrical_ladder", "evaluate.py"))
    import bench as B
    import holdout_b as H
    label = sys.argv[1] if len(sys.argv) > 1 else "final"
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else max(1, (os.cpu_count() or 2) - 1)
    items = (tapped_items() + [("r_neg", s) for s in R_NEG_SEEDS] + [("n_neg", s) for s in N_SEEDS]
             + [("final", s) for s in B.FINAL_SEEDS] + [("holdout_b", s) for s in H.SEEDS] + [("jitter", s) for s in J_SEEDS])
    with run_folder(__file__, label) as run:
        t0 = time.time()
        res = collections.defaultdict(list)
        with ProcessPoolExecutor(workers) as ex:
            for i, (kind, key, d, out) in enumerate(ex.map(job, items, chunksize=2)):
                res[kind].append({"key": key, "desc": d, "out": out})
                if (i + 1) % 50 == 0:
                    print(f"{i + 1}/{len(items)} done ({time.time() - t0:.0f} s)", flush=True)
        S, lines = {}, ["# Ladder v2, held-out checks R, N, J", "", f"Run `{os.path.basename(run.path)}`, {time.time() - t0:.0f} s.", ""]
        for a in ARMS:
            s = {}
            for gs in ("final", "holdout_b"):
                g = E.score([(r["out"][a], r["desc"]["beat"], r["desc"]["desc"]) for r in res[gs]])
                s[gs] = {k: g[k] for k in ("coverage", "median_size", "meter_acc", "meter_baseline")}
                s[gs]["seeded"] = g.get("seeded", 0)
                s[gs]["meter_n"] = g["meter_detail"].get("scored", 0)
            s["tapped_on"] = sum(r["out"][a]["on"] for r in res["tapped"])
            s["tapped_n"] = len(res["tapped"])
            s["tapped_median_size"] = float(np.median([len(r["out"][a]["bpm"]) for r in res["tapped"]]))
            s["r_neg_empty"] = sum(not r["out"][a] for r in res["r_neg"])
            s["n_neg_nonempty"] = sum(bool(r["out"][a]) for r in res["n_neg"])
            s["j_on"] = sum(r["out"][a] for r in res["jitter"])
            sizes_ok = all(s[gs]["median_size"] <= 5 for gs in ("final", "holdout_b")) and s["tapped_median_size"] <= 5
            meter_ok = all(s[gs]["meter_acc"] >= 0.70 and s[gs]["meter_acc"] > s[gs]["meter_baseline"] for gs in ("final", "holdout_b"))
            s["H1_R"] = bool(all(s[gs]["coverage"] >= 0.95 for gs in ("final", "holdout_b")) and s["tapped_on"] >= 11
                             and sizes_ok and meter_ok and s["r_neg_empty"] >= 0.95 * len(res["r_neg"]))
            s["H2_N"] = bool(s["n_neg_nonempty"] <= 6)
            s["H3_J"] = bool(s["j_on"] >= 0.9 * len(res["jitter"]))
            S[a] = s
        lines += ["| | v1 | v2 |", "|---|---|---|"]
        for gs in ("final", "holdout_b"):
            for k, f in (("coverage", "{:.3f}"), ("median_size", "{:.0f}"), ("meter_acc", "{:.3f}")):
                lines.append(f"| {gs}: {k} | " + " | ".join(f.format(S[a][gs][k]) for a in ARMS) + " |")
            lines.append(f"| {gs}: meter baseline, n | " + " | ".join(f"{S[a][gs]['meter_baseline']:.3f}, {S[a][gs]['meter_n']}" for a in ARMS) + " |")
        lines += [f"| tapped tracks on the ladder | " + " | ".join(f"{S[a]['tapped_on']}/{S[a]['tapped_n']}" for a in ARMS) + " |",
                  f"| R negatives empty | " + " | ".join(rate_text(S[a]['r_neg_empty'], len(res['r_neg'])) for a in ARMS) + " |",
                  f"| N fresh negatives non-empty | " + " | ".join(rate_text(S[a]['n_neg_nonempty'], len(res['n_neg'])) for a in ARMS) + " |",
                  f"| J jitter set, beat on the ladder | " + " | ".join(rate_text(S[a]['j_on'], len(res['jitter'])) for a in ARMS) + " |",
                  "", f"**v2:** H1 (R) {'holds' if S['v2']['H1_R'] else 'fails'}, H2 (N) {'holds' if S['v2']['H2_N'] else 'fails'}, "
                  f"H3 (J) {'holds' if S['v2']['H3_J'] else 'fails'}. H4 waits for the new live set.", ""]
        nonempty = [(r["key"], r["desc"]["family"], r["out"]["v2"]) for k in ("r_neg", "n_neg") for r in res[k] if r["out"]["v2"]]
        lines += ["Non-empty v2 ladders on negatives: " + ("; ".join(f"seed {k} ({f}): {b}" for k, f, b in nonempty) or "none") + "."]
        md = "\n".join(lines) + "\n"
        print(md)
        open(os.path.join(run.path, "results.md"), "w", encoding="utf-8").write(md)
        json.dump({"summary": S, "results": res}, open(os.path.join(run.path, "results.json"), "w", encoding="utf-8"), indent=1, default=float)


if __name__ == "__main__":
    main()
