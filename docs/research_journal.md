# Research journal: the journey

The chronological record of the research: for each step, the question, the expectation, what was tried, what failed, and why the next step was taken. Failed and rejected attempts stay in the record. Held-out sets are run once, after the method is fixed, and a set that has been inspected is marked as development data from then on.

## Entries

The entries below were **reconstructed on 2026-11-12** from commits, experiment READMEs and the working session, after the steps had run. Times are not given, because they were not recorded. Hypotheses are stated as they were written in the issues before the runs.

### 2026-11-12-confirm-001: is a best peak a period? (issue #7)

- **Before:** the peak rule always returns a candidate. *Hypothesis:* a test against the noise level of the autocorrelation separates real periods from chance peaks. *Check:* train the thresholds on one set, then apply them unchanged to other generators and to real stems.
- **Runs:**
  - first version, rejected: the stems were downsampled, which stretched time by ×1.088;
  - second version, rejected: the shuffle control cut pieces of one fixed length (120 ms), which built a 120 ms grid;
  - final version: native sample rate, and pieces of random length with fades.
- **Outcome:** 0% false and 0% missed periods on the held-out sets, against 100% false with the bare rule. Earlier claims were corrected: the harmonic rhythm is confirmed on 4 of 7 tracks, and Loop and Repetition are never confirmed.
- **Use:** `confirm_period()` in `pts/`. PR #9.

### 2026-11-12-collider-001: runs racing the recipe; random controls (issue #8)

- **Outcome:** each run works on a snapshot of the recipe and its version, and the noise is seeded. Two renders agreed to 1.2·10⁻⁷. Checked by moving a slider in the middle of a run. PR #11.

### 2026-11-12-collider-002: false Variation at 150 BPM in 3/4 (issue #10)

- **Before:** the issue blamed the synthesis.
- **What happened:** four causes, found one after another:
  1. **The same hit rendered differently** depending on its place in a 128-frame block. Snapping the start to a whole sample did not help; removing the pitch sweep did. Fix: each hit is rendered once and copied.
  2. **The bar grid drifted.** After fix 1 the bars were equal sample for sample, but Variation was still reported. Fix: a Theil–Sen fit.
  3. **The pulse rule picked the bar** on the new sound, because the onset curve was spiky. Fix: a ±15 ms triangle.
  4. **The meter median took the upper middle value.** Fix: a true median.
- **Threshold:** a one-beat fill fell below the threshold of 0.1. The new floor (0.0035) and the weakest fill (0.081) were measured, and the threshold was set to 0.02.
- **Interrupted:** one comparison run timed out in the browser. It was repeated in the background, with its state kept in the page.
- **Outcome:** 359 of 360 settings pass, up from 304. The one failure is kept as a known limit. PR #12.

### 2026-11-12-confirm-002: a single smooth burst confirmed as a period (issue #13, review)

- **Before:** review reported three problems:
  - one swell in 100 s was confirmed at 14 σ;
  - reports ignored `confirmed=False`;
  - the wrong-period rate on real stems defaulted to "right".
- **Runs:**
  - return test with the valley searched from lag 0: 3 of 40 smooth signals were still confirmed, with 5% false detections on the test set (**rejected**);
  - valley searched from lag/2 to the lag: 0 of 40 (adopted).
- **Implementation error found:** the meter script crashed on `meter_6-8_real`, a folder without a drum stem. The input checks of issue #5 now reject that case, and the script skips such folders.
- **Outcome:** smooth signals confirmed went from 25 of 40 to 0. The thresholds came out the same. Two verdicts changed, and both are documented. PR #14.

### 2026-11-12-pulse-001: are the remaining wrong periods a defect? (issue #15)

- **Before:** one wrong period in 60 test positives. *Question:* doubling, halving, the bar, or something else?
- **What happened:**
  - there were **three** wrong periods, not one: 5 beats twice, and a beat 3.2% off;
  - the metric counted any multiple as right, which hid bar-instead-of-beat: the beat itself was chosen in only 47 and 37 of 60;
  - candidate rules were tried on synthetic and on real stems.
