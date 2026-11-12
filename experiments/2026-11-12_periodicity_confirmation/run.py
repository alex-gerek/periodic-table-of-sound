"""When is a period real? Train the confirmation thresholds, then test them on new signals.

Training set (seeds 0..59):
  negatives: white noise, pink noise, random clicks, random drum hits, smooth swells
             (noise under one to three slow bell-shaped envelopes), crescendos
  positives: click trains, 60-200 BPM, with timing jitter, dropped beats and added noise
Test set (seeds 1000.., a different positive generator, and real material):
  negatives: the six non-periodic families with new seeds; real drum stems cut into 120 ms
             pieces and shuffled, which keeps the sounds but destroys the beat
  positives: synthetic drum grooves (kick, snare, hats, swing, humanised timing, noise);
             the real drum stems themselves

For each signal the onset envelope is computed, the pulse candidate is picked in
0.25-2 s, and the evidence (significance in sigma, repetitions, significance in each
half, and the return: the height of the peak above the lowest correlation between
half the lag and the lag)
is recorded. The thresholds are swept on the training set; the pair with at most
1% false detections and the most true detections is chosen, and then applied unchanged
to the test set.

Writes results.md and results.json next to this file.
"""
import glob
import json
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from pts import periodicity as P  # noqa: E402

SR = 22050
TAU_LO, TAU_HI = 0.25, 2.0


# ---------------------------------------------------------------- generators

def burst(rng, kind):
    n = int(0.04 * SR)
    t = np.arange(n) / SR
    if kind == "kick":
        return np.sin(2 * np.pi * (50 + 80 * np.exp(-t / 0.02)) * t) * np.exp(-t / 0.08)
    if kind == "snare":
        return (rng.standard_normal(n) * 0.7 + np.sin(2 * np.pi * 190 * t)) * np.exp(-t / 0.05)
    return rng.standard_normal(n) * np.exp(-t / 0.008) * 0.3          # hat


def place(x, t, b, amp=1.0):
    i = int(t * SR)
    if 0 <= i < len(x):
        seg = x[i:i + len(b)]
        seg += amp * b[:len(seg)]


def white(rng, dur):
    return rng.standard_normal(int(dur * SR))


def pink(rng, dur):
    n = int(dur * SR)
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X[1:] /= np.sqrt(f[1:])
    X[0] = 0
    return np.fft.irfft(X, n)


def random_clicks(rng, dur):
    x = np.zeros(int(dur * SR))
    rate = rng.uniform(2, 8)
    t = 0.0
    while t < dur:
        t += rng.exponential(1 / rate)
        place(x, t, burst(rng, "hat") * 3, rng.lognormal(0, 0.5))
    return x


def random_drums(rng, dur):
    x = np.zeros(int(dur * SR))
    rate = rng.uniform(2, 8)
    t = 0.0
    while t < dur:
        t += rng.exponential(1 / rate)
        place(x, t, burst(rng, rng.choice(["kick", "snare", "hat"])), rng.lognormal(0, 0.4))
    return x


def swells(rng, dur):
    """Noise under one to three slow bell-shaped swells: change without repetition."""
    t = np.arange(int(dur * SR)) / SR
    env = sum(np.exp(-0.5 * ((t - rng.uniform(0.15, 0.85) * dur) / rng.uniform(0.5, 8.0)) ** 2)
              for _ in range(rng.integers(1, 4)))
    return env * rng.standard_normal(len(t))


def crescendo(rng, dur):
    """Noise that only grows louder."""
    t = np.arange(int(dur * SR)) / SR
    return (t / dur) ** rng.uniform(0.5, 3.0) * rng.standard_normal(len(t))


NEGATIVES = {"white noise": white, "pink noise": pink, "random clicks": random_clicks,
             "random drum hits": random_drums, "smooth swells": swells, "crescendo": crescendo}


def add_noise(rng, x, snr_db):
    p = np.mean(x ** 2) + 1e-12
    return x + rng.standard_normal(len(x)) * np.sqrt(p / 10 ** (snr_db / 10))


def click_train(rng, dur):
    """Training positives: a pulse with jitter, dropped beats and noise."""
    beat = 60 / rng.uniform(60, 200)
    jitter = rng.choice([0.0, 0.01, 0.025])
    drop = rng.choice([0.0, 0.3])
    x = np.zeros(int(dur * SR))
    b = burst(rng, "kick")
    for i in range(int(dur / beat)):
        if rng.random() >= drop:
            place(x, i * beat + rng.normal(0, jitter), b, 1.0 if i % 4 == 0 else 0.7)
    return add_noise(rng, x, rng.choice([10.0, 0.0, -5.0])), beat


