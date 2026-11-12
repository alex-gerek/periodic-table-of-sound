# 2026-11-12: is the pulse the beat, or its bar, or its eighths?

Issue #15. The confirmation test (#7, #13) says *whether* a track repeats. This experiment asks whether the pulse rule picks the right *level* of the repetition: the beat, not its subdivision and not its bar.

The old metric hid the problem. It counted the beat or any multiple of it (2, 3 or 4 beats) as right, so "0% wrong periods" included bars returned as pulses.

`bench.py` holds the signals, the metric and both rules; `run.py` runs them. **Nothing in `pts/` has been replaced yet:** whether the new rule becomes the pulse rule is a separate decision.

## Metric

Each returned period is compared with the known beat (ratio = found / beat):

| Class | Ratio |
|---|---|
| exact | within ±3% of 1 |
| precision | the right level, but off by 3 to 10% |
| subdivision | 1/2, 1/3 or 1/4 of the beat (±3%) |
| multiple | 2 to 8 beats (±3%) |
| other | anything else |
| none | no period returned |

## Signals

A new generator (`groove()` in `bench.py`):
- **Meters** of 2 to 7 beats, and **compound meters** (2, 3 or 4 dotted-quarter beats of three eighths).
- **Hats** on every 8th, triplet or 16th; swing on some 8ths.
- **An accent** on the downbeat.
- **Four patterns:** a kick on every beat, backbeat, oom-pah, and boom-bap with kicks on some off-beats.
- Timing jitter up to 20 ms, and noise from 30 dB down to 0 dB SNR.

Every beat carries a strong event (kick or snare) and every subdivision a weak one (hat), so the beat is well defined.

| Set | Contents | Use |
|---|---|---|
| **Development** | seeds 0–199, and the 120 positives of the confirmation experiment (already investigated) | developing the rule; regression tests |
| **Final** | seeds 50000–50199 | run **once**, after the rule and its constants were fixed |
| **Real** | 13 drum stems | the level each rule returns; scored only against verified labels |

## The rules

**Old** (`pts` today): the comb score over four multiples of an *integer* lag, then the shortest peak whose comb is within 0.9 of the best.

**New** (candidate, `rule_new()`):
1. The onset envelope of the **strong events only** (40 Hz to 2.5 kHz: kick and snare bodies; hats and cymbals sit above).
2. Peaks of its autocorrelation that are the highest within ±5% of their lag, so a shoulder of a widened peak is not taken.
3. Each period is **refined from its first four multiples** instead of being read from one peak.
4. From the shortest: the first period whose comb over four multiples reaches **0.5 of the best comb** and that passes `confirm_period()`.

Constants chosen on the development set only:
- The comb share is 0.5, the middle of a plateau from 0.4 to 0.6.
- The band edge is 2.5 kHz. 4 kHz scored one example more, but real hats reach below 4 kHz.

## What was wrong before

The development set reproduced the three wrong periods of the confirmation experiment:

| Example | Old | Cause | New |
|---|---|---|---|
| click train, seed 29, 196 BPM | 5 beats | the comb checks multiples of an integer lag with ±1 frame: the beat peak sits at lag 60 while the beat is 61.3 frames, so its 2nd to 4th multiples miss by 2.6 to 5.2 frames; the 5-beat lag lands on its multiples by chance | exact |
| groove, seed 1001, 180 BPM | 5 beats | the same | exact |
| click train, seed 58, 62 BPM | 3.2% off | the period was read from one peak, widened by jitter | exact (0.9%) |

Two more causes appeared on the new signals:
- **An interval is not a period.** In boom-bap, the time from a beat to an off-beat kick (0.75 beat) passes the confirmation test, but it does not repeat at its multiples. Step 4 rejects it.
- **The bar is stronger than the beat.** With an accented downbeat, the autocorrelation at the bar is genuinely higher than at the beat, so "the shortest peak within 0.9 of the best" returns the bar. The new rule asks for the shortest level that repeats and is confirmed, instead of the highest one.

## Results

### Final set (held out, 200 signals)

| Rule | exact | precision | subdivision | multiple | other | none |
|---|---|---|---|---|---|---|
| Old | 160 (80%) | 0 | 0 | 40 | 0 | 0 |
| **New** | **190 (95%)** | 0 | 1 | 9 | 0 | 0 |

- **Improved: 34. Worsened: 4.** Each worsened signal was exact with the old rule and is now 2 beats (three of them) or the eighths (one). They are listed in `results_final.md`.
- **The new rule's errors cluster in oom-pah:** 6 of its 10 errors, 4 of them in 5/4. With a kick on 1 and soft snares on the other beats, the strong-band envelope repeats most clearly at 2 or 5 beats.
- **Development gave 98.4% (315 of 320) and the final set 95%.** The gap is the optimism of choosing constants on the development set, and the final number is the one to quote.

### Development set (320 signals)

| Rule | exact | precision | subdivision | multiple | other | none |
|---|---|---|---|---|---|---|
| Old | 251 | 1 | 0 | 68 | 0 | 0 |
| New | 315 | 0 | 1 | 4 | 0 | 0 |

Improved 66, worsened 2: boom-bap seed 106 (now the eighths) and click train seed 40 (now 2 beats). Both are kept as `xfail` tests.

### Real drum stems

No real track has a verified beat yet. The tempo in a Suno prompt is not a label, because a generation can differ from it. `labels.json` marks two tracks as **ambiguous** (174 BPM breakbeat: 174 or 87; the jig retake: a binary groove, the beat or its half) and the rest as **unverified**.

