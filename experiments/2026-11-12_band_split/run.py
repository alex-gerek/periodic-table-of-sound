"""Does splitting events by band tell the beat from its subdivision? (issue #15)

For every controlled signal (pairs.py) the task is: of the two levels T and T/2, which one is
the beat? The same feature vector is computed from an envelope:

  correlation at T/4, T/2, 3T/4, T, 3T/2, 2T; how uneven the event strengths are on the T/2
  grid and on the T grid; and how much stronger the even T/2 slots are than the odd ones

Feature sets:
  full    the full-band onset envelope (pts.onset_envelope)
  bands   the same features of a low (30-150 Hz), a mid (150-2500 Hz) and a high (4-11 kHz)
          envelope, plus their joint pattern: the cross-correlation of low with high and of
          mid with high at 0, T/4 and T/2
  both    full + bands

Two classifiers, written here: logistic regression and k nearest neighbours. Cross-validation
is grouped by seed (5 folds), so the timbres of a seed are never in training and test at once.
Signals whose event timeline is the same under both labels are ambiguous by construction:
they are counted apart and left out of the accuracy.

  python run.py dev     seeds 0-19 (exploration)
  python run.py final   seeds 1000-1019 (run once, only if a candidate is made)
"""
import collections
import json
import os
import sys

import numpy as np

import pairs as PR

B = PR.B
P = B.P
SR = PR.SR
HERE = PR.HERE
LAGS = (0.25, 0.5, 0.75, 1.0, 1.5, 2.0)


def band_env(x, fmin, fmax, nb=4):
    Pw, fs = P.stft_power(x, SR, 1024, 0.005)
    L = 10 ** (P.log_bands(Pw, SR, 1024, nb, fmin, fmax) / 10 * 0.3)
    return np.maximum(np.diff(L, axis=0, prepend=L[:1]), 0.0).sum(axis=1), fs


def _r_at(r, lag):
    i = int(round(lag))
    return float(r[max(1, i - 1):i + 2].max()) if i + 2 < len(r) else 0.0


def _slots(env, step):
    """Event strength at each grid point of the given step (frames), at the best phase."""
    n, w = len(env), max(2, int(0.08 * step))
    phases = np.linspace(0, step, 16, endpoint=False)
    best = max(phases, key=lambda ph: env[np.arange(ph, n - w - 1, step).astype(int)].sum())
    idx = np.arange(best, n - w - 1, step).astype(int)
    return np.array([env[max(0, i - w):i + w + 1].max() for i in idx])


def features(env, fs, T):
    r = P.autocorr(env, int(2.2 * T * fs) + 4)
    f = [_r_at(r, k * T * fs) for k in LAGS]
    for step in (T / 2, T):
        v = _slots(env, step * fs)
        f.append(float(v.std() / (v.mean() + 1e-12)))
    v = _slots(env, T / 2 * fs)
    m = len(v) // 2 * 2
    ev, od = v[:m:2].mean(), v[1:m:2].mean()
    f.append(float(np.log((max(ev, od) + 1e-12) / (min(ev, od) + 1e-12))))
    return f


def cross(a, b, fs, T):
    a = (a - a.mean()) / (a.std() + 1e-12)
    b = (b - b.mean()) / (b.std() + 1e-12)
    out = []
    for k in (0.0, 0.25, 0.5):
        s = int(round(k * T * fs))
        out.append(float(np.mean(a[: len(a) - s] * b[s:])) if s else float(np.mean(a * b)))
    return out


def describe(x, T):
    full, fs = P.onset_envelope(x, SR)
    lo, _ = band_env(x, 30, 150, 2)
    mid, _ = band_env(x, 150, 2500, 4)
    hi, _ = band_env(x, 4000, 11000, 3)
    fb = features(lo, fs, T) + features(mid, fs, T) + features(hi, fs, T) + cross(lo, hi, fs, T) + cross(mid, hi, fs, T)
    return features(full, fs, T), fb


