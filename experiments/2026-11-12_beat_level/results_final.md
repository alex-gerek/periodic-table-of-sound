# Beat level: final (held out) set

200 signals with a known beat. A level counts as *exact* within ±3%, as a *precision* error within ±10%, as a *subdivision* at 1/2, 1/3 or 1/4 of the beat, and as a *multiple* at 2 to 8 beats.

| Rule | exact | precision | subdivision | multiple | other | none |
|---|---|---|---|---|---|---|
| old | 160 | 0 | 0 | 40 | 0 | 0 |
| new | 190 | 0 | 1 | 9 | 0 | 0 |

## Old → new

| Old \ New | exact | precision | subdivision | multiple | other | none |
|---|---|---|---|---|---|---|
| **exact** | 156 |  | 1 | 3 |  |  |
| **multiple** | 34 |  |  | 6 |  |  |

**Improved:** 34. **Worsened:** 4.

### Worsened (exact before, not after)

| Signal | Beat | Old | New |
|---|---|---|---|
| 5 beats, hats in 4s, seed 50080, oompah | 0.9980 s | 0.996 | multiple (2.003) |
| 5 beats, hats in 2s, seed 50130, boombap | 0.4011 s | 1.017 | multiple (2.006) |
| 3 beats, hats in 2s, seed 50134, boombap | 0.6160 s | 0.999 | subdivision (0.500) |
| 3 beats, hats in 3s, seed 50188, backbeat | 0.3619 s | 0.998 | multiple (2.003) |

## By group

| Group | Signals | Old exact | New exact | New errors |
|---|---|---|---|---|
| 2 beats, hats in 2s | 16 | 11 | 14 | multiple 2 |
| 2 beats, hats in 3s | 4 | 2 | 4 | – |
| 2 beats, hats in 4s | 7 | 4 | 7 | – |
| 3 beats, hats in 2s | 16 | 13 | 15 | subdivision 1 |
| 3 beats, hats in 3s | 4 | 3 | 3 | multiple 1 |
| 3 beats, hats in 4s | 14 | 9 | 14 | – |
| 4 beats, hats in 2s | 15 | 11 | 15 | – |
| 4 beats, hats in 3s | 9 | 9 | 9 | – |
| 4 beats, hats in 4s | 6 | 5 | 6 | – |
| 5 beats, hats in 2s | 12 | 9 | 9 | multiple 3 |
| 5 beats, hats in 3s | 8 | 7 | 7 | multiple 1 |
| 5 beats, hats in 4s | 7 | 7 | 6 | multiple 1 |
| 6 beats, hats in 2s | 14 | 11 | 14 | – |
| 6 beats, hats in 3s | 7 | 7 | 7 | – |
| 6 beats, hats in 4s | 9 | 8 | 8 | multiple 1 |
| 7 beats, hats in 2s | 7 | 7 | 7 | – |
| 7 beats, hats in 3s | 4 | 3 | 4 | – |
| 7 beats, hats in 4s | 10 | 9 | 10 | – |
| compound 2x3 eighths | 12 | 10 | 12 | – |
| compound 3x3 eighths | 11 | 10 | 11 | – |
| compound 4x3 eighths | 8 | 5 | 8 | – |

## Every error of the new rule

| Signal | Beat | New | Old |
|---|---|---|---|
| 2 beats, hats in 2s, seed 50065, oompah | 0.3825 s | multiple (2.000) | multiple (4.003) |
| 5 beats, hats in 2s, seed 50070, oompah | 0.3336 s | multiple (5.004) | multiple (4.999) |
| 5 beats, hats in 3s, seed 50075, oompah | 0.3987 s | multiple (4.999) | multiple (4.998) |
| 6 beats, hats in 4s, seed 50079, oompah | 0.3637 s | multiple (2.007) | multiple (2.013) |
| 5 beats, hats in 4s, seed 50080, oompah | 0.9980 s | multiple (2.003) | exact (0.996) |
| 5 beats, hats in 2s, seed 50083, oompah | 0.3010 s | multiple (2.984) | multiple (4.997) |
| 5 beats, hats in 2s, seed 50130, boombap | 0.4011 s | multiple (2.006) | exact (1.017) |
| 3 beats, hats in 2s, seed 50134, boombap | 0.6160 s | subdivision (0.500) | exact (0.999) |
| 2 beats, hats in 2s, seed 50177, boombap | 0.5065 s | multiple (2.006) | multiple (1.987) |
| 3 beats, hats in 3s, seed 50188, backbeat | 0.3619 s | multiple (2.003) | exact (0.998) |
