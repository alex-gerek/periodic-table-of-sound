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
