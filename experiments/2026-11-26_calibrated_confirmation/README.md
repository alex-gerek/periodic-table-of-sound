# 2026-11-26: a calibrated false-alarm rate for period confirmation

Issue #32, journal step `2026-11-26-calib-001` (hypotheses and decision rule written before the run).

`confirm_period()` decides in sigma. A sigma is a distance, not a probability, so the rule could not say how often it confirms a period that is not there. This step adds a test that states its rate directly:

- `pts.periodicity.surrogate_p()`: the full search (best lag in 0.25 to 2 s, then S = min(significance, return, √2 × weaker half)) is repeated on 199 shuffles of the track's own onset envelope, cut into pieces of 83 to 250 ms. p = (1 + surrogates with S ≥ S_track) / 200. If the order of the events is random, P(p ≤ α) ≤ α exactly.
- `pts/stats.py`: exact (Clopper-Pearson) and Wilson intervals, conformal p-values and thresholds (with "not attainable" when there are too few null cases), and the shuffled-pieces surrogate. The method comes from our Blind Signal Discovery project and is re-derived with numpy only.

Run `python run.py <label>`; each run gets its own folder under `runs/`.

## Result (run `20261126T124214Z-final-7d14a7e63135`)

| Set | False detections, sigma rule | False detections, surrogate p ≤ 0.01 | Periodic signals confirmed (both rules) |
|---|---|---|---|
| Fresh synthetic (seeds 2000–2119) | 0 of 120 (CI 0–3.0%) | 2 of 120 (CI 0.2–5.9%) | 120 of 120 |
| Fresh real (12 drum stems, new shuffles) | 0 of 12 (CI 0–26.5%) | 0 of 12 | 12 of 12 |
| Development (2026-11-12 sets) | 0 of 132 | 1 of 132 | sigma 131, surrogate 132 of 132 |

- The p-values of the fresh negatives are close to uniform (median 0.54; 5% at or below 0.05): the test is near calibrated even on families it does not model.
- The sigma rule is more conservative than 1%: 0 of 252 negatives in all sets (95% CI 0 to 1.5%).
- 262 of 263 periodic signals confirmed by the sigma rule have p at the floor 1/200.

**Decision:** the surrogate p-value is reported evidence, not a gate: on fresh data the sigma rule confirmed no negative, so a gate would never act. Full tables: `runs/…/results.md`.

## Limits

- The surrogates keep repetition shorter than their pieces, so a period just above 0.25 s is tested against a slightly periodic null (one click train got p = 0.010 instead of the floor). This makes the test conservative there, not lax.
- Only 12 real stems; other genres are untested.
