"""Amplitude envelope (issue #21): ground truth, control, scaling, and agreement with the study."""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "experiments", "2026-11-12_envelope"))
from pts import periodicity as P  # noqa: E402
import envelope as E  # noqa: E402

SR = 44100


def rise_time(env, n0, T):
    t, *_ = E.characteristic_time(env, "rise", n0, T, SR)
    return t


@pytest.mark.parametrize("T,f0,w", [(0.01, 880, 0.0025), (0.05, 220, 0.01), (0.2, 3520, 0.002)])
def test_a_known_rise_is_read_inside_the_region(T, f0, w):
    """w <= T/4 and w * f0 >= 2: the 10-90 % rise time within 2 %."""
    for kind in ("sine", "harmonic"):
        x, a, n0 = E.make("rise", T, kind, f0, np.inf, 7)
        assert rise_time(P.amplitude_envelope(x, SR, w), n0, T) == pytest.approx(T, rel=0.02)


def test_a_known_burst_and_decay_are_read():
    for shape in ("burst", "decay"):
        x, a, n0 = E.make(shape, 0.02, "sine", 880, np.inf, 3)
        t, *_ = E.characteristic_time(P.amplitude_envelope(x, SR, 0.0025), shape, n0, 0.02, SR)
        assert t == pytest.approx(0.02, rel=0.02)


def test_a_constant_level_does_not_move_and_doubling_gives_6_db():
    x, *_ = E.make("constant", 0, "harmonic", 880, np.inf, 1)
    e = P.amplitude_envelope(x, SR, 0.005)
    seg = e[SR // 4:-SR // 4]
    assert 20 * np.log10(seg.max() / seg.min()) < 1.0
    e2 = P.amplitude_envelope(2 * x, SR, 0.005)
    assert 20 * np.log10(np.median(e2) / np.median(e)) == pytest.approx(6.0206, abs=1e-6)


def test_tape_speed_scales_the_time_and_z():
    """Compressing by 4 with the window scaled by 4: the time is a quarter (within the 5 % criterion of
    issue #21) and Z falls by 2. With this seed the error is 2.0 %; the held-out worst was 0.55 %."""
    T, w = 0.05, 0.0025
    x, a, n0 = E.make("rise", T, "harmonic", 880, np.inf, 5)
    t1 = rise_time(P.amplitude_envelope(x, SR, w), n0, T)
    y = P.compress_time(x, 4)
    t4, *_ = E.characteristic_time(P.amplitude_envelope(y, SR, w / 4), "rise", n0 // 4, T / 4, SR, scale=0.25)
    assert t4 / t1 == pytest.approx(0.25, rel=0.05)
    assert (np.log2(t4) - np.log2(t1)) == pytest.approx(-2.0, abs=0.075)


def test_the_core_function_equals_the_validated_one():
    x, *_ = E.make("burst", 0.03, "noise", 0, 20.0, 9)
    for w in (0.001, 0.01):
        np.testing.assert_allclose(P.amplitude_envelope(x, SR, w), E.envelope(x, "analytic", w), rtol=1e-9, atol=1e-12)


def test_outside_the_region_the_reading_degrades():
    """Known limit: a 2 ms rise on a 110 Hz harmonic tone (0.2 carrier periods) is not readable within 10 %."""
    x, a, n0 = E.make("rise", 0.002, "harmonic", 110, np.inf, 2)
    t = rise_time(P.amplitude_envelope(x, SR, 0.0005), n0, 0.002)
    assert t is None or abs(t / 0.002 - 1) > 0.10


def test_degenerate_input():
    assert P.amplitude_envelope(np.zeros(0), SR, 0.005).shape == (0,)
    with pytest.raises(ValueError):
        P.amplitude_envelope(np.ones(100), SR, 0.0)