| Track | Old | New | Reading |
|---|---|---|---|
| 10 of 13 tracks | | | the same level |
| 80 BPM retake (boom-bap) | 80.5 BPM | 160.9 BPM | probably **worse**: the eighths, the same error as seeds 106 and 50134 |
| 174 BPM (ambiguous) | 43.5 BPM, the bar | 174.0 BPM | the new rule gives an accepted reading; the old one gave none |
| 3/4 waltz | 60.8 BPM, the bar | 181.9 BPM | probably better: the meter README reads 182.4 BPM by hand, but this is not verified |

A real score needs verified labels: a published beat annotation, or a check that does not use these detectors.

## Version 2 and a second held-out set

After its run, the first final set (seeds 50000–50199) became development data. Its four worsened signals have two causes.

| Signals | Cause | Version 2 |
|---|---|---|
| 50080, 50130, 50188 | **Noise breaks the stability test.** In heavy noise (SNR 0 to 6 dB, 20 ms jitter) the beat is found: comb 0.80 to 0.93 of the best, 6.0 to 6.4 σ. But one half of the track reaches only 3.0 to 3.5 σ against 3.54, and the next confirmed level, 2 beats, wins. | **Fixed.** A level that fails only the stability test is accepted when a whole multiple of it (2 to 8) is confirmed. A divisor of a confirmed period is not a chance peak. |
| 50134 (and 106 in development) | **A quieter kick on the "and".** In boom-bap the off-beat kick makes the half beat a real period of strong events. Its strong–weak structure is the same as that of a beat with a 2-beat bar. | **Not fixed.** Two measures were tried and rejected: the ratio r(T)/r(2T) and the share of grid slots that hold an event. Both overlap between true beats and these half beats, and the second one cost 31 to 72 correct beats. |

The remaining errors in development are mostly oom-pah: the beat is carried by soft snares and the bar by an accented kick. In 5/4 the beat is confirmed but its comb is 0.48 of the best, below the 0.5 rule. In 2/4 the beat reaches only 3.9 σ. The 0.5 rule was not moved: it sits on a plateau, and moving it for these cases would be fitting.

`rule_v2.py` holds version 2. Version 1 in `bench.py` is unchanged, because the Ballroom adapter is pinned to it.

**Development data** (520 signals: seeds 0–199, the 120 investigated examples, seeds 50000–50199):

| Rule | exact | subdivision | multiple | precision |
|---|---|---|---|---|
| Old | 411 | 0 | 108 | 1 |
| v1 | 505 | 2 | 13 | 0 |
| v2 | 510 | 2 | 8 | 0 |

### Second held-out set: a new generator

`holdout_b.py` was written for this check and committed with v2 before either was run (commit `fc24348`):

| File | SHA-256 (line endings normalised) |
|---|---|
| `bench.py` | `283b1c1d…` |
| `rule_v2.py` | `c292fc29…` |
| `holdout_b.py` | `2762ff0e…` |

It differs from the development generator:
- **Timbres:** a kick with a click, rimshot or clap, and a closed hat, shaker or ride.
- **Patterns:** rock (kick on 1 and 3 and on the "and" of 3), march, disco and waltz.
- **Sound:** pink or white noise, a reverb tail, slow level changes, 15 to 45 s.

Seeds 70000–70199. It was run once.

| Rule | exact | subdivision | multiple | other |
|---|---|---|---|---|
| Old | 153 (76.5%) | 0 | 46 | 1 |
| v1 | 188 (94%) | 6 | 6 | 0 |
| **v2** | **188 (94%)** | 7 | 5 | 0 |

- **Old → v2:** 42 improved, **7 worsened.** All seven are rock: the kick on the "and" of 3 turns the half beat into a period of strong events, the same limitation as boom-bap above. The old rule had them right.
- **v1 → v2:** 1 improved, 1 worsened (70100, rock). Version 2 gives **nothing measurable** over version 1 on independent data; its gain in development (505 → 510) did not carry over.
- **The errors of v2:** 7 half beats (rock) and 5 multiples (waltz: kick on 1, rimshot on the others, the same as oom-pah). Disco and march are 100%.
- The two families of error the development data predicted are the two that remain. No new kind of error appeared.

### Still open

- **Real recordings with verified labels.** No real track is scored yet. The Ballroom adapter (`experiments/2026-11-12_ballroom_eval/`, internal) is ready, but its use waits until the terms are clear.
- **A kick on the "and".** Rock and boom-bap patterns are the main error of both candidates. The old rule gets them right, because it prefers the higher comb.

## Regression tests

`tests/test_beat_level.py` covers:
- the metric;
- the 5-beat error (seeds 29 and 1001);
- the precision error (seed 58);
- the off-beat interval (seeds 55, 59, 118 and 172);
- four bars-for-beats;
- the two known errors of the new rule, as strict `xfail` tests.

## Also fixed

`confirm_period()` raised `ValueError` on a negative candidate period. A non-positive or non-finite period is now "no candidate". This came up during development, from an unclamped parabolic shift in a prototype.

## Limits

- **The synthetic beat is defined by strong events,** and the new rule reads strong events. It can therefore be expected to do well here. Real music sometimes marks the beat with hats or a ride, or plays kicks on the eighths, as on the 80 BPM retake.
- **The 2.5 kHz edge assumes** that hats and cymbals are above it and kick and snare bodies below.
- **The final set comes from the same generator family** as the development set, with new seeds. A generator that was not used in development would be a stronger test.