def groove(rng, dur):
    """Test positives, a different generator: kick, snare on 2 and 4, swung hats."""
    beat = 60 / rng.uniform(70, 180)
    swing = rng.uniform(0.5, 0.66)
    human = rng.choice([0.0, 0.008, 0.02])
    x = np.zeros(int(dur * SR))
    k, s, h = burst(rng, "kick"), burst(rng, "snare"), burst(rng, "hat")
    for i in range(int(dur / beat)):
        t = i * beat
        place(x, t + rng.normal(0, human), k if i % 2 == 0 else s, rng.uniform(0.8, 1.0))
        place(x, t + rng.normal(0, human), h, 0.5)
        place(x, t + swing * beat + rng.normal(0, human), h, 0.35)
    return add_noise(rng, x, rng.choice([10.0, 0.0, -5.0])), beat


# ---------------------------------------------------------------- real material

def drum_stems():
    out = []
    for folder in sorted(glob.glob(os.path.join(ROOT, "data", "stems", "*"))) + \
            sorted(glob.glob(os.path.join(ROOT, "data", "material", "tempo_series", "*"))) + \
            sorted(glob.glob(os.path.join(ROOT, "data", "material", "meters", "meter_*"))):
        f = [p for p in glob.glob(os.path.join(folder, "*.wav")) if "Drums" in os.path.basename(p)]
        if f:
            x, sr = sf.read(f[0], always_2d=True)       # measured at the stem's own rate
            out.append((os.path.basename(folder), P.mono(x)[: int(60 * sr)], sr))
    return out


def shuffle_chunks(rng, x, sr, lo_s=0.08, hi_s=0.25, fade_s=0.005):
    """Cut into pieces of random length and shuffle them, with short fades.

    Pieces of one fixed length would put a join every 120 ms and create the very
    periodicity this control must not contain. Random lengths and fades avoid that.
    """
    pieces, i = [], 0
    fade = int(fade_s * sr)
    ramp = np.linspace(0.0, 1.0, fade)
    while i < len(x):
        c = int(rng.uniform(lo_s, hi_s) * sr)
        p = x[i:i + c].copy()
        if len(p) > 2 * fade:
            p[:fade] *= ramp
            p[-fade:] *= ramp[::-1]
        pieces.append(p)
        i += c
    order = rng.permutation(len(pieces))
    return np.concatenate([pieces[k] for k in order])


# ---------------------------------------------------------------- evidence

def evidence(x, sr=SR):
    env, fs = P.onset_envelope(x, sr)
    cand = P.envelope_periodicity(env, fs, TAU_LO, TAU_HI, confirm=False)
    c = P.confirm_period(env, fs, cand, TAU_LO, P.autocorr, z_min=0.0, min_reps=0.0)
    if c.tau is None:
        return {"tau": None, "sig": 0.0, "reps": 0.0, "half": 0.0, "ret": 0.0}
    return {"tau": c.tau, "sig": c.evidence["significance"], "reps": c.evidence["repetitions"],
            "half": min(c.evidence["significance_halves"]), "ret": c.evidence["return"]}


def accept(e, z, reps, use_return=True):
    return (e["tau"] is not None and e["sig"] >= z and e["reps"] >= reps and e["half"] >= z / np.sqrt(2)
            and (not use_return or e["ret"] >= z))


def right_period(e, beat):
    """A detection counts only if it is the beat or a whole multiple of it (2, 3, 4)."""
    if e["tau"] is None:
        return False
    q = e["tau"] / beat
    return min(abs(q - m) / m for m in (1, 2, 3, 4)) < 0.03


