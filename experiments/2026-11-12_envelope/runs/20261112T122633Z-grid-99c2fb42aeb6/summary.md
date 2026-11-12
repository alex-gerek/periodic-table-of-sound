# Envelope validation: summary

Grid run `20261112T122633Z-grid-99c2fb42aeb6`, scaling run `20261112T122633Z-scaling-99c2fb42aeb6`.
A cell passes when, over its shapes and seeds, the median |time error| ≤ 10%, the 95th percentile ≤ 20%, and the median shape error ≤ 0.05.

## 1. Clean tonal carriers, analytic: pass map (rows: true time T, columns: window w)

Each cell: passing carriers out of 8 (sine and harmonic at 55, 220, 880, 3520 Hz), SNR ∞.

| T \ w | 0.5 ms | 1 ms | 2 ms | 5 ms | 10 ms | 20 ms |
|---|---|---|---|---|---|---|
| 1 ms | 3 | 2 | 0 | 0 | 0 | 0 |
| 2 ms | 3 | 3 | 4 | 0 | 0 | 0 |
| 5 ms | 4 | 4 | 5 | 5 | 0 | 0 |
| 10 ms | 5 | 5 | 6 | 5 | 6 | 0 |
| 20 ms | 5 | 5 | 6 | 6 | 7 | 7 |
| 50 ms | 5 | 5 | 6 | 6 | 7 | 7 |
| 100 ms | 5 | 5 | 6 | 6 | 7 | 7 |
| 200 ms | 5 | 5 | 6 | 6 | 7 | 7 |
| 500 ms | 5 | 5 | 6 | 6 | 7 | 7 |

## 1. Clean tonal carriers, rms: pass map (rows: true time T, columns: window w)

Each cell: passing carriers out of 8 (sine and harmonic at 55, 220, 880, 3520 Hz), SNR ∞.

| T \ w | 0.5 ms | 1 ms | 2 ms | 5 ms | 10 ms | 20 ms |
|---|---|---|---|---|---|---|
| 1 ms | 2 | 0 | 0 | 0 | 0 | 0 |
| 2 ms | 2 | 3 | 0 | 0 | 0 | 0 |
| 5 ms | 2 | 3 | 4 | 0 | 0 | 0 |
| 10 ms | 2 | 3 | 4 | 5 | 0 | 0 |
| 20 ms | 2 | 3 | 4 | 5 | 6 | 0 |
| 50 ms | 2 | 3 | 4 | 5 | 6 | 7 |
| 100 ms | 2 | 3 | 4 | 5 | 6 | 7 |
| 200 ms | 2 | 3 | 4 | 5 | 6 | 7 |
| 500 ms | 2 | 3 | 4 | 5 | 6 | 7 |

## 2. Where it works, in dimensionless terms (tonal carriers, SNR ∞)

Share of passing cells by the window/time ratio w/T and the carrier cycles inside the window w·f0.

| method | w/T ≤ 0.1, w·f0 ≥ 2 | w/T ≤ 0.25, w·f0 ≥ 2 | w/T ≤ 0.25, w·f0 < 2 | w/T 0.25–0.5 | w/T > 0.5 |
|---|---|---|---|---|---|
| analytic | 100% (68) | 100% (88) | 56% (176) | 62% (48) | 20% (120) |
| rms | 100% (68) | 100% (88) | 24% (176) | 56% (48) | 0% (120) |

## 3. Pitch: the shortest time read within the criteria (SNR ∞, best window)

| Carrier | f0 | analytic | rms | T·f0 at the limit (analytic) |
|---|---|---|---|---|
| sine | 55 | 10 ms | 50 ms | 0.6 |
| sine | 220 | 5 ms | 10 ms | 1.1 |
| sine | 880 | 1 ms | 2 ms | 0.9 |
| sine | 3520 | 1 ms | 1 ms | 3.5 |
| harmonic | 55 | none | none | – |
| harmonic | 220 | 10 ms | 20 ms | 2.2 |
| harmonic | 880 | 2 ms | 5 ms | 1.8 |
| harmonic | 3520 | 1 ms | 1 ms | 3.5 |
| noise | – | 10 ms | 5 ms | – |

