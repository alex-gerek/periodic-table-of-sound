"""Seam hunt, pilot (issue #34, journal step 2026-11-26-seam-001; plan fixed before any run).

A Seam is a join where the background of the sound changes without a musical reason. The
detector watches the background (the floor of each band between notes, and the bandwidth),
not the notes, and compares the median of 6 s before and after every second. The idea is the
regime monitor of our Blind Signal Discovery project, re-derived here for music.

  live windows   17 live recordings, 30 s windows; conformal p against the windows of the
                 other recordings (leave one recording out)
  known seams    four seams written into every live window at a known time
  Suno windows   our Suno tracks (mix = sum of stems), scored against all live windows

Usage: python run.py [label]   (writes runs/<run-id>/results.json and results.md)
Audio stays outside git; the inputs are listed with their SHA-256 in results.json.
"""
import glob
import hashlib
import json
import os
import sys
import time

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(HERE))
from pts.stats import conformal_p, rate_text  # noqa: E402
from runlog import run_folder  # noqa: E402

WIN_S = 30
SIDE = 6                       # blocks of 1 s on each side of a boundary
NFFT = 2048
HOP_S = 0.05
BANDS = np.geomspace(100.0, 16000.0, 9)          # 8 log bands
FLOOR_Q = 10.0                 # percentile of frame power inside a block: the floor between notes
MAD_FLOOR_DB = 0.5
ALPHA = 0.05
SEED = 20261126
SEAM_TYPES = ("bandwidth", "floor", "tilt", "splice")
LOC_TOL_S = 1.0
SPLICE_OFFSET_S = 60.0
XFADE_S = 0.005
DB_MIN = -140.0


# ---------------------------------------------------------------- input

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_mono(path):
    x, sr = sf.read(path, always_2d=True)
    return x.mean(axis=1), sr


def live_recordings():
    files = sorted(f for f in glob.glob(os.path.join(ROOT, "data", "material", "live", "*"))
                   if not f.endswith(".txt"))
    return [(os.path.basename(f), f) for f in files]


def suno_tracks():
    folders = (sorted(glob.glob(os.path.join(ROOT, "data", "stems", "*")))
               + sorted(glob.glob(os.path.join(ROOT, "data", "material", "tempo_series", "*")))
               + sorted(g for g in glob.glob(os.path.join(ROOT, "data", "material", "meters", "*"))
                        if not g.endswith("meter_6-8_real"))
               + sorted(g for g in glob.glob(os.path.join(ROOT, "data", "material", "vibrato", "*")) if os.path.isdir(g)))
    out = [(os.path.basename(d), sorted(glob.glob(os.path.join(d, "*.wav")))) for d in folders]
    single = os.path.join(ROOT, "data", "material", "vibrato", "suno_vibrato_01.wav")
    if os.path.exists(single):
        out.append(("suno_vibrato_01", [single]))
    return [(n, fs) for n, fs in out if fs]


def suno_mix(files):
    mix, sr0 = None, None
    for f in files:
        x, sr = load_mono(f)
        if sr0 is None:
            mix, sr0 = x.copy(), sr
        else:
            if sr != sr0:
                raise ValueError(f"stems at different rates in {f}")
            n = min(len(mix), len(x))
            mix = mix[:n] + x[:n]
    return mix, sr0


# ---------------------------------------------------------------- detector

def block_features(x, sr):
    """Per 1 s block: 8 band floors (dB) and the bandwidth ratio (dB). Returns (n_blocks, 9)."""
    hop = int(round(HOP_S * sr))
    win = np.hanning(NFFT)
    n_frames = 1 + (len(x) - NFFT) // hop
    idx = np.arange(NFFT)[None, :] + hop * np.arange(n_frames)[:, None]
    P = np.abs(np.fft.rfft(x[idx] * win, axis=1)) ** 2
    f = np.fft.rfftfreq(NFFT, 1.0 / sr)
    bands = np.stack([P[:, (f >= lo) & (f < hi)].sum(axis=1) for lo, hi in zip(BANDS[:-1], BANDS[1:])], axis=1)
    top = min(20000.0, 0.95 * sr / 2)
    hi_band = P[:, (f >= 16000.0) & (f < top)].sum(axis=1)
    mid_band = P[:, (f >= 8000.0) & (f < 16000.0)].sum(axis=1)
    per_block = int(round(1.0 / HOP_S))
    n_blocks = n_frames // per_block
    feats = []
    for b in range(n_blocks):
        s = slice(b * per_block, (b + 1) * per_block)
        floor = np.percentile(bands[s], FLOOR_Q, axis=0)
        ratio = hi_band[s].mean() / max(mid_band[s].mean(), 1e-30)
        feats.append(np.concatenate([floor, [max(ratio, 1e-30)]]))
    F = 10.0 * np.log10(np.maximum(np.array(feats), 1e-30))
    return np.maximum(F, DB_MIN)


