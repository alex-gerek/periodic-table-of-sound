"""Stem leakage with the other stem as a witness (issue #38, journal step 2026-11-26-leak-001).

The plan, hypotheses and decision rule were committed before this script was first run.

For a target stem D and a witness stem V (complex STFTs, frames t, bins k):
  g_k        = sum_t D V* / sum_t |V|^2                    complex gain of the witness in bin k
  explained  = sum_k |sum_t D V*|^2 / sum_t |V|^2           target energy that the witness explains
  share      = explained / sum_k sum_t |D|^2               the statistic; 10 log10(share) = leak in dB
Significance: the share for the witness circularly shifted by K random offsets (2 s to length - 2 s).

Inputs: Suno stem sets in Lex's archive (environment variable PTS_ARCHIVE_DIR) and in data/stems.
Usage: python run.py [label]
"""
import glob
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
from pts.stats import conformal_p, exact_interval, rate_text  # noqa: E402
from runlog import run_folder  # noqa: E402

SR = 48000
NFFT, HOP = 2048, 512
F_LO, F_HI = 100.0, 12000.0
EXCERPT_S = 60
K = 199
ALPHA = 0.01
MIN_SHIFT_S = 2.0
SEED = 20261126
LEVELS_DB = (-50, -45, -40, -35, -30, -25, -20)
MASK_KEEP = 0.5

ARCHIVE_SETS = {                      # song -> folder inside PTS_ARCHIVE_DIR
    "Boo-da Boo-da Boo-da Boom": "Boo-da Boo-da Boo-da Boom/Stems",
    "Data Corruption": "Data Corruption/The 42nd Blueprint Ash_Circuit",
    "EVERYTHINGS ALRIGHT": "EVERYTHINGS ALRIGHT/Stems_2",
    "Metro": "Metro/Stems",
    "Pocket Blues": "Pocket Blues/Stems",
}
LOCAL_SETS = {"GRAVITY HAS AN ADDRESS": "data/stems/gravity", "Pure voltage": "data/stems/pure_voltage"}
STEM_RE = re.compile(r"^\d+\s+(.+?)(\s*\(\d+\))?\.(wav|mp3|flac)$", re.I)


# ---------------------------------------------------------------- input

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def song_folders():
    archive = os.environ.get("PTS_ARCHIVE_DIR")
    if not archive:
        raise SystemExit("set PTS_ARCHIVE_DIR to the archive root")
    out = {s: os.path.join(archive, rel) for s, rel in ARCHIVE_SETS.items()}
    out.update({s: os.path.join(ROOT, rel) for s, rel in LOCAL_SETS.items()})
    return out


def load_song(folder):
    stems, hashes = {}, {}
    for p in sorted(glob.glob(os.path.join(folder, "*"))):
        m = STEM_RE.match(os.path.basename(p))
        if not m:
            continue
        x, sr = sf.read(p, always_2d=True)
        if sr != SR:
            raise ValueError(f"{p}: {sr} Hz")
        stems[m.group(1).strip()] = x.mean(axis=1)
        hashes[os.path.basename(p)] = sha256(p)
    n = min(len(v) for v in stems.values())
    return {k: v[:n] for k, v in stems.items()}, hashes


def excerpt_start(vocal):
    """Start (whole seconds) of the 60 s window with the most lead-vocal energy."""
    e = np.add.reduceat(vocal ** 2, np.arange(0, len(vocal) - SR + 1, SR))
    if len(e) <= EXCERPT_S:
        return 0
    c = np.convolve(e, np.ones(EXCERPT_S), mode="valid")
    return int(np.argmax(c))


# ---------------------------------------------------------------- estimator

WIN = np.hanning(NFFT + 1)[:NFFT]                  # periodic Hann: overlap-adds to a constant
FREQS = np.fft.rfftfreq(NFFT, 1.0 / SR)
BAND = (FREQS >= F_LO) & (FREQS <= F_HI)
N_BANDS = 16
BAND_EDGES = np.geomspace(F_LO, F_HI, N_BANDS + 1)


