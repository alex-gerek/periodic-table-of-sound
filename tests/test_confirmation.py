"""Confirmation of a period candidate (issue #7).

The peak rule always returns a candidate. These tests check that noise is not confirmed,
a real pulse is, and that each of the three tests (significance, repetitions, stability)
can reject a candidate on its own.
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from pts import periodicity as P  # noqa: E402

SR = 22050


def clicks(times, dur, rng):
    x = np.zeros(int(dur * SR))
    n = int(0.03 * SR)
    b = rng.standard_normal(n) * np.exp(-np.arange(n) / (0.004 * SR))
    for t in times:
        i = int(t * SR)
        seg = x[i:i + n]
        seg += b[:len(seg)]
    return x


def pulse_of(x):
    env, fs = P.onset_envelope(x, SR)
    return P.envelope_periodicity(env, fs, 0.25, 2.0)


@pytest.mark.parametrize("seed", range(10))
def test_white_noise_is_not_confirmed(seed):
    x = np.random.default_rng(500 + seed).standard_normal(20 * SR)
    p = pulse_of(x)
    assert p.tau is not None                 # the rule still names a candidate ...
    assert p.confirmed is False              # ... but it is not confirmed


def test_random_clicks_are_not_confirmed():
    rng = np.random.default_rng(42)
    times = np.cumsum(rng.exponential(0.25, 120))
    assert pulse_of(clicks(times[times < 30], 30, rng)).confirmed is False


def test_a_real_pulse_is_confirmed_with_its_evidence():
    rng = np.random.default_rng(1)
    p = pulse_of(clicks(np.arange(60) * 0.5, 30, rng))
    assert p.confirmed is True
    assert p.tau == pytest.approx(0.5, rel=0.02)
    assert p.evidence["significance"] >= P.Z_MIN
    assert p.evidence["repetitions"] >= P.MIN_REPS


def test_too_few_repetitions_are_not_confirmed():
    """Three beats of a 1.5 s pulse in 4.5 s: clear, but not enough repeats."""
    rng = np.random.default_rng(2)
    p = pulse_of(clicks(np.arange(3) * 1.5, 4.5, rng))
    assert p.confirmed is False
    assert "repetitions" in p.evidence["reason"]


def test_a_pulse_in_one_half_only_is_not_stable():
    """Clicks for 15 s, then 15 s of noise: strong overall, but missing from one half."""
    rng = np.random.default_rng(3)
    x = clicks(np.arange(30) * 0.5, 30, rng)
    x[15 * SR:] = 0.02 * rng.standard_normal(15 * SR)
    p = pulse_of(x)
    assert p.confirmed is False
    assert "halves" in p.evidence["reason"]


def test_confirmation_can_be_switched_off():
    rng = np.random.default_rng(4)
    env, fs = P.onset_envelope(rng.standard_normal(10 * SR), SR)
    p = P.envelope_periodicity(env, fs, 0.25, 2.0, confirm=False)
    assert p.confirmed is None and p.evidence == {}