def timeline(combo, label):
    """Canonical event list in units of T/4 over one 2T cycle, to find signals that are the same under both labels."""
    kick, snare, hats, accent = combo
    unit = 4 if label == "T" else 2                       # beat length in quarters of T
    if PR.HAT_BALANCE and label == "T/2":
        hats //= 2
    ev = set()
    for i in range(8 // unit * 2):                         # beats in 4T
        t, pos = i * unit, i % 4
        acc = accent and pos == 0
        if kick == "every" or (kick in ("1_3", "1_3_and3") and pos in (0, 2)) or (kick == "1" and pos == 0):
            ev.add(("k", t % 16, acc))
        if kick == "1_3_and3" and pos == 2:
            ev.add(("k2", (t + unit / 2) % 16, False))
        if snare == "every" or (snare == "2_4" and pos in (1, 3)):
            ev.add(("s", t % 16, acc))
        for q in range(hats):
            ev.add(("h", (t + q * unit / hats) % 16, q == 0 and PR.HAT_ACCENT != 1.0))
    return frozenset(ev)


# ---------------------------------------------------------------- classifiers (own code)

def _standardise(Xtr, Xte):
    m, s = Xtr.mean(0), Xtr.std(0) + 1e-9
    return (Xtr - m) / s, (Xte - m) / s


def logistic(Xtr, ytr, Xte, lam=1e-2, steps=3000, lr=0.2):
    Xtr, Xte = _standardise(Xtr, Xte)
    Xtr, Xte = np.c_[Xtr, np.ones(len(Xtr))], np.c_[Xte, np.ones(len(Xte))]
    w = np.zeros(Xtr.shape[1])
    for _ in range(steps):
        p = 1 / (1 + np.exp(-Xtr @ w))
        g = Xtr.T @ (p - ytr) / len(ytr) + lam * np.r_[w[:-1], 0]
        w -= lr * g
    return (Xte @ w > 0).astype(int)


def knn(Xtr, ytr, Xte, k=7):
    Xtr, Xte = _standardise(Xtr, Xte)
    d = ((Xte[:, None, :] - Xtr[None, :, :]) ** 2).sum(-1)
    nn = np.argsort(d, axis=1)[:, :k]
    return (ytr[nn].mean(1) > 0.5).astype(int)


def cross_validate(X, y, groups, clf, folds=5):
    ug = np.unique(groups)
    pred = np.zeros_like(y)
    for f in range(folds):
        te = np.isin(groups, ug[f::folds])
        pred[te] = clf(X[~te], y[~te], X[te])
    return pred


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
    seeds = range(0, 20) if mode == "dev" else range(1000, 1020)
    tl = {(c, l): timeline(c, l) for c in PR.COMBOS for l in ("T", "T/2")}
    same = collections.defaultdict(set)
    for (c, l), t in tl.items():
        same[t].add(l)
    tag = (mode if PR.HAT_ACCENT == 0.8 else f"{mode}_hat{PR.HAT_ACCENT:g}") + ("_balanced" if PR.HAT_BALANCE else "")
    cache = os.path.join(HERE, f"features_{tag}.json")    # features only, no audio
    if os.path.exists(cache):
        rows = json.load(open(cache, encoding="utf-8"))
        for r in rows:
            r["combo"] = tuple(r["combo"])
    else:
        rows = []
        for x, T, label, combo, s in PR.signals(seeds):
            f_full, f_band = describe(x, T)
            rows.append({"seed": s, "combo": combo, "label": label, "full": f_full, "bands": f_band})
        json.dump(rows, open(cache, "w", encoding="utf-8"))
    for r in rows:
        r["ambiguous"] = len(same[tl[(r["combo"], r["label"])]]) > 1
    keep = [r for r in rows if not r["ambiguous"]]
    y = np.array([1 if r["label"] == "T" else 0 for r in keep])
    g = np.array([r["seed"] for r in keep])
    sets = {"full": np.array([r["full"] for r in keep]), "bands": np.array([r["bands"] for r in keep])}
    sets["both"] = np.c_[sets["full"], sets["bands"]]
    res = {"signals": len(rows), "ambiguous": len(rows) - len(keep), "scored": len(keep), "accuracy": {}, "per_combo": {}}
    preds = {}
    for name, X in sets.items():
        for cn, clf in (("logistic", logistic), ("knn", knn)):
            p = cross_validate(X, y, g, clf)
            preds[(name, cn)] = p
            res["accuracy"][f"{name} / {cn}"] = float((p == y).mean())
    # which combinations does the full envelope get wrong, and do the bands fix them?
    best_full = max((k for k in preds if k[0] == "full"), key=lambda k: (preds[k] == y).mean())
    best_both = max((k for k in preds if k[0] == "both"), key=lambda k: (preds[k] == y).mean())
    pc = collections.defaultdict(lambda: [0, 0, 0])
    for r, yi, pf, pb in zip(keep, y, preds[best_full], preds[best_both]):
        key = f"{'|'.join(map(str, r['combo']))} as {r['label']}"
        pc[key][0] += 1
        pc[key][1] += int(pf == yi)
        pc[key][2] += int(pb == yi)
    res["per_combo"] = {k: {"n": v[0], "full": v[1], "both": v[2]} for k, v in pc.items()}
    # McNemar between the best full and the best both
    a = int(((preds[best_full] == y) & (preds[best_both] != y)).sum())
    b = int(((preds[best_full] != y) & (preds[best_both] == y)).sum())
    res["mcnemar"] = {"full_right_both_wrong": a, "full_wrong_both_right": b,
                      "chi2": float((abs(a - b) - 1) ** 2 / (a + b)) if a + b else 0.0, "best_full": best_full, "best_both": best_both}
    with open(os.path.join(HERE, f"results_{tag}.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    L = [f"# Band split, {tag}", "", f"{res['signals']} signals, {res['ambiguous']} ambiguous by construction (the same events under both labels), {res['scored']} scored.", "",
         "| Features / classifier | Accuracy |", "|---|---|"]
    L += [f"| {k} | {100 * v:.1f}% |" for k, v in res["accuracy"].items()]
    m = res["mcnemar"]
    L += ["", f"Best full ({' / '.join(m['best_full'])}) against best both ({' / '.join(m['best_both'])}): "
          f"full right and both wrong {m['full_right_both_wrong']}, full wrong and both right {m['full_wrong_both_right']}, McNemar χ² = {m['chi2']:.1f}.", "",
          "## Combinations the full envelope gets wrong most often", "", "| Combination (kick, snare, hats per beat, accent) | Signals | Full right | Both right |", "|---|---|---|---|"]
    worst = sorted(res["per_combo"].items(), key=lambda kv: kv[1]["full"] / kv[1]["n"])[:16]
    L += [f"| {k} | {v['n']} | {v['full']} | {v['both']} |" for k, v in worst]
    md = "\n".join(L) + "\n"
    with open(os.path.join(HERE, f"results_{tag}.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print(md)


if __name__ == "__main__":
    main()
