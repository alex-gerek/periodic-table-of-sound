# 2026-11-26: seam hunt, pilot

Issue #34, journal step `2026-11-26-seam-001` (hypotheses and decision rule written before the run). **Outcome: negative.**

A Seam is a join in generated audio where the background changes without a musical reason. The prototype detector (`run.py`, not in `pts/`) follows the regime monitor of our Blind Signal Discovery project: per 1 s block it measures the floor of 8 bands (10th percentile of frame power) and the energy above 16 kHz against 8 to 16 kHz, and scores every second by the change of the median over 6 s before and after. Each 30 s window gets a conformal p-value against live recordings (leave one recording out).

## Result (run `20261126T130343Z-final-8b6fbfe16b76`)

| | Result | Hypothesis |
|---|---|---|
| Live windows flagged (calibration) | S_all 4 of 95, S_bw 5 of 95 | holds (≤ 10%) |
| Bandwidth join (16 kHz low-pass) found | S_bw 43 of 95 (45%), S_all 9 of 95 | **fails** (≥ 80%) |
| Noise floor join (−60 dB) found | 1 of 95 | **fails** (≥ 60%) |
| Tilt join (+3 dB above 4 kHz) found | 1 of 95 | **fails** (≥ 50%) |
| Splice (crossfaded) found | 0 of 89 (S_all), 3 of 89 (S_bw) | no target |
| Suno windows flagged by S_bw | 13 of 65 (20%) against 5 of 95 live | holds by the letter, not interpretable |

**Why** (post-hoc, `diagnose.py`): the live background moves more than these joins change it. With floor, tilt or splice joins the scores stay at the level of untouched windows. Bandwidth joins are invisible where a recording has nothing above 16 kHz.

**Decision:** nothing adopted. The next attempt needs generated tracks with known extend times (`data/material_request.md`, section 7), a null from the same track instead of live recordings, and a level sweep.

Audio stays outside git; `results.json` lists the SHA-256 of every input file.
