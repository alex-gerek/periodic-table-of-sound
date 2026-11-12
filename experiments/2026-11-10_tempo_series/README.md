# 2026-11-10: tempo series and the Z 16 border

The tracks were made with one Suno prompt in 4/4, changing only the tempo (`data/suno_prompts.md`). All six have arrived. The first 80 BPM request came out at 122 BPM; a retake in a slow genre hit 80.5 BPM (see below). Run `python run.py`; the full numbers are in `results.md` and `results.json`.

No search is limited by row borders:
- The pulse is searched over 0.25 to 2 s.
- The harmonic rhythm is searched over 1 to 8 s. It is the period of chord changes, taken from the harmonic-change curve of the pitched stems (`pts.periodicity.harmonic_change`).

## Result

| Requested | Pulse measured | 4/4 bar | Z of the bar | Row | Harmonic rhythm | ΔZ to the pulse |
|---|---|---|---|---|---|---|
| 80 BPM | **122.0 BPM** (not 80) | 1.966 s | 15.98 | 4 | 7.858 s = 16 pulses = 4 bars | 3.999 |
| 80 BPM, retake | **80.5 BPM** | 2.980 s | **16.58** | **5** | 2.980 s = 4 pulses = **1 bar** | 2.000 |
| 100 BPM | 100.0 BPM | 2.400 s | **16.26** | **5** | 4.799 s = 8 pulses = 2 bars | 3.000 |
| 120 BPM | 121.1 BPM | 1.983 s | 15.99 | 4 (by 0.01) | 3.970 s = 8 pulses = 2 bars | 3.002 |
| 140 BPM | 141.6 BPM | 1.695 s | **15.76** | **4** | 1.691 s = 4 pulses = **1 bar** | 1.997 |
| 160 BPM | 164.1 BPM | 1.463 s | **15.55** | **4** | 2.928 s = 8 pulses = 2 bars | 3.001 |
| 174 BPM | see below | **1.380 s** | **15.46** | **4** | 5.522 s = 16 beats = 4 bars | 2.001 to the bar |

**174 BPM.** The drum pattern is a breakbeat. It repeats most strongly once per bar (1.3797 s, comb 0.87), then every half bar (0.69 s, 87 BPM, 0.77), and most weakly every beat (0.345 s, 174 BPM, 0.63). The pulse rule therefore returned the bar. That bar is exactly 4 × 0.345 s, so the track runs at 174.0 BPM as requested. Whether to tap at 174 or at 87 is a real ambiguity of the genre, not a measuring error. A pulse definition that can return 174 or 87 here is still open.

**80 BPM requested, about 122 BPM generated.** The drums have no periodicity at 80 BPM (r = 0.13 at 0.75 s). They repeat at 122 BPM (r = 0.86) and at its half, 61 BPM (r = 0.81). Suno ignored the requested tempo and returned its usual dance tempo. Measured as it is, the track agrees with the rule (bar at Z 15.98, row 4), but it could not test the prediction for a real 80 BPM bar.

**80 BPM retake** (downtempo hip hop prompt, `data/suno_prompts.md`): 80.5 BPM. The bar lands at **Z 16.58, row 5, exactly the value predicted before measuring**. The chord changes, found independently, fall every 4.00 pulses (ΔZ = 2.000), once per bar as requested. Both periodicities are weaker than in the electronic tracks (drum comb 0.34–0.38, harmonic r = 0.14), because a boom-bap pattern is less regular.

**Corrected on 2026-11-12 (issue #7).** The confirmation test now separates a candidate from a proven period. On this retake the pulse is confirmed (42 σ), so the bar at Z 16.58 stands. The chord-change period is **not** confirmed: it reaches 4.8 σ, below the 5 σ threshold, and is not stable in both halves. The earlier sentence "the two independent cues agree exactly" was too strong. The bar here rests on the pulse alone.

## What it shows

1. **The bar crosses the Z 16 border with tempo, as option A predicts.** At 80.5 BPM the bar is at Z 16.58 and at 100 BPM at Z 16.26, both in row 5 (Bar), both predicted in this file before measuring. At 100 BPM the bar is at Z 16.26, in row 5 (Bar). This value was predicted in this file before the track was measured. At 121 BPM the bar is at Z 15.99, right on the border. At 142, 164 and 174 BPM it is at Z 15.76, 15.55 and 15.46, all in row 4 (Beat). A 4/4 bar is therefore an element whose Z depends on tempo, and the border at Z 16 has to cut through it. This is a physical fact about the absolute axis, not an error of the table.
2. **The metric levels nest exactly where the chord changes are confirmed.** The harmonic rhythm sits at ΔZ = 3.000, 3.002, 1.997, 3.001 and 2.001 from the pulse or the bar, log₂ 4 and log₂ 8 within 0.003.

   **Corrected on 2026-11-12 (issue #7).** The chord-change period is confirmed (issue #7: at least 5 σ, at least 4 repetitions, stable in both halves) at 100, 120, 140 and 160 BPM only (7.9 to 18 σ). At the track requested at 80 BPM (122 BPM), at the 80 BPM retake and at 174 BPM it is not confirmed (2.1 to 5.6 σ, not stable in both halves). The claim "at every tempo" was too strong: it holds for four of the seven tracks.
3. **Suno did not follow "chord changing once per bar" exactly.** The chords change every bar at 140 BPM, every 2 bars at 100, 120 and 160, and every 4 bars at 174. This is useful in itself: the harmonic rhythm is a Makeup-group element with its own period, separate from the meter.

## Limits

- The bar is taken as 4 pulses because the prompt asked for 4/4. Nothing here measures the meter independently: no harmonic or drum cue separated 4/4 from 2/4. Tracks in 3/4 and 6/8 are needed to test that.
- The harmonic-rhythm peaks at 160 and 174 BPM are weak (r = 0.22 and 0.18).
- The electronic-groove prompt pulled Suno towards about 120 BPM; naming a slow genre fixed it. The genre changed between the 80 BPM retake and the rest of the series, which is a small confound.
