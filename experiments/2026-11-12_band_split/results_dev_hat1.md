# Band split, dev_hat1

1920 signals, 80 ambiguous by construction (the same events under both labels), 1840 scored.

| Features / classifier | Accuracy |
|---|---|
| full / logistic | 90.8% |
| full / knn | 95.1% |
| bands / logistic | 96.7% |
| bands / knn | 97.8% |
| both / logistic | 96.8% |
| both / knn | 97.8% |

Best full (full / knn) against best both (both / knn): full right and both wrong 17, full wrong and both right 67, McNemar χ² = 28.6.

## Combinations the full envelope gets wrong most often

| Combination (kick, snare, hats per beat, accent) | Signals | Full right | Both right |
|---|---|---|---|
| 1_3|none|4|1 as T | 20 | 1 | 0 |
| 1_3|none|2|1 as T/2 | 20 | 2 | 18 |
| 1_3|none|4|0 as T/2 | 20 | 3 | 20 |
| 1_3|none|4|1 as T/2 | 20 | 3 | 20 |
| every|none|4|1 as T | 20 | 17 | 3 |
| 1|none|4|0 as T/2 | 20 | 17 | 20 |
| 1_3|2_4|4|0 as T | 20 | 18 | 20 |
| 1_3|2_4|4|1 as T | 20 | 18 | 20 |
| 1|none|4|1 as T/2 | 20 | 18 | 20 |
| 1_3_and3|none|2|0 as T/2 | 20 | 19 | 20 |
| 1_3_and3|none|2|1 as T/2 | 20 | 19 | 20 |
| 1_3_and3|none|4|0 as T/2 | 20 | 19 | 20 |
| 1_3_and3|none|4|1 as T/2 | 20 | 19 | 20 |
| 1|none|2|1 as T/2 | 20 | 19 | 18 |
| 1|2_4|4|0 as T | 20 | 19 | 20 |
| 1|2_4|4|0 as T/2 | 20 | 19 | 20 |
