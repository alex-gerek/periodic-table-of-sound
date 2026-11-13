"""Metrical ladder (issue #29): the levels of a pulse and their groupings.

The ladder went into pts after the held-out check (journal step 2026-11-13-ladder-001). The
evaluated copy stays in experiments/2026-11-13_metrical_ladder/ladder.py, and the last test
checks that the two agree.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "experiments", "2026-11-12_beat_level"))
sys.path.insert(0, os.path.dirname(HERE))
import bench as B             # noqa: E402
from pts import ladder as L   # noqa: E402

SR = B.SR


def clicks(beat, accent_every, dur=30.0, accent=1.6, seed=0):
    """A kick on every beat, louder on every accent_every-th beat (0: all equal)."""
    rng = np.random.default_rng(seed)
    k = B._kick(rng)
    x = np.zeros(int(dur * SR) + SR)
    for i in range(int(dur / beat)):
        B._place(x, i * beat, k, accent if accent_every and i % accent_every == 0 else 1.0)
    return x[: int(dur * SR)] + 1e-3 * rng.standard_normal(int(dur * SR))


def taus(levels):
    return [lv["tau"] for lv in levels]


def test_three_four_groups_by_three():
    lv = L.ladder(clicks(0.5, 3), SR)
    i = L.on_ladder(lv, 0.5)
    assert i is not None
    assert i + 1 < len(lv) and lv[i + 1]["step"] == 3
    assert L.on_ladder(lv, 1.0) is None


def test_four_four_groups_by_two():
    lv = L.ladder(clicks(0.5, 4), SR)
    i = L.on_ladder(lv, 0.5)
    assert i is not None
    assert i + 1 < len(lv) and lv[i + 1]["step"] == 2
    assert L.on_ladder(lv, 1.5) is None


def test_equal_clicks_have_no_grouping():
    lv = L.ladder(clicks(0.5, 0), SR)
    assert L.on_ladder(lv, 0.5) is not None
    assert all(v["role"] != "grouping" for v in lv)


def test_noise_has_an_empty_ladder():
    rng = np.random.default_rng(3)
    assert L.ladder(rng.standard_normal(30 * SR), SR) == []


def test_ladder_is_ordered_and_related():
    lv = L.ladder(clicks(0.4, 4), SR)
    t = taus(lv)
    assert t == sorted(t)
    assert len(t) >= 2
    for j in range(len(lv) - 1):
        k = lv[j + 1]["step"] if lv[j + 1]["role"] == "grouping" else lv[j]["step"]
        assert abs(t[j + 1] / t[j] / k - 1) < 0.03


def test_core_matches_the_evaluated_copy():
    import importlib.util
    path = os.path.join(os.path.dirname(HERE), "experiments", "2026-11-13_metrical_ladder", "ladder.py")
    spec = importlib.util.spec_from_file_location("ladder_evaluated", path)
    E = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(E)
    for seed in (0, 7, 21):
        x, _, _ = B.groove(seed)
        assert L.ladder(x, SR) == E.ladder(x, SR)