## 4. Noise: median |time error| at the best window per cell, analytic

| Carrier | T | SNR ∞ | 20 dB | 10 dB |
|---|---|---|---|---|
| sine 880 | 5 ms | 0.1% | 1.9% | 5.2% |
| sine 880 | 20 ms | 0.0% | 0.8% | 7.6% |
| sine 880 | 50 ms | 0.0% | 0.6% | 3.7% |
| sine 880 | 200 ms | 0.0% | 1.1% | 3.8% |
| harmonic 220 | 5 ms | 8.2% | 6.1% | 29.5% |
| harmonic 220 | 20 ms | 2.4% | 2.7% | 4.9% |
| harmonic 220 | 50 ms | 0.4% | 0.4% | 1.9% |
| harmonic 220 | 200 ms | 0.0% | 0.6% | 1.6% |
| noise  | 5 ms | 6.0% | 6.7% | 13.5% |
| noise  | 20 ms | 4.6% | 3.5% | 6.6% |
| noise  | 50 ms | 2.4% | 2.4% | 3.0% |
| noise  | 200 ms | 1.9% | 2.2% | 3.6% |

## 5. Constant level: false change (median dB) and linearity (doubling the amplitude)

| Carrier | method | w | false change, SNR ∞ | 20 dB | 10 dB | linearity, worst deviation from 6.02 dB |
|---|---|---|---|---|---|---|
| sine 55 | analytic | 2 ms | 0.00 | 0.54 | 1.68 | 0.000 dB |
| sine 55 | analytic | 5 ms | 0.00 | 0.32 | 1.01 | 0.000 dB |
| sine 55 | analytic | 20 ms | 0.00 | 0.18 | 0.55 | 0.000 dB |
| sine 55 | rms | 2 ms | 17.88 | 17.86 | 14.71 | 0.000 dB |
| sine 55 | rms | 5 ms | 9.98 | 10.23 | 9.52 | 0.000 dB |
| sine 55 | rms | 20 ms | 0.19 | 0.37 | 0.69 | 0.000 dB |
| sine 880 | analytic | 2 ms | 0.00 | 0.74 | 2.23 | 0.000 dB |
| sine 880 | analytic | 5 ms | 0.00 | 0.46 | 1.41 | 0.000 dB |
| sine 880 | analytic | 20 ms | 0.00 | 0.17 | 0.51 | 0.000 dB |
| sine 880 | rms | 2 ms | 0.06 | 0.78 | 2.19 | 0.000 dB |
| sine 880 | rms | 5 ms | 0.00 | 0.46 | 1.37 | 0.000 dB |
| sine 880 | rms | 20 ms | 0.00 | 0.17 | 0.50 | 0.000 dB |
| harmonic 55 | analytic | 2 ms | 16.89 | 17.45 | 14.95 | 0.000 dB |
| harmonic 55 | analytic | 5 ms | 11.78 | 11.98 | 10.92 | 0.000 dB |
| harmonic 55 | analytic | 20 ms | 2.97 | 3.11 | 3.14 | 0.000 dB |
| harmonic 55 | rms | 2 ms | 21.30 | 21.42 | 17.30 | 0.000 dB |
| harmonic 55 | rms | 5 ms | 14.07 | 14.17 | 12.48 | 0.000 dB |
| harmonic 55 | rms | 20 ms | 2.65 | 2.78 | 2.83 | 0.000 dB |
| harmonic 880 | analytic | 2 ms | 0.35 | 1.03 | 2.37 | 0.000 dB |
| harmonic 880 | analytic | 5 ms | 0.03 | 0.49 | 1.39 | 0.000 dB |
| harmonic 880 | analytic | 20 ms | 0.00 | 0.21 | 0.61 | 0.000 dB |
| harmonic 880 | rms | 2 ms | 0.30 | 0.97 | 2.27 | 0.000 dB |
| harmonic 880 | rms | 5 ms | 0.02 | 0.43 | 1.21 | 0.000 dB |
| harmonic 880 | rms | 20 ms | 0.00 | 0.19 | 0.54 | 0.000 dB |
| noise  | analytic | 2 ms | 5.45 | 5.30 | 5.53 | 0.000 dB |
| noise  | analytic | 5 ms | 2.95 | 2.88 | 3.12 | 0.000 dB |
| noise  | analytic | 20 ms | 1.19 | 1.14 | 1.13 | 0.000 dB |
| noise  | rms | 2 ms | 5.16 | 5.11 | 5.41 | 0.000 dB |
| noise  | rms | 5 ms | 2.88 | 3.00 | 3.21 | 0.000 dB |
| noise  | rms | 20 ms | 1.12 | 1.10 | 1.12 | 0.000 dB |

