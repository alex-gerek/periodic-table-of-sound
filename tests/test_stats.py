"""Calibrated decisions (issue #32): exact intervals, conformal p-values, surrogates.

Reference values for the exact interval are the published Clopper-Pearson bounds
(also reproduced by any Beta quantile function); they are written in as numbers so the
test needs nothing but numpy.
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from pts import periodicity as P  # noqa: E402
from pts import stats as S  # noqa: E402


@pytest.mark.parametrize("k,n,lo,hi", [
    (0, 60, 0.0, 0.0596295),        # 1 - 0.025 ** (1 / 60)
    (12, 12, 0.7353515, 1.0),       # 0.025 ** (1 / 12)
    (1, 10, 0.0025286, 0.4450161),
    (5, 10, 0.1870860, 0.8129140),
])
def test_exact_interval_matches_known_bounds(k, n, lo, hi):
    a, b = S.exact_interval(k, n)
    assert a == pytest.approx(lo, abs=1e-6)
    assert b == pytest.approx(hi, abs=1e-6)


def test_interval_edges_and_bad_counts():
    assert S.exact_interval(0, 0) == (0.0, 1.0)
    assert S.wilson_interval(0, 0) == (0.0, 1.0)
    lo, hi = S.wilson_interval(3, 50)
    elo, ehi = S.exact_interval(3, 50)
    assert elo <= lo and hi <= ehi            # Wilson is the shorter of the two here
    for k, n in ((5, 3), (-1, 4), (1.5, 4)):
        with pytest.raises(ValueError):
            S.exact_interval(k, n)


def test_rate_text():
    assert S.rate_text(0, 60) == "0 of 60 (0.0%, 95% CI 0.0 to 6.0%)"


def test_conformal_p_and_threshold():
    null = np.arange(1, 200, dtype=float)      # 199 null scores: 1..199
    assert S.conformal_p(1000.0, null) == pytest.approx(1 / 200)
    assert S.conformal_p(199.0, null) == pytest.approx(2 / 200)
    assert S.conformal_p(0.0, null) == 1.0
    assert S.conformal_p(float("nan"), null) == 1.0
    t = S.conformal_threshold(null, 0.01)       # two tail cases allowed: above the 198th score
    assert t == 198.0
    assert S.conformal_p(np.nextafter(t, np.inf), null) <= 0.01
    assert S.conformal_p(t, null) > 0.01
    assert S.conformal_threshold(np.arange(98.0), 0.01) is None     # 1/99 > 0.01: abstain


def test_conformal_p_is_uniform_under_the_null():
    """Exchangeable scores: P(p <= alpha) <= alpha, measured over many draws."""
    rng = np.random.default_rng(0)
    ps = [S.conformal_p(rng.standard_normal(), rng.standard_normal(19)) for _ in range(20000)]
    ps = np.array(ps)
    for a in (0.05, 0.1, 0.5):
        assert np.mean(ps <= a) <= a + 3 * np.sqrt(a * (1 - a) / len(ps))


def test_shuffle_pieces_keeps_values_and_breaks_order():
    rng = np.random.default_rng(1)
    x = np.arange(1000, dtype=float)
    y = S.shuffle_pieces(x, rng, 20, 60)
    assert np.array_equal(np.sort(y), x)        # the same values, nothing lost or added
    assert not np.array_equal(y, x)
    F = np.stack([x, -x], axis=1)               # 2-D: frames on the first axis
    G = S.shuffle_pieces(F, np.random.default_rng(1), 20, 60)
    assert G.shape == F.shape and np.array_equal(G[:, 0], -G[:, 1])
    with pytest.raises(ValueError):
        S.shuffle_pieces(x, rng, 0, 5)


def test_surrogate_p_separates_pulse_from_random_events():
    fs = 200.0
    rng = np.random.default_rng(2)
    n = int(30 * fs)
    pulse = np.zeros(n)
    pulse[::100] = 1.0                           # a hit every 0.5 s
    pulse += 0.05 * rng.standard_normal(n)
    random_hits = np.zeros(n)
    random_hits[rng.choice(n, 60, replace=False)] = 1.0
    random_hits += 0.05 * rng.standard_normal(n)
    sp = P.surrogate_p(pulse, fs, 0.25, 2.0, k=99, seed=3)
    sn = P.surrogate_p(random_hits, fs, 0.25, 2.0, k=99, seed=3)
    assert sp["p"] == pytest.approx(0.01)        # above every surrogate
    assert sn["p"] > 0.05
