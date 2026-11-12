# Band split, dev

1920 signals, 0 ambiguous by construction (the same events under both labels), 1920 scored.

| Features / classifier | Accuracy |
|---|---|
| full / logistic | 90.3% |
| full / knn | 93.4% |
| bands / logistic | 97.7% |
| bands / knn | 98.5% |
| both / logistic | 97.7% |
| both / knn | 98.1% |

Best full (full / knn) against best both (both / knn): full right and both wrong 18, full wrong and both right 109, McNemar χ² = 63.8.

## Combinations the full envelope gets wrong most often

| Combination (kick, snare, hats per beat, accent) | Signals | Full right | Both right |
|---|---|---|---|
| 1_3|none|4|0 as T | 20 | 5 | 11 |
| 1_3|none|4|1 as T/2 | 20 | 5 | 20 |
| 1_3|none|2|0 as T/2 | 20 | 6 | 18 |
| 1_3|none|2|1 as T/2 | 20 | 6 | 17 |
| 1_3|none|4|1 as T | 20 | 6 | 14 |
| 1_3|none|4|0 as T/2 | 20 | 8 | 20 |
| every|none|4|1 as T | 20 | 16 | 14 |
| 1_3|2_4|4|0 as T | 20 | 16 | 20 |
| 1_3|2_4|4|1 as T | 20 | 16 | 20 |
| 1|none|2|1 as T/2 | 20 | 16 | 16 |
| every|none|4|0 as T | 20 | 17 | 15 |
| every|2_4|4|1 as T | 20 | 17 | 20 |
| 1|none|4|1 as T/2 | 20 | 17 | 20 |
| every|2_4|4|0 as T | 20 | 18 | 20 |
| 1_3|none|2|1 as T | 20 | 18 | 20 |
| 1|none|4|0 as T/2 | 20 | 18 | 20 |
