# Beat level: development set

320 signals with a known beat. A level counts as *exact* within ±3%, as a *precision* error within ±10%, as a *subdivision* at 1/2, 1/3 or 1/4 of the beat, and as a *multiple* at 2 to 8 beats.

| Rule | exact | precision | subdivision | multiple | other | none |
|---|---|---|---|---|---|---|
| old | 251 | 1 | 0 | 68 | 0 | 0 |
| new | 315 | 0 | 1 | 4 | 0 | 0 |

## Old → new

| Old \ New | exact | precision | subdivision | multiple | other | none |
|---|---|---|---|---|---|---|
| **exact** | 249 |  | 1 | 1 |  |  |
| **precision** | 1 |  |  |  |  |  |
| **multiple** | 65 |  |  | 3 |  |  |

**Improved:** 66. **Worsened:** 2.

### Worsened (exact before, not after)

| Signal | Beat | Old | New |
|---|---|---|---|
| 4 beats, hats in 2s, seed 106, boombap | 0.7773 s | 1.001 | subdivision (0.500) |
| investigated: click_train, seed 40 | 0.7825 s | 0.990 | multiple (2.006) |

## By group

| Group | Signals | Old exact | New exact | New errors |
|---|---|---|---|---|
| 2 beats, hats in 2s | 13 | 11 | 13 | – |
| 2 beats, hats in 3s | 7 | 5 | 7 | – |
| 2 beats, hats in 4s | 7 | 7 | 7 | – |
| 3 beats, hats in 2s | 13 | 9 | 13 | – |
| 3 beats, hats in 3s | 8 | 8 | 8 | – |
| 3 beats, hats in 4s | 7 | 4 | 7 | – |
| 4 beats, hats in 2s | 11 | 8 | 10 | subdivision 1 |
| 4 beats, hats in 3s | 11 | 8 | 11 | – |
| 4 beats, hats in 4s | 4 | 4 | 4 | – |
| 5 beats, hats in 2s | 12 | 12 | 12 | – |
| 5 beats, hats in 3s | 10 | 8 | 10 | – |
| 5 beats, hats in 4s | 7 | 6 | 7 | – |
| 6 beats, hats in 2s | 8 | 8 | 8 | – |
| 6 beats, hats in 3s | 6 | 5 | 6 | – |
| 6 beats, hats in 4s | 14 | 12 | 13 | multiple 1 |
| 7 beats, hats in 2s | 10 | 8 | 10 | – |
| 7 beats, hats in 3s | 9 | 9 | 9 | – |
| 7 beats, hats in 4s | 9 | 9 | 9 | – |
| compound 2x3 eighths | 9 | 6 | 9 | – |
| compound 3x3 eighths | 9 | 6 | 9 | – |
| compound 4x3 eighths | 16 | 14 | 16 | – |
| investigated: click_train | 60 | 47 | 57 | multiple 3 |
| investigated: groove | 60 | 37 | 60 | – |

## Every error of the new rule

| Signal | Beat | New | Old |
|---|---|---|---|
| 4 beats, hats in 2s, seed 106, boombap | 0.7773 s | subdivision (0.500) | exact (1.001) |
| 6 beats, hats in 4s, seed 138, oompah | 0.4333 s | multiple (1.996) | multiple (2.991) |
| investigated: click_train, seed 11 | 0.5703 s | multiple (2.004) | multiple (1.999) |
| investigated: click_train, seed 20 | 0.3857 s | multiple (2.994) | multiple (2.993) |
| investigated: click_train, seed 40 | 0.7825 s | multiple (2.006) | exact (0.990) |
