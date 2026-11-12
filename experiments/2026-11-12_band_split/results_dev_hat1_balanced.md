# Band split, dev_hat1_balanced

1920 signals, 160 ambiguous by construction (the same events under both labels), 1760 scored.

| Features / classifier | Accuracy |
|---|---|
| full / logistic | 90.7% |
| full / knn | 95.5% |
| bands / logistic | 95.5% |
| bands / knn | 96.0% |
| both / logistic | 95.7% |
| both / knn | 95.5% |

Best full (full / knn) against best both (both / logistic): full right and both wrong 56, full wrong and both right 61, McNemar χ² = 0.1.

## Combinations the full envelope gets wrong most often

| Combination (kick, snare, hats per beat, accent) | Signals | Full right | Both right |
|---|---|---|---|
| 1_3|none|2|1 as T/2 | 20 | 0 | 17 |
| 1_3|none|4|1 as T/2 | 20 | 2 | 16 |
| 1_3|none|2|1 as T | 20 | 8 | 20 |
| 1_3|none|4|1 as T | 20 | 10 | 20 |
| 1|none|2|1 as T/2 | 20 | 14 | 0 |
| 1|none|4|1 as T/2 | 20 | 15 | 0 |
| 1_3|2_4|4|1 as T | 20 | 18 | 20 |
| 1_3_and3|none|2|1 as T/2 | 20 | 18 | 20 |
| every|none|4|1 as T | 20 | 19 | 7 |
| 1_3|2_4|4|0 as T | 20 | 19 | 20 |
| 1_3_and3|none|4|1 as T/2 | 20 | 19 | 20 |
| 1|2_4|4|0 as T | 20 | 19 | 20 |
| 1|2_4|4|1 as T | 20 | 19 | 20 |
| every|none|2|0 as T/2 | 20 | 20 | 20 |
| every|none|2|1 as T | 20 | 20 | 7 |
| every|none|2|1 as T/2 | 20 | 20 | 20 |
