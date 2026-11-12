# 2026-11-12: does splitting events by band tell the beat from its subdivision?

Issue #15. A **negative result, within its scope**: with the features, the two classifiers and the generator tested here, and under a fair control, separate envelopes for low hits, mid hits and high percussion add no information about the beat level beyond the full-band envelope. The pulse algorithm is not made more complex.

## Question

Two candidate levels, T and T/2. Which one is the beat? The question is whether the low band (kick), the mid band (snare) and the high band (hats), separately and in their joint pattern, carry information that the full-band onset envelope does not.

Nothing assumes that the kick marks the beat. The label comes from the grid the pattern was written in, and a classifier learns from data which features matter.

## Controlled pairs (`pairs.py`)

Each seed fixes the grid step T (0.5 to 1.0 s), the timbres of kick, snare and hat, the jitter and the noise. Every combination of the following is then rendered twice, once with the beat T and once with the beat T/2 (the same pattern in a grid twice as fast), four beats per bar:
- **kick:** every beat / 1 and 3 / 1, 3 and the "and" of 3 / 1 only;
- **snare:** none / 2 and 4 / every beat;
- **hats:** 2 or 4 per beat;
- **accent:** none / on beat 1.

20 seeds × 48 combinations × 2 labels = 1920 signals. Signals whose events are the same under both labels are ambiguous by construction. They are counted apart and not scored.

## Features and test (`run.py`)

The same features are taken from any envelope:
- correlation at T/4, T/2, 3T/4, T, 3T/2 and 2T;
- how uneven the event strengths are on the T/2 and T grids;
- how much the even T/2 slots differ from the odd ones.

**Bands:**
- low: 30 to 150 Hz;
- mid: 150 to 2500 Hz;
- high: 4 to 11 kHz;
- the joint pattern: cross-correlation of low with high and of mid with high, at 0, T/4 and T/2.

**Classifiers:** logistic regression and 7 nearest neighbours, written here. Cross-validation is grouped by seed (5 folds), so a seed's timbres are never in training and test at once. Best full-band against best band-based is compared with McNemar's test.

## Results

| Condition | Ambiguous | Full band, best | Bands + full, best | Full right, bands wrong / full wrong, bands right | McNemar χ² |
|---|---|---|---|---|---|
| Hats: the first hat of each beat louder (0.8 for the rest) | 0 | 93.4% | 98.1% | 18 / 109 | 63.8 |
| Hats all at one level | 80 | 95.1% | 97.8% | 17 / 67 | 28.6 |
| **Hats at one level, and at the same physical step under both labels** | 160 | **95.5%** | **95.7%** | 56 / 61 | **0.1** |

The first two rows show a large and significant gain from the bands. **It comes from the generator, not from the beat:**
- **Hat accent.** When the first hat of each beat is louder, the high band marks the beat directly. Real music may or may not do this.
- **Hat rate.** In the first two conditions the hats divide the beat into 2 or 4, so their physical step tells the label: T/8 occurs only with the beat T/2, and T/2 only with the beat T. That is a convention of the generator.

When both are removed (third row), the hats have the same level and the same step (T/2 or T/4) under both labels. The bands then add nothing: 95.5% against 95.7%, with 56 and 61 disagreements either way. The joint pattern of kick, snare and hats, with no hint from the hats, carries no information about the beat level beyond the full-band envelope.

## What this means

- **In this test, the bands did not help.** Where the full envelope could not tell T from T/2, the band features did not help either, unless the hats followed a beat convention.
- **The scope of that statement:**
  - these features: correlations at six lags, the unevenness of the grid, the even/odd contrast, and cross-correlations at three lags;
  - these two classifiers: logistic regression and 7 nearest neighbours;
  - this generator: four beats per bar, the T and T/2 grids, these kick, snare and hat patterns, and 20 seeds of timbres.
  Other features, a stronger model, other meters or real music could still find band information. That has not been tested.
- **A hat convention can be a real cue.** For example, hats that divide the beat into 2 or 4, or a louder hat on the beat. Whether real music follows it is an empirical question, and it can only be answered on real recordings with verified beat labels. This joins the open stage of issue #15.
- **No candidate was made, and no final set was run.** The plan was to run one only if information appeared.

## Reproduce

```
python run.py dev                                       # hat accent 0.8
PTS_HAT_ACCENT=1.0 python run.py dev                    # equal hats
PTS_HAT_ACCENT=1.0 PTS_HAT_BALANCE=1 python run.py dev  # equal hats, same step under both labels
```

Each writes `results_<condition>.md/.json`. The features are cached in `features_<condition>.json` (features only, no audio).
