"""Stem leakage on full tracks: estimator A (unweighted) and B (frames weighted by the target).

Issue #38, journal step 2026-11-26-leak-002 (plan, hypotheses and decision rule committed before
this script was first run). Loading, STFT and masking are imported unchanged from leak-001.

A: per band b, g_b = sum_t D V* / sum_t |V|^2 over all frames of the full common length.
B: the same with weights w[t, b] = 1 / (running median over 11 frames of the target's band power
   + 1e-3 x its median): drum hits get little weight, the frames between them much.
For both, p is the explained share at shift 0 against K circular shifts of the witness, and the
leak estimate is the (unweighted) energy of g_b V over the target's band energy, minus its median
over the shifts (the chance level).

Usage: PTS_ARCHIVE_DIR=<archive> python run.py [label]
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
from pts.stats import conformal_p, rate_text  # noqa: E402
from runlog import run_folder  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "leak001", os.path.join(os.path.dirname(HERE), "2026-11-26_stem_leakage", "run.py"))
L1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L1)

SEED = 20261127
K, ALPHA = L1.K, L1.ALPHA
LEVELS_DB = L1.LEVELS_DB
MED_FRAMES = 11
FLOOR_FRAC = 1e-3
BAND_OF = np.digitize(L1.FREQS[L1.BAND], L1.BAND_EDGES[1:-1])          # band index of each bin
N_BANDS = L1.N_BANDS


def spec(x):
    return L1.stft(x)[:, L1.BAND]


def running_median(x, n):
    pad = n // 2
    xp = np.pad(x, (pad, pad), mode="edge")
    return np.median(np.lib.stride_tricks.sliding_window_view(xp, n), axis=1)


def xcorr_t(a, b):
    """sum_t a[t] conj(b[t - s]) for every circular shift s (along axis 0)."""
    return np.fft.ifft(np.fft.fft(a, axis=0) * np.conj(np.fft.fft(b, axis=0)), axis=0)


def estimate(D, V, shifts):
    """Both estimators on spectrograms D (target) and V (witness) of equal length."""
    T = D.shape[0]
    out = {}
    P = np.stack([np.sum(np.abs(D[:, BAND_OF == b]) ** 2, axis=1) for b in range(N_BANDS)], axis=1)
    Pv = np.stack([np.sum(np.abs(V[:, BAND_OF == b]) ** 2, axis=1) for b in range(N_BANDS)], axis=1)
    ED, EV = P.sum(axis=0), Pv.sum(axis=0)
    ed_total = ED.sum()
    W = np.stack([1.0 / (running_median(P[:, b], MED_FRAMES) + FLOOR_FRAC * max(np.median(P[:, b]), 1e-30))
                  for b in range(N_BANDS)], axis=1)
    idx = np.concatenate([[0], shifts])
    explA = np.zeros(len(idx)); leakA = np.zeros(len(idx))
    explB = np.zeros(len(idx)); leakB = np.zeros(len(idx))
    edw = float(np.sum(W * P))
    for b in range(N_BANDS):
        sel = BAND_OF == b
        if EV[b] <= 0 or not np.any(sel):
            continue
        Cb = xcorr_t(D[:, sel], V[:, sel]).sum(axis=1)[idx]                    # A
        explA += np.abs(Cb) ** 2 / EV[b]
        leakA += np.abs(Cb / EV[b]) ** 2 * EV[b]
        Cw = xcorr_t(W[:, b:b + 1] * D[:, sel], V[:, sel]).sum(axis=1)[idx]    # B
        den = np.real(xcorr_t(W[:, b], Pv[:, b]))[idx]
        den = np.maximum(den, 1e-300)
        explB += np.abs(Cw) ** 2 / den
        leakB += np.abs(Cw / den) ** 2 * EV[b]
    for name, expl, leak, norm in (("A", explA, leakA, ed_total), ("B", explB, leakB, edw)):
        stat = expl / norm
        lvl = leak / ed_total
        est = lvl[0] - float(np.median(lvl[1:]))
        out[name] = {"p": conformal_p(stat[0], stat[1:]), "db": 10 * np.log10(est) if est > 0 else float("-inf"),
                     "chance_db": float(10 * np.log10(max(np.median(lvl[1:]), 1e-30)))}
    return out


def shifts_for(T, rng):
    lo = int(np.ceil(L1.MIN_SHIFT_S * L1.SR / L1.HOP))
    return rng.choice(np.arange(lo, T - lo), size=K, replace=False)


def band_energy_spec(S):
    return float(np.sum(np.abs(S) ** 2))


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    with run_folder(__file__, label) as run:
        t0 = time.time()
        rng = np.random.default_rng(SEED)
        songs, inputs, specs = {}, {}, {}
        for song, folder in L1.song_folders().items():
            stems, hashes = L1.load_song(folder)
            songs[song] = stems
            specs[song] = {k: spec(v) for k, v in stems.items()}
            inputs[song] = {"length_s": len(next(iter(stems.values()))) / L1.SR, "stems": hashes}
            print(f"{song}: {len(stems)} stems, {inputs[song]['length_s']:.0f} s", flush=True)
        names = list(songs)

        cross = []
        for a in names:
            Dfull = specs[a]["Drums"]
            for b in names:
                if a == b:
                    continue
                v = songs[b]["Lead Vocals"]
                T = min(Dfull.shape[0], specs[b]["Lead Vocals"].shape[0])
                D, V = Dfull[:T], specs[b]["Lead Vocals"][:T]
                Vm = spec(L1.masked(v, rng))[:T]
                ed, ev, evm = band_energy_spec(D), band_energy_spec(V), band_energy_spec(Vm)
                sh = shifts_for(T, rng)
                row = {"target_song": a, "witness_song": b, "frames": T, "none": estimate(D, V, sh)}
                for lev in LEVELS_DB:
                    want = ed * 10 ** (lev / 10)
                    row[f"linear{lev}"] = estimate(D + V * np.sqrt(want / ev), V, sh)
                    row[f"masked{lev}"] = estimate(D + Vm * np.sqrt(want / evm), V, sh)
                cross.append(row)
            print(f"cross pairs for {a} done ({time.time() - t0:.0f} s)", flush=True)

        within = {}
        for song in names:
            keys = list(specs[song])
            T = min(s.shape[0] for s in specs[song].values())
            sh = shifts_for(T, rng)
            within[song] = {t: {w: estimate(specs[song][t][:T], specs[song][w][:T], sh) for w in keys if w != t} for t in keys}
            print(f"within {song} done ({time.time() - t0:.0f} s)", flush=True)

        n = len(cross)
        lines = ["# Stem leakage on full tracks: results", "",
                 f"Run `{os.path.basename(run.path)}`. {len(names)} songs, {n} cross-song pairs, full common length. "
                 f"Detection at p <= {ALPHA:g} against K = {K} shifts. Rates with exact 95% intervals.", ""]
        summary = {}
        for est in ("A", "B"):
            det = lambda key: sum(r[key][est]["p"] <= ALPHA for r in cross)  # noqa: E731
            s = {"none": det("none"), "chance_db_median": float(np.median([r["none"][est]["chance_db"] for r in cross]))}
            lines += [f"## Estimator {est}", "", f"**No leak:** {rate_text(s['none'], n)} detected. Chance level (median): {s['chance_db_median']:.1f} dB.", "",
                      "| Leak (dB) | Linear: detected | Linear: median estimate | Linear: median abs. error | Masked: detected | Masked: median estimate |",
                      "|---|---|---|---|---|---|"]
            for lev in LEVELS_DB:
                lin = np.array([r[f"linear{lev}"][est]["db"] for r in cross])
                msk = np.array([r[f"masked{lev}"][est]["db"] for r in cross])
                s[lev] = {"linear_detected": det(f"linear{lev}"), "masked_detected": det(f"masked{lev}"),
                          "linear_median_db": float(np.median(lin)), "linear_mae_db": float(np.median(np.abs(lin - lev))),
                          "masked_median_db": float(np.median(msk))}
                q = s[lev]
                lines.append(f"| {lev} | {rate_text(q['linear_detected'], n)} | {q['linear_median_db']:.1f} | {q['linear_mae_db']:.2f} | "
                             f"{rate_text(q['masked_detected'], n)} | {q['masked_median_db']:.1f} |")
            ok1 = s["none"] <= 2
            ok2 = s[-35]["linear_detected"] >= 0.9 * n and s[-30]["masked_detected"] >= 0.9 * n
            ok3 = all(s[lev]["linear_mae_db"] <= 1.0 for lev in LEVELS_DB if lev >= -40)
            s["H1"], s["H2"], s["H3"] = ok1, ok2, ok3
            lines += ["", f"H1 {'holds' if ok1 else 'fails'}, H2 {'holds' if ok2 else 'fails'}, H3 {'holds' if ok3 else 'fails'}.", ""]
            summary[est] = s
        chosen = next((e for e in ("A", "B") if summary[e]["H1"] and summary[e]["H2"] and summary[e]["H3"]), None)
        lines += [f"**Estimator meeting H1 to H3:** {chosen or 'none'}.", ""]
        show = chosen or "B"
        lines += [f"## Within each song, estimator {show}: leak estimate (dB of the target), p in brackets", ""]
        for song, m in within.items():
            keys = list(m)
            lines += [f"### {song}", "", "| target \\ witness | " + " | ".join(keys) + " |", "|---" * (len(keys) + 1) + "|"]
            for t in keys:
                cells = []
                for w in keys:
                    if w == t:
                        cells.append("–")
                        continue
                    e = m[t][w][show]
                    c = f"{e['db']:.1f} ({e['p']:.3f})"
                    cells.append(f"**{c}**" if e["p"] <= ALPHA else c)
                lines.append(f"| {t} | " + " | ".join(cells) + " |")
            lines.append("")
        lines.append(f"Run time: {time.time() - t0:.0f} s.")
        res = {"config": {"seed": SEED, "k": K, "alpha": ALPHA, "levels_db": LEVELS_DB, "med_frames": MED_FRAMES,
                          "floor_frac": FLOOR_FRAC, "estimator_code": "leak-001 STFT and bands, imported"},
               "inputs": inputs, "summary": summary, "chosen": chosen, "cross": cross, "within": within}
        with open(os.path.join(run.path, "results.json"), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=float)
        with open(os.path.join(run.path, "results.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print("\n".join(lines))


if __name__ == "__main__":
    main()
