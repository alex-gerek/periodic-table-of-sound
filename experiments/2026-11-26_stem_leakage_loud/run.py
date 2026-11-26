"""Leaks written where the target is loud (issue #38, journal step 2026-11-26-leak-003).

Plan, hypotheses and decision rule committed before this script was first run. Estimators A and B
are imported unchanged from leak-002; loading and STFT from leak-001.

Leak kinds (each scaled to L dB of the target's band energy):
  linear      the witness itself
  independent the witness through a random binary mask (keep 0.5), as in leak-001 and leak-002
  wiener      the witness through |D|^2 / (|D|^2 + |V|^2): the separator's mask for the target
  loud        the witness kept only where the target's cell power is above its bin's median
Real-stem check: A on full tracks (leak-002) against the 60 s estimator (leak-001), within songs,
median absolute difference over the pairs that both detect.

Usage: PTS_ARCHIVE_DIR=<archive> python run.py [label]
"""
import glob
import importlib.util
import json
import os
import sys
import time

import numpy as np
import scipy.fft as sfft   # multithreaded FFT for estimator C (speed only)

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
ROOT = os.path.dirname(EXP)
sys.path.insert(0, ROOT)
sys.path.insert(0, EXP)
from pts.stats import rate_text  # noqa: E402
from runlog import run_folder  # noqa: E402


