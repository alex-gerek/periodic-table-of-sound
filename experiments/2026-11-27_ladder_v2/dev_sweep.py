"""Development sweep for ladder v2 (journal step 2026-11-27-ladder-002, selection rule fixed there).

Arms: v1 (pts/ladder.py, for comparison), v2a (sm 0), v2b (sm 0.01, 0.02, 0.03).
Sets: synthetic clicks (seeds 7000-7599), dev grooves (0-199), dev negatives (calib-001 fresh,
2000-2119), the 16 labelled live excerpts.

    PTS_TAPPING_DIR=<tapping_live folder> python dev_sweep.py [label] [workers]
"""
import collections
import importlib.util
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
          os.path.join(EXP, "2026-11-13_metrical_ladder")):
    sys.path.insert(0, p)

ARMS = {"v1": None, "v2a": 0.0, "v2b_0.01": 0.01, "v2b_0.02": 0.02, "v2b_0.03": 0.03}
CLICK_SEEDS = range(7000, 7600)
NEG_SEEDS = range(2000, 2120)
CLICK_DUR, CLICK_SR = 30.0, 22050


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def click_track(seed):
    """Dev click train: tempo 30-240 BPM (log-uniform), jitter (seed mod 7) %, drift up to 6%,
    accents every 1st, 2nd or 3rd beat, a noise floor 10-40 dB below the clicks."""
    rng = np.random.default_rng(seed)
    bpm = float(np.exp(rng.uniform(np.log(30), np.log(240))))
    jitter = (seed % 7) / 100
    drift = float(rng.uniform(-0.06, 0.06))
    accent = int(rng.integers(1, 4))
    snr = float(rng.uniform(10, 40))
    n = int(CLICK_DUR * CLICK_SR)
    x = np.zeros(n)
    beat = 60.0 / bpm
    m = int(0.03 * CLICK_SR)
    burst = rng.standard_normal(m) * np.exp(-np.arange(m) / (0.005 * CLICK_SR))
    t, i = 0.2, 0
    while t < CLICK_DUR - 0.05:
        a = int(max(0.0, t + rng.normal(0, jitter * beat)) * CLICK_SR) if jitter else int(t * CLICK_SR)
        g = 2.0 if accent > 1 and i % accent == 0 else 1.0
        if a < n:                                    # jitter can push the last click past the end
            seg = burst[: n - a]
            x[a:a + len(seg)] += g * seg
        t += beat / (1 + drift * (t / CLICK_DUR - 0.5))
        i += 1
    rms = np.sqrt(np.mean(x ** 2))
    x += rng.standard_normal(n) * rms * 10 ** (-snr / 20)
    return x, CLICK_SR, beat, {"bpm": bpm, "jitter": jitter, "drift": drift, "accent": accent, "snr": snr}


def run_arm(arm, x, sr):
    if ARMS[arm] is None:
        from pts import ladder as L
        return L.ladder(x, sr)
    import ladder_v2 as V
    return V.ladder(x, sr, sm=ARMS[arm])


def job(item):
    """One signal, all arms. item = (set, key, payload)."""
    from pts import ladder as L
    kind, key, payload = item
    if kind == "click":
        x, sr, beat, d = click_track(key)
        return kind, key, d, {a: L.on_ladder(run_arm(a, x, sr), beat) is not None for a in ARMS}
    if kind == "groove":
        import bench as B
        x, beat, d = B.groove(key)
        return kind, key, {"beat": beat, "desc": d}, {a: [{"tau": v["tau"], "step": v["step"]} for v in run_arm(a, x, B.SR)] for a in ARMS}
    if kind == "neg":
        G = _load("conf12", os.path.join(EXP, "2026-11-12_periodicity_confirmation", "run.py"))
        rng = np.random.default_rng(key)
        dur = rng.uniform(20, 40)
        fam = list(G.NEGATIVES)[key % len(G.NEGATIVES)]
        x = G.NEGATIVES[fam](rng, dur)
        return kind, key, {"family": fam}, {a: len(run_arm(a, x, G.SR)) for a in ARMS}
    if kind == "live":
        import soundfile as sf
        x, sr = sf.read(payload["path"])
        x = x.mean(axis=1) if x.ndim == 2 else x
        out = {}
        for a in ARMS:
            lv = run_arm(a, x, sr)
            out[a] = {"on": any(L.on_ladder(lv, b) is not None for b in payload["beats_s"]),
                      "bpm": [round(60 / v["tau"], 1) for v in lv]}
        return kind, key, {"name": payload["name"], "tapped_bpm": [round(60 / b, 1) for b in payload["beats_s"]]}, out
    raise ValueError(kind)


def live_items(data):
    S = _load("score_live", os.path.join(EXP, "2026-11-22_live_ladder", "score_live.py"))
    taps = json.load(open(os.path.join(data, "taps.json"), encoding="utf-8"))
    key = json.load(open(os.path.join(data, "key.json"), encoding="utf-8"))["tracks"]
    out = []
    for k in key:
        lab = S.label(taps.get(k["id"], {}))
        if lab["status"] in ("verified", "ambiguous"):
            out.append(("live", k["id"], {"path": os.path.join(data, "audio", k["id"] + ".wav"), "name": k["name"],
                                          "beats_s": lab["beats_s"]}))
    return out


