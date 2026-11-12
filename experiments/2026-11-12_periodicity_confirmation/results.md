# Confirming a period: results

Thresholds chosen on the training set: **significance ≥ 5 σ**, **at least 4 repetitions**, ≥ 3.54 σ in each half, and a **return of ≥ 5 σ** above the lowest correlation between half the lag and the lag.

| Set | Signals (neg / pos) | False detections on non-periodic signals | Misses on periodic signals | Confirmed but wrong period |
|---|---|---|---|---|
| Training (click trains) | 60 / 60 | 0.0% | 1.7% | 3.3% |
| Test (grooves, new seeds) | 60 / 60 | 0.0% | 0.0% | 1.7% |
| Real drum stems | 12 / 12 | 0.0% | 0.0% | not evaluated (no independent beat labels) |

Without the return test, 25 of 40 smooth swells and crescendos (training and test) would be confirmed; with it, 0.

Before issue #7, a period was returned for 100% (train), 100% (test), 100% (real) of the non-periodic signals.

## Real drum stems

| Stem | Candidate | Significance | Repetitions | Weaker half | Return | Confirmed | Shuffled: significance | Shuffled: confirmed |
|---|---|---|---|---|---|---|---|---|
| gravity | 0.504 s | 53.2 σ | 119 | 32.6 σ | 56.0 σ | yes | 1.8 σ | no |
| pure_voltage | 0.540 s | 52.8 σ | 111 | 27.5 σ | 54.9 σ | yes | 3.3 σ | no |
| tempo_080_4-4 | 0.494 s | 50.9 σ | 121 | 31.2 σ | 55.9 σ | yes | 2.7 σ | no |
| tempo_080_4-4_retake | 1.499 s | 35.0 σ | 40 | 23.2 σ | 37.8 σ | yes | 1.3 σ | no |
| tempo_100_4-4 | 0.600 s | 52.9 σ | 100 | 36.9 σ | 57.7 σ | yes | 2.4 σ | no |
| tempo_120_4-4 | 0.496 s | 55.2 σ | 121 | 37.2 σ | 59.6 σ | yes | 2.5 σ | no |
| tempo_140_4-4 | 0.426 s | 52.2 σ | 141 | 35.0 σ | 58.0 σ | yes | 2.2 σ | no |
| tempo_160_4-4 | 0.367 s | 50.2 σ | 163 | 14.9 σ | 53.8 σ | yes | 2.0 σ | no |
| tempo_174_4-4 | 0.690 s | 40.3 σ | 87 | 26.3 σ | 46.6 σ | yes | 2.2 σ | no |
| meter_3-4 | 0.986 s | 50.6 σ | 61 | 35.0 σ | 54.5 σ | yes | 2.3 σ | no |
| meter_6-8 | 0.945 s | 32.3 σ | 64 | 21.6 σ | 33.1 σ | yes | 2.5 σ | no |
| meter_6-8_retake | 0.287 s | 35.5 σ | 209 | 23.5 σ | 39.7 σ | yes | 1.2 σ | no |

## Significance by family (median, training and test)

| Family | Median significance | Largest |
|---|---|---|
| white noise | 1.7 σ | 3.0 σ |
| pink noise | 1.8 σ | 3.2 σ |
| random clicks | 2.3 σ | 5.2 σ |
| random drum hits | 1.5 σ | 3.9 σ |
| smooth swells | 7.6 σ | 9.0 σ |
| crescendo | 7.5 σ | 8.9 σ |
| click_train | 18.6 σ | 41.9 σ |
| groove | 24.1 σ | 47.3 σ |
