"""Score Suno tracks with known extend points, ONCE (seam protocol v2, see PROTOCOL.md).

Input: data/material/seams/<track>/ with
  joins.txt   the extend times, one per line, in seconds or m:ss, written by Lex before scoring
  <one audio file>   the full track as exported (stems, if any, in a stems/ subfolder; not used here)
Refuses to run if seam_features.py differs from the frozen version, or if a folder has no joins.txt.

Usage: python score_joins.py [label]
"""
import glob
import hashlib
import json
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from pts.stats import rate_text  # noqa: E402
from runlog import run_folder  # noqa: E402

FROZEN_SHA256 = "b7243441c4a70367c9f49c7857e6ae98d7985e0c44048587b201a040da63bbc5"
AUDIO = (".wav", ".mp3", ".flac", ".aiff", ".aif")


def check_frozen():
    with open(os.path.join(HERE, "seam_features.py"), "rb") as f:
        h = hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()
    if h != FROZEN_SHA256:
        raise SystemExit(f"seam_features.py changed since it was frozen ({h}); the protocol forbids scoring with it")


def parse_time(s):
    s = s.strip()
    if ":" in s:
        m, sec = s.split(":", 1)
        return 60.0 * float(m) + float(sec)
    return float(s)


def load_tracks():
    out = []
    for d in sorted(glob.glob(os.path.join(ROOT, "data", "material", "seams", "*"))):
        if not os.path.isdir(d):
            continue
        jt = os.path.join(d, "joins.txt")
        if not os.path.exists(jt):
            raise SystemExit(f"{os.path.basename(d)}: no joins.txt; the times must be written down before scoring")
        joins = [parse_time(l) for l in open(jt, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")]
        audio = [p for p in glob.glob(os.path.join(d, "*")) if p.lower().endswith(AUDIO)]
        if len(audio) != 1:
            raise SystemExit(f"{os.path.basename(d)}: expected one full-track audio file, found {len(audio)}")
        out.append((os.path.basename(d), audio[0], joins))
    return out


def main():
    check_frozen()
    import seam_features as SF
    label = sys.argv[1] if len(sys.argv) > 1 else "score"
    with run_folder(__file__, label) as run:
        rows, inputs = [], {}
        for name, path, joins in load_tracks():
            with open(path, "rb") as f:
                sha = hashlib.sha256(f.read()).hexdigest()
            x, sr = sf.read(path, always_2d=True)
            x = x.mean(axis=1)
            inputs[name] = {"file": os.path.basename(path), "sha256": sha, "duration_s": len(x) / sr, "joins": joins}
            usable = [j for j in joins if SF.EXCL_S <= j <= len(x) / sr - SF.EXCL_S]
            for feat, lst in SF.join_pvalues(x, sr, usable).items():
                for e in lst:
                    rows.append({"track": name, "feature": feat, **e})
            inputs[name]["excluded_joins"] = [j for j in joins if j not in usable]
        n_joins = len({(r["track"], r["join_s"]) for r in rows})
        tails, lines = [], ["# Seam protocol v2: Stage 1 on tracks with known joins", "",
                            f"Run `{os.path.basename(run.path)}`. {len(inputs)} tracks, {n_joins} usable joins.", "",
                            "| Feature | Joins with p <= 0.05 | Binomial tail (rate 0.05) | Holm, alpha 0.05 |", "|---|---|---|---|"]
        for feat in SF.FEATURES:
            sel = [r for r in rows if r["feature"] == feat]
            k = sum(r["p"] <= 0.05 for r in sel)
            tails.append(SF.binomial_tail(k, len(sel)))
        rej = SF.holm(np.array(tails))
        for feat, tail, r_ in zip(SF.FEATURES, tails, rej):
            sel = [r for r in rows if r["feature"] == feat]
            k = sum(r["p"] <= 0.05 for r in sel)
            lines.append(f"| {feat} | {rate_text(k, len(sel))} | {tail:.4g} | {'visible' if r_ else 'not shown'} |")
        lines += ["", "## Every join", "", "| Track | Join (s) | " + " | ".join(SF.FEATURES) + " |", "|---" * (len(SF.FEATURES) + 2) + "|"]
        for (track, j) in sorted({(r["track"], r["join_s"]) for r in rows}):
            ps = {r["feature"]: r["p"] for r in rows if r["track"] == track and r["join_s"] == j}
            lines.append(f"| {track} | {j:.1f} | " + " | ".join(f"{ps[f]:.3f}" for f in SF.FEATURES) + " |")
        res = {"frozen_sha256": FROZEN_SHA256, "inputs": inputs, "rows": rows,
               "binomial_tails": dict(zip(SF.FEATURES, tails)), "holm_visible": dict(zip(SF.FEATURES, map(bool, rej)))}
        json.dump(res, open(os.path.join(run.path, "results.json"), "w", encoding="utf-8"), indent=1, default=float)
        open(os.path.join(run.path, "results.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print("\n".join(lines))


if __name__ == "__main__":
    main()
