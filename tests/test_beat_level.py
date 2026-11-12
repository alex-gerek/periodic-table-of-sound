"""Beat level (issue #15): regression tests on the examples investigated during development.

The rules live in experiments/2026-11-12_beat_level/bench.py until it is decided whether the
new rule replaces the old one in pts. The signals are regenerated from their seeds.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "experiments", "2026-11-12_beat_level"))
import bench as B  # noqa: E402

_INV = {}


def investigated(family, seed):
    if not _INV:
        for x, beat, d in B.investigated():
            _INV[(d["family"], d["seed"])] = (x, beat)
    return _INV[(family, seed)]


# ---------------------------------------------------------------- the metric

@pytest.mark.parametrize("found,cls", [(1.0, "exact"), (1.029, "exact"), (1.06, "precision"), (0.5, "subdivision"),
                                       (1 / 3, "subdivision"), (2.0, "multiple"), (5.01, "multiple"),
                                       (0.75, "other"), (None, "none")])
def test_classify(found, cls):
    assert B.classify(found, 1.0)[0] == cls


# ---------------------------------------------------------------- investigated examples

@pytest.mark.parametrize("family,seed", [("click_train", 29), ("groove", 1001)])
def test_five_beats_is_reproduced_with_the_old_rule_and_fixed_with_the_new(family, seed):
    """The old comb on integer lags chose 5 beats at fast tempos."""
    x, beat = investigated(family, seed)
    old = B.classify(B.rule_old(x, B.SR), beat)
    assert old[0] == "multiple" and old[1] == pytest.approx(5.0, rel=0.01)
    assert B.classify(B.rule_new(x, B.SR), beat)[0] == "exact"


def test_precision_of_a_jittered_beat():
    """Seed 58: one widened peak gave the beat 3.2% off; the multiples give it within 1%."""
    x, beat = investigated("click_train", 58)
    assert B.classify(B.rule_old(x, B.SR), beat)[0] == "precision"
    c, q = B.classify(B.rule_new(x, B.SR), beat)
    assert c == "exact" and abs(q - 1) < 0.01


@pytest.mark.parametrize("seed", [55, 59, 118, 172])
def test_an_offbeat_kick_interval_is_not_a_period(seed):
    """Boom-bap: kick to off-beat kick (0.75 beat) is an interval, not a period."""
    x, beat, _ = B.groove(seed)
    assert B.classify(B.rule_new(x, B.SR), beat)[0] == "exact"


@pytest.mark.parametrize("seed", [36, 43, 110, 189])
def test_the_bar_is_not_the_beat(seed):
    """Development examples where the old rule returned 2, 3, 4 or 5 beats."""
    x, beat, _ = B.groove(seed)
    assert B.classify(B.rule_old(x, B.SR), beat)[0] == "multiple"
    assert B.classify(B.rule_new(x, B.SR), beat)[0] == "exact"


# ---------------------------------------------------------------- known errors of the new rule

@pytest.mark.xfail(strict=True, reason="known: the new rule returns the eighths on this boom-bap (issue #15)")
def test_known_error_boombap_seed_106():
    x, beat, _ = B.groove(106)
    assert B.classify(B.rule_new(x, B.SR), beat)[0] == "exact"


@pytest.mark.xfail(strict=True, reason="known: the new rule returns 2 beats; the old rule was exact (issue #15)")
def test_known_error_click_train_seed_40():
    x, beat = investigated("click_train", 40)
    assert B.classify(B.rule_new(x, B.SR), beat)[0] == "exact"


# ---------------------------------------------------------------- version 2: the four worsened signals of the first final set

import rule_v2 as V  # noqa: E402


@pytest.mark.parametrize("seed", [50080, 50130, 50188])
def test_a_noisy_beat_is_supported_by_its_confirmed_multiple(seed):
    """Exact with the old rule, 2 beats with version 1: the beat failed only the stability
    test in heavy noise. Version 2 accepts it because 2 beats is confirmed."""
    x, beat, _ = B.groove(seed)
    assert B.classify(B.rule_old(x, B.SR), beat)[0] == "exact"
    assert B.classify(B.rule_new(x, B.SR), beat)[0] == "multiple"
    assert B.classify(V.rule_new_v2(x, B.SR), beat)[0] == "exact"


@pytest.mark.parametrize("seed", [29, 1001, 58])
def test_version_2_keeps_the_investigated_fixes(seed):
    family = "groove" if seed >= 1000 else "click_train"
    x, beat = investigated(family, seed)
    assert B.classify(V.rule_new_v2(x, B.SR), beat)[0] == "exact"


@pytest.mark.parametrize("seed", [50134, 106])
@pytest.mark.xfail(strict=True, reason="known: boom-bap with a quieter kick on the 'and' has the same "
                                        "strong-weak structure at the half beat as a beat with a 2-beat bar")
def test_known_error_boombap_half_beat_version_2(seed):
    x, beat, _ = B.groove(seed)
    assert B.classify(V.rule_new_v2(x, B.SR), beat)[0] == "exact"


# ---------------------------------------------------------------- the second held-out set (seen after its single run)

import holdout_b as H  # noqa: E402


@pytest.mark.parametrize("seed", [70011, 70195])
def test_rock_kick_on_the_and_old_rule_is_exact(seed):
    x, beat, _ = H.groove_b(seed)
    assert B.classify(B.rule_old(x, B.SR), beat)[0] == "exact"


@pytest.mark.parametrize("seed", [70011, 70195])
@pytest.mark.xfail(strict=True, reason="known: the kick on the 'and' of 3 makes the half beat a period of strong events")
def test_known_error_rock_half_beat_version_2(seed):
    x, beat, _ = H.groove_b(seed)
    assert B.classify(V.rule_new_v2(x, B.SR), beat)[0] == "exact"