def stft(x):
    n = 1 + (len(x) - NFFT) // HOP
    idx = np.arange(NFFT)[None, :] + HOP * np.arange(n)[:, None]
    return np.fft.rfft(x[idx] * WIN, axis=1)


def istft(X, length):
    frames = np.fft.irfft(X, NFFT, axis=1) * WIN
    y = np.zeros(length)
    w = np.zeros(length)
    for t in range(X.shape[0]):
        y[t * HOP:t * HOP + NFFT] += frames[t]
        w[t * HOP:t * HOP + NFFT] += WIN ** 2
    # at the very edges the window sum is near zero; dividing there blows up a masked
    # spectrogram (found in the synthetic check before any data run), so those samples are zeroed
    ok = w > 1e-3 * w.max()
    out = np.zeros(length)
    out[ok] = y[ok] / w[ok]
    return out


def shares(target, witness, shifts):
    """Explained share for shift 0 and for each circular shift (in frames) of the witness."""
    D, V = stft(target)[:, BAND], stft(witness)[:, BAND]
    ed = float(np.sum(np.abs(D) ** 2))
    ev = np.sum(np.abs(V) ** 2, axis=0)                       # per bin, shift-invariant
    keep = ev > 0
    D, V, ev = D[:, keep], V[:, keep], ev[keep]
    # c_k(s) = sum_t D[t, k] conj(V[t - s, k]) for every circular shift s, by FFT along time
    C = np.fft.ifft(np.fft.fft(D, axis=0) * np.conj(np.fft.fft(V, axis=0)), axis=0)
    # one complex gain per log band, not per bin (amendment before the first data run):
    # fewer free gains lower the chance level of the explained share
    band_of = np.digitize(FREQS[BAND][keep], BAND_EDGES[1:-1])
    expl = np.zeros(C.shape[0])
    for b in range(N_BANDS):
        sel = band_of == b
        if np.any(sel):
            expl += np.abs(C[:, sel].sum(axis=1)) ** 2 / ev[sel].sum()
    if ed <= 0:
        return 0.0, np.zeros(len(shifts))
    return float(expl[0] / ed), expl[np.asarray(shifts)] / ed


def band_energy(x):
    """Energy in the measured band (100 Hz to 12 kHz). Leak levels are defined in this band,
    the same band the estimator measures (amendment before the first data run)."""
    return float(np.sum(np.abs(stft(x)[:, BAND]) ** 2))


def shift_set(n_frames, rng):
    lo = int(np.ceil(MIN_SHIFT_S * SR / HOP))
    return rng.choice(np.arange(lo, n_frames - lo), size=K, replace=False)


def test(target, witness, rng):
    n_frames = 1 + (len(target) - NFFT) // HOP
    sh = shift_set(n_frames, rng)
    s0, null = shares(target, witness, sh)
    # the estimate subtracts the chance level (median of the shifted shares); amendment before the first data run
    est = s0 - float(np.median(null))
    return {"share": s0, "raw_db": 10 * np.log10(max(s0, 1e-30)),
            "db": 10 * np.log10(est) if est > 0 else float("-inf"), "p": conformal_p(s0, null),
            "null_median_db": float(10 * np.log10(max(np.median(null), 1e-30)))}


def masked(witness, rng):
    X = stft(witness)
    M = rng.random(X.shape) < MASK_KEEP
    y = istft(X * M, len(witness))
    return y


# ---------------------------------------------------------------- main

