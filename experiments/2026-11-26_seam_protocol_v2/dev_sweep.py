"""Development sweep for seam protocol v2 (journal step 2026-11-26-seam-002, issue #34).

Known joins written into Suno mixes from Lex's archive (extend status unknown), two per track,
scored with the frozen Stage 1 of seam_features.py. Gives each feature's sensitivity to each kind
and size of join.

Inputs: PTS_ARCHIVE_DIR (archive root) and PTS_ARCHIVE_MANIFEST (its manifest CSV).
Usage: python dev_sweep.py [label]
"""
import csv
import hashlib
import json
import os
import re
import sys
import time

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from pts.stats import rate_text  # noqa: E402
from runlog import run_folder  # noqa: E402
import seam_features as SF  # noqa: E402

SEED = 20261126
MIN_LEN_S = 90.0
CONDITIONS = [("none", None)] + [("splice", x) for x in (0.0, 0.005, 0.05)] + [("lowpass", x) for x in (16000.0, 12000.0)] \
    + [("shelf", x) for x in (1.0, 2.0, 4.0)] + [("level", x) for x in (0.5, 1.0, 2.0)] + [("noise", x) for x in (-70.0, -60.0, -50.0)]


def tracks():
    root, man = os.environ["PTS_ARCHIVE_DIR"], os.environ["PTS_ARCHIVE_MANIFEST"]
    rows = [r for r in csv.DictReader(open(man, encoding="utf-8")) if r["class_guess"] == "suno_mix"]
    seen_sha, seen_name, out = set(), set(), []
    for r in sorted(rows, key=lambda r: (r["ext"] != "wav", r["path"])):      # prefer wav over mp3
        p = r["path"]
        name = os.path.splitext(os.path.basename(p))[0]
        if (r["sha256"] in seen_sha or name in seen_name or "htdemucs" in p.lower()
                or re.search(r"\(\d+(\.\d+)?x\)", p) or float(r["duration_s"]) < MIN_LEN_S):
            continue
        seen_sha.add(r["sha256"]); seen_name.add(name)
        out.append((name, os.path.join(root, p), r["sha256"]))
    return out


def fft_gain(x, sr, gain):
    X = np.fft.rfft(x)
    return np.fft.irfft(X * gain(np.fft.rfftfreq(len(x), 1.0 / sr)), len(x))


def inject(x, sr, joins, kind, size, rng):
    y = x.copy()
    for j in joins:
        i = int(j * sr)
        if kind == "none":
            continue
        if kind == "splice":
            # audio after the join comes from at least 30 s away in the same track
            cand = [s for s in range(0, len(x) - (len(x) - i), sr) if abs(s - i) >= 30 * sr]
            src = int(rng.choice(cand)) if cand else 0
            tail = x[src:src + len(x) - i]
            tail = np.pad(tail, (0, len(x) - i - len(tail)))
            n = int(size * sr)
            if n > 0:
                r = np.linspace(0, 1, n)
                y[i:i + n] = (1 - r) * y[i:i + n] + r * tail[:n]
                y[i + n:] = tail[n:]
            else:
                y[i:] = tail
            continue
        seg = y[i:]
        if kind == "lowpass":
            seg = fft_gain(seg, sr, lambda f: 1.0 / np.sqrt(1.0 + (f / size) ** 16))
        elif kind == "shelf":
            seg = fft_gain(seg, sr, lambda f: 1.0 + (10 ** (size / 20) - 1.0) / (1.0 + (4000.0 / np.maximum(f, 1.0)) ** 4))
        elif kind == "level":
            seg = seg * 10 ** (size / 20)
        elif kind == "noise":
            seg = seg + rng.standard_normal(len(seg)) * np.sqrt(np.mean(x ** 2)) * 10 ** (size / 20)
        n = int(0.005 * sr)                                    # 5 ms crossfade into the changed audio
        r = np.linspace(0, 1, n)
        seg[:n] = (1 - r) * y[i:i + n] + r * seg[:n]
        y[i:] = seg
    return y


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    with run_folder(__file__, label) as run:
        t0 = time.time()
        rng = np.random.default_rng(SEED)
        rows, inputs = [], {}
        for name, path, sha in tracks():
            x, sr = sf.read(path, always_2d=True)
            x = x.mean(axis=1)
            dur = len(x) / sr
            while True:
                joins = sorted(rng.uniform(20.0, dur - 20.0, 2))
                if joins[1] - joins[0] >= 30.0:
                    break
            inputs[name] = {"sha256": sha, "duration_s": dur, "joins": joins}
            for kind, size in CONDITIONS:
                y = inject(x, sr, joins, kind, size, rng)
                pv = SF.join_pvalues(y, sr, joins)
                for feat, lst in pv.items():
                    for e in lst:
                        rows.append({"track": name, "kind": kind, "size": size, "feature": feat, **e})
            print(f"{name}: done ({time.time() - t0:.0f} s)", flush=True)

        lines = ["# Seam protocol v2: development sweep", "",
                 f"Run `{os.path.basename(run.path)}`. {len(inputs)} Suno mixes, 2 joins each; share of joins with p <= 0.05 "
                 "against the same track's other places (exact 95% intervals).", "",
                 "| Join | " + " | ".join(SF.FEATURES) + " |", "|---" * (len(SF.FEATURES) + 1) + "|"]
        table = {}
        for kind, size in CONDITIONS:
            cells = []
            for feat in SF.FEATURES:
                sel = [r for r in rows if r["kind"] == kind and r["size"] == size and r["feature"] == feat]
                k = sum(r["p"] <= 0.05 for r in sel)
                table[f"{kind}:{size}:{feat}"] = (k, len(sel))
                cells.append(f"{k}/{len(sel)} ({100 * k / max(1, len(sel)):.0f}%)")
            lines.append(f"| {kind} {'' if size is None else size} | " + " | ".join(cells) + " |")
        lines += ["", "With no join written, every feature should flag about 5% of the fake joins (at most 10%):", ""]
        for feat in SF.FEATURES:
            lines.append(f"- {feat}: {rate_text(*table[f'none:None:{feat}'])}")
        lines.append(f"\nRun time: {time.time() - t0:.0f} s.")
        res = {"conditions": CONDITIONS, "inputs": inputs, "table": table, "rows": rows}
        json.dump(res, open(os.path.join(run.path, "results.json"), "w", encoding="utf-8"), indent=1, default=float)
        open(os.path.join(run.path, "results.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print("\n".join(lines))


if __name__ == "__main__":
    main()
