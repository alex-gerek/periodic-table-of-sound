# 2026-11-26: stem leakage on full tracks

Issue #38, journal step `2026-11-26-leak-002` (plan and decision rule written before the run). Two estimators on the full common length of the stems: **A**, the leak-001 estimator unchanged; **B**, the same with frames weighted by the inverse of the target's own smoothed power.

## Result (run `20261126T144633Z-final-16b0271af642`)

| | A | B |
|---|---|---|
| False alarms (42 pairs) | 0 | 0 |
| Chance level | −43.6 dB | −96.8 dB |
| Reliable detection from | −30 dB | −40 dB |
| Level error | ~1 dB from −40 dB | < 0.1 dB from −50 dB |
| Pre-registered H1–H3 | H2, H3 fail | all hold |
| Voice in drums: GRAVITY / Pure voltage | −23.9 / −25.0 dB | −92.5 / −43.2 dB |

**B is not adopted, though it met the pre-registered rule.** On real stems it contradicts A (and the 60 s estimator) by up to 70 dB. A separator leaves another source where the target is loud; B ignores those frames. The cross-song ground truth wrote leaks evenly over time and could not show this. Nothing goes into `pts/`. The next ground truth writes leaks where the target is loud.

Full matrices for B: `runs/…/results.md`; A's values are in `results.json`.