- **Set aside, with reasons:**
  - the shortest confirmed level returns the eighths on 6 real tracks;
  - the exact comb flips the 80 BPM retake to the eighths;
  - the old rule plus a descent to T/q was tuned on the same real tracks it would be judged on.
- **Decision (Lex):** a strict benchmark first.

### 2026-11-12-pulse-002: strict beat-level benchmark, candidate v1 (issue #15)

- **Runs:**
  - on the development set of 320 signals: rules A, B and C, the band edge, and the share ρ (the sweep scripts are preserved);
  - v1 fixed at ρ = 0.5 and 2.5 kHz, then the first final set, run once.
- **Implementation error:** a prototype produced a negative period, and `confirm_period()` raised on it. The first prototype comparison crashed for this reason and was rerun. A guard was added to `pts/`, with a test.
- **Outcome:** on the final set the old rule got 160 and v1 190 of 200, with 4 worsened. Real stems are not scored, because no label is verified. Commit `babad3f`.

### 2026-11-12-pulse-003: four worsened signals, v2, second held-out set (issue #15)

- **Status change:** the first final set became development data once it was inspected.
- **Runs:**
  - occupancy check, κ from 0.6 to 0.9: it cost 31 to 72 beats (**rejected**);
  - ratio r(T)/r(2T): the classes overlap (**rejected**);
  - support by a confirmed multiple: 505 → 510 of 520 (adopted as v2);
  - a new generator (`holdout_b.py`), committed together with v2 before either was run, then run once.
- **Outcome:** old 153, v1 188, v2 188 of 200. v2 gives nothing over v1 on independent data. The known errors are kept as strict xfail tests. Tag `beat-level-comparison-2026-11-12`.

### 2026-11-12-bands-001: does splitting events by band tell the beat from its half? (issue #15)

- **Before:** *hypothesis:* low, mid and high envelopes and their joint pattern carry beat information that the full envelope lacks. *Rule set by Lex:* if they do, make a candidate and test it on a new set; if they do not, keep the negative result.
- **Runs:**
  - hats with an accent on the beat: bands 98.1%, full 93.4%;
  - hats all at one level: 97.8% against 95.1%;
  - hats at one level and at the same physical step under both labels: 95.7% against 95.5%, McNemar χ² = 0.1.
