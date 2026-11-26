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

### 2026-11-12-cards-001: the sample element card, Vibrato (issue #24)

- **Before:** one sample card, shown to Lex before the other nine are built. Every "measured" line on it must link to evidence. Every prediction must have been written down before its test, and must say what would prove it wrong.
- **Done:**
  - `table/cards.json` holds the card data, and `table/build_cards.py` builds it into both copies of the third edition;
  - the card opens on a click and holds its sections, a chart drawn from the vibrato experiment's numbers, and three predictions (one came true, two are waiting);
  - the collider opens from `?recipe=vibrato` with a with/without button.
- **Checks:**
  - In the browser, the card opens and has all its sections. Elements without a card keep the old panel.
  - The prediction "Vibrato lives in the Event row" is backed by the git history: the second edition placed Vibrato in row 3 (commit `3916a46`, 2026-11-10 21:32) before the measurement (`86ca8e1`, 23:11).
  - The collider found vibrato at 5.49 Hz with it on, found nothing with it off, and found 5.49 Hz again after switching back.
- **Corrections while building:**
  - The draft condition for refuting the prediction said "faster than 8 wobbles a second". The Event row ends at 20 (Z 10.7), so the condition did not match the prediction. It was corrected before publishing.
  - Locally, `edition3.html` shows broken characters, because the fragment has no charset and the local server sends none. The standalone copy and GitHub Pages are unaffected.

### 2026-11-12-cards-002: the other nine cards of wave 1 (issue #24)

- **Before:** Lex approved the Vibrato card. The rule is the same as for the sample: every measured line links to evidence, and every prediction says what would refute it and links to a record from before its test.
- **Done:**
  - cards for Pitch, Pulse, Sidechain pump, Meter, Harmonic rhythm and Envelope;
  - cards for the predicted cells Variation, Spatial motion and Width arc, which are marked 🔮 and say plainly that they are only built in the collider;
  - collider recipes `pitch`, `pulse`, `meter`, `variation`, `spatial` and `width`.
  - Envelope, Sidechain pump and Harmonic rhythm have no collider element yet. Their cards say so.
- **Checks:**
  - in the browser, all ten cards open without errors, each with its six sections;
  - every linked file exists;
  - for every recipe with a switch, the collider's detector finds the element when it is on and finds nothing when it is off: Vibrato 5.49 Hz, Pulse 110.0 BPM, Meter 3 beats, Variation 4 bars, Spatial motion 2.01 bars, Width arc 8.01 bars.
- **Corrections before publishing:**
  - Sidechain pump is built on Momentary loudness, not on "Loudness".
  - The evidence link for the bar prediction pointed to `docs/z16_border.md`, which does not hold the numbers. The real record is the tempo-series README at commit `069cff0` (2026-11-10 23:15): "the bar should land in row 5 (Z 16.58 and 16.26)". Those tracks were measured at 23:17 and 23:31.
  - Collider facts are labelled as collider facts (for example "in the collider, a rhythm without accents gives no meter").
- **Next:** collider elements for Envelope, Sidechain pump and chord changes, each with a detector and a control; then wave 2 (defects to hear).

### 2026-11-12-cards-003: the prediction scoreboard (issue #24)

- **Before:** a prediction is counted only if it was written down before its test. Every entry names its record and its test.
- **Checked in the git history:**
  - the row predictions of the second edition and the compression test date from 21:32, and the Periodicity column was measured at 21:43;
  - vibrato was measured at 23:11;
  - the bar values were written at 23:15 and measured at 23:17 and 23:31;
  - "finds 3 where 3 is" was written at 23:34 and measured at 23:46;
  - the Envelope criteria were fixed before its runs.
  - Observed patterns that became hypotheses (late vibrato, rigid harmonic rhythm) are listed as waiting, not as results.
- **Result:** `table/predictions.json` holds 23 predictions: 8 came true, 1 partly, 3 did not (Loop, Repetition, and Envelope scaling for every carrier), and 11 are waiting.
- **The scoreboard:** a strip above the table in both copies; each entry opens its element's card or panel.
- **Checked in the browser:** all 23 entries render, every element link resolves, and there are no errors.

### 2026-11-13-tapping-001: verified beat labels by tapping (issue #15)

- **State:** done. The protocol was written before any tap; the deviation and the outcome were added after the taps.
- **Question:** do the frozen pulse rules (old, candidate v1, candidate v2) return the beat on our own real recordings, when the beat is labelled by a person?
- **Protocol, fixed now:**
  - **Material:** one 30 s excerpt per track from the full mix (all stems summed), starting at 30% of the track. There are 13 tracks, the drum-stem set of `experiments/2026-11-12_beat_level/labels.json`.
  - **Blinding:** tracks are shown as "Track 1" to "Track 13" in a random order, fixed by seed 20261113. No track name, no requested tempo and no detector output is shown.
  - **Tapping:** two passes per track, with a key or a button on every beat. The first 4 taps of a pass are dropped. Intervals outside 0.6 to 1.6 times the pass median are dropped as slips. A pass needs at least 12 remaining intervals.
  - **Labels:**
    - verified: the two pass medians agree within 4%; the beat is their mean;
    - ambiguous: the passes are a factor of 2 apart (within 4%), and both levels are accepted;
    - otherwise the track is tapped again;
    - "no steady beat" is recorded as none.
  - **Scoring, after all labels are in:** the frozen old rule, v1 and v2 each run once on the drum stem of each track (full length, as in `results_real`). The beat-level metric is unchanged: exact within 3%, then precision, subdivision, multiple, other. Ambiguous tracks are scored against both levels and reported apart.
- **Hypothesis:**
  - v1 and v2 are exact on more verified tracks than the old rule;
  - the 80 BPM boom-bap retake is the expected error of the candidates.
