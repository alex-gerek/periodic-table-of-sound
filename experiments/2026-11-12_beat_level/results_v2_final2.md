# Beat level, old vs v1 vs v2: second held-out set (new generator)

200 signals.

| Rule | exact | precision | subdivision | multiple | other | none |
|---|---|---|---|---|---|---|
| old | 153 | 0 | 0 | 46 | 1 | 0 |
| v1 | 188 | 0 | 6 | 6 | 0 | 0 |
| v2 | 188 | 0 | 7 | 5 | 0 | 0 |

## old → v2: improved 42, worsened 7

| Worsened | Beat | old | v2 |
|---|---|---|---|
| seed 70011, rock, 3 beats compound, subdivision 3 | 0.8846 s | exact | subdivision (0.500) |
| seed 70023, rock, 3 beats compound, subdivision 3 | 0.7140 s | exact | subdivision (0.500) |
| seed 70052, rock, 7 beats, subdivision 3 | 0.9002 s | exact | subdivision (0.500) |
| seed 70089, rock, 4 beats compound, subdivision 3 | 1.2261 s | exact | subdivision (0.500) |
| seed 70100, rock, 7 beats, subdivision 3 | 0.7270 s | exact | subdivision (0.500) |
| seed 70114, rock, 3 beats compound, subdivision 3 | 0.6678 s | exact | subdivision (0.500) |
| seed 70195, rock, 3 beats, subdivision 2 | 0.9878 s | exact | subdivision (0.500) |

## v1 → v2: improved 1, worsened 1

| Worsened | Beat | v1 | v2 |
|---|---|---|---|
| seed 70100, rock, 7 beats, subdivision 3 | 0.7270 s | exact | subdivision (0.500) |

## By pattern (exact)

| Pattern | Signals | old | v1 | v2 |
|---|---|---|---|---|
| disco | 52 | 50 | 52 | 52 |
| march | 54 | 36 | 54 | 54 |
| rock | 47 | 35 | 40 | 40 |
| waltz | 47 | 32 | 42 | 42 |

## Every error of v2

| Signal | Beat | v2 | old |
|---|---|---|---|
| seed 70000, waltz, 3 beats, subdivision 2 | 0.3023 s | multiple (2.988) | multiple (3.002) |
| seed 70011, rock, 3 beats compound, subdivision 3 | 0.8846 s | subdivision (0.500) | exact (1.000) |
| seed 70016, waltz, 6 beats, subdivision 4 | 0.3245 s | multiple (1.994) | multiple (1.990) |
| seed 70023, rock, 3 beats compound, subdivision 3 | 0.7140 s | subdivision (0.500) | exact (1.000) |
| seed 70032, waltz, 2 beats, subdivision 2 | 0.4866 s | multiple (1.997) | multiple (1.986) |
| seed 70052, rock, 7 beats, subdivision 3 | 0.9002 s | subdivision (0.500) | exact (1.000) |
| seed 70089, rock, 4 beats compound, subdivision 3 | 1.2261 s | subdivision (0.500) | exact (1.000) |
| seed 70100, rock, 7 beats, subdivision 3 | 0.7270 s | subdivision (0.500) | exact (0.999) |
| seed 70114, rock, 3 beats compound, subdivision 3 | 0.6678 s | subdivision (0.500) | exact (1.000) |
| seed 70126, waltz, 6 beats, subdivision 4 | 0.4634 s | multiple (2.013) | multiple (2.016) |
| seed 70127, waltz, 6 beats, subdivision 4 | 0.3024 s | multiple (5.996) | multiple (5.990) |
| seed 70195, rock, 3 beats, subdivision 2 | 0.9878 s | subdivision (0.500) | exact (1.000) |
