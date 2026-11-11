"""The time axis of the table: time octave Z and the seven periods.

Z = log2(tau / 1 s) + 15. One step of Z doubles tau.
"""
import math

# Period borders in Z (see docs/ordering_criteria.md, section 3).
CUTS = (6.0, 10.7, 13.0, 16.0, 18.0, 20.0)
PERIODS = ("Wave", "Tone", "Event", "Beat", "Bar", "Phrase", "Form")


def z_of(tau_s: float) -> float:
    """Time octave of a characteristic time tau in seconds."""
    return math.log2(tau_s) + 15.0


def tau_of(z: float) -> float:
    """Characteristic time in seconds for a time octave z."""
    return 2.0 ** (z - 15.0)


def period_of(z: float) -> int:
    """Row of the table (1..7) that a time octave falls into."""
    return 1 + sum(z >= c for c in CUTS)


def period_bounds(period: int) -> tuple[float, float]:
    """(tau_min, tau_max) in seconds of a row; the last row is capped at 10 minutes."""
    edges = (-math.inf,) + CUTS + (math.inf,)
    lo, hi = edges[period - 1], edges[period]
    return (tau_of(lo) if lo > -math.inf else 0.0, tau_of(hi) if hi < math.inf else 600.0)