- **Clarification of the protocol (before any real tap):**
  - when a track is tapped more than twice, any two valid passes that agree within 4% verify it; the beat is the mean of that pair;
  - a factor of 2 between two passes, with no agreeing pair, makes the track ambiguous.
  - Found while testing the page on synthetic taps: comparing only the last two passes would have asked for a fourth pass after a good first and third.
- **Deviation during tapping (written after the taps, before any scoring):**
  - the first three passes of Track 1 followed the drum rhythm (bursts of fast taps and pauses), not a steady pulse. Two of them happened to agree within 4%, so the rule alone would have accepted a label that is not a beat;
  - those passes were moved to `taps_practice.json` outside the repository (the timestamped history keeps them), Track 1 was restarted, and the page instruction was clarified to "a steady, even pulse ... the same gap every time, even through breaks";
  - lesson: agreement between passes does not prove a steady pulse. A future protocol should also bound the spread of the kept intervals;
  - the restarted Track 1 got four steady passes that never agreed (each slower than the one before), so it is incomplete and excluded;
  - the other 12 tracks were verified on their first two passes (ratios 1.000 to 1.016). No detector output was seen before or during tapping.
- **Outcome (run `20261113T060232Z-score-3ca4a3164622`, one scoring run):**
  - labels: 12 verified, 0 ambiguous, 0 none, 1 incomplete (Track 1);
  - exact on the 12 verified tracks: **old 9, v1 7, v2 7**. The hypothesis is false: the candidates are not better on tapped labels, they are worse by two tracks;
  - per track, against the old rule:
    - v1 and v2 lost `meter_3-4` (tapped 62 BPM, the bar; old found 60.8, the candidates 181.9) and `tempo_080_4-4_retake` (tapped 80.3; the candidates found 160.9);
    - v1 and v2 moved `tempo_174_4-4` from multiple (old 43.5) to subdivision (174.0); the tapped beat was 87.7, half the requested tempo, so no rule found it;
    - both 6/8 tracks were tapped at the dotted level (105.5 and 63.4 BPM) and every rule returned twice that;
    - `tempo_080_4-4` was tapped at 120.7 BPM, and every rule agreed with the listener, not with the prompt. This confirms that the prompt tempo is not a label;
  - every miss of every rule is a metrical relative of the tapped beat (×2, ×3 or ½). No rule returned an unrelated period. The rules find the metrical grid; they disagree with the listener about which level is the beat;
  - limits: one listener, 12 tracks. This listener tapped slow levels (half time, the bar in 3/4, the dotted beat in 6/8), and another listener may choose differently. A difference of two tracks is not significant, but it is against the pre-registered direction.
