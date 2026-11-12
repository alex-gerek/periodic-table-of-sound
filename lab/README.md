# Lab: Sound Collider (sandbox)

`collider.html` opens in any modern browser by double-click. Pick elements, set their dials and press **Collide**. The page synthesises the sound from scratch (Web Audio, no samples) and plays it. It then runs simplified detectors on the separate stems (rhythm, melody, pad), without reading the recipe. **Run controls** removes each element in turn, and the detector must stop finding it.

This is a sandbox for listening and exploring. Official results come only from `pts/` in Python. The pulse, meter and variation rules in the page are provisional and are marked as such in the code.

## Elements

| Element | Group, cell | What you hear | Detector |
|---|---|---|---|
| Pulse | Periodicity | a kick on every beat, a hat between | the shortest clear repeat of the rhythm onset envelope |
| Meter | Periodicity | an accented kick and a low bass note on beat 1 | the median beat strength at each position of an n-beat cycle, with beats followed one by one |
| Variation | Irregularity, **predicted cell** | a snare fill in the last bar of every phrase, or in random bars | each bar compared with the median bar; a period only if the bars that stand out sit on an exact grid (80% precision and 80% recall) |
| Vibrato | Periodicity (second-order) | a swing in the pitch of the held melody notes | the pitch track of the melody, with note steps removed |
| Spatial motion | Space, **predicted cell** | the melody travels left to right and back | the period of the melody's left–right balance |
| Width arc | Space, **predicted cell** | the pad opens from mono to wide | the period of the pad's side-to-mid energy |

## Check on 2026-11-11 (in the browser)

A battery of 18 settings, from 60 to 200 BPM in 2 to 7 beats per bar, with no fills, fills of one or two beats every 4 bars, and random fills. Pulse, meter and variation must all be right for a setting to pass.

- **18 of 18 settings pass.**
- **Pulse:** the comb rule picks the beat even when fills make the half-beat loud. The previous rule failed at 100/4 and 80/4 with fills.
- **Meter:** 2 to 7 beats are correct, and no meter is reported for a rhythm without accents.
- **Variation:** fills every 4 bars give exactly 4 bars, including one-beat fills. Random fills give variation without a period. A rhythm without fills gives no variation; the threshold was 0.1, because fills reached 0.17 to 0.19 and timing noise reached about 0.07 at slow tempos. That noise turned out to be errors in the render and the grid; see the check of 2026-11-12, where the threshold becomes 0.02.
- **Vibrato, Spatial motion and Width arc** are found at the set rate or length.
- **Controls:** with all six elements on, each one disappears when it is removed.
- **Results follow the recipe.** Changing any dial or checkbox clears the old results, and *Run controls* measures the full recipe first.
- **No race (issue #8).** Each run works on a snapshot of the recipe and remembers its version. If the recipe changes before the run finishes, the result is dropped with a message, and the run buttons are disabled while a run is in progress. Checked by moving the tempo slider in the middle of a run.
- **Deterministic controls (issue #8).** The noise of hats and fills comes from a seeded generator instead of `Math.random()`. Two renders of the same recipe agree to 1.2·10⁻⁷ (one float32 rounding step), and a control without Variation matches the full sound up to the first fill.
## Check on 2026-11-12: false Variation (issue #10)

At 150 BPM in 3/4 without fills, the detector reported "variation without a period". There were four causes. Two were in the sound and two were in the detector, and each one alone was enough to break some settings.

1. **The same hit did not render the same.** Web Audio evaluates parameter automation in blocks of 128 frames, and the result depends on where a hit falls inside its block. The same downbeat kick differed by up to 1.9, at a peak of 1.5, from one bar to the next, and the hats by up to 0.76. *Fix:* every distinct hit is rendered once, from frame 0, and copied into the rhythm stem at a whole-sample offset. Bars written the same are now equal sample for sample, and two renders of a recipe are identical (before: 1.2·10⁻⁷).
2. **The bar grid drifted.** The tracker places its first beats before it locks on, and a least-squares fit followed them: the beat came out as 0.39985 s instead of 0.4 s, and the cuts drifted by about 14 ms over the sound. *Fix:* a robust fit (Theil–Sen, the median slope over all pairs of beats), and bars cut from the downbeat, so that a fill is not split between two bars.
3. **The pulse depended on the frame phase.** A beat is rarely a whole number of 5 ms frames (at 110 BPM it is 109.3), so the onset curve was spiky. The beat correlated at 0.71 while the bar reached 0.995, and the pulse rule chose the bar. *Fix:* the pulse is searched on the onset curve smoothed by a ±15 ms triangle.
4. **The meter median was biased.** With an even count it took the upper of the two middle values, and a 4-beat bar at 90 BPM read as 6 beats. *Fix:* a true median.

With the sound and the grid correct, plain bars differ by at most **0.0035** and the weakest fill (one beat at 200 BPM in 3/4) gives **0.081**. The Variation threshold is now **0.02**, between the two; the old 0.1 was set when the errors above made plain bars differ by up to 0.07.

**Battery:** 15 tempos (60 to 200 BPM) × 6 meters (2 to 7 beats) × 4 fill modes (none, one beat every 4 bars, two beats every 4 bars, random) = 360 settings. Pulse, meter and variation must all be right.

| | No fills | One-beat fills | Two-beat fills | Random fills | Total |
|---|---|---|---|---|---|
| Before (#8) | 81 / 90 | 67 / 90 | 75 / 90 | 81 / 90 | **304 / 360** |
| **After (#10)** | **90 / 90** | **90 / 90** | **90 / 90** | **89 / 90** | **359 / 360** |

- The one failure is 60 BPM in 2/4 with random two-beat fills: a fill then fills the whole bar with sixteenths, and the pulse reads 120 BPM. It is left as a known limit, not tuned away.
- The controls still pass: with all six elements on, each one disappears when it is removed.
- The guard from #8 still holds: changing the recipe in the middle of a run drops the result.

Known limits:
- An 8-bar phrase needs at least three phrases in the sound to be proven.
- Thresholds were chosen on synthetic batteries, so they are sandbox rules, not results.
- The sound is clean by construction. Real recordings have timing noise that this battery does not have, so the threshold of 0.02 is a sandbox value, not a rule for `pts/`.

## How to hear Variation

- **Phrase** = how many bars until the fill comes back.
- **Fill length** = how many beats the fill takes.
- **Random** = 1 puts the same number of fills into random bars.

Compare Random = 0 with Random = 1 at the same settings. The amount of change is the same; only the order differs. The detector hears the difference as "period of N bars" against "no period".
