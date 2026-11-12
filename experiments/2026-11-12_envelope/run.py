"""Envelope validation grid (issue #21). Every run writes into runs/<run-id>/ (experiments/runlog.py).

  python run.py grid      shapes x times x carriers x SNR x seeds x estimators x windows
  python run.py scaling   tape-speed compression and stretching of selected signals

Outputs in the run folder: cases.json (every case), summary.md.
"""
import collections
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import envelope as E                         # noqa: E402
from runlog import run_folder                # noqa: E402
from pts import periodicity as P             # noqa: E402
from pts.zscale import z_of, period_of       # noqa: E402

TIMES = (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5)
CARRIERS = [("sine", f) for f in (55, 220, 880, 3520)] + [("harmonic", f) for f in (55, 220, 880, 3520)] + [("noise", 0)]
SNRS = (np.inf, 20.0, 10.0)
SEEDS = (0, 1, 2)
METHODS = ("rms", "analytic")
WINDOWS = (0.0005, 0.001, 0.002, 0.005, 0.01, 0.02)


def grid(run):
    cases = []
    for shape in ("rise", "decay", "burst"):
        for T in TIMES:
            for kind, f0 in CARRIERS:
                for snr in SNRS:
                    for seed in SEEDS:
                        x, a, n0 = E.make(shape, T, kind, f0, snr, seed)
                        mag = np.abs(E.analytic(x))
                        for m in METHODS:
                            for w in WINDOWS:
                                h = E._hann(w, E.SR)
                                e = np.sqrt(np.maximum(E._smooth(x ** 2, h), 0)) if m == "rms" else E._smooth(mag, h) / np.sqrt(2)
                                Tm, fl, tp = E.characteristic_time(e, shape, n0, T)
                                se = E.shape_error(e, a, fl, tp, n0, T, shape)
                                cases.append({"shape": shape, "T": T, "carrier": kind, "f0": f0, "snr": snr, "seed": seed,
                                              "method": m, "w": w, "T_meas": Tm,
                                              "time_err": None if Tm is None else (Tm - T) / T, "shape_err": se})
        print(shape, "done", flush=True)
    for kind, f0 in CARRIERS:                                   # constant level and linearity
        for snr in SNRS:
            for seed in SEEDS:
                x1, *_ = E.make("constant", 0, kind, f0, snr, seed, amp=1.0)
                x2, *_ = E.make("constant", 0, kind, f0, snr, seed, amp=2.0)
                for m in METHODS:
                    for w in WINDOWS:
                        e1, e2 = E.envelope(x1, m, w), E.envelope(x2, m, w)
                        cases.append({"shape": "constant", "carrier": kind, "f0": f0, "snr": snr, "seed": seed, "method": m, "w": w,
                                      "false_change_db": E.false_change_db(e1, w),
                                      "linearity_db": float(20 * np.log10(np.median(e2) / np.median(e1)))})
    json.dump(cases, open(os.path.join(run.path, "cases.json"), "w"), default=float)
    return cases


HOLDOUT = {"times": (0.0015, 0.003, 0.007, 0.015, 0.03, 0.07, 0.15, 0.3),
           "carriers": [("sine", f) for f in (110, 440, 1760, 7040)] + [("harmonic", f) for f in (110, 440, 1760, 7040)] + [("noise", 0)],
           "snrs": (np.inf, 30.0, 20.0, 10.0), "seeds": (100, 101, 102), "windows": (0.0007, 0.0015, 0.003, 0.007, 0.015, 0.03)}


def holdout(run):
    """The held-out grid: other seeds, pitches, times and windows. Run once, after the method and
    the valid region were fixed on the development grid."""
    global TIMES, CARRIERS, SNRS, SEEDS, WINDOWS
    TIMES, CARRIERS, SNRS, SEEDS, WINDOWS = (HOLDOUT[k] for k in ("times", "carriers", "snrs", "seeds", "windows"))
    return grid(run)