def change_scores(F):
    """|median after - median before| / (1.4826 x pooled MAD + 0.5 dB) at each boundary, per feature."""
    out = {}
    for b in range(SIDE, len(F) - SIDE + 1):
        before, after = F[b - SIDE:b], F[b:b + SIDE]
        mb, ma = np.median(before, axis=0), np.median(after, axis=0)
        dev = np.concatenate([np.abs(before - mb), np.abs(after - ma)])
        out[b] = np.abs(ma - mb) / (1.4826 * np.median(dev, axis=0) + MAD_FLOOR_DB)
    return out


def window_score(x, sr):
    F = block_features(x, sr)
    cs = change_scores(F)
    if not cs:
        raise ValueError("window too short")
    bs = sorted(cs)
    all_ = [float(np.max(cs[b])) for b in bs]
    bw = [float(cs[b][-1]) for b in bs]
    ia, ib = int(np.argmax(all_)), int(np.argmax(bw))
    return {"S_all": all_[ia], "t_all": bs[ia], "feature_all": int(np.argmax(cs[bs[ia]])),
            "S_bw": bw[ib], "t_bw": bs[ib]}


# ---------------------------------------------------------------- known seams

def fft_filter(x, sr, gain_fn):
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1.0 / sr)
    return np.fft.irfft(X * gain_fn(f), n)


def lowpass_16k(f):
    return 1.0 / (1.0 + (f / 16000.0) ** 16)          # |H|^2 of an 8th-order Butterworth: zero phase


def shelf_3db(f):
    s = 1.0 / (1.0 + (4000.0 / np.maximum(f, 1.0)) ** 4)
    return 1.0 + (10 ** (3.0 / 20) - 1.0) * s