## 6. Tape-speed scaling: measured time ratio against k

Ratio error = (T_k / T_1) / k − 1. ΔZ should equal log₂ k. Window scaled with k, or kept fixed.

| Carrier | window | k | median |ratio error| | worst | median |ΔZ − log₂ k| | rows that changed |
|---|---|---|---|---|---|---|
| sine | scaled | 0.125 | 0.01% | 0.3% | 0.000 | 6 of 12 |
| sine | scaled | 0.25 | 0.01% | 0.3% | 0.000 | 6 of 12 |
| sine | scaled | 0.5 | 0.00% | 0.1% | 0.000 | 0 of 12 |
| sine | scaled | 2 | 0.00% | 0.0% | 0.000 | 6 of 12 |
| sine | scaled | 4 | 0.00% | 0.1% | 0.000 | 9 of 12 |
| sine | fixed | 0.125 | 3.33% | 81.1% | 0.047 | 6 of 12 |
| sine | fixed | 0.25 | 0.76% | 23.3% | 0.011 | 6 of 12 |
| sine | fixed | 0.5 | 0.15% | 5.2% | 0.002 | 0 of 12 |
| sine | fixed | 2 | 0.04% | 1.4% | 0.001 | 6 of 12 |
| sine | fixed | 4 | 0.04% | 1.6% | 0.001 | 9 of 12 |
| harmonic | scaled | 0.125 | 1.53% | 10.0% | 0.022 | 10 of 12 |
| harmonic | scaled | 0.25 | 1.23% | 11.0% | 0.018 | 8 of 12 |
| harmonic | scaled | 0.5 | 0.13% | 2.5% | 0.002 | 6 of 12 |
| harmonic | scaled | 2 | 0.06% | 1.1% | 0.001 | 3 of 12 |
| harmonic | scaled | 4 | 0.09% | 1.7% | 0.001 | 5 of 12 |
| harmonic | fixed | 0.125 | 116.26% | 6137.8% | 1.103 | 5 of 12 |
| harmonic | fixed | 0.25 | 80.57% | 6078.0% | 0.852 | 5 of 12 |
| harmonic | fixed | 0.5 | 29.43% | 3157.1% | 0.372 | 2 of 12 |
| harmonic | fixed | 2 | 14.16% | 25.5% | 0.220 | 2 of 12 |
| harmonic | fixed | 4 | 29.34% | 49.1% | 0.501 | 3 of 12 |
| noise | scaled | 0.125 | 11.79% | 38.3% | 0.181 | 7 of 12 |
| noise | scaled | 0.25 | 11.08% | 26.7% | 0.161 | 6 of 12 |
| noise | scaled | 0.5 | 4.60% | 12.1% | 0.068 | 1 of 12 |
| noise | scaled | 2 | 0.17% | 1.1% | 0.002 | 5 of 12 |
| noise | scaled | 4 | 0.15% | 1.0% | 0.002 | 8 of 12 |
| noise | fixed | 0.125 | 20.85% | 316.1% | 0.273 | 4 of 12 |
| noise | fixed | 0.25 | 9.47% | 121.6% | 0.130 | 3 of 12 |
| noise | fixed | 0.5 | 6.67% | 40.5% | 0.093 | 1 of 12 |
| noise | fixed | 2 | 8.06% | 18.4% | 0.121 | 5 of 12 |
| noise | fixed | 4 | 14.93% | 36.1% | 0.233 | 8 of 12 |
