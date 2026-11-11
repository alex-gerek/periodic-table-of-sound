"""Degenerate input: short recordings, silence, empty and constant data.

Every function must return a defined result (an empty track, None or zeros), with no
exception and no NaN. These cases come from issue #2.
"""
import os
import sys
import warnings

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from pts import periodicity as P  # noqa: E402

SR = 48000


@pytest.fixture(autouse=True)
def warnings_are_errors():
    """A RuntimeWarning (division by zero, mean of an empty slice) counts as a failure."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        yield


def finite(a):
    return np.all(np.isfinite(np.asarray(a, dtype=float)))


# ---------------------------------------------------------------- the four reported cases

def test_pitch_of_a_signal_shorter_than_one_frame():
    assert P.pitch(np.zeros(100), SR) is None


def test_level_track_shorter_than_its_detrend_window():
    lv, fs = P.level_track(np.zeros(SR), SR)          # 1 s of track, 4 s detrend window
    assert len(lv) == SR // int(0.01 * SR)
    assert finite(lv)


def test_autocorr_of_an_empty_sequence():
    r = P.autocorr(np.array([]), 10)
    assert len(r) == 1 and finite(r)


def test_lag_similarity_of_constant_features():
    r = P.lag_similarity(np.ones((50, 4)), 10)
    assert len(r) == 11 and finite(r) and not r.any()


# ---------------------------------------------------------------- related cases

@pytest.mark.parametrize("x", [np.zeros(1), np.full(1000, 0.1), np.ones(1000)])
def test_autocorr_of_flat_or_single_values(x):
    r = P.autocorr(x, 50)
    assert finite(r) and not r.any()


def test_vibrato_of_a_signal_shorter_than_one_frame():
    per, runs = P.vibrato(np.zeros(1000), SR)
    assert per.tau is None and runs == 0


def test_pitch_of_silence_and_of_an_empty_signal():
    assert P.pitch(np.zeros(SR), SR) is None
    assert P.pitch(np.zeros(0), SR) is None


def test_level_track_shorter_than_one_hop():
    lv, _ = P.level_track(np.zeros(100), SR)
    assert len(lv) == 0


def test_lag_similarity_of_too_few_frames():
    assert finite(P.lag_similarity(np.ones((1, 4)), 10))
    assert finite(P.lag_similarity(np.zeros((0, 4)), 10))


@pytest.mark.parametrize("n", [0, 100, 1000])
def test_envelopes_and_features_of_short_signals(n):
    x = np.zeros(n)
    env, _ = P.onset_envelope(x, SR)
    hc, _ = P.harmonic_change(x, SR)
    F, _ = P.frame_features(x, SR)
    assert finite(env) and finite(hc) and finite(F)
    assert P.envelope_periodicity(env, 200, 0.25, 2.0).tau is None
    assert P.feature_periodicity(F, 10, 1.0, 8.0).tau is None


def test_normal_signals_are_unchanged():
    """The guards must not touch real measurements: a 220 Hz saw and a 2 Hz click train."""
    t = np.arange(SR) / SR
    saw = 2 * ((t * 220.0) % 1.0) - 1
    assert P.pitch(saw, SR)["tau"] == pytest.approx(1 / 220.0, rel=0.005)
    r = P.autocorr(np.tile(np.r_[1.0, np.zeros(99)], 20), 300)
    assert r[100] == pytest.approx(1.0, abs=1e-9)
