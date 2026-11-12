# Beat level, old vs v1 vs v2: development data

520 signals.

| Rule | exact | precision | subdivision | multiple | other | none |
|---|---|---|---|---|---|---|
| old | 411 | 1 | 0 | 108 | 0 | 0 |
| v1 | 505 | 0 | 2 | 13 | 0 | 0 |
| v2 | 510 | 0 | 2 | 8 | 0 | 0 |

## old → v2: improved 102, worsened 3

| Worsened | Beat | old | v2 |
|---|---|---|---|
| seed 106, boombap, 4 beats, subdivision 2 | 0.7773 s | exact | subdivision (0.500) |
| investigated click_train 40 | 0.7825 s | exact | multiple (2.006) |
| seed 50134, boombap, 3 beats, subdivision 2 | 0.6160 s | exact | subdivision (0.500) |

## v1 → v2: improved 5, worsened 0


## By pattern (exact)

| Pattern | Signals | old | v1 | v2 |
|---|---|---|---|---|
| backbeat | 98 | 81 | 97 | 98 |
| boombap | 88 | 73 | 84 | 85 |
| click_train | 60 | 47 | 57 | 59 |
| four | 108 | 98 | 108 | 108 |
| groove | 60 | 37 | 60 | 60 |
| oompah | 106 | 75 | 99 | 100 |

## Every error of v2

| Signal | Beat | v2 | old |
|---|---|---|---|
| seed 106, boombap, 4 beats, subdivision 2 | 0.7773 s | subdivision (0.500) | exact (1.001) |
| seed 138, oompah, 6 beats, subdivision 4 | 0.4333 s | multiple (1.996) | multiple (2.991) |
| investigated click_train 40 | 0.7825 s | multiple (2.006) | exact (0.990) |
| seed 50065, oompah, 2 beats, subdivision 2 | 0.3825 s | multiple (2.000) | multiple (4.003) |
| seed 50070, oompah, 5 beats, subdivision 2 | 0.3336 s | multiple (5.004) | multiple (4.999) |
| seed 50075, oompah, 5 beats, subdivision 3 | 0.3987 s | multiple (4.999) | multiple (4.998) |
| seed 50079, oompah, 6 beats, subdivision 4 | 0.3637 s | multiple (2.007) | multiple (2.013) |
| seed 50083, oompah, 5 beats, subdivision 2 | 0.3010 s | multiple (2.984) | multiple (4.997) |
| seed 50134, boombap, 3 beats, subdivision 2 | 0.6160 s | subdivision (0.500) | exact (0.999) |
| seed 50177, boombap, 2 beats, subdivision 2 | 0.5065 s | multiple (2.006) | multiple (1.987) |