def main():
    data = {"train": {"neg": [], "pos": []}, "test": {"neg": [], "pos": []}}
    for split, seeds, posgen in (("train", range(60), click_train), ("test", range(1000, 1060), groove)):
        for s in seeds:
            rng = np.random.default_rng(s)
            dur = rng.uniform(20, 40)
            fam = list(NEGATIVES)[s % len(NEGATIVES)]
            data[split]["neg"].append({"family": fam, **evidence(NEGATIVES[fam](rng, dur))})
            x, beat = posgen(rng, dur)
            e = evidence(x)
            e["right"] = right_period(e, beat)
            data[split]["pos"].append({"family": posgen.__name__, "beat": beat, **e})
        print(split, "done", flush=True)
    rng = np.random.default_rng(7)
    real = drum_stems()
    data["real"] = {"pos": [], "neg": []}
    for name, x, sr in real:
        data["real"]["pos"].append({"family": name, **evidence(x, sr)})
        data["real"]["neg"].append({"family": name + " (shuffled)", **evidence(shuffle_chunks(rng, x, sr), sr)})
    print("real done:", len(real), "drum stems", flush=True)

    # sweep on the training set only
    grid = []
    for z in (3, 4, 5, 6, 7, 8, 10, 12):
        for reps in (4, 6, 8, 12):
            fp = np.mean([accept(e, z, reps) for e in data["train"]["neg"]])
            tp = np.mean([accept(e, z, reps) for e in data["train"]["pos"]])
            grid.append((z, reps, fp, tp))
    ok = [g for g in grid if g[2] <= 0.01]
    z_best, r_best, fp_tr, tp_tr = max(ok, key=lambda g: (g[3], g[0]))

    def rates(split, z, reps):
        neg, pos = data[split]["neg"], data[split]["pos"]
        fp = np.mean([accept(e, z, reps) for e in neg])
        miss = np.mean([not accept(e, z, reps) for e in pos])
        # a wrong period can only be judged where the true beat is known: not on the real stems
        if all("right" in e for e in pos):
            wrong = np.mean([accept(e, z, reps) and not e["right"] for e in pos])
        else:
            wrong = None
        return fp, miss, wrong

    res = {"chosen": {"z_min": z_best, "min_reps": r_best},
           "train": rates("train", z_best, r_best), "test": rates("test", z_best, r_best),
           "real": rates("real", z_best, r_best),
           "without_return_test": {s: float(np.mean([accept(e, z_best, r_best, use_return=False) for e in data[s]["neg"]]))
                                   for s in data},
           "old_rule_false_detections": {s: float(np.mean([e["tau"] is not None for e in data[s]["neg"]])) for s in data},
           "grid": grid, "data": data}
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=float)

    L = ["# Confirming a period: results", "",
         f"Thresholds chosen on the training set: **significance ≥ {z_best:g} σ**, **at least {r_best:g} repetitions**, ≥ {z_best / np.sqrt(2):.2f} σ in each half, and a **return of ≥ {z_best:g} σ** above the lowest correlation between half the lag and the lag.", "",
         "| Set | Signals (neg / pos) | False detections on non-periodic signals | Misses on periodic signals | Confirmed but wrong period |",
         "|---|---|---|---|---|"]
    for split, label in (("train", "Training (click trains)"), ("test", "Test (grooves, new seeds)"), ("real", "Real drum stems")):
        fp, miss, wrong = res[split]
        wr = "not evaluated (no independent beat labels)" if wrong is None else f"{100 * wrong:.1f}%"
        L.append(f"| {label} | {len(data[split]['neg'])} / {len(data[split]['pos'])} | {100 * fp:.1f}% | {100 * miss:.1f}% | {wr} |")
    sw = [e for sp in ("train", "test") for e in data[sp]["neg"] if e["family"] in ("smooth swells", "crescendo")]
    L += ["", f"Without the return test, {sum(accept(e, z_best, r_best, use_return=False) for e in sw)} of {len(sw)} smooth swells and crescendos "
          f"(training and test) would be confirmed; with it, {sum(accept(e, z_best, r_best) for e in sw)}.", ""]
    L += ["Before issue #7, a period was returned for "
          + ", ".join(f"{100 * v:.0f}% ({k})" for k, v in res["old_rule_false_detections"].items())
          + " of the non-periodic signals.", "",
          "## Real drum stems", "",
          "| Stem | Candidate | Significance | Repetitions | Weaker half | Return | Confirmed | Shuffled: significance | Shuffled: confirmed |",
          "|---|---|---|---|---|---|---|---|---|"]
    for p_, n_ in zip(data["real"]["pos"], data["real"]["neg"]):
        L.append(f"| {p_['family']} | {p_['tau']:.3f} s | {p_['sig']:.1f} σ | {p_['reps']:.0f} | {p_['half']:.1f} σ | {p_['ret']:.1f} σ | "
                 f"{'yes' if accept(p_, z_best, r_best) else 'no'} | {n_['sig']:.1f} σ | {'yes' if accept(n_, z_best, r_best) else 'no'} |")
    L += ["", "## Significance by family (median, training and test)", "",
          "| Family | Median significance | Largest |", "|---|---|---|"]
    fams = {}
    for split in ("train", "test"):
        for kind in ("neg", "pos"):
            for e in data[split][kind]:
                fams.setdefault(e["family"], []).append(e["sig"])
    for k, v in fams.items():
        L.append(f"| {k} | {np.median(v):.1f} σ | {np.max(v):.1f} σ |")
    with open(os.path.join(HERE, "results.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
