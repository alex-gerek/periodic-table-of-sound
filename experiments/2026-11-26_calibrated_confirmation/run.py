"""A calibrated false-alarm rate for period confirmation (issue #32, step 2026-11-26-calib-001).

For every signal: the sigma rule of `confirm_period` (as adopted in 2026-11-12) and the
surrogate p-value of `pts.periodicity.surrogate_p` (K = 199 shuffles of the onset envelope).
The generators are imported unchanged from experiments/2026-11-12_periodicity_confirmation.

Sets:
  fresh        seeds 2000..2119: the six non-periodic families in turn, and grooves
  fresh real   the 12 real drum stems, and each shuffled as audio with seed 26
  development  seeds 0..59 (click trains) and 1000..1059 (grooves), and the real stems
               shuffled with seed 7: inspected in 2026-11-12, re-run only to compare rules

Usage: python run.py [label]   (writes runs/<run-id>/results.json and results.md)
"""
import importlib.util
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(HERE))
from pts import periodicity as P  # noqa: E402
from pts.stats import rate_text  # noqa: E402
from runlog import run_folder  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "conf1112", os.path.join(os.path.dirname(HERE), "2026-11-12_periodicity_confirmation", "run.py"))
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

ALPHA = 0.01
K = 199
TAU_LO, TAU_HI = G.TAU_LO, G.TAU_HI
Z_MIN, MIN_REPS = 5.0, 4.0          # the sigma rule adopted in 2026-11-12


def measure(x, sr, seed):
    env, fs = P.onset_envelope(x, sr)
    e = G.evidence(x, sr)
    sigma_ok = bool(G.accept(e, Z_MIN, MIN_REPS))
    sp = P.surrogate_p(env, fs, TAU_LO, TAU_HI, k=K, seed=seed)
    reps_ok = e["tau"] is not None and e["reps"] >= MIN_REPS
    return {**e, "sigma_rule": sigma_ok, "S": sp["statistic"], "p": sp["p"],
            "null_median": sp["null_median"], "null_max": sp["null_max"],
            "p_rule": bool(sp["p"] <= ALPHA and reps_ok)}


def synthetic(seeds, posgen, out):
    for s in seeds:
        rng = np.random.default_rng(s)
        dur = rng.uniform(20, 40)
        fam = list(G.NEGATIVES)[s % len(G.NEGATIVES)]
        out["neg"].append({"seed": s, "family": fam, **measure(G.NEGATIVES[fam](rng, dur), G.SR, s)})
        x, beat = posgen(rng, dur)
        m = measure(x, G.SR, s + 100000)
        m["right"] = bool(G.right_period(m, beat))
        out["pos"].append({"seed": s, "family": posgen.__name__, "beat": beat, **m})


def real(stems, shuffle_seed, out):
    rng = np.random.default_rng(shuffle_seed)
    for i, (name, x, sr) in enumerate(stems):
        out["pos"].append({"family": name, **measure(x, sr, 500 + i)})
        out["neg"].append({"family": name + " (shuffled)",
                           **measure(G.shuffle_chunks(rng, x, sr), sr, 600 + i)})


def summary(block):
    rows = {}
    for kind in ("neg", "pos"):
        cases = block[kind]
        n = len(cases)
        for rule in ("sigma_rule", "p_rule"):
            k = sum(c[rule] for c in cases)
            rows[(kind, rule)] = (k, n)
        rows[(kind, "both")] = (sum(c["sigma_rule"] and c["p_rule"] for c in cases), n)
        rows[(kind, "disagree")] = (sum(c["sigma_rule"] != c["p_rule"] for c in cases), n)
    return rows


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    with run_folder(__file__, label) as run:
        t0 = time.time()
        data = {name: {"neg": [], "pos": []} for name in ("fresh", "fresh_real", "dev_train", "dev_test", "dev_real")}
        synthetic(range(2000, 2120), G.groove, data["fresh"])
        print(f"fresh done ({time.time() - t0:.0f} s)", flush=True)
        stems = G.drum_stems()
        real(stems, 26, data["fresh_real"])
        print(f"fresh real done: {len(stems)} stems ({time.time() - t0:.0f} s)", flush=True)
        synthetic(range(60), G.click_train, data["dev_train"])
        synthetic(range(1000, 1060), G.groove, data["dev_test"])
        real(stems, 7, data["dev_real"])
        print(f"development done ({time.time() - t0:.0f} s)", flush=True)

        L = ["# Calibrated period confirmation: results", "",
             f"Run `{os.path.basename(run.path)}`. Sigma rule: {Z_MIN:g} sigma, {MIN_REPS:g} repetitions, stable halves, return "
             f"(2026-11-12). Surrogate rule: p <= {ALPHA:g} against K = {K} shuffles of the onset envelope, and at least "
             f"{MIN_REPS:g} repetitions. Rates are k of n with exact 95% intervals.", "",
             "| Set | Cases | Sigma rule | Surrogate rule | Both | Disagree |", "|---|---|---|---|---|---|"]
        res = {"alpha": ALPHA, "k": K, "z_min": Z_MIN, "min_reps": MIN_REPS, "data": data, "summary": {}}
        for name, block in data.items():
            rows = summary(block)
            res["summary"][name] = {f"{a}/{b}": v for (a, b), v in rows.items()}
            for kind, what in (("neg", "non-periodic: passed (false detections)"), ("pos", "periodic: passed")):
                L.append(f"| {name} | {what} | {rate_text(*rows[(kind, 'sigma_rule')])} | {rate_text(*rows[(kind, 'p_rule')])} | "
                         f"{rate_text(*rows[(kind, 'both')])} | {rows[(kind, 'disagree')][0]} |")
        L += ["", "## False detections of the surrogate rule by family (fresh set)", "",
              "| Family | Surrogate rule | Sigma rule | Median p |", "|---|---|---|---|"]
        fams = {}
        for c in data["fresh"]["neg"]:
            fams.setdefault(c["family"], []).append(c)
        for fam, cs in fams.items():
            L.append(f"| {fam} | {rate_text(sum(c['p_rule'] for c in cs), len(cs))} | "
                     f"{rate_text(sum(c['sigma_rule'] for c in cs), len(cs))} | {np.median([c['p'] for c in cs]):.3f} |")
        L += ["", "## Every disagreement", "", "| Set | Kind | Family | Seed | Sigma rule | p | S | Significance | Return | Weaker half |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for name, block in data.items():
            for kind in ("neg", "pos"):
                for c in block[kind]:
                    if c["sigma_rule"] != c["p_rule"]:
                        L.append(f"| {name} | {kind} | {c['family']} | {c.get('seed', '')} | {'yes' if c['sigma_rule'] else 'no'} | "
                                 f"{c['p']:.3f} | {c['S']:.1f} | {c['sig']:.1f} | {c['ret']:.1f} | {c['half']:.1f} |")
        pos_conf = [c for b in data.values() for c in b["pos"] if c["sigma_rule"]]
        at_floor = sum(c["p"] <= 1.0 / (K + 1) + 1e-12 for c in pos_conf)
        L += ["", f"Positives confirmed by the sigma rule with p at the floor 1/{K + 1}: {rate_text(at_floor, len(pos_conf))}.",
              f"Run time: {time.time() - t0:.0f} s."]
        res["positives_at_floor"] = (at_floor, len(pos_conf))
        with open(os.path.join(run.path, "results.json"), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=float)
        with open(os.path.join(run.path, "results.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(L) + "\n")
        print("\n".join(L))


if __name__ == "__main__":
    main()