def crossfade_at(a, b, i, sr):
    """a before sample i, b after it, with a short linear crossfade."""
    n = int(XFADE_S * sr)
    y = a.copy()
    y[i:] = b[i:]
    lo = max(0, i - n // 2)
    hi = min(len(a), lo + n)
    r = np.linspace(0.0, 1.0, hi - lo)
    y[lo:hi] = (1 - r) * a[lo:hi] + r * b[lo:hi]
    return y


def inject(kind, rec, start, sr, t0, rng):
    w = rec[start:start + WIN_S * sr]
    i = int(t0 * sr)
    if kind == "bandwidth":
        return crossfade_at(w, fft_filter(w, sr, lowpass_16k), i, sr)
    if kind == "tilt":
        return crossfade_at(w, fft_filter(w, sr, shelf_3db), i, sr)
    if kind == "floor":
        rms = np.sqrt(np.mean(w ** 2)) + 1e-12
        noisy = w + rng.standard_normal(len(w)) * rms * 10 ** (-60 / 20)
        return crossfade_at(w, noisy, i, sr)
    if kind == "splice":
        off = int(SPLICE_OFFSET_S * sr)
        for src in (start + off, start - off):
            if src >= 0 and src + len(w) <= len(rec):
                return crossfade_at(w, rec[src:src + len(w)], i, sr)
        return None                                   # recording too short: excluded and counted
    raise ValueError(kind)


# ---------------------------------------------------------------- main

def windows_of(x, sr):
    n = WIN_S * sr
    return [k * n for k in range(len(x) // n)]


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    with run_folder(__file__, label) as run:
        t_start = time.time()
        rng = np.random.default_rng(SEED)
        inputs = {}
        live, recs = [], {}
        for name, path in live_recordings():
            x, sr = load_mono(path)
            inputs[name] = sha256(path)
            recs[name] = (x, sr)
            for s in windows_of(x, sr):
                live.append({"rec": name, "start_s": s / sr, **window_score(x[s:s + WIN_S * sr], sr)})
        print(f"live: {len(live)} windows from {len(recs)} recordings ({time.time() - t_start:.0f} s)", flush=True)

        def p_vs(score_key, value, exclude_rec=None):
            null = [w[score_key] for w in live if w["rec"] != exclude_rec]
            return conformal_p(value, null)

        for w in live:
            w["p_all"] = p_vs("S_all", w["S_all"], w["rec"])
            w["p_bw"] = p_vs("S_bw", w["S_bw"], w["rec"])

        seams = []
        for w in live:
            x, sr = recs[w["rec"]]
            start = int(round(w["start_s"] * sr))
            for kind in SEAM_TYPES:
                t0 = float(rng.uniform(8.0, 22.0))
                y = inject(kind, x, start, sr, t0, rng)
                if y is None:
                    seams.append({"rec": w["rec"], "start_s": w["start_s"], "kind": kind, "t0": t0, "excluded": True})
                    continue
                s = window_score(y, sr)
                e = {"rec": w["rec"], "start_s": w["start_s"], "kind": kind, "t0": t0, "excluded": False, **s,
                     "p_all": p_vs("S_all", s["S_all"], w["rec"]), "p_bw": p_vs("S_bw", s["S_bw"], w["rec"])}
                e["found_all"] = bool(e["p_all"] <= ALPHA and abs(e["t_all"] - t0) <= LOC_TOL_S)
                e["found_bw"] = bool(e["p_bw"] <= ALPHA and abs(e["t_bw"] - t0) <= LOC_TOL_S)
                seams.append(e)
        print(f"known seams: {len(seams)} ({time.time() - t_start:.0f} s)", flush=True)

        suno = []
        for name, files in suno_tracks():
            x, sr = suno_mix(files)
            inputs[name] = {os.path.basename(f): sha256(f) for f in files}
            for s in windows_of(x, sr):
                sc = window_score(x[s:s + WIN_S * sr], sr)
                suno.append({"track": name, "start_s": s / sr, **sc,
                             "p_all": p_vs("S_all", sc["S_all"]), "p_bw": p_vs("S_bw", sc["S_bw"])})
        print(f"suno: {len(suno)} windows ({time.time() - t_start:.0f} s)", flush=True)

        # ------------------------------------------------------------ report
        feat_names = [f"floor {int(lo)}-{int(hi)} Hz" for lo, hi in zip(BANDS[:-1], BANDS[1:])] + ["bandwidth ratio"]
        k = lambda xs, key: (sum(1 for v in xs if v[key] <= ALPHA), len(xs))  # noqa: E731
        L = ["# Seam hunt, pilot: results", "",
             f"Run `{os.path.basename(run.path)}`. Windows of {WIN_S} s, change of the median over {SIDE} s on each side, "
             f"flagged at conformal p <= {ALPHA:g}. Rates with exact 95% intervals.", "",
             "## P1: live windows flagged (leave one recording out)", "",
             f"- S_all: {rate_text(*k(live, 'p_all'))}",
             f"- S_bw: {rate_text(*k(live, 'p_bw'))}", "",
             "| Recording | Windows | Flagged by S_all | Flagged by S_bw |", "|---|---|---|---|"]
        for name in recs:
            ws = [w for w in live if w["rec"] == name]
            L.append(f"| {name[:60]} | {len(ws)} | {k(ws, 'p_all')[0]} | {k(ws, 'p_bw')[0]} |")
        L += ["", "## P2: known seams found (flagged and within 1 s of the join)", "",
              "| Seam | Cases (excluded) | Found by S_all | Found by S_bw | Flagged by S_all, any time |", "|---|---|---|---|---|"]
        res_seams = {}
        for kind in SEAM_TYPES:
            cs = [s for s in seams if s["kind"] == kind and not s["excluded"]]
            ex = sum(1 for s in seams if s["kind"] == kind and s["excluded"])
            fa, fb = sum(s["found_all"] for s in cs), sum(s["found_bw"] for s in cs)
            anyf = sum(s["p_all"] <= ALPHA for s in cs)
            res_seams[kind] = {"n": len(cs), "excluded": ex, "found_all": fa, "found_bw": fb, "flagged_all": anyf}
            L.append(f"| {kind} | {len(cs)} ({ex}) | {rate_text(fa, len(cs))} | {rate_text(fb, len(cs))} | {rate_text(anyf, len(cs))} |")
        L += ["", "## P3: Suno windows flagged (against all live windows; a comparison, not a calibrated test)", "",
              f"- S_all: Suno {rate_text(*k(suno, 'p_all'))}; live {rate_text(*k(live, 'p_all'))}",
              f"- S_bw: Suno {rate_text(*k(suno, 'p_bw'))}; live {rate_text(*k(live, 'p_bw'))}", "",
              "Candidates for a test with known join times (not counted as seams):", "",
              "| Track | Window start | S_all time | S_all | p_all | Feature | S_bw time | S_bw | p_bw |", "|---|---|---|---|---|---|---|---|---|"]
        for s in sorted(suno, key=lambda s: min(s["p_all"], s["p_bw"])):
            if s["p_all"] <= ALPHA or s["p_bw"] <= ALPHA:
                L.append(f"| {s['track']} | {s['start_s']:.0f} s | {s['start_s'] + s['t_all']:.0f} s | {s['S_all']:.1f} | {s['p_all']:.3f} | "
                         f"{feat_names[s['feature_all']]} | {s['start_s'] + s['t_bw']:.0f} s | {s['S_bw']:.1f} | {s['p_bw']:.3f} |")
        med = lambda xs, key: float(np.median([v[key] for v in xs]))  # noqa: E731
        L += ["", "## Score medians", "", "| Set | S_all | S_bw |", "|---|---|---|",
              f"| live | {med(live, 'S_all'):.2f} | {med(live, 'S_bw'):.2f} |",
              f"| Suno | {med(suno, 'S_all'):.2f} | {med(suno, 'S_bw'):.2f} |", "",
              f"Run time: {time.time() - t_start:.0f} s."]
        res = {"config": {"win_s": WIN_S, "side": SIDE, "nfft": NFFT, "hop_s": HOP_S, "bands": BANDS.tolist(),
                          "floor_q": FLOOR_Q, "mad_floor_db": MAD_FLOOR_DB, "alpha": ALPHA, "seed": SEED,
                          "loc_tol_s": LOC_TOL_S, "splice_offset_s": SPLICE_OFFSET_S, "xfade_s": XFADE_S},
               "inputs_sha256": inputs, "features": feat_names, "live": live, "seams": seams, "seam_summary": res_seams,
               "suno": suno}
        with open(os.path.join(run.path, "results.json"), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=float)
        with open(os.path.join(run.path, "results.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(L) + "\n")
        print("\n".join(L))


if __name__ == "__main__":
    main()
