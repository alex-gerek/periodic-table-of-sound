"""Ground-truth tests for group II, Periodicity, on synthetic signals with known answers."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from pts import periodicity as P          # noqa: E402
from pts.zscale import z_of, period_of, period_bounds  # noqa: E402

SR = 48000
rng = np.random.default_rng(7)


def clicks(times, sr=SR, dur=None, amps=None):
    dur = dur or (max(times) + 1.0)
    x = np.zeros(int(dur * sr))
    amps = np.ones(len(times)) if amps is None else amps
    burst = np.exp(-np.arange(int(0.03 * sr)) / (0.004 * sr)) * rng.standard_normal(int(0.03 * sr))
    for t, a in zip(times, amps):
        i = int(t * sr)
        seg = x[i:i + len(burst)]
        seg += a * burst[:len(seg)]
    return x


def saw(f, dur, sr=SR):
    t = np.arange(int(dur * sr)) / sr
    return 2 * ((t * f) % 1.0) - 1


def test_z_scale_landmarks():
    assert z_of(0.5) == pytest.approx(14.0)
    assert z_of(2.0) == pytest.approx(16.0)
    assert period_of(z_of(0.5)) == 4
    assert period_of(z_of(1 / 440)) == 2
    lo, hi = period_bounds(4)
    assert lo == pytest.approx(0.25) and hi == pytest.approx(2.0)


@pytest.mark.parametrize("f", [41.2, 110.0, 220.0, 440.0])
def test_pitch_of_saw(f):
    res = P.pitch(saw(f, 1.0), SR, 30, 1000)
    assert res["tau"] == pytest.approx(1 / f, rel=0.005)


def test_vibrato_rate():
    dur, f0, rate, depth_cents = 3.0, 220.0, 6.0, 50
    t = np.arange(int(dur * SR)) / SR
    inst = f0 * 2 ** (depth_cents / 1200 * np.sin(2 * np.pi * rate * t))
    x = np.sin(2 * np.pi * np.cumsum(inst) / SR)
    per, runs = P.vibrato(x, SR)
    assert runs >= 1
    assert per.tau == pytest.approx(1 / rate, rel=0.03)
    assert per.period == 3


def test_subdivision_pulse_meter():
    beat = 0.5                                   # 120 BPM
    n16 = 4 * 4 * 16                             # 16 bars of 16ths
    times = np.arange(n16) * beat / 4
    amps = np.full(n16, 0.25)                    # hats on every 16th
    amps[::4] = 0.8                              # kicks on every beat
    amps[::16] = 1.6                             # an accent on beat one of each bar
    env, fs = P.onset_envelope(clicks(times, amps=amps), SR)
    sub = P.envelope_periodicity(env, fs, *period_bounds(3))
    pulse = P.envelope_periodicity(env, fs, *period_bounds(4))
    meter = P.envelope_periodicity(env, fs, *period_bounds(5))
    assert sub.tau == pytest.approx(beat / 4, rel=0.03)
    assert pulse.tau == pytest.approx(beat, rel=0.02)
    assert meter.tau == pytest.approx(4 * beat, rel=0.02)


def test_sidechain_pump():
    dur, beat = 16.0, 0.5
    t = np.arange(int(dur * SR)) / SR
    duck = 1 - 0.8 * np.exp(-((t % beat) / 0.08))   # level drops on every beat and recovers
    x = rng.standard_normal(len(t)) * duck
    lv, fs = P.level_track(x, SR)
    per = P.envelope_periodicity(lv, fs, *period_bounds(4))
    assert per.tau == pytest.approx(beat, rel=0.02)


def test_loop_length():
    seg, n_seg, repeats = 0.5, 16, 6              # a loop of 16 different half-second sounds = 8 s
    freqs = np.fft.rfftfreq(int(seg * SR), 1 / SR)
    loop = []
    for _ in range(n_seg):
        shape = np.exp(-((np.log(freqs + 20) - rng.uniform(4, 9)) ** 2) / 0.5)
        spec = shape * np.exp(2j * np.pi * rng.random(len(freqs)))
        loop.append(np.fft.irfft(spec, int(seg * SR)))
    loop = np.concatenate(loop)
    x = np.concatenate([loop * (1 + 0.05 * rng.standard_normal()) for _ in range(repeats)])
    F, fs = P.frame_features(x, SR)
    per = P.feature_periodicity(F, fs, *period_bounds(6))
    assert per.tau == pytest.approx(seg * n_seg, rel=0.02)


def test_time_compression_pulse_becomes_pitch():
    """A 120 BPM pulse sped up 32 times is a 64 Hz pitch: same column, Z lower by exactly 5."""
    x = clicks(np.arange(40) * 0.5, dur=20.5)
    env, fs = P.onset_envelope(x, SR)
    pulse = P.envelope_periodicity(env, fs, *period_bounds(4))
    y = P.compress_time(x, 32)
    pitch = P.pitch(y, SR, 30, 1000)
    assert pulse.period == 4
    assert period_of(z_of(pitch["tau"])) == 2
    assert z_of(pulse.tau) - z_of(pitch["tau"]) == pytest.approx(5.0, abs=0.02)


def test_partials_find_vibrato_over_steady_chord():
    """A vibrato tone over a steady chord: only the vibrato tone's partials swing."""
    from pts.partials import partial_tracks, track_modulation
    dur = 4.0
    t = np.arange(int(dur * SR)) / SR
    chord = sum(0.3 * np.sin(2 * np.pi * f * t) for f in (261.6, 329.6, 392.0))
    inst = 880.0 * 2 ** (30 / 1200 * np.sin(2 * np.pi * 5.5 * t))
    phase = 2 * np.pi * np.cumsum(inst) / SR
    voice = sum(0.4 / h * np.sin(h * phase) for h in (1, 2, 3))
    tracks, fs = partial_tracks(chord + voice, SR)
    mods = [(np.median(f), track_modulation(f, fs)) for _, f, _ in tracks]
    swing = [(f0, m) for f0, m in mods if m and m["rate"] and m["r"] >= 0.5 and m["depth"] >= 5]
    steady = [f0 for f0, m in mods if f0 < 500]
    assert len(steady) >= 3
    assert all(f0 > 800 for f0, _ in swing) and len(swing) >= 2
    for _, m in swing:
        assert m["rate"] == pytest.approx(5.5, rel=0.05)
        assert m["depth"] == pytest.approx(30, rel=0.3)
