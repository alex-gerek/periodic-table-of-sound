# Envelope: verdict on the held-out runs

Grid `20261112T123234Z-holdout-c578dc8bc74d`, scaling `20261112T123234Z-scaling_holdout-c578dc8bc74d`. Region and criteria as frozen in commit `c578dc8`.

## Inside the region

| Estimator | Cells passing | Cases | Median |time error| | 95th percentile | Worst | Median shape error | Worst shape error |
|---|---|---|---|---|---|---|---|
| analytic | 279 of 279 | 2511 | 0.32% | 3.92% | 12.9% | 0.0030 | 0.035 |
| rms | 279 of 279 | 2511 | 0.38% | 3.56% | 12.7% | 0.0034 | 0.031 |

## Outside the region (for the limits)

| Estimator | Cells passing outside the region | of |
|---|---|---|
| analytic | 516 | 1449 |
| rms | 359 | 1449 |

| Condition (analytic) | Cells | Passing |
|---|---|---|
| SNR 10 dB | 432 | 87 (20%) |
| noise carrier, w < 10 ms or w > T/4 | 129 | 27 (21%) |
| tonal, fewer than 2 carrier periods in the window | 300 | 152 (51%) |
| tonal, noisy and w < T/50 or w < 2 ms | 84 | 77 (92%) |
| tonal, w > T/4 | 504 | 173 (34%) |

## Constant level and linearity (inside the region)

| Estimator | Tonal: worst false change | Noise carrier: worst false change | Worst linearity deviation from 6.02 dB |
|---|---|---|---|
| analytic | 0.61 dB | 1.69 dB | 0.0000 dB |
| rms | 0.60 dB | 1.59 dB | 0.0000 dB |

## Tape-speed scaling inside the region (analytic, window scaled with k)

| Carrier | k | Cases | Median |ratio error| | Worst | Worst |ΔZ − log₂ k| | Row changed |
|---|---|---|---|---|---|---|
| sine | 0.25 | 9 | 0.00% | 0.02% | 0.000 | 3 |
| sine | 0.5 | 9 | 0.00% | 0.00% | 0.000 | 0 |
| sine | 2 | 9 | 0.00% | 0.00% | 0.000 | 6 |
| sine | 4 | 9 | 0.00% | 0.00% | 0.000 | 9 |
| harmonic | 0.25 | 9 | 0.08% | 0.55% | 0.008 | 3 |
| harmonic | 0.5 | 9 | 0.02% | 0.08% | 0.001 | 0 |
| harmonic | 2 | 9 | 0.02% | 0.08% | 0.001 | 6 |
| harmonic | 4 | 9 | 0.03% | 0.12% | 0.002 | 9 |
| noise | 0.25 | 6 | 3.56% | 7.16% | 0.107 | 3 |
| noise | 0.5 | 6 | 3.31% | 6.44% | 0.090 | 0 |
| noise | 2 | 6 | 0.11% | 0.21% | 0.003 | 6 |
| noise | 4 | 6 | 0.13% | 0.21% | 0.003 | 6 |

## Criteria (fixed before the runs)

| Criterion | Held-out result |
|---|---|
| time error, median ≤ 10% and 95th percentile ≤ 20% in every region cell | **met** |
| shape error ≤ 0.05 (median, every region cell) | **met** |
| constant tonal level, false change < 1 dB | **met** |
| doubling the amplitude: 6.02 ± 0.1 dB | **met** |
| tape-speed factor within 5% | **not met** |