def _load(name, folder):
    spec = importlib.util.spec_from_file_location(name, os.path.join(EXP, folder, "run.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


L1 = _load("leak001", "2026-11-26_stem_leakage")
L2 = _load("leak002", "2026-11-26_stem_leakage_full")

SEED = 20261128
LEVELS_DB = (-40, -35, -30, -25)
KINDS = ("linear", "independent", "wiener", "loud")


N_CLASSES = 4


def estimate_c(D, V, shifts):
    """Estimator C (added before the first data run): one complex gain per band and per class
    of target loudness. The classes are the quartiles of each bin's cell power over the frames,
    so a leak that sits only where the target is loud gets its own gain."""
    from pts.stats import conformal_p
    idx = np.concatenate([[0], shifts])
    pd = np.abs(D) ** 2
    q = np.minimum((np.argsort(np.argsort(pd, axis=0), axis=0) * N_CLASSES) // pd.shape[0], N_CLASSES - 1)
    pv = np.abs(V) ** 2
    ed = float(pd.sum())
    expl = np.zeros(len(idx))
    for b in range(L2.N_BANDS):
        sel = L2.BAND_OF == b
        if not np.any(sel):
            continue
        Db, Vb, qb, pvb = D[:, sel], V[:, sel], q[:, sel], pv[:, sel]
        FV, FPV = sfft.fft(Vb, axis=0, workers=-1), sfft.fft(pvb, axis=0, workers=-1)
        for c in range(N_CLASSES):
            ind = (qb == c).astype(float)
            Cc = sfft.ifft(sfft.fft(ind * Db, axis=0, workers=-1) * np.conj(FV), axis=0, workers=-1).sum(axis=1)[idx]
            den = np.real(sfft.ifft(sfft.fft(ind, axis=0, workers=-1) * np.conj(FPV), axis=0, workers=-1)).sum(axis=1)[idx]
            expl += np.abs(Cc) ** 2 / np.maximum(den, 1e-300)
    stat = expl / ed
    est = stat[0] - float(np.median(stat[1:]))
    return {"p": conformal_p(stat[0], stat[1:]), "db": 10 * np.log10(est) if est > 0 else float("-inf"),
            "chance_db": float(10 * np.log10(max(np.median(stat[1:]), 1e-30)))}


def estimate_all(D, V, shifts):
    out = L2.estimate(D, V, shifts)
    out["C"] = estimate_c(D, V, shifts)
    return out


def leak_audio(kind, Dfull, Vfull, n_samples, rng):
    """Leak signal (audio) of the given kind, before scaling."""
    if kind == "linear":
        X = Vfull
    elif kind == "independent":
        X = Vfull * (rng.random(Vfull.shape) < 0.5)
    elif kind == "wiener":
        pd, pv = np.abs(Dfull) ** 2, np.abs(Vfull) ** 2
        X = Vfull * (pd / np.maximum(pd + pv, 1e-30))
    elif kind == "loud":
        pd = np.abs(Dfull) ** 2
        X = Vfull * (pd > np.median(pd, axis=0, keepdims=True))
    else:
        raise ValueError(kind)
    return L1.istft(X, n_samples)


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    with run_folder(__file__, label) as run:
        t0 = time.time()
        rng = np.random.default_rng(SEED)
        songs, inputs = {}, {}
        for song, folder in L1.song_folders().items():
            stems, hashes = L1.load_song(folder)
            songs[song] = {"Drums": stems["Drums"], "Lead Vocals": stems["Lead Vocals"]}
            inputs[song] = {"stems": {k: v for k, v in hashes.items() if "Drums" in k or "Lead Vocals" in k}}
        names = list(songs)
        cross = []
        for a in names:
            for b in names:
                if a == b:
                    continue
                d, v = songs[a]["Drums"], songs[b]["Lead Vocals"]
                n = min(len(d), len(v))
                T = 1 + (n - L1.NFFT) // L1.HOP
                n = (T - 1) * L1.HOP + L1.NFFT
                d, v = d[:n], v[:n]
                Dfull, Vfull = L1.stft(d), L1.stft(v)
                D, V = Dfull[:, L1.BAND], Vfull[:, L1.BAND]
                ed = L2.band_energy_spec(D)
                sh = L2.shifts_for(T, rng)
                row = {"target_song": a, "witness_song": b, "frames": T, "none": estimate_all(D, V, sh)}
                for kind in KINDS:
                    S = L2.spec(leak_audio(kind, Dfull, Vfull, n, rng))[:T]
                    es = L2.band_energy_spec(S)
                    for lev in LEVELS_DB:
                        row[f"{kind}{lev}"] = estimate_all(D + S * np.sqrt(ed * 10 ** (lev / 10) / es), V, sh)
                cross.append(row)
            print(f"pairs for {a} done ({time.time() - t0:.0f} s)", flush=True)

        # real-stem agreement (amended before the first data run): target = Drums of each song, every
        # other stem as witness, full tracks, all three estimators here; against leak-001's 60 s values
        r1 = json.load(open(sorted(glob.glob(os.path.join(EXP, "2026-11-26_stem_leakage", "runs", "*final*", "results.json")))[-1], encoding="utf-8"))
        diffs, real = {"A": [], "B": [], "C": []}, {}
        for song, folder in L1.song_folders().items():
            stems, _ = L1.load_song(folder)
            S_ = {k: L2.spec(x) for k, x in stems.items()}
            Tn = min(x.shape[0] for x in S_.values())
            sh = L2.shifts_for(Tn, rng)
            real[song] = {}
            for w in S_:
                if w == "Drums":
                    continue
                e = estimate_all(S_["Drums"][:Tn], S_[w][:Tn], sh)
                real[song][w] = e
                e1 = r1["within"][song]["Drums"][w]
                for est in ("A", "B", "C"):
                    if e1["p"] <= L1.ALPHA and e[est]["p"] <= L1.ALPHA and np.isfinite(e1["db"]) and np.isfinite(e[est]["db"]):
                        diffs[est].append(abs(e[est]["db"] - e1["db"]))
            print(f"real drums row for {song} done ({time.time() - t0:.0f} s)", flush=True)
        n = len(cross)
        lines = ["# Leaks written where the target is loud: results", "",
                 f"Run `{os.path.basename(run.path)}`. {len(names)} songs, {n} pairs. Detected = p <= {L1.ALPHA:g}. "
                 "Estimate = median leak estimate (dB).", ""]
        summary = {}
        for est in ("A", "B", "C"):
            fa = sum(r["none"][est]["p"] <= L1.ALPHA for r in cross)
            lines += [f"## Estimator {est}", "", f"No leak: {rate_text(fa, n)} detected.", "",
                      "| Kind | " + " | ".join(f"{lev} dB: detected / estimate" for lev in LEVELS_DB) + " |", "|---" * (len(LEVELS_DB) + 1) + "|"]
            s = {"false_alarms": fa}
            for kind in KINDS:
                cells = []
                for lev in LEVELS_DB:
                    det = sum(r[f"{kind}{lev}"][est]["p"] <= L1.ALPHA for r in cross)
                    med = float(np.median([r[f"{kind}{lev}"][est]["db"] for r in cross]))
                    s[f"{kind}{lev}"] = {"detected": det, "median_db": med}
                    cells.append(f"{det}/{n}, {med:.1f}")
                lines.append(f"| {kind} | " + " | ".join(cells) + " |")
            ok = fa <= 2 and all(s[f"{k}-30"]["detected"] >= 0.9 * n and abs(s[f"{k}-30"]["median_db"] + 30) <= 3 for k in KINDS)
            agree = float(np.median(diffs[est])) if diffs[est] else float("nan")
            s["real_agreement_median_abs_db"], s["real_pairs_both_detect"] = agree, len(diffs[est])
            s["passes"] = bool(ok and np.isfinite(agree) and agree <= 3.0)
            lines += ["", f"Real stems, against the 60 s estimator: median |difference| {agree:.1f} dB over {len(diffs[est])} pairs that both detect.",
                      f"**Passes the decision rule:** {'yes' if s['passes'] else 'no'}.", ""]
            summary[est] = s
        lines.append(f"Run time: {time.time() - t0:.0f} s.")
        json.dump({"seed": SEED, "levels_db": LEVELS_DB, "kinds": KINDS, "inputs": inputs, "summary": summary, "cross": cross,
                   "real_diffs": diffs, "real_drums_row": real}, open(os.path.join(run.path, "results.json"), "w", encoding="utf-8"), indent=1, default=float)
        open(os.path.join(run.path, "results.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print("\n".join(lines))


if __name__ == "__main__":
    main()
