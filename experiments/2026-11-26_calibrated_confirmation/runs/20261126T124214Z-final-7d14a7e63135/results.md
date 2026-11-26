# Calibrated period confirmation: results

Run `20261126T124214Z-final-7d14a7e63135`. Sigma rule: 5 sigma, 4 repetitions, stable halves, return (2026-11-12). Surrogate rule: p <= 0.01 against K = 199 shuffles of the onset envelope, and at least 4 repetitions. Rates are k of n with exact 95% intervals.

| Set | Cases | Sigma rule | Surrogate rule | Both | Disagree |
|---|---|---|---|---|---|
| fresh | non-periodic: passed (false detections) | 0 of 120 (0.0%, 95% CI 0.0 to 3.0%) | 2 of 120 (1.7%, 95% CI 0.2 to 5.9%) | 0 of 120 (0.0%, 95% CI 0.0 to 3.0%) | 2 |
| fresh | periodic: passed | 120 of 120 (100.0%, 95% CI 97.0 to 100.0%) | 120 of 120 (100.0%, 95% CI 97.0 to 100.0%) | 120 of 120 (100.0%, 95% CI 97.0 to 100.0%) | 0 |
| fresh_real | non-periodic: passed (false detections) | 0 of 12 (0.0%, 95% CI 0.0 to 26.5%) | 0 of 12 (0.0%, 95% CI 0.0 to 26.5%) | 0 of 12 (0.0%, 95% CI 0.0 to 26.5%) | 0 |
| fresh_real | periodic: passed | 12 of 12 (100.0%, 95% CI 73.5 to 100.0%) | 12 of 12 (100.0%, 95% CI 73.5 to 100.0%) | 12 of 12 (100.0%, 95% CI 73.5 to 100.0%) | 0 |
| dev_train | non-periodic: passed (false detections) | 0 of 60 (0.0%, 95% CI 0.0 to 6.0%) | 1 of 60 (1.7%, 95% CI 0.0 to 8.9%) | 0 of 60 (0.0%, 95% CI 0.0 to 6.0%) | 1 |
| dev_train | periodic: passed | 59 of 60 (98.3%, 95% CI 91.1 to 100.0%) | 60 of 60 (100.0%, 95% CI 94.0 to 100.0%) | 59 of 60 (98.3%, 95% CI 91.1 to 100.0%) | 1 |
| dev_test | non-periodic: passed (false detections) | 0 of 60 (0.0%, 95% CI 0.0 to 6.0%) | 0 of 60 (0.0%, 95% CI 0.0 to 6.0%) | 0 of 60 (0.0%, 95% CI 0.0 to 6.0%) | 0 |
| dev_test | periodic: passed | 60 of 60 (100.0%, 95% CI 94.0 to 100.0%) | 60 of 60 (100.0%, 95% CI 94.0 to 100.0%) | 60 of 60 (100.0%, 95% CI 94.0 to 100.0%) | 0 |
| dev_real | non-periodic: passed (false detections) | 0 of 12 (0.0%, 95% CI 0.0 to 26.5%) | 0 of 12 (0.0%, 95% CI 0.0 to 26.5%) | 0 of 12 (0.0%, 95% CI 0.0 to 26.5%) | 0 |
| dev_real | periodic: passed | 12 of 12 (100.0%, 95% CI 73.5 to 100.0%) | 12 of 12 (100.0%, 95% CI 73.5 to 100.0%) | 12 of 12 (100.0%, 95% CI 73.5 to 100.0%) | 0 |

## False detections of the surrogate rule by family (fresh set)

| Family | Surrogate rule | Sigma rule | Median p |
|---|---|---|---|
| random clicks | 0 of 20 (0.0%, 95% CI 0.0 to 16.8%) | 0 of 20 (0.0%, 95% CI 0.0 to 16.8%) | 0.573 |
| random drum hits | 1 of 20 (5.0%, 95% CI 0.1 to 24.9%) | 0 of 20 (0.0%, 95% CI 0.0 to 16.8%) | 0.670 |
| smooth swells | 1 of 20 (5.0%, 95% CI 0.1 to 24.9%) | 0 of 20 (0.0%, 95% CI 0.0 to 16.8%) | 0.420 |
| crescendo | 0 of 20 (0.0%, 95% CI 0.0 to 16.8%) | 0 of 20 (0.0%, 95% CI 0.0 to 16.8%) | 0.472 |
| white noise | 0 of 20 (0.0%, 95% CI 0.0 to 16.8%) | 0 of 20 (0.0%, 95% CI 0.0 to 16.8%) | 0.782 |
| pink noise | 0 of 20 (0.0%, 95% CI 0.0 to 16.8%) | 0 of 20 (0.0%, 95% CI 0.0 to 16.8%) | 0.665 |

## Every disagreement

| Set | Kind | Family | Seed | Sigma rule | p | S | Significance | Return | Weaker half |
|---|---|---|---|---|---|---|---|---|---|
| fresh | neg | random drum hits | 2007 | no | 0.010 | 3.4 | 3.4 | 6.0 | 2.4 |
| fresh | neg | smooth swells | 2044 | no | 0.005 | 3.1 | 4.4 | 3.1 | 3.0 |
| dev_train | neg | random clicks | 14 | no | 0.005 | 4.5 | 5.2 | 7.8 | 3.2 |
| dev_train | pos | click_train | 40 | no | 0.010 | 4.7 | 4.7 | 6.3 | 3.3 |

Positives confirmed by the sigma rule with p at the floor 1/200: 262 of 263 (99.6%, 95% CI 97.9 to 100.0%).
Run time: 534 s.