def scaling(run):
    """Tape speed: compress by k = 2, 4, 8 (pts.compress_time) or stretch by k = 2, 4 (envelope.stretch)."""
    cases = []
    for shape in ("rise", "decay", "burst"):
        for T in (0.005, 0.02, 0.05, 0.2):
            for kind, f0 in (("sine", 220), ("harmonic", 220), ("noise", 0)):
                x, a, n0 = E.make(shape, T, kind, f0, np.inf, 0)
                for m in METHODS:
                    w0 = 0.002 if kind != "noise" else 0.005
                    e = E.envelope(x, m, w0)
                    T0, *_ = E.characteristic_time(e, shape, n0, T)
                    for k, op in [(1 / 8, "compress"), (1 / 4, "compress"), (1 / 2, "compress"), (2, "stretch"), (4, "stretch")]:
                        y = P.compress_time(x, int(round(1 / k))) if op == "compress" else E.stretch(x, int(k))
                        Tk_true, nk = T * k, int(round(n0 * k))
                        for wmode, w in (("scaled", w0 * k), ("fixed", w0)):
                            ek = E.envelope(y, m, max(w, 1 / E.SR * 3))
                            Tk, fl, tp = E.characteristic_time(ek, shape, nk, Tk_true, scale=k)
                            cases.append({"shape": shape, "T": T, "carrier": kind, "f0": f0, "method": m, "k": k, "window": wmode,
                                          "T0_meas": T0, "Tk_meas": Tk, "ratio": None if (Tk is None or T0 is None) else Tk / T0,
                                          "ratio_err": None if (Tk is None or T0 is None) else Tk / T0 / k - 1,
                                          "dz": None if (Tk is None or T0 is None) else z_of(Tk) - z_of(T0), "dz_expected": float(np.log2(k)),
                                          "row0": None if T0 is None else period_of(z_of(T0)), "rowk": None if Tk is None else period_of(z_of(Tk)),
                                          "carrier_f_after": f0 / k})
        print(shape, "done", flush=True)
    json.dump(cases, open(os.path.join(run.path, "cases.json"), "w"), default=float)
    return cases


def scaling_holdout(run):
    """Tape-speed scaling inside the valid region (region.py), with the held-out seed 100:
    tonal carriers at 880 Hz with a 2.5 ms window (w*f0 = 2.2), noise with a 10 ms window.
    The window is scaled with k. Run once, after the region was fixed."""
    cases = []
    for shape in ("rise", "decay", "burst"):
        for kind, f0, w0, Ts in (("sine", 880, 0.0025, (0.02, 0.05, 0.2)), ("harmonic", 880, 0.0025, (0.02, 0.05, 0.2)), ("noise", 0, 0.01, (0.05, 0.2))):
            for T in Ts:
                x, a, n0 = E.make(shape, T, kind, f0, np.inf, 100)
                e = E.envelope(x, "analytic", w0)
                T0, *_ = E.characteristic_time(e, shape, n0, T)
                for k, op in [(1 / 4, "compress"), (1 / 2, "compress"), (2, "stretch"), (4, "stretch")]:
                    y = P.compress_time(x, int(round(1 / k))) if op == "compress" else E.stretch(x, int(k))
                    ek = E.envelope(y, "analytic", w0 * k)
                    Tk, *_ = E.characteristic_time(ek, shape, int(round(n0 * k)), T * k, scale=k)
                    cases.append({"shape": shape, "T": T, "carrier": kind, "f0": f0, "k": k, "w0": w0, "T0_meas": T0, "Tk_meas": Tk,
                                  "ratio_err": None if (Tk is None or T0 is None) else Tk / T0 / k - 1,
                                  "dz": None if (Tk is None or T0 is None) else z_of(Tk) - z_of(T0), "dz_expected": float(np.log2(k)),
                                  "row0": None if T0 is None else period_of(z_of(T0)), "rowk": None if Tk is None else period_of(z_of(Tk))})
    json.dump(cases, open(os.path.join(run.path, "cases.json"), "w"), default=float)
    return cases


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "grid"
    with run_folder(__file__, mode) as run:
        print("run", run.meta["run_id"])
        {"grid": grid, "scaling": scaling, "holdout": holdout, "scaling_holdout": scaling_holdout}[mode](run)


if __name__ == "__main__":
    main()