- **Decision (issue #15):**
  - the old rule stays; candidates v1 and v2 are not adopted. Their gains on synthetic and held-out sets did not transfer to tapped labels, because refine-from-multiples pushes them towards faster levels;
  - this is kept as a negative result, with all runs;
  - next, in a new issue: report the confirmed metrical ladder (all related levels) instead of one "beat", and collect labels from more listeners before choosing a preferred level. The beat level is a perceptual choice, and one listener cannot settle it.

### 2026-11-13-ladder-001: the metrical ladder instead of one beat (issue #29)

- **State:** done. The protocol was written before any ladder run; the dev changes, the frozen constants and the outcome were added in order.
- **Question:** can the pulse be reported as a ladder of related levels (the tatum and its groupings by 2 or by 3), each confirmed, so that the listener's beat is on the ladder without the ladder being every multiple?
- **Method, fixed now:**
  - the seed is the old rule's period (onset envelope, `envelope_periodicity`). A seed that is not confirmed gives an empty ladder;
  - **down:** from the current level l, try l/2 and l/3 (each moved to the nearest autocorrelation peak within 2%). A division joins the ladder if it passes `confirm_period`; if both pass, the one with the higher significance wins. Repeat while the level is at least 0.06 s;
  - **up:** from the current level l, try 2l and 3l. The grouping evidence for factor k is z_k = (r(kl) - mean of r(jl) for j = 1..k-1) / sigma, with the Bartlett sigma at lag kl. A grouping joins the ladder if z_k reaches Z_ACC and kl passes `confirm_period`; the larger z wins. Repeat while the level is at most 4.5 s;
  - Z_ACC is the only free constant. It is chosen on the dev grooves (seeds 0-199) and frozen before any held-out run.
- **Held-out check, run once:** the final grooves (seeds 50000-50199), the second held-out set (`holdout_b`), the negatives of the confirmation experiment, and the 12 tapped tracks.
- **Success criteria:**
  - S1, coverage: the true beat is on the ladder (within 3%) in at least 95% of the held-out grooves with a confirmed seed, and on at least 11 of the 12 tapped tracks;
  - S2, compactness: the median ladder has at most 5 levels between 0.06 s and 4.5 s (all ×2 and ×3 relatives in that range would be about 10);
  - S3, meter: for simple meters with 2, 3 or 4 beats a bar, the first grouping above the true beat is 2 for 2 and 4 beats and 3 for 3 beats in at least 70% of cases, and more often than the baseline that always answers 2;
  - S4, negatives: the ladder is empty on at least 95% of the negatives;
  - reported without a target: the level just below the beat against the true subdivision, and the meters with 5, 6 and 7 beats.
- **Decision rule:** the ladder goes into the core only if S1 to S4 all hold. Otherwise it stays an experiment and the failure is recorded.
- **Changes on the dev grooves (before any held-out run):**
  - divisions were never confirmed in the full-band onset envelope: the kick and the snare dominate its autocorrelation, and quiet hats between the beats hardly change it (dev seeds 1, 5 and 7). Divisions are now also looked for in a high-band envelope (2500 Hz to 11 kHz), and a division joins the ladder if it is confirmed in either envelope. They are still rarely confirmed when white noise covers the hats (SNR 0 to 15 dB), which is the honest answer;
  - **first tuning run, autocorrelation evidence for groupings** (its run folder was deleted by mistake before it was committed; the numbers below are copied from its console). Coverage 0.980 and median size 1 to 2 at every Z_ACC. Meter accuracy 0.537, 0.300, 0.225, 0.150, 0.113, 0.025 and 0.000 at Z_ACC 1, 2, 3, 4, 5, 6 and 8, against a baseline of 0.662 (n = 80). When a grouping was found it was mostly right (43 of 47 at Z_ACC 1), but most bars got no grouping at all. The autocorrelation difference is too weak a test;
  - the grouping evidence is therefore replaced by an accent test. The envelope maximum near each event of the level is taken in three bands (40-150 Hz, 150-2500 Hz, 2500 Hz-11 kHz). For factor k, a Welch t compares every k-th event with the others, taking the best band and the best offset. Z_ACC is now a threshold on that t;
  - the division metric in `evaluate.py` read the step of the wrong level (it scored 0.000 at every Z_ACC); this was fixed.
  - selection rule for the accent threshold, written while the second tuning run was still going: Z_ACC is the grid value (2, 3, 4, 5, 6 or 8) with the highest dev meter accuracy among those with coverage of at least 0.95 and a median size of at most 5. A tie goes to the larger value, which makes fewer false groupings.
  - **second tuning run (accent test):** coverage 0.980 and median size 2 at every Z_ACC; meter accuracy 0.762, 0.713, 0.700, 0.688, 0.637 and 0.613 at Z_ACC 2, 3, 4, 5, 6 and 8, against a baseline of 0.662 (n = 80); division 0.286;
  - two defects found by the new regression test `tests/test_ladder.py` (kicks every 0.4 s, no hats):
    - a false division at 0.14 s, confirmed in the high band from a bump inside each kick (autocorrelation 0.035 against 0.8 at the beat). A division must now reach DIV_SHARE = 0.25 of the level's own peak in the same envelope (real hats on dev give 0.5 to 1.05);
    - the meter and division metrics read the step stored on a level, which is wrong when the beat lies below the seed. Both now read the factor from the two periods;
  - so the tuning was run a third time, and the selection rule above applies to that run.

### 2026-11-13-cards-004: the Sidechain pump in the collider (issue #24)

- **State:** done.
- **What:** a new collider element, Sidechain pump (Sc). The pad and the melody pass through one gain that drops by Depth (3 to 18 dB) on every beat and ramps back over Release (60 to 400 ms, at most 90% of a beat). The Sc card now opens the recipe `?recipe=sidechain` (120 BPM, 9 dB, 200 ms), with the with / without switch.
- **Detector (sandbox only):** the level of the pad's mid signal (L + R, so that the width arc cancels) in 50 ms windows every 10 ms, in dB. It needs a level swing of at least 1.5 dB (5th to 95th percentile), then the shortest autocorrelation peak from 0.2 to 2 s whose comb over four multiples reaches 0.9 of the best, with r of at least 0.5.
- **Check, every element of the first wave on, with and without Sc,** at 60 BPM 9 dB 200 ms 4/4, 90 BPM 3 dB 100 ms 3/4, 128 BPM 6 dB 150 ms 4/4, 174 BPM 12 dB 60 ms 4/4, 200 BPM 18 dB 400 ms 7/4 and 100 BPM 3 dB 400 ms 5/4:
  - with Sc: the pump was found at the beat every time, within 0.6% (worst: 671 ms against 667 ms at 90 BPM and 3 dB, r 0.83);
  - without Sc: no pump in any of the six;
  - the pulse and the width arc were found the same with and without Sc;
  - the recipe's own control run (Pulse and Sc) removed each element in turn, and each one disappeared.
- **Limit:** this is the sandbox detector, a simplified copy; official results stay in `pts/`.

- **2026-11-13-ladder-001, continued: the frozen ladder.**
  - third tuning run `20261113T063038Z-tune`: coverage 0.980 and median size 2 at every Z_ACC; meter accuracy 0.925, 0.875, 0.863, 0.850, 0.800 and 0.775 at Z_ACC 2, 3, 4, 5, 6 and 8, against a baseline of 0.662 (n = 80); division 0.281. At Z_ACC 2, bars of 5 and 7 beats got no grouping by 2 or 3 in 50 of 54 cases;
  - by the selection rule, **Z_ACC = 2**, frozen with DIV_SHARE = 0.25 and HIGH_FMIN = 2500 Hz before any held-out run. The second tuning run is kept as `20261113T061835Z-tune`.
- **Outcome, one held-out run each** (`20261113T064201Z-final`, `20261113T071718Z-tapped`):

  | Set | Seeded | Coverage | Median size | Meter (baseline) | Division |
  |---|---|---|---|---|---|
  | final grooves | 200/200 | 0.965 | 3 | 0.888 (0.629), n 89 | 0.306 |
  | second held-out set | 199/200 | 0.965 | 3 | 0.955 (0.731), n 67 | 0.802 |
  | tapped tracks | 12/12 | 12/12 | 3 | not scored | not scored |
  | negatives | 0/120 | empty 120/120 | | | |

  - S1 to S4 all hold;
  - on the tapped tracks every listener's beat is on the ladder: the bar of the waltz (60.8 BPM, grouping by 3 above 181.8), the dotted beats of both 6/8 tracks (105.0 and 64.0), and the half time of the 174 BPM track (87.0). The prompt tempo of `tempo_080_4-4` is not on its ladder, and the listener's 120.7 is;
  - every meter error on the final grooves was a 3-beat bar read as 2 (5 cases), a 2-beat bar read as 3 (1) or no grouping (4);
  - divisions stay weak on the final grooves (0.306), where white noise often covers the hats; they are much better on the second set (0.802);
  - limits: the meter rule only says 2 or 3 above a level; 5 and 7 beats are left without a grouping in most cases (41 of 45 on the final set), which is honest but not a meter. One listener labelled the real tracks.
- **Decision:** by the pre-registered rule the ladder goes into the core, as `pts/ladder.py`, beside the old rule, which still gives the single period of `envelope_periodicity`. The evaluated copy stays in the experiment folder, and a test checks that the two agree. Issue #15's question, which level is "the beat", is now answered by not choosing: the report shows the whole ladder.

### 2026-11-22-live-001: the metrical ladder on live recordings (issue #29)

- **State:** planned. Written before any ladder run on these recordings.
- **Question:** does the frozen ladder (`pts/ladder.py`) put the listener's beat on its ladder for real musicians, in rooms, streets and old 78s, and does it stay empty where there is no steady beat?
- **Material:** 17 live recordings in `data/material/live/` (sources and licences in `SOURCES.txt`; the audio stays out of git): a folk dance band, a jig, four street and village bands, bagpipes and drums, three jazz records of 1923, a work song, body percussion, a beach celebration recorded on the move, a Macedonian tambura improvisation, a Bulgarian krivo horo, and two free-rhythm controls (a violin improvisation and a taksim soundcheck). Lex's sung pair (free, with claps, claps only) will be added before tapping if it is recorded in time, under the same protocol.
- **Excerpts:** one 30 s excerpt per recording, starting at 30% of its length, but never before the music starts (20 s for the folk festival) and never running past the end. Peak 0.89, 50 ms fades. A random order with seed 20261122 and names hidden, as in step 2026-11-13-tapping-001. **Blinding is only partial:** Lex chose these recordings and knows their kinds; the detector output stays hidden until all labels are in.
- **Labels:** the tapping protocol of 2026-11-13-tapping-001 with its clarification, plus one bound learnt from that day's rhythm-tapping passes: a pass is valid only if the spread (coefficient of variation) of its kept intervals is at most 0.15. The steady passes of 2026-11-13 reached at most 0.149; the passes that followed the drum rhythm gave 0.164 to 0.294.
- **Scoring, once, after all labels are in:** the frozen ladder runs on each 30 s excerpt (what was tapped) and, as a secondary result, on the whole recording from the music start. The first 20 s of the folk festival (room sound only) is an extra negative.
- **Hypotheses:**
  - H1: the tapped beat is on the excerpt's ladder (within 3%) on at least 80% of the verified tracks. Live tempo drift and 30 s excerpts make this harder than the synthetic check (0.965);
  - H2: the ladder is empty on the two free-rhythm controls and on the room-only segment;
  - H3, reported without a target (too few cases): where the source states the meter (3/4 waltz by tag, 6/8 jig, 4/4 "When the Saints", 4/4 jazz, an uneven krivo horo), the first grouping above the tapped beat against that meter.
- **Decision rule:** if H1 or H2 fails, the failures are analysed and a defect issue is opened; the core is not changed on this material without a new held-out check.
- **Addition on 2026-11-25, before any tap or run on the live material:** one prediction is added to H3 with a target. On the krivo horo (`tsalapishko_krivo_horo_gerganov.ogg`) the ladder finds no grouping by 2 or by 3 directly above the tapped beat. Grouping by 2 or 3 there would be a wrong meter; no grouping is the honest answer for a crooked bar. The live hypotheses H1, H2 and this one are now on the prediction scoreboard as "waiting".

### 2026-11-25-cards-005: the scoreboard after issues #15 and #29 (issue #24)

- **State:** done.
- The issue #15 prediction "a rule can be found that returns the beat itself" is now **false**: the candidate lost on the tapped labels (7 exact against 9), and the beat level proved to be the listener's choice.
- Two pre-registered ladder criteria are added as **true** (coverage, and bars of 3 against 2), and the three live predictions as **waiting**.
- Scoreboard: 28 predictions, 10 true, 1 partly, 4 false, 13 waiting.
- The Pulse card was brought up to date: the ladder in its numbers and limits, the issue #15 prediction marked false, the ladder prediction added as true.
- The table page had no `<meta charset="utf-8">`. GitHub Pages sends the encoding itself, but a local server does not, and the scoreboard symbols then showed as mojibake. The tag was added; the standalone file already had it.
- **Clarification on 2026-11-25, still before any tap on the live material:** the krivo horo prediction can only be tested if the tapped level is a beat inside the dance cycle. A crooked cycle has long and short beats, so tapping every step gives uneven intervals that the spread bound (0.15) rejects, and the listener may instead tap the whole cycle or press "No steady beat". If the tapped level is the whole cycle, a grouping found above it would be about phrases, not about the meter. So in that case, or with "No steady beat", the prediction is recorded as **not testable** and stays out of the true and false counts. The listener gets no instruction specific to this track.
- **Uneven cycles (added on 2026-11-25, before any tap on the live material):** a musician can tap the steps of a crooked dance, long and short, and that is a correct beat. So a pass that fails the spread bound is now also tested as a **repeating uneven cycle**, instead of being thrown away:
  - the first 4 taps are dropped, and only extreme slips (under 0.3 or over 3 times the median interval) are removed;
  - for k = 2 to 5 taps per cycle and every starting phase, the cycle lengths (sums of k neighbouring intervals) must have a spread of at most 0.08, each step position a spread of at most 0.15, at least 6 whole cycles must fit, and the longest step must be at least 1.25 times the shortest (otherwise the pulse is even and the normal rule applies). The smallest k that passes is taken;
  - two such passes with the same k and cycle lengths within 4% give the label **uneven**, with the cycle length and the median step lengths;
  - uneven tracks are reported apart from H1. The ladder is asked only whether it holds the cycle length, and the krivo horo prediction stays **not testable** for an uneven label, as written above. The labels are kept for a future element of uneven meters.
  - checked before any real tap: synthetic 2+2+3 steps give an uneven cycle of k = 3 and no even period; steady taps give a period and no cycle; random taps give neither; two matching uneven passes label the track "uneven", two different ones ask for another pass. None of the 2026-11-13 passes is read as a cycle, so the three passes that followed the drum rhythm are still rejected.

### 2026-11-26-collider-003: a Noise control in the collider (issue #24)

- **State:** done.
- **What:** a new collider control, Noise (Ns): independent, seeded white noise in each channel of every stem, at Level dB RMS (-40 to -6 dB, full scale 0 dB). It is a control, not an element: it has no period, the results table says "nothing to find", and the control run does not remove it. Recipe `?recipe=noise`, presets "Noise only" and "Pulse through noise".
- **Findings:**
  - **noise only**, at -36, -30, -24, -18, -12 and -6 dB and two tempi: before the fix, the width detector reported a false 378 ms period at -12 dB. The cause: in noise the side-share curve decays slowly, and a bump of 0.01 on that slope passed as a peak. `detectSlow` now needs the peak to rise at least 0.15 above the lowest correlation between half its lag and its lag (as in `confirm_period`) and the period to be at least 0.4 s. After the fix: nothing found in 12 of 12;
  - **spatial motion and width arc under noise** (60 to 200 BPM, clean, -24 and -12 dB): all 15 spatial motions were found within 1%; width arcs were found in 12 of 15. Of the 3 misses, two are a 22 s cycle at 174 BPM, half the sound, which the old rule missed too; the third (120 BPM at -12 dB) is masked by noise: the old rule would have reported a wrong 0.39 s there, the new one reports nothing;
  - **pulse under noise:** a pulse alone is found at every level up to -6 dB (13 dB of noise over the drums). With a meter, whose weak beats are at 0.42 of the downbeat, the sandbox rule reads the bar as the pulse from -24 dB on and loses the meter. This is the beat-or-bar choice of issue #15 again; the Python ladder keeps both levels, the sandbox does not. Recorded as a known limit, and said in the recipe hint.

### 2026-11-26-calib-001: a calibrated false-alarm rate for period confirmation (issue #32)

- **State:** planned. Written before any run of the surrogate test.
- **Owner:** Claude. **Previous step:** 2026-11-12, period confirmation (issue #7), `experiments/2026-11-12_periodicity_confirmation/`.
- **Question:** `confirm_period()` decides in sigma (Bartlett's formula, 5 sigma, chosen on a training set). A sigma is a distance, not a probability: smooth swells, which have no period, reach a median of 7.6 sigma on the significance test and are stopped only by the return test. Can the decision state its false-alarm rate directly, and does that change any decision?
- **Method (from our Blind Signal Discovery project, re-derived in `pts/stats.py` with numpy only):**
  - the statistic of a track is S = min(significance, return, sqrt(2) x weaker half), all three from `confirm_period` with its thresholds set to zero. The candidate is picked by the full search in 0.25 to 2 s, so the choice of the best lag is inside the statistic (the look-elsewhere effect);
  - the null cases are K = 199 surrogates of the same onset envelope: cut into pieces of tau_lo/3 to tau_lo (83 to 250 ms) of random length and shuffled. They keep the track's own sounds and density and destroy repetition at the searched lags;
  - p = (1 + number of surrogates with S >= S_track) / 200; a period passes the surrogate test at alpha = 0.01, the smallest p-value that is reachable with two tail cases (p <= 2/200);
  - all rates are reported with exact (Clopper-Pearson) 95% intervals.
- **Data and split status:**
  - **fresh**, never seen: seeds 2000 to 2119 with the generators of 2026-11-12 (the six non-periodic families in turn, and grooves as positives); the 12 real drum stems shuffled again in the audio domain with a new seed (26);
  - **development**, already inspected in 2026-11-12: the training (0 to 59) and test (1000 to 1059) seeds, and the real stems with the seed 7 shuffles. They are re-run only to compare the two rules on the same signals.
- **Hypotheses:**
  - H1 (calibration): on the shuffled real stems, the null by construction, the surrogate test passes at most 1% plus sampling error; the guarantee is approximate, because the stems are shuffled as audio and the surrogates as envelopes. Expected: 0 of 12, which can only show gross miscalibration;
  - H2 (other negatives, no guarantee): on the fresh negatives of all six families, the surrogate test passes at most 5% (6 of 120). The swells are the risk: shuffling destroys a swell, so a swell differs from its own surrogates without being periodic. The return term of S is meant to prevent that;
  - H3 (power): every positive that the sigma rule confirms has p at the floor (1/200), because rhythm reaches 19 to 55 sigma;
  - H4: the two rules disagree on at most 2% of all signals. Every disagreement is listed with its evidence.
- **Decision rule, fixed now:**
  - the surrogate p-value is added to `confirm_period` as an optional, reported piece of evidence (off by default, because it costs 199 extra searches) if H1 holds;
  - it becomes part of the decision (sigma rule AND p <= 0.01) only if, on the fresh data, it rejects at least one negative that the sigma rule confirms and loses no positive that the sigma rule confirms. If it changes nothing, it stays evidence only: a gate that never acts only adds cost;
  - if H2 fails, the surrogate test is not adopted as a gate, and the failing family is analysed in a defect note.
- **Limits known before the run:** 12 real stems can reveal only a gross error; the surrogates test "the order of events is random", which is not the only way a track can be non-periodic.
- **Run:** `20261126T124214Z-final-7d14a7e63135` (code at 7d14a7e, 534 s), one run, no reruns. Results: `experiments/2026-11-26_calibrated_confirmation/runs/20261126T124214Z-final-7d14a7e63135/`.
- **Outcome against the hypotheses:**
  - H1 **holds**: 0 of 12 shuffled real stems pass the surrogate test (95% CI 0 to 26.5%), on both shuffle seeds. As stated before the run, 12 cases can only exclude a gross error;
  - H2 **holds**: 2 of 120 fresh negatives pass (1.7%, CI 0.2 to 5.9%), against a limit of 6. One is random drum hits at p = 0.010, exactly at alpha; the other is a smooth swell at p = 0.005, the risk named before the run. The p-values of the fresh negatives are close to uniform (median 0.54, 5% of them at or below 0.05), although only the shuffled stems are exchangeable with the surrogates by construction;
  - H3 **fails by one case**: 262 of 263 positives confirmed by the sigma rule have p at the floor 1/200. The exception is a training click train (seed 58) at p = 0.010: one of its 199 surrogates reached S = 8.58 against its own 8.46. Shuffled pieces of up to 250 ms keep part of a fast pulse, so the surrogates are not a perfect null near the short end of the range (tau_lo). It still passes at alpha;
  - H4 **holds**: 4 disagreements in 528 signals (0.8%). Three are negatives that the surrogate test passes and the sigma rule rejects; one is a training click train (seed 40) that the surrogate test confirms at p = 0.010 and the sigma rule misses (4.7 sigma).
- **What this shows:** the sigma rule is **more conservative** than a 1% false-alarm rate: it passed 0 of 252 negatives in all sets (CI 0 to 1.5%), where a calibrated 1% test passes about 1%. Its real false-alarm rate is below 1.5% (95%), but sigma does not say how far below. The surrogate p-value states its rate directly and is close to calibrated even on families it does not model.
- **Decision, by the rule fixed before the run:**
  - the surrogate p-value is **adopted as reported evidence** (H1 holds): `pts.periodicity.surrogate_p()`, off by default because it costs 199 extra searches (about 1 s per track);
  - it is **not made a gate**: on the fresh data the sigma rule confirmed no negative, so the AND gate would never have acted. The decision rule stays the sigma rule;
  - every counted rate on the scoreboard now carries its exact 95% interval (computed by `table/build_cards.py`).
- **Found on the way:** with intervals, the issue #15 result reads 7 of 12 (CI 28 to 85%) against 9 of 12 (CI 43 to 94%). The prediction is "false" by its pre-registered rule (the candidate had to win and did not), but these 12 tracks do not show that the old rule is better. The scoreboard entry is unchanged; this note is the correction of its reading.
- **Limits:** the surrogates keep repetition shorter than tau_lo, so a period just above tau_lo is tested against a slightly periodic null (conservative, as seed 58 shows). The 12 real stems are the only real material; other genres are untested.
- **Next:** the pilot "seam hunt" (step 2 of the plan in issue #32's motivation): the excess-power detector and the regime monitor on Suno tracks against the live recordings, with the shuffled-pieces null from `pts/stats.py`.

### 2026-11-26-seam-001: seam hunt, pilot (issue #34)

- **State:** planned. Written before any run on the material below.
- **Owner:** Claude. **Previous step:** 2026-11-26-calib-001 (conformal p-values in `pts/stats.py`).
- **Question:** a Seam is a join in generated audio where the background changes without a musical reason. Can a join be found from the background of the sound alone, with a calibrated false-alarm rate, before we have generated tracks with known join times?
- **Detector (prototype in the experiment folder, not in `pts/`):** the idea is the regime monitor of our Blind Signal Discovery project, re-derived for music.
  - mono mix, STFT of 2048 samples, hop 50 ms; 1 s blocks;
  - per block, 9 background features: the 10th percentile of frame power (dB) in 8 log bands from 100 Hz to 16 kHz (the floor between notes, not the notes), and the bandwidth ratio: energy above 16 kHz against 8 to 16 kHz (dB);
  - change score at each block boundary: |median of the next 6 blocks - median of the previous 6| / (1.4826 x pooled MAD of both sides + 0.5 dB), per feature;
  - two scores, both fixed now: **S_all** = the largest change over all 9 features, **S_bw** = the change of the bandwidth ratio alone (the feature that arrangement changes should move least);
  - a 30 s window gets the largest score over its boundaries 6 to 24 s, and the time of that boundary.
- **Calibration:** the 17 live recordings (`data/material/live/`), cut into non-overlapping 30 s windows. Each window gets a conformal p-value against the windows of the other 16 recordings (leave one recording out). A window is flagged at p <= 0.05.
- **Known seams (injection):** every live window gets each of four seams at a time drawn uniformly in 8 to 22 s (seed 20261126), scored against the windows of the other recordings:
  - bandwidth: everything after the join low-passed at 16 kHz (8th order Butterworth, zero phase);
  - floor: white noise at -60 dB relative to the window RMS added after the join;
  - tilt: a +3 dB high shelf above 4 kHz after the join;
  - splice: the audio after the join replaced by audio of the same recording from 60 s later (or earlier, if too close to the end), joined with a 5 ms crossfade.
  A seam counts as found if the window is flagged and the found time is within 1 s of the join.
- **Generated material (exploration):** the Suno tracks we hold as stems (`data/stems/*`, `data/material/tempo_series/*`, `data/material/meters/*` without `meter_6-8_real`, `data/material/vibrato/*`), each mixed by summing its stems, cut into 30 s windows and scored against all live windows.
- **Hypotheses:**
  - P1 (calibration): at most 10% of live windows are flagged under leave-one-recording-out (5% nominal; windows of one recording are not independent);
  - P2 (sensitivity): the bandwidth seam is found in at least 80% of windows by S_bw and by S_all; the floor seam in at least 60% by S_all; the tilt seam in at least 50% by S_all. The splice is reported without a target;
  - P3 (exploration, direction only): S_bw flags a larger share of Suno windows than of live windows. If not, there is no sign of bandwidth joins in this Suno material.
- **Decision rule:** nothing goes into `pts/` from this pilot. If P1 and P2 hold, the next step is a test on generated tracks with known join times (tracks extended at recorded times, requested from Lex), and the Suno candidates of P3 are listed for that test, not counted as seams. If P1 fails, the null is analysed first. If P2 fails for a seam type, that type is outside what background features can see.
- **Not tested here:** the excess-power detector of Blind Signal Discovery itself (a join without a crossfade would be a short broadband transient). It is a separate step.
- **Known confounds:** live recordings have room noise, walking microphones and crowd; Suno tracks are studio-clean, so they are not exchangeable with the live windows, and P3 is a comparison, not a calibrated test. Arrangement changes (instruments entering) move band floors too; that is why S_bw is kept apart.
- **Run:** `20261126T130343Z-final-8b6fbfe16b76` (code at 8b6fbfe, 107 s), one run. 95 live windows from 17 recordings, 380 known seams (6 splices excluded: recordings too short for a 60 s offset), 65 Suno windows from 15 tracks.
- **Outcome against the hypotheses:**
  - P1 **holds**: 4 of 95 live windows flagged by S_all (4.2%, CI 1.2 to 10.4%), 5 of 95 by S_bw (5.3%, CI 1.7 to 11.9%);
  - P2 **fails for every seam type**: bandwidth found by S_bw in 43 of 95 (45.3%, CI 35.0 to 55.8%; target 80%) and by S_all in 9 of 95; floor 1 of 95 by S_all (target 60%); tilt 1 of 95 (target 50%); splice 0 of 89 by S_all, 3 of 89 by S_bw;
  - P3 holds by the letter: S_bw flags 13 of 65 Suno windows (20.0%, CI 11.1 to 31.8%) against 5 of 95 live. It cannot be read as seams: the same score misses half of the known bandwidth joins, and Suno mixes are studio-clean, where energy above 16 kHz comes and goes with cymbals and hats. Several candidates sit in the first 10 to 20 s of a track, where the drums enter.
- **Post-hoc diagnosis** (`diagnose.py`, run `20261126T130602Z-diagnose-6f24a5d6bb7d`, written after the results, exploratory):
  - the live null is loud: its 95th percentiles are S_all 12.7 and S_bw 4.2. With the floor, tilt and splice seams the median scores (4.4 to 5.1 for S_all) are the same as without any seam (4.3): at these levels the joins are smaller than the natural movement of a live background (walking microphones, crowds, room noise);
  - bandwidth seams are invisible where there is nothing above 16 kHz to remove (the krivo horo file, -55 dB: 0 of 7). The 1923 transfers have the most energy above 16 kHz (-3 to -7 dB), which is surface noise of the record, not music;
  - S_all is worse than S_bw on bandwidth seams (9 against 43): taking the largest change over nine features adds the volatility of eight band floors to the one feature that carries the seam.
- **Decision, by the rule fixed before the run:** nothing goes into `pts/`; P2 failed, so there is no step to Suno joins from this design. What failed is narrower than "background features cannot see seams": against a live-recording null, single seams of these sizes (-60 dB noise, +3 dB tilt, a 16 kHz low-pass, a crossfaded splice) are below the background movement of live music. The pilot does not test a studio null, larger seams or a level sweep.
- **What it says about Blind Signal Discovery:** its regime-monitor idea, ported as it is, does not find seams in music. Its calibration did its job (P1 held, and the failure is measured, not guessed).
- **Next:**
  1. ground truth first: generated tracks with known extend times (request in `data/material_request.md`, section 7). Without them a seam detector can only be tuned on our own guesses of what a seam is;
  2. on those tracks: a null of the same track (its other joins-free windows), not of live recordings; the bandwidth feature alone; and the short-scale excess-power detector of Blind Signal Discovery for joins without a crossfade;
  3. a level sweep of the injected seams on a studio null, to give a detection limit in dB instead of one pass or fail.

### 2026-11-26-leak-001: stem leakage with the other stem as a witness (issue #38)

- **State:** planned. Written before any run.
- **Owner:** Claude. **Previous step:** 2026-11-26-calib-001 (conformal p-values).
- **Question:** a separated stem can hold part of another source, for example voice in the drum stem. The vocal stem of the same track is a witness of that voice. How much of a target stem does the witness explain, and from what level can we tell?
- **Estimator** (prototype in the experiment folder; the method is the witness-channel regression used to remove known noise in gravitational-wave detectors, re-derived):
  - mono, STFT of 2048 samples with a Hann window, hop 512, at 48 kHz; bins from 100 Hz to 12 kHz;
  - for every bin k, the complex gain of the witness V in the target D over all frames, g_k = sum_t D V* / sum_t |V|^2. The **explained energy** is sum_k |sum_t D V*|^2 / sum_t |V|^2;
  - the statistic is the **explained share** of the target: explained energy / sum_k sum_t |D|^2. The leakage estimate in dB relative to the target is 10 log10 of that share;
  - significance: the same statistic for the witness circularly shifted by K = 199 random offsets between 2 s and the length minus 2 s (seed 20261126); conformal p, detection at p <= 0.01. A shift keeps the witness's own sound and timing statistics and destroys only its alignment with the target.
- **Material:** Suno stem sets with a lead vocal and drums at 48 kHz, one per song: Boo-da Boo-da Boo-da Boom, Data Corruption (The 42nd Blueprint Ash_Circuit), EVERYTHINGS ALRIGHT, Metro, Pocket Blues (from Lex's archive, listed with hashes in an internal manifest outside git; provenance guessed from Suno's stem naming, not yet confirmed by Lex) and GRAVITY and Pure voltage (`data/stems/`). Excluded: the set of 04.03.26 (its stems have different lengths, so they are not one track), the 44.1 kHz second exports of Metro and Pocket Blues (the same songs).
- **Excerpts:** 60 s per song, the window with the most lead-vocal energy (1 s steps).
- **Ground truth across songs:** for every ordered pair of different songs (7 x 6 = 42 pairs), the drums of song A are the target and the lead vocal of song B is the witness. Before writing, the true leakage of B's voice into A's drums is zero. Written in at L = -50, -45, -40, -35, -30, -25 and -20 dB of the drum energy:
  - **linear:** the witness itself, scaled;
  - **masked:** the witness passed through a random binary time-frequency mask that keeps each STFT cell with probability 0.5 (seeded), then scaled to the same leak energy. This is closer to what a separator leaves behind.
- **Hypotheses:**
  - H1 (false alarms): without writing, at most 2 of the 42 pairs are detected (1% nominal);
  - H2 (detection limit): linear leaks are detected in at least 90% of pairs at -35 dB; masked leaks at -30 dB;
  - H3 (level): for linear leaks at -40 dB and above, the median absolute error of the leakage estimate is at most 1 dB. For masked leaks the estimate only counts the part coherent with the witness; its bias is reported, not judged;
  - H4 (exploration, no target): within each song, the matrix of explained shares between all its stems (target rows, witness columns), with p-values.
- **Decision rule:** if H1 to H3 hold, the estimator goes into `pts/` as a measurement of stem leakage, with its detection limit stated, and the within-song matrices become the first leakage report on Suno stems (a candidate metric for the PHARMAKON splitter, noted in the internal journal). If H1 fails, the shift null is analysed before anything else. If H2 or H3 fails, the limit is reported as measured and nothing is adopted.
- **Limits known before the run:** seven songs, all Suno; mono only; a leak that is not coherent with the witness (a separator's own noise, a reverb tail it invents) is not measured by this estimator.
- **Amendments before the first data run** (found by a synthetic check only: white noise as the target, gated filtered noise as the witness; no stem was analysed):
  - with one complex gain per bin (508 free gains) the chance level of the explained share was about -35 dB, and a -40 dB leak read as -33 dB. The estimator now uses **one complex gain per log band (16 bands, 100 Hz to 12 kHz)**, which lowers the chance level to about -47 dB, and the leak estimate **subtracts the chance level** (the median share over the shifted witnesses). The p-value is unchanged in kind (share at shift 0 against the shifted shares);
  - the inverse STFT divided by a near-zero window sum at the two ends of the excerpt; after masking this blew the energy up by 10^4. Those edge samples are now zeroed;
  - leak levels are defined as energy **in the measured band** relative to the target's energy in that band, so that the written level and the estimate measure the same thing (white noise has half its energy above 12 kHz, which gave a +2.5 dB offset).
  - After the changes, on the same synthetic signals: linear leaks written at -45, -40 and -30 dB read -43.3, -39.1 and -29.8 dB; masked leaks -44.0, -39.9 and -30.7 dB; all with p = 0.005. Hypotheses and decision rule are unchanged.
- **Run:** `20261126T135152Z-final-30531db5f2eb` (code at 30531db, 1437 s), one run. 7 songs, 42 cross-song pairs, 7 within-song matrices. Inputs and excerpt starts with SHA-256 in `results.json`.
- **Outcome against the hypotheses:**
  - H1 **holds**: 1 of 42 pairs detected without any leak (2.4%, CI 0.1 to 12.6%; drums of Data Corruption against the voice of Pocket Blues, p = 0.005);
  - H2 **fails**: linear leaks at -35 dB are detected in 6 of 42 (14%; target 90%), masked leaks at -30 dB in 30 of 42 (71%). The measured limit: **-25 dB for both kinds** (41 of 42, CI 87 to 100%); -30 dB gives 83% (linear) and 71% (masked);
  - H3 **fails at -40 dB and holds from -35 dB up**: median absolute error 3.1 dB at -40, 0.99 at -35, 0.49 at -30, 0.17 at -25, 0.06 at -20. Masked leaks read about 1 dB low from -35 dB up (the coherent part only, as expected);
  - why the synthetic check was too optimistic: the chance level of the share on real drums is -39 dB (median; -44 to -37 by song), against -47 dB on white noise. Drum energy sits in few frames, so fewer frames carry the estimate.
- **H4, exploration** (within-song matrices; only values above -25 dB are inside the measured reliable range):
  - **voice in the drum stem:** GRAVITY -21.8 dB and Pure voltage -21.5 dB (both p = 0.005, inside the reliable range); EVERYTHINGS ALRIGHT -29.8 dB (p = 0.005, in the range where detection is 71 to 83%); not detected in Boo-da, Data Corruption, Metro, Pocket Blues (below about -30 dB, or absent);
  - **stems that share the same audio:** Keyboard and Synth explain each other at -1.0 to -1.1 dB in GRAVITY and EVERYTHINGS ALRIGHT, Bass and Synth or Keyboard at -2 dB in GRAVITY; Lead and Backing Vocals at -5 to -7 dB in four songs; Backing Vocals and Percussion at -6 dB in Data Corruption. The estimator cannot tell which stem the shared part belongs to;
  - Pure voltage is coherent almost everywhere (-5 to -30 dB between most pairs): its twelve stems are heavily mixed into each other;
  - stems that are silent in the excerpt show -inf with p = 1 (Guitar and Woodwinds in EVERYTHINGS ALRIGHT, Strings and Brass in GRAVITY).
- **Decision, by the rule fixed before the run:** H2 and H3 failed, so **nothing goes into `pts/`**. The limit is stated as measured: on 60 s excerpts of real drums, a voice leak is detected reliably from -25 dB and its level is read within 1 dB from -35 dB. The within-song findings above -25 dB are reported as measurements with that limit.
- **Next (not run):** the full track instead of 60 s (about 4 times the frames, so the chance level should fall by about 6 dB), and weighting frames by the witness's activity. Both need a new pre-registered run on the same cross-song design.
