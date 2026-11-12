# 2026-11-12: when is a period real?

Issue #7. The peak rule always returns its best candidate. On 20 recordings of white noise it returned a period every time, with correlations of only 0.008 to 0.045. A best peak is not evidence that a signal repeats.

The candidate and the proof are now separate. `confirm_period()` in `pts/periodicity.py` marks each candidate as confirmed or not and records why:

1. **Significance.** Without periodicity, the autocorrelation of a track at a long lag is noise. Its standard deviation follows from Bartlett's formula, using the track's own short-lag correlation (below the search range), which describes how smooth the track is. The candidate's peak must stand at least `Z_MIN` standard deviations above zero.
2. **Repetitions.** The period must fit into the track at least `MIN_REPS` times.
3. **Stability.** The same lag must stay significant in each half of the track, at `Z_MIN / √2`.

Run `python run.py`; the numbers are in `results.md` and `results.json`.

## Design

| Set | Non-periodic (negatives) | Periodic (positives) |
|---|---|---|
| **Training** (seeds 0–59) | white noise, pink noise, random clicks, random drum hits | click trains at 60–200 BPM with timing jitter, dropped beats and noise down to −5 dB SNR |
| **Test** (seeds 1000–1059) | the same four families with new seeds | **another generator**: grooves with kick, snare on 2 and 4, swung hats, humanised timing and noise |
| **Real** | the 12 real drum stems cut into pieces of random length (80–250 ms) and shuffled: the sounds stay, the beat is destroyed | the 12 real drum stems |

The thresholds were swept on the training set only. The chosen pair has the most true detections with at most 1% false detections: **5 σ and 4 repetitions**. It was then applied unchanged to the test set and the real material.

## Result

| Set | False detections on non-periodic signals | Misses on periodic signals | Confirmed with a wrong period |
|---|---|---|---|
| Training | 0.0% (0 of 60) | 3.3% (2 of 60) | 1.7% |
| **Test (held out)** | **0.0%** (0 of 60) | **0.0%** (0 of 60) | 0.0% |
| **Real drum stems (held out)** | **0.0%** (0 of 12) | **0.0%** (0 of 12) | 0.0% |
| Before (bare peak rule) | 100% on every set | | |

- **Noise:** median 1.8 to 2.1 σ. **Rhythm:** median 19 to 25 σ, and 32 to 55 σ on the real stems. The gap is wide.
- **The margin is narrow in one place.** The noisiest negative, random clicks, reached 5.2 σ once and was rejected by the stability test (3.2 σ in its weaker half). The three tests are meant to work together.
- **The repetitions test did not decide anything here**, because every signal in this experiment is long (20 to 60 s). It is checked separately in `tests/test_confirmation.py`, on a short signal.

## What it changes in earlier results

Re-running the earlier experiments with confirmation leaves every number the same and adds a verdict:

- **Confirmed:** the pulse on every track (42 to 116 σ), the meter (21 to 45 σ), and the sidechain pump on GRAVITY and Pure voltage (18 to 42 σ).
- **Not confirmed, and this is correct:** the sidechain on Metro (4.0 σ). The earlier verdict "no pump" is now backed by the test.
- **Not confirmed, which corrects earlier claims:**
  - **Loop and Repetition, on every track (0.2 to 3.6 σ).** This agrees with the earlier note that Loop is not yet a well-posed element.
  - **The harmonic rhythm on three of seven tempo tracks**: the track requested at 80 BPM (122 BPM), the 80 BPM retake, and 174 BPM. The claim that it nests "at every tempo" was too strong. It holds on the four tracks where it is confirmed. The tempo-series README, the roadmap, the article, the README and the table are corrected.
  - **The subdivision on GRAVITY** (10.4 σ overall, but not stable in both halves).

## Limits

- The noise model assumes that a non-periodic track has only short-range correlation. Slow trends that are not periodic, such as a crescendo, are not part of the training set yet.
- The thresholds come from synthetic signals and twelve real stems. They should be checked again on other genres.
