"""Cut the blinded tapping excerpts of the live recordings (journal step 2026-11-22-live-001).

  PTS_TAPPING_DIR=<output folder> python make_excerpts.py

Reads data/material/live/SOURCES.txt. Each recording gives one 30 s excerpt starting at 30% of
its length, never before the music starts ("music starts at about N s" in its source line) and
never past the end. The excerpts are written as audio/track_NN.wav in a random order (seed
20261122); key.json maps each track to its recording, start time and SHA-256, and is never served.
"""
import hashlib
import json
import os
import re

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LIVE = os.path.join(ROOT, "data", "material", "live")
SEED, LEN_S, FADE_S, PEAK = 20261122, 30.0, 0.05, 0.89


def recordings():
    out = []
    for line in open(os.path.join(LIVE, "SOURCES.txt"), encoding="utf-8").read().splitlines()[1:]:
        if "|" not in line:
            continue
        name = line.split("|")[0].strip()
        m = re.search(r"music starts at about (\d+(?:\.\d+)?) s", line)
        out.append((name, float(m.group(1)) if m else 0.0))
    return out


def excerpt_start(dur, music_start):
    return max(music_start, min(0.3 * dur, dur - LEN_S - 0.5))


def main():
    dst = os.environ["PTS_TAPPING_DIR"]
    os.makedirs(os.path.join(dst, "audio"), exist_ok=True)
    recs = recordings()
    order = np.random.default_rng(SEED).permutation(len(recs))
    key = []
    for i, j in enumerate(order, 1):
        name, music = recs[j]
        x, sr = sf.read(os.path.join(LIVE, name), always_2d=True)
        dur = len(x) / sr
        t0 = excerpt_start(dur, music)
        y = x[int(t0 * sr): int((t0 + LEN_S) * sr)].copy()
        f = int(FADE_S * sr)
        ramp = np.linspace(0, 1, f)[:, None]
        y[:f] *= ramp
        y[-f:] *= ramp[::-1]
        y *= PEAK / (np.abs(y).max() + 1e-12)
        tid = f"track_{i:02d}"
        path = os.path.join(dst, "audio", tid + ".wav")
        sf.write(path, y, sr, subtype="PCM_16")
        key.append({"id": tid, "name": name, "start_s": round(t0, 3), "music_start_s": music,
                    "duration_s": round(dur, 3), "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest()})
        print(tid, "written", flush=True)
    json.dump({"seed": SEED, "tracks": key}, open(os.path.join(dst, "key.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