- **Interrupted:** the first analysis crashed at the very end (`HERE` undefined), after computing every feature. It was rerun with a feature cache.
- **Outcome:** negative, within its scope (these features, two classifiers, one generator). The gain came from conventions in the generator, not from the beat. No candidate was made. Commit `ccbd8b4`.
- **Correction (issue #17):** the first wording, "the bands carry no information about the beat", was wider than the evidence. It was narrowed to the tested features, classifiers and generator.

### 2026-11-12-level-001: measure and validate the amplitude envelope (issue #21)

- **State:** planned. Written before any run.
- **Question:** can our own method read the envelope of a sound accurately, its shape and its characteristic time? And does Envelope behave as an element of the Level column when the sound is compressed or stretched in time?
- **Method:**
  - **Estimators:** a moving RMS, and the smoothed magnitude of the analytic signal (computed with the FFT, our own code). Both use a Hann analysis window w from 0.5 to 20 ms.
  - **True envelopes:** a raised-cosine rise, an exponential decay, a Gaussian burst, and a constant level.
  - **True times:** the 10–90% rise, the 90–10% fall, and the full width at half maximum, from 1 ms to 500 ms.
  - **Carriers:** a sine and a harmonic tone at 55, 220, 880 and 3520 Hz, and white noise. Additive noise at ∞, 20 and 10 dB SNR. Three seeds for the random parts.
- **Hypotheses:**
  - **H1:** where the window is at most a quarter of the true time and at least three carrier periods, the time is recovered within 10% and the shape within 0.05, measured as the RMS of the peak-normalised difference.
  - **H2:** a change faster than about two carrier periods cannot be read. The limit scales as 1/f0.
  - **H3:** a noise carrier needs a longer window, because its envelope fluctuates by itself.
  - **H4:** under a tape-speed change by k, the measured time changes by 1/k within 5%, Z moves by −log₂ k, and the normalised shape stays the same.
- **Criteria fixed now:** Envelope counts as checked, in the conditions tested, if inside a stated valid region:
  - the time error is at most 10% at the median and 20% at the 95th percentile;
  - the shape error is at most 0.05;
  - a constant tonal level shows less than 1 dB of false change;
  - doubling the amplitude raises the reading by 6.02 ± 0.1 dB;
  - the time-scaling factor holds within 5%;
  - the valid region covers the table's τ range, 2 to 50 ms, at least for tonal carriers above some stated f0.
- **Development, runs and outcomes (appended after the runs):**
  - **Grid v1** (`runs/20261112T121927Z-grid-04751999c485`): inside the region w ≤ T/4 and w·f0 ≥ 2, all 88 clean tonal cells passed, but only 1 of 88 at 20 dB SNR. *Cause:* an implementation error in the measure, not a limit of the method. The noise floor was removed in amplitude (e − floor), but noise adds in power, so every time read in noise came out short (−9 to −23%).
  - **Scaling v1:** crashed (`runs/20261112T121927Z-scaling-04751999c485` keeps the crash). The analysis margins were fixed in seconds and longer than a signal compressed eight times. Fixed by scaling the margins with the tape speed; this changes nothing at speed 1. Rerun: `runs/20261112T122408Z-scaling-04751999c485`.
  - **runlog gap found:** untracked experiment files were not in the recorded diff. Grid v1 ran on an uncommitted `envelope.py`. `runlog.py` now hashes every `.py` file of the experiment folder.
  - **Grid v2** (`runs/20261112T122633Z-grid-99c2fb42aeb6`): the floor removed in power, √(e² − floor²). Version 1 can still be run with `FLOOR = "amplitude"`. The grid is development data from here on.
  - **Scaling, dev:** it used a 2 ms window on a 220 Hz carrier (w·f0 = 0.44), which is outside the region. Its errors therefore do not test H4. A new scaling check inside the region is added for the held-out run.
- **Frozen before the held-out run:**
  - **Method:** the analytic estimator, v2.
  - **Region** (`region.py`):
    - tonal: w ≤ T/4 and w·f0 ≥ 2, and, if SNR is finite, SNR ≥ 20 dB with w ≥ T/50 and w ≥ 2 ms;
    - noise carrier: T/4 ≥ w ≥ 10 ms and SNR ≥ 20 dB;
    - outside the region: SNR below 20 dB.
  - **On development:** 168 of 168 region cells pass for both estimators; a constant tonal level shows at most 0.80 dB of false change; a noise carrier shows 2.04 dB, which is its own fluctuation.
- **Held-out:** other seeds (100–102), pitches (110, 440, 1760 and 7040 Hz), times (1.5 to 300 ms), windows (0.7 to 30 ms), and SNR 30 dB added; plus a scaling check inside the region. Run once.
- **Held-out outcome** (`runs/20261112T123234Z-holdout-c578dc8bc74d`, `…-scaling_holdout-…`), run once:
  - **Region:** 279 of 279 cells pass for both estimators; median time error 0.32%, 95th percentile 3.9%, worst 12.9%; shape error at most 0.035.
  - **Constant tonal level:** at most 0.61 dB of false change. Linearity is exact.
  - **Tape speed:** tones within 0.55%; a compressed noise carrier is off by up to 7.2%, so **that criterion is not met for noise**. The compressed noise cases leave the region, because the scaled window falls below 10 ms while the bandwidth stays full.
  - **Extra check after the held-out run, not part of it:** 20 seeds of a harmonic tone compressed by 4 gave a median of 0.09% and a maximum of 1.97%. A core test first failed with a 1% tolerance, tighter than the 5% criterion. Its tolerance now follows the criterion.
- **Decision:**
  - Envelope is **checked for tonal sounds** in the region, where a change lasts at least 8 carrier periods and the SNR is at least 20 dB. It is marked ✓ in the table for Z 5.62 to 13.26.
  - It is **not checked for noise-like sounds** at its typical time; the reading needs a 10 ms window, so only changes of 40 ms and longer.
  - The analytic estimator is adopted as `pts.amplitude_envelope()`, with tests.
  - Next: real notes with known onsets; other envelope shapes; inharmonic sounds.
