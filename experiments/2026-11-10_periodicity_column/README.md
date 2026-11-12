# 2026-11-10: the Periodicity column on real stems

The first measurement of the second edition. One tool, the autocorrelation of a track, is applied at every time scale of group II (Periodicity). The track is the waveform, the pitch track, the onset envelope, the level track or the sequence of spectral frames. For each element we record τ, Z and the row it falls into, on three tracks: GRAVITY, Metro and Pure voltage.

- Code: [`pts/periodicity.py`](../../pts/periodicity.py), [`pts/zscale.py`](../../pts/zscale.py)
- Synthetic ground-truth tests: [`tests/test_periodicity.py`](../../tests/test_periodicity.py), 10 of 10 passing
- Known effects written into real stems: [`vibrato_injection.py`](vibrato_injection.py)
- Run: `python run.py`. Full numbers: [`results.md`](results.md) and `results.json`.

Every parameter was fixed by the synthetic tests before the stems were opened. All three tracks are therefore held-out data for this step.

## Read this first: which checks are real evidence

Some elements are defined with a time range that comes from perception. A pulse is what can be tapped (0.25 to 2 s); a pitch is a repeat faster than about 20 Hz. The table's rows were cut at the same perceptual borders. For these elements, landing in the predicted row is true by definition, so it is not evidence.

The headline count in `results.md` (23 of 27 in the predicted row) mixes both kinds and must not be quoted as proof. The evidence is in the four checks below. None of them uses the row borders.

## What held

1. **The time-compression test passes on real drums.** 32 seconds of each drum stem were played 32 times faster. The pitch detector, a waveform tool, found periods that, multiplied back by 32, are exactly 2.00, 2.00 and 1.00 pulses of the original, within 0.3%. The detector found the kick-snare pattern (two beats) on GRAVITY and Metro and the pulse itself on Pure voltage. The same column, exactly 5 octaves of Z lower: this is the column law on real music, not on a synthetic click train.
2. **The second-order element confirms itself.** Sidechain pump was searched freely, from 50 ms to 4 s, in the level track of the bass stem. Where pumping exists, it nests in the drum pulse measured from a different stem and a different track type. On GRAVITY it equals the pulse: 502.8 vs 504.3 ms (0.3%). It lands in row 4 as predicted. Metro's bass shows no pump (r = 0.10), which is a correct negative.

   **Corrected on 2026-11-11 (issue #5).** On Pure voltage the bass level repeats most strongly every **two** pulses (1.072 s, r = 0.49), and less strongly every pulse (0.537 s, r = 0.37). The first run reported one pulse, but only because that candidate sat just above the 0.9 threshold of the peak rule. After the level track stopped dipping at both ends of the recording, the two-pulse repeat became slightly cleaner, and the rule now picks it: 1.072 vs 1.077 s (two pulses), ratio 1.991. The pump on this track is therefore ambiguous between one and two beats. The nesting in whole pulses holds either way. The earlier claim "equal to the pulse on two tracks" was too strong; it holds on one track.
3. **The periods of one track nest as whole numbers.** Pulse/Subdivision is 4.03 and 2.00. Meter/Pulse is 4.00, 8.00 and 3.98. The worst case is 0.6% off an integer.
4. **Pitch ranges.** Bass sits at Z 8.5 to 9.7 and the lead vocal at Z 5.1 to 8.7 (10th to 90th percentile). Both are in the Tone row, except the highest vocal notes on Pure voltage. Above 500 Hz they cross into Wave, as the Z rule says they should.

## What did not hold, and what it teaches

| Problem | Evidence | What to do |
|---|---|---|
| **The Beat/Bar border cuts real bars in two.** | Metro runs at 132 BPM. Its 4/4 bar is 1.82 s, Z 15.86, which is in the Beat row. The meter search, limited to the Bar row, found two bars (3.63 s) instead. A 4/4 bar at 100 to 140 BPM lasts 1.7 to 2.4 s, so it sits right on the border at Z 16. | Decide: either Meter is an element that spans rows 4 and 5 (allowed, since elements have ranges), or the border moves. Searches must not be limited to row borders. |
| **The first vibrato detector was blind; fixed and calibrated.** | Known vibrato was written into the real vocals (`vibrato_injection.py`, `vibrato_injection.md`), and at first even 60 cents was missed. There were two causes. The autocorrelation pitch tracker accepted only 22% of frames of a reverberant voice, and a moving-average detrend left note steps in, so a melody moving on the beat looked like 2 Hz. A new difference-function tracker, octave-error cleaning and a running-median detrend fixed it. On Pure voltage 15 cents is found (r = 0.33), and 5 of 5 injected cases pass. | Pure voltage: **no natural vibrato** (r ≤ 0.09), which is now a valid result. GRAVITY: the vocal pitch moves at 1.99 Hz, locked to the pulse (1.98 Hz), with r = 0.47. This masks small vibrato. A vocal delay of one beat is one hypothesis (not verified). Metro: the vocal stem is almost silent. |
| **"Loop" is not yet a well-posed element.** | A free search finds the shortest repeating spectral unit, which is the two-beat drum pattern (0.99 s on GRAVITY), not a phrase. Since the return test, even that candidate is not confirmed: the similarity hardly falls between one and two beats. Inside the Phrase row the comb score preferred 14.1 s (7 bars) over the strongest single peak, 8.1 s (4 bars). It did so because multiples of 14.1 s hit section repeats. | Define a loop by exactness of repetition (similarity close to 1), not by shortest strong lag. Use pitch-class frames as well as band levels. |
| **Repetition on GRAVITY hit the search edge.** | 140.9 s is half the track. The strongest single peak is 56.5 s. | The comb score must require at least two multiples inside the track. |
| **Subdivision not found on Pure voltage.** | No positive peak in 50 to 250 ms. | Check the drum stem: the pattern may have no steady subdivision, or the envelope may need the high band separately. |
| **Spectral-frame similarity is weak.** | Loop and repetition peaks have r = 0.07 to 0.30. | Better long-scale features (pitch classes, per-stem frames). |

## Status after this step

- **Periodicity column law: supported on real data.** The compression test passes and the nesting check passes. Sidechain pump nests in the pulse on both tracks with pumping: one pulse on GRAVITY, two pulses on Pure voltage (see the correction above).
- **Period borders: one border (Z 16) conflicts with real bars.** It needs a decision.
- **Vibrato:** the detector is calibrated on real voices. Natural vibrato material is needed (see `data/material_request.md`).
- **Loop and Repetition:** the definition is not good enough yet.
- **Z 16 border:** analysis and options are in `docs/z16_border.md`.