def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    with run_folder(__file__, label) as run:
        t0 = time.time()
        rng = np.random.default_rng(SEED)
        songs, inputs = {}, {}
        for song, folder in song_folders().items():
            stems, hashes = load_song(folder)
            lead = next(k for k in stems if k.lower() == "lead vocals")
            s = excerpt_start(stems[lead])
            songs[song] = {k: v[s * SR:(s + EXCERPT_S) * SR] for k, v in stems.items()}
            inputs[song] = {"excerpt_start_s": s, "stems": hashes}
            print(f"{song}: {len(stems)} stems, excerpt from {s} s", flush=True)

        names = list(songs)
        cross = []
        for a in names:
            drums = songs[a]["Drums"]
            ed = band_energy(drums)
            for b in names:
                if a == b:
                    continue
                v = songs[b]["Lead Vocals"]
                ev = band_energy(v)
                row = {"target_song": a, "witness_song": b, "none": test(drums, v, rng)}
                vm = masked(v, rng)
                evm = band_energy(vm)
                for L in LEVELS_DB:
                    want = ed * 10 ** (L / 10)
                    row[f"linear{L}"] = test(drums + v * np.sqrt(want / ev), v, rng)
                    row[f"masked{L}"] = test(drums + vm * np.sqrt(want / evm), v, rng)
                cross.append(row)
            print(f"cross pairs for {a} done ({time.time() - t0:.0f} s)", flush=True)

        within = {}
        for song, stems in songs.items():
            keys = list(stems)
            within[song] = {t: {w: test(stems[t], stems[w], rng) for w in keys if w != t} for t in keys}
        print(f"within-song matrices done ({time.time() - t0:.0f} s)", flush=True)

        # ------------------------------------------------------------ report
        n = len(cross)
        det = lambda key: sum(r[key]["p"] <= ALPHA for r in cross)  # noqa: E731
        L_ = ["# Stem leakage: results", "",
              f"Run `{os.path.basename(run.path)}`. {len(names)} songs, {n} cross-song pairs (drums of A, lead vocal of B). "
              f"Detection at conformal p <= {ALPHA:g} against K = {K} circular shifts. Rates with exact 95% intervals.", "",
              f"**H1, no leak written:** {rate_text(det('none'), n)} detected; median share {np.median([r['none']['db'] for r in cross]):.1f} dB.", "",
              "| Leak written (dB of drum energy) | Linear: detected | Linear: estimate, median (dB) | Linear: median abs. error (dB) | Masked: detected | Masked: estimate, median (dB) |",
              "|---|---|---|---|---|---|"]
        summary = {"none": det("none")}
        for L in LEVELS_DB:
            lin = [r[f"linear{L}"]["db"] for r in cross]
            msk = [r[f"masked{L}"]["db"] for r in cross]
            summary[L] = {"linear_detected": det(f"linear{L}"), "masked_detected": det(f"masked{L}"),
                          "linear_median_db": float(np.median(lin)), "linear_mae_db": float(np.median(np.abs(np.array(lin) - L))),
                          "masked_median_db": float(np.median(msk))}
            s = summary[L]
            L_.append(f"| {L} | {rate_text(s['linear_detected'], n)} | {s['linear_median_db']:.1f} | {s['linear_mae_db']:.2f} | "
                      f"{rate_text(s['masked_detected'], n)} | {s['masked_median_db']:.1f} |")
        L_ += ["", "## Within each song: explained share (dB of the target), p in brackets", "",
               "Rows are targets, columns witnesses. Bold: p <= 0.01.", ""]
        for song, m in within.items():
            keys = list(m)
            L_ += [f"### {song}", "", "| target \\ witness | " + " | ".join(keys) + " |", "|---" * (len(keys) + 1) + "|"]
            for t in keys:
                cells = []
                for w in keys:
                    if w == t:
                        cells.append("–")
                        continue
                    e = m[t][w]
                    c = f"{e['db']:.1f} ({e['p']:.3f})"
                    cells.append(f"**{c}**" if e["p"] <= ALPHA else c)
                L_.append(f"| {t} | " + " | ".join(cells) + " |")
            L_.append("")
        L_.append(f"Run time: {time.time() - t0:.0f} s.")
        res = {"config": {"sr": SR, "nfft": NFFT, "hop": HOP, "band_hz": [F_LO, F_HI], "excerpt_s": EXCERPT_S, "k": K,
                          "alpha": ALPHA, "min_shift_s": MIN_SHIFT_S, "seed": SEED, "levels_db": LEVELS_DB, "mask_keep": MASK_KEEP},
               "inputs": inputs, "summary": summary, "cross": cross, "within": within}
        with open(os.path.join(run.path, "results.json"), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=float)
        with open(os.path.join(run.path, "results.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(L_) + "\n")
        print("\n".join(L_))


if __name__ == "__main__":
    main()
