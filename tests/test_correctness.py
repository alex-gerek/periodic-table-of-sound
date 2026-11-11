"""Correct results on degenerate input (issue #5).

The tests in test_robustness.py check that nothing crashes. These check that the answer is
right: a clear ValueError for an invalid parameter, no pitch in a constant signal, and a
flat detrended level where the level is steady, including the first and last second.
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from pts import periodicity as P  # noqa: E402

SR = 48000


# ---------------------------------------------------------------- 1. invalid parameters

@pytest.mark.parametrize("call, name", [
    (lambda: P.compress_time(np.ones(100), 0), "k"),
    (lambda: P.compress_time(np.ones(100), -2), "k"),
    (lambda: P.compress_time(np.ones(100), 1.5), "k"),
    (lambda: P.pitch(np.ones(100), 0), "sr"),
    (lambda: P.pitch(np.ones(100), -48000), "sr"),
    (lambda: P.pitch_track(np.ones(4800), SR, fmin=500, fmax=100), "fmin"),
    (lambda: P.pitch_track(np.ones(4800), SR, hop_s=0), "hop_s"),
    (lambda: P.pitch_track(np.ones(4800), SR, frame_s=0), "frame_s"),
    (lambda: P.level_track(np.ones(1000), SR, hop_s=0), "hop_s"),
    (lambda: P.level_track(np.ones(1000), 0), "sr"),
    (lambda: P.level_track(np.ones(1000), SR, detrend_s=0), "detrend_s"),
    (lambda: P.onset_envelope(np.ones(1000), SR, hop_s=0), "hop_s"),
    (lambda: P.onset_envelope(np.ones(1000), 0), "sr"),
])
def test_invalid_parameters_raise_a_named_value_error(call, name):
    with pytest.raises(ValueError, match=name):
        call()


def test_compress_time_with_k_one_is_identity():
    x = np.sin(np.arange(1000) * 0.01)
    assert np.allclose(P.compress_time(x, 1), x)


# ---------------------------------------------------------------- 2. no pitch in a constant signal

@pytest.mark.parametrize("dc", [1.0, -0.3, 1e-6])
def test_constant_signal_has_no_pitch(dc):
    assert P.pitch(np.full(SR, dc), SR) is None


def test_constant_frames_are_unvoiced():
    _, per = P.pitch_track(np.ones(SR), SR)
    assert np.isnan(per).all()


def test_a_tone_on_a_dc_offset_keeps_its_pitch():
    """Removing the mean must not remove the tone: 220 Hz riding on a large offset."""
    t = np.arange(SR) / SR
    x = 5.0 + 0.5 * (2 * ((t * 220.0) % 1.0) - 1)
    res = P.pitch(x, SR)
    assert res is not None
    assert res["tau"] == pytest.approx(1 / 220.0, rel=0.005)


def test_silence_after_a_tone_is_unvoiced():
    t = np.arange(SR) / SR
    x = np.concatenate([np.sin(2 * np.pi * 220 * t), np.full(SR, 0.2)])
    times, per = P.pitch_track(x, SR)
    tone, dc = per[times < 0.9], per[times > 1.1]
    assert np.isfinite(tone).mean() > 0.9
    assert np.isnan(dc).all()


# ---------------------------------------------------------------- 3. flat level, also at the edges

def _edges(lv, fs, seconds=1.0):
    n = int(seconds * fs)
    return lv[:n], lv[-n:]


def test_level_of_silence_is_flat_everywhere():
    lv, fs = P.level_track(np.zeros(8 * SR), SR)
    first, last = _edges(lv, fs)
    assert np.abs(lv).max() < 1e-9
    assert np.abs(first).max() < 1e-9 and np.abs(last).max() < 1e-9


def test_level_of_a_steady_tone_is_flat_everywhere():
    t = np.arange(8 * SR) / SR
    lv, fs = P.level_track(0.5 * np.sin(2 * np.pi * 1000 * t), SR)
    first, last = _edges(lv, fs)
    assert np.abs(lv).max() < 0.01
    assert np.abs(first).max() < 0.01 and np.abs(last).max() < 0.01


def test_level_keeps_a_real_change():
    """The fix must not flatten real movement: a 6 dB step stays visible."""
    t = np.arange(8 * SR) / SR
    x = 0.25 * np.sin(2 * np.pi * 1000 * t)
    x[4 * SR:] *= 2.0                                  # +6 dB from 4 s on
    lv, fs = P.level_track(x, SR)
    i = int(4 * fs)
    assert lv[i + 10] - lv[i - 10] == pytest.approx(6.02, abs=0.5)


def test_sidechain_period_is_unchanged_by_the_edge_fix():
    rng = np.random.default_rng(3)
    dur, beat = 16.0, 0.5
    t = np.arange(int(dur * SR)) / SR
    x = rng.standard_normal(len(t)) * (1 - 0.8 * np.exp(-((t % beat) / 0.08)))
    lv, fs = P.level_track(x, SR)
    per = P.envelope_periodicity(lv, fs, 0.25, 2.0)
    assert per.tau == pytest.approx(beat, rel=0.02)
