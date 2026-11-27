# Leaks written where the target is loud: results

Run `20261127T090128Z-final-2ede313c2142`. 7 songs, 42 pairs. Detected = p <= 0.01. Estimate = median leak estimate (dB).

## Estimator A

No leak: 0 of 42 (0.0%, 95% CI 0.0 to 8.4%) detected.

| Kind | -40 dB: detected / estimate | -35 dB: detected / estimate | -30 dB: detected / estimate | -25 dB: detected / estimate |
|---|---|---|---|---|
| linear | 1/42, -40.4 | 27/42, -35.1 | 42/42, -30.0 | 42/42, -25.0 |
| independent | 1/42, -41.5 | 21/42, -36.2 | 41/42, -31.0 | 42/42, -26.0 |
| wiener | 0/42, -51.3 | 0/42, -43.3 | 14/42, -38.0 | 32/42, -32.9 |
| loud | 0/42, -42.6 | 12/42, -37.2 | 35/42, -32.3 | 40/42, -27.3 |

Real stems, against the 60 s estimator: median |difference| 2.2 dB over 10 pairs that both detect.
**Passes the decision rule:** no.

## Estimator B

No leak: 0 of 42 (0.0%, 95% CI 0.0 to 8.4%) detected.

| Kind | -40 dB: detected / estimate | -35 dB: detected / estimate | -30 dB: detected / estimate | -25 dB: detected / estimate |
|---|---|---|---|---|
| linear | 41/42, -40.1 | 42/42, -35.1 | 42/42, -30.1 | 42/42, -25.1 |
| independent | 38/42, -41.5 | 41/42, -36.5 | 41/42, -31.5 | 41/42, -26.5 |
| wiener | 4/42, -98.1 | 9/42, -88.9 | 13/42, -84.5 | 16/42, -81.0 |
| loud | 13/42, -92.4 | 18/42, -89.1 | 20/42, -86.9 | 22/42, -84.2 |

Real stems, against the 60 s estimator: median |difference| 21.8 dB over 10 pairs that both detect.
**Passes the decision rule:** no.

## Estimator C

No leak: 0 of 42 (0.0%, 95% CI 0.0 to 8.4%) detected.

| Kind | -40 dB: detected / estimate | -35 dB: detected / estimate | -30 dB: detected / estimate | -25 dB: detected / estimate |
|---|---|---|---|---|
| linear | 0/42, -45.7 | 1/42, -36.0 | 24/42, -30.3 | 42/42, -25.1 |
| independent | 0/42, -51.1 | 0/42, -37.2 | 17/42, -31.3 | 42/42, -26.0 |
| wiener | 0/42, -inf | 0/42, -39.8 | 8/42, -33.6 | 29/42, -28.7 |
| loud | 0/42, -45.0 | 2/42, -36.3 | 21/42, -30.7 | 42/42, -25.5 |

Real stems, against the 60 s estimator: median |difference| 1.6 dB over 10 pairs that both detect.
**Passes the decision rule:** no.

Run time: 11682 s.
