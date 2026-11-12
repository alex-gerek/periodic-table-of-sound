# 2026-11-12: when is a period real?

Issue #7. The peak rule always returns its best candidate. On 20 recordings of white noise it returned a period every time, with correlations of only 0.008 to 0.045. A best peak is not evidence that a signal repeats.

The candidate and the proof are now separate. `confirm_period()` in `pts/periodicity.py` marks each candidate as confirmed or not and records why:

1. **Significance.** Without periodicity, the autocorrelation of a track at a long lag is noise. Its standard deviation follows from Bartlett's formula, using the track's own short-lag correlation (below the search range), which describes how smooth the track is. The candidate's peak must stand at least `Z_MIN` standard deviations above zero.
2. **Repetitions.** The period must fit into the track at least `MIN_REPS` times.
3. **Stability.** The same lag must stay significant in each half of the track, at `Z_MIN / √2`.
4. **Return** (added after review). A period means the track becomes unlike itself and then like itself again. The correlation must fall after half the lag and rise back at the lag: the peak must stand `Z_MIN` standard deviations above the lowest correlation between lag/2 and lag.

Run `python run.py`; the numbers are in `results.md` and `results.json`.

## Why the fourth test

Review found that **a single smooth burst was confirmed as periodic**: one swell in 100 s gave a "period" at 14 σ. The autocorrelation of a smooth swell is high at every short lag and only falls. Tests 1 to 3 measure how high the peak is, not whether the track ever stops resembling itself, so a ripple on that slope passed all three.

The valley is searched between lag/2 and the lag, not from lag 0. An onset envelope dips at its shortest lags by construction, and a valley searched from lag 0 gave smooth swells up to 10 σ. Between lag/2 and the lag:
- smooth swells reach at most **1.6 σ** and crescendos at most **2.0 σ**;
- every periodic signal reaches at least **6.3 σ** (click trains) and **10.9 σ** (grooves).

## Design

| Set | Non-periodic (negatives) | Periodic (positives) |
|---|---|---|
| **Training** (seeds 0–59) | white noise, pink noise, random clicks, random drum hits, **smooth swells** (noise under one to three slow bell-shaped envelopes), **crescendos** | click trains at 60–200 BPM with timing jitter, dropped beats and noise down to −5 dB SNR |
| **Test** (seeds 1000–1059) | the same six families with new seeds | **another generator**: grooves with kick, snare on 2 and 4, swung hats, humanised timing and noise |
| **Real** | the 12 real drum stems cut into pieces of random length (80–250 ms) and shuffled: the sounds stay, the beat is destroyed | the 12 real drum stems |

The thresholds were swept on the training set only. The chosen pair has the most true detections with at most 1% false detections. With the two new families in the training set, the same pair came out again: **5 σ and 4 repetitions**. It was then applied unchanged to the test set and the real material.

## Result

| Set | False detections on non-periodic signals | Misses on periodic signals | Confirmed with a wrong period |
|---|---|---|---|
| Training | 0.0% (0 of 60) | 1.7% (1 of 60) | 3.3% |
| **Test (held out)** | **0.0%** (0 of 60) | **0.0%** (0 of 60) | 1.7% |
| **Real drum stems (held out)** | **0.0%** (0 of 12) | **0.0%** (0 of 12) | **not evaluated** |
| Before #7 (bare peak rule) | 100% on every set | | |

- **Smooth swells and crescendos:** without the return test, 25 of 40 (training and test) are confirmed; with it, 0.
- **Noise:** median 1.5 to 2.3 σ. **Rhythm:** median 19 to 24 σ, and 32 to 55 σ on the real stems.
- **The margin is narrow in one place.** The noisiest negative, random clicks, reached 5.2 σ once and was rejected by the stability test (3.2 σ in its weaker half). The tests are meant to work together. The return test alone does not separate noise from rhythm: noise can reach 7.8 σ on it, because its valley is noise too.
- **A wrong period can only be judged where the true beat is known.** That holds for the synthetic sets, where a detection counts as right if it is the beat or 2, 3 or 4 beats. The real stems have no independent beat labels, so the column says *not evaluated* instead of a rate. An earlier version counted every real detection as right by default and reported 0%.
- **The numbers differ slightly from the first version** (training misses 3.3% → 1.7%, wrong periods 1.7% → 3.3% in training and 0% → 1.7% in test). Each seed now draws a different noise family first, so the positives drawn after it are different signals too.
- **The repetitions test did not decide anything here**, because every signal in this experiment is long (20 to 60 s). It is checked separately in `tests/test_confirmation.py`, on a short signal.

## What it changes in earlier results

The earlier experiments were run again with all four tests. Every period and every number stays the same. Reports now show a candidate that is not confirmed in italics, with the reason, and leave it out of their counts.

- **Confirmed:** the pulse on every track (42 to 116 σ), the meter (21 to 45 σ), and the sidechain pump on GRAVITY and Pure voltage (18 to 42 σ). In the meter test, the chord changes of the waltz (8 σ) and of the 6/8 retake (9 σ) are confirmed.
- **Not confirmed, and this is correct:** the sidechain on Metro (4.0 σ). The earlier verdict "no pump" is now backed by the test.
- **Not confirmed, which corrects earlier claims:**
  - **Loop and Repetition, on every track (0.2 to 3.6 σ).** This agrees with the earlier note that Loop is not yet a well-posed element.
  - **The harmonic rhythm on three of seven tempo tracks**: the track requested at 80 BPM (122 BPM), the 80 BPM retake, and 174 BPM. The claim that it nests "at every tempo" was too strong. It holds on the four tracks where it is confirmed.
  - **The subdivision on GRAVITY** (10.4 σ overall, but not stable in both halves).
  - **The chord changes in the first 6/8 take** (2.0 σ). The meter README already called this peak weak and the track inconclusive.
- **Changed by the return test:** the free Loop search on GRAVITY (0.99 s, the two-beat drum pattern) was confirmed by tests 1 to 3 at 11 σ. It is now rejected: the spectral similarity hardly falls between 0.5 and 0.99 s, because the one-beat repetition is nearly as strong. This is a limit of the test, described below. It does not change a conclusion, because Loop was already not a well-posed element.

## Limits

- **A multiple of a strong shorter period can be rejected** when the track is smooth between them, as with the free Loop search above. The shorter period itself is found and confirmed. Sharp onset envelopes, such as drums, always have a valley between beats.
- The thresholds come from synthetic signals and twelve real stems. They should be checked again on other genres.
