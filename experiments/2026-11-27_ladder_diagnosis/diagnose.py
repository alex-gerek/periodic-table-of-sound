"""Why the ladder misses on live music (issue #41, journal step 2026-11-27-ladder-diag-001).

Diagnosis on development data only: nothing here changes pts/ladder.py or accepts a hypothesis.

Part A: synthetic click trains (tempo range, jitter, drift, accents).
Part B: the live excerpts whose tapped beat is not on the ladder: which test rejects the beat.

    PTS_TAPPING_DIR=<tapping_live folder> python diagnose.py [label]
"""
import importlib.util
import json
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
ROOT = os.path.dirname(EXP)
sys.path.insert(0, ROOT)
sys.path.insert(0, EXP)
from pts import ladder as L          # noqa: E402
from pts import periodicity as P     # noqa: E402
from runlog import run_folder        # noqa: E402

_spec = importlib.util.spec_from_file_location("score_live", os.path.join(EXP, "2026-11-22_live_ladder", "score_live.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

SR = 44100
DUR = 30.0
SEED = 20261127
BPMS = (20, 25, 30, 35, 40, 45, 48, 50, 55, 60, 65, 70, 80, 90, 100, 110, 120, 140, 160, 180, 200, 220, 240, 270, 300)


def clicks(bpm, rng, jitter=0.0, drift=0.0, accent=1):
    """Noise clicks (5 ms decay) at bpm; jitter = sd as a share of the beat; drift = total tempo change."""
    x = np.zeros(int(DUR * SR))
    beat = 60.0 / bpm
    t, i = 0.2, 0
    burst = rng.standard_normal(int(0.03 * SR)) * np.exp(-np.arange(int(0.03 * SR)) / (0.005 * SR))
    while t < DUR - 0.05:
        tt = t + (rng.normal(0, jitter * beat) if jitter else 0.0)
        a = int(max(0, tt) * SR)
        g = 2.0 if accent > 1 and i % accent == 0 else 1.0
        seg = burst[: len(x) - a]
        x[a:a + len(seg)] += g * seg
        local = beat / (1 + drift * (t / DUR - 0.5))
        t += local
        i += 1
    return x + 1e-3 * rng.standard_normal(len(x))


def evidence_at(env, fs, tau):
    c = P.confirm_period(env, fs, P.Periodicity(tau, 0.0), min(L.SEED_LO, 0.5 * tau), P.autocorr)
    ev = c.evidence
    return {"confirmed": bool(c.confirmed), "significance": round(float(ev.get("significance", 0)), 2),
            "return": round(float(ev.get("return", 0)), 2),
            "halves": [round(float(v), 2) for v in ev.get("significance_halves", (0, 0))],
            "repetitions": round(float(ev.get("repetitions", 0)), 1), "reason": ev.get("reason")}


def seed_info(x, sr):
    env, fs = P.onset_envelope(P.mono(np.asarray(x, dtype=np.float64)), sr)
    s = P.envelope_periodicity(env, fs, L.SEED_LO, L.SEED_HI)
    return env, fs, {"tau": None if s.tau is None else round(float(s.tau), 4),
                     "bpm": None if s.tau is None else round(60 / s.tau, 1),
                     "confirmed": bool(s.confirmed), "reason": s.evidence.get("reason"),
                     "top_peaks_bpm": [round(60 / t, 1) for t, _ in s.candidates]}


def drift_from_taps(passes):
    out = []
    for p in passes.values():
        if p.get("no_steady_beat"):
            continue
        d = np.diff(p["taps_s"][S.DROP_FIRST:])
        if len(d) < 8:
            continue
        h = len(d) // 2
        out.append(float(np.median(d[h:]) / np.median(d[:h]) - 1))
    return out


def part_a(rng):
    rows = []
    variants = [("plain", {}), ("jitter2", {"jitter": 0.02}), ("jitter5", {"jitter": 0.05}),
                ("drift3", {"drift": 0.03}), ("drift6", {"drift": 0.06}), ("accent3", {"accent": 3})]
    for name, kw in variants:
        for bpm in BPMS:
            x = clicks(bpm, rng, **kw)
            lv = L.ladder(x, SR)
            beat = 60.0 / bpm
            on = L.on_ladder(lv, beat) is not None
            row = {"variant": name, "bpm": bpm, "ladder_bpm": S.bpm(lv), "on_ladder": on}
            if not on:
                env, fs, si = seed_info(x, SR)
                row["seed"] = si
                row["at_beat"] = evidence_at(env, fs, beat)
            if name == "accent3":
                row["bar_on_ladder"] = L.on_ladder(lv, 3 * beat) is not None
            rows.append(row)
        print(name, "on ladder:", [r["bpm"] for r in rows if r["variant"] == name and r["on_ladder"]], flush=True)
    return rows


def part_b(data):
    taps = json.load(open(os.path.join(data, "taps.json"), encoding="utf-8"))
    key = json.load(open(os.path.join(data, "key.json"), encoding="utf-8"))["tracks"]
    rows = []
    for k in key:
        lab = S.label(taps.get(k["id"], {}))
        if lab["status"] not in ("verified", "ambiguous"):
            continue
        x, sr = sf.read(os.path.join(data, "audio", k["id"] + ".wav"))
        x = S.mono(x)
        lv = L.ladder(x, sr)
        hit = next((L.on_ladder(lv, b) for b in lab["beats_s"] if L.on_ladder(lv, b) is not None), None)
        env, fs, si = seed_info(x, sr)
        row = {"id": k["id"], "name": k["name"], "tapped_bpm": [round(60 / b, 1) for b in lab["beats_s"]],
               "ladder_bpm": S.bpm(lv), "on_ladder": hit is not None, "seed": si,
               "tap_drift": [round(v, 3) for v in drift_from_taps(taps[k["id"]])]}
        if hit is None:
            row["at_beat"] = {f"{60 / b:.1f}": evidence_at(env, fs, b) for b in lab["beats_s"]}
            feats = L.band_envelopes(x, sr)
            acc = []
            for level in lv:
                for b in lab["beats_s"]:
                    ratio = b / level["tau"]
                    for kk in (2, 3):
                        if abs(ratio / kk - 1) <= 0.05:
                            acc.append({"from_bpm": round(60 / level["tau"], 1), "k": kk, "ratio": round(ratio, 3),
                                        "accent_t": round(L.accent_t(feats, fs, level["tau"], kk), 2),
                                        "confirm_k_tau": evidence_at(env, fs, kk * level["tau"])})
            row["groupings_towards_beat"] = acc
        rows.append(row)
        print(json.dumps(row), flush=True)
    return rows


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "diag"
    with run_folder(__file__, label) as run:
        rng = np.random.default_rng(SEED)
        a = part_a(rng)
        b = part_b(os.environ["PTS_TAPPING_DIR"])
        json.dump({"seed": SEED, "synthetic": a, "live": b}, open(os.path.join(run.path, "results.json"), "w", encoding="utf-8"),
                  indent=1, default=float)


if __name__ == "__main__":
    main()
