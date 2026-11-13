# Metrical ladder (issue #29)

The pulse is reported as a ladder of related levels instead of one beat: the seed period of the old rule, the divisions below it (by 2 or by 3, in the full or the high band) and the groupings above it (by 2 or by 3, from an accent test). Journal step 2026-11-13-ladder-001 holds the protocol, the three tuning runs, the frozen constants and the outcome.

- `ladder.py`: the evaluated copy (the core copy is `pts/ladder.py`).
- `evaluate.py tune | final | tapped`: dev tuning, the single held-out run, and the tapped tracks.
- `runs/`: every run, with its console and results.

Held-out result: coverage 0.965 on both groove sets and 12 of 12 tapped tracks, median ladder size 3, meter 0.888 and 0.955 against baselines 0.629 and 0.731, all 120 negatives empty.
