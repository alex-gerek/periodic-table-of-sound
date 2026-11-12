"""Second held-out set (issue #15): a generator that was not used in development.

Written and frozen before any rule was run on it. It differs from bench.groove() in:
  - timbres: a kick with a click, a rimshot or a clap instead of the snare, and a closed hat,
    a shaker or a ride for the subdivisions;
  - patterns: rock (kick on 1 and 3 and on the "and" of 3, snare on 2 and 4), march (snare on
    every beat, kick on 1), disco (kick on every beat, open hat on the off-beat, clap on 2 and
    4), waltz (kick on 1, rimshot on the others);
  - noise: pink or white; sometimes a short reverb tail; sometimes a slow change in level;
  - length 15 to 45 s, tempo 55 to 210 BPM.

As in bench.groove(), every beat carries a strong event and every subdivision a weak one.
Seeds 70000-70199. Run once: `python run_v2.py final2`.
"""
import numpy as np

import bench as B

SR = B.SR
SEEDS = range(70000, 70200)
PATTERNS = ("rock", "march", "disco", "waltz")


def _kick(rng):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (rng.uniform(45, 65) + rng.uniform(80, 160) * np.exp(-t / 0.02)) * t)
    click = rng.standard_normal(n) * np.exp(-t / 0.002) * 0.4
    return (body + click) * np.exp(-t / rng.uniform(0.08, 0.2))


def _rim(rng):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * rng.uniform(380, 520) * t) + 0.5 * np.sin(2 * np.pi * rng.uniform(900, 1300) * t)
    return (tone + 0.4 * rng.standard_normal(n)) * np.exp(-t / rng.uniform(0.01, 0.03))


def _clap(rng):
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    noise = np.convolve(rng.standard_normal(n), np.ones(4) / 4, "same")
    env = sum(np.exp(-np.clip(t - d, 0, None) / 0.008) * (t >= d) for d in (0.0, 0.009, 0.019))
    return noise * (env + np.exp(-t / 0.09) * 0.6)


def _weak(rng, kind):
    n = int(0.15 * SR)
    t = np.arange(n) / SR
    if kind == "ride":
        f = rng.uniform(3000, 4200) * np.array([1.0, 1.47, 2.09, 2.72])
        w = sum(np.sin(2 * np.pi * fi * t + rng.uniform(0, 6.28)) for fi in f) + 0.5 * np.diff(rng.standard_normal(n + 1))
        return w / 3 * np.exp(-t / 0.12)
    w = np.diff(np.diff(rng.standard_normal(n + 2)))
    if kind == "shaker":
        return w / 3 * np.minimum(t / 0.015, 1) * np.exp(-t / 0.04)
    return w / 3 * np.exp(-t / 0.012)                   # closed hat


def _place(x, t, b, amp):
    B._place(x, t, b, amp)


def groove_b(seed):
    rng = np.random.default_rng(seed)
    compound = rng.random() < 0.2
    if compound:
        nb, sub, bpm = int(rng.choice([2, 3, 4])), 3, rng.uniform(45, 105)
    else:
        nb, sub, bpm = int(rng.choice([2, 3, 4, 5, 6, 7])), int(rng.choice([2, 2, 3, 4])), rng.uniform(55, 210)
    beat = 60.0 / bpm
    if beat / sub < 0.06:
        sub = 2 if beat / 2 >= 0.06 else 1
    pattern = str(rng.choice(PATTERNS))
    weak_kind = str(rng.choice(["hat", "shaker", "ride"]))
    swing = rng.uniform(0.5, 0.6) if sub == 2 and rng.random() < 0.3 else 0.5
    jitter = float(rng.choice([0.0, 0.004, 0.01, 0.018]))
    accent = rng.uniform(1.1, 1.5)
    weak_level = rng.uniform(0.2, 0.7)
    dur = rng.uniform(15, 45)
    kick, rim, clap, weak = _kick(rng), _rim(rng), _clap(rng), _weak(rng, weak_kind)
    back = clap if rng.random() < 0.5 else rim
    x = np.zeros(int(dur * SR) + SR)
    j = lambda: rng.normal(0, jitter) if jitter else 0.0
    for i in range(int(dur / beat)):
        t, pos = i * beat, i % nb
        a = accent if pos == 0 else 1.0
        if pattern == "rock":
            _place(x, t + j(), kick if pos % 2 == 0 else back, a)
            if pos % 4 == 2 and sub >= 2:
                _place(x, t + beat / 2 + j(), kick, 0.5)
        elif pattern == "march":
            _place(x, t + j(), rim, a * 0.9)
            if pos == 0:
                _place(x, t + j(), kick, a)
        elif pattern == "disco":
            _place(x, t + j(), kick, a)
            if pos % 2 == 1:
                _place(x, t + j(), clap, 0.7)
        else:                                            # waltz
            _place(x, t + j(), kick if pos == 0 else rim, a if pos == 0 else 0.65)
        for q in range(sub):
            off = (q / sub) if not (sub == 2 and q == 1) else swing
            _place(x, t + off * beat + j(), weak, weak_level * (1.0 if q == 0 else 0.75))
    x = x[: int(dur * SR)]
    if rng.random() < 0.4:                               # a short reverb tail
        n = int(rng.uniform(0.2, 0.8) * SR)
        ir = rng.standard_normal(n) * np.exp(-np.arange(n) / (rng.uniform(0.05, 0.25) * SR)) * 0.08
        ir[0] = 1.0
        x = np.convolve(x, ir)[: len(x)]
    if rng.random() < 0.3:                               # a slow change in level
        x *= np.linspace(rng.uniform(0.3, 1.0), rng.uniform(0.3, 1.0), len(x))
    snr = float(rng.choice([24.0, 12.0, 6.0, 3.0]))
    noise = rng.standard_normal(len(x))
    if rng.random() < 0.5:                               # pink
        X = np.fft.rfft(noise)
        f = np.fft.rfftfreq(len(noise), 1 / SR)
        X[1:] /= np.sqrt(f[1:])
        X[0] = 0
        noise = np.fft.irfft(X, len(noise))
    p = np.mean(x ** 2) + 1e-12
    x = x + noise / (noise.std() + 1e-12) * np.sqrt(p / 10 ** (snr / 10))
    desc = {"seed": seed, "bpm": bpm, "beats_per_bar": nb, "subdivision": sub, "compound": compound,
            "pattern": pattern, "weak": weak_kind, "swing": swing, "jitter_s": jitter, "snr_db": snr, "duration_s": dur}
    return x, beat, desc