def main():
    from runlog import run_folder
    from pts.stats import rate_text
    label = sys.argv[1] if len(sys.argv) > 1 else "dev"
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else max(1, (os.cpu_count() or 2) - 1)
    E = _load("evaluate13", os.path.join(EXP, "2026-11-13_metrical_ladder", "evaluate.py"))
    items = (live_items(os.environ["PTS_TAPPING_DIR"]) + [("neg", s, None) for s in NEG_SEEDS]
             + [("groove", s, None) for s in range(0, 200)] + [("click", s, None) for s in CLICK_SEEDS])
    with run_folder(__file__, label) as run:
        t0 = time.time()
        res = collections.defaultdict(list)
        with ProcessPoolExecutor(workers) as ex:
            for i, (kind, key, d, out) in enumerate(ex.map(job, items, chunksize=2)):
                res[kind].append({"key": key, "desc": d, "out": out})
                if (i + 1) % 50 == 0 or kind == "live":
                    print(f"{i + 1}/{len(items)} done ({time.time() - t0:.0f} s)", flush=True)
        summary = {}
        for a in ARMS:
            g = E.score([(r["out"][a], r["desc"]["beat"], r["desc"]["desc"]) for r in res["groove"]])
            clicks = res["click"]
            j5 = [r for r in clicks if abs(r["desc"]["jitter"] - 0.05) < 1e-9]
            summary[a] = {
                "groove_coverage": g["coverage"], "groove_seeded": g.get("seeded", 0), "groove_median_size": g["median_size"],
                "groove_meter": g["meter_acc"], "groove_meter_baseline": g["meter_baseline"],
                "neg_nonempty": sum(r["out"][a] > 0 for r in res["neg"]),
                "live_on": sum(r["out"][a]["on"] for r in res["live"]),
                "clicks_on": sum(r["out"][a] for r in clicks), "clicks_n": len(clicks),
                "clicks_j5_on": sum(r["out"][a] for r in j5), "clicks_j5_n": len(j5),
            }
        v1_live = {r["key"] for r in res["live"] if r["out"]["v1"]["on"]}
        qual = []
        for a in ARMS:
            if a == "v1":
                continue
            s = summary[a]
            lost = sorted(k for k in v1_live if not next(r for r in res["live"] if r["key"] == k)["out"][a]["on"])
            s["live_lost_vs_v1"] = lost
            s["qualifies"] = bool(s["groove_coverage"] >= 0.95 and s["neg_nonempty"] <= 2 and not lost)
            if s["qualifies"]:
                qual.append(a)
        order = ["v2a", "v2b_0.01", "v2b_0.02", "v2b_0.03"]
        chosen = max(qual, key=lambda a: (summary[a]["clicks_j5_on"], -order.index(a))) if qual else None
        lines = ["# Ladder v2, development sweep", "", f"Run `{os.path.basename(run.path)}`, {time.time() - t0:.0f} s.", "",
                 "| Arm | Dev grooves: coverage (seeded) | median size | meter (baseline) | Dev negatives non-empty | Live dev on ladder | Clicks on ladder | Clicks, 5% jitter | Qualifies |",
                 "|---|---|---|---|---|---|---|---|---|"]
        nl, nn = len(res["live"]), len(res["neg"])
        for a in ARMS:
            s = summary[a]
            lines.append(f"| {a} | {s['groove_coverage']:.3f} ({s['groove_seeded']}) | {s['groove_median_size']:.0f} | "
                         f"{s['groove_meter']:.3f} ({s['groove_meter_baseline']:.3f}) | {rate_text(s['neg_nonempty'], nn)} | "
                         f"{s['live_on']}/{nl} | {rate_text(s['clicks_on'], s['clicks_n'])} | {rate_text(s['clicks_j5_on'], s['clicks_j5_n'])} | "
                         f"{'—' if a == 'v1' else ('yes' if s['qualifies'] else 'no' + (' (loses ' + ', '.join(s['live_lost_vs_v1']) + ')' if s['live_lost_vs_v1'] else ''))} |")
        lines += ["", f"**Chosen by the selection rule:** {chosen or 'none (the step ends here)'}.", "", "## Live dev tracks", "",
                  "| Track | Tapped BPM | " + " | ".join(ARMS) + " |", "|---" * (len(ARMS) + 2) + "|"]
        for r in sorted(res["live"], key=lambda r: r["key"]):
            lines.append(f"| {r['key']} {r['desc']['name'][:40]} | {r['desc']['tapped_bpm']} | "
                         + " | ".join(("**on** " if r["out"][a]["on"] else "") + str(r["out"][a]["bpm"]) for a in ARMS) + " |")
        md = "\n".join(lines) + "\n"
        print(md)
        open(os.path.join(run.path, "results.md"), "w", encoding="utf-8").write(md)
        json.dump({"arms": ARMS, "summary": summary, "chosen": chosen, "results": res},
                  open(os.path.join(run.path, "results.json"), "w", encoding="utf-8"), indent=1, default=float)


if __name__ == "__main__":
    main()
