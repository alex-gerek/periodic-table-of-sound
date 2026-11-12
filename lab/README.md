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
- **Variation:** fills every 4 bars give exactly 4 bars, including one-beat fills. Random fills give variation without a period. A rhythm without fills gives no variation; the threshold is 0.1, because fills reach 0.17 to 0.19 and timing noise reaches about 0.07 at slow tempos.
- **Vibrato, Spatial motion and Width arc** are found at the set rate or length.
- **Controls:** with all six elements on, each one disappears when it is removed.
- **Results follow the recipe.** Changing any dial or checkbox clears the old results, and *Run controls* measures the full recipe first.
- **No race (issue #8).** Each run works on a snapshot of the recipe and remembers its version. If the recipe changes before the run finishes, the result is dropped with a message, and the run buttons are disabled while a run is in progress. Checked by moving the tempo slider in the middle of a run.
- **Deterministic controls (issue #8).** The noise of hats and fills comes from a seeded generator instead of `Math.random()`. Two renders of the same recipe agree to 1.2·10⁻⁷ (one float32 rounding step), and a control without Variation matches the full sound up to the first fill.
- **Known false Variation at 150 BPM in 3/4** without fills (issue #10). It is older than #8 and comes from the synthesis: the downbeat renders differently from bar to bar.

Known limits:
- An 8-bar phrase needs at least three phrases in the sound to be proven.
- Thresholds were chosen on this battery, so they are sandbox rules, not results.

## How to hear Variation

- **Phrase** = how many bars until the fill comes back.
- **Fill length** = how many beats the fill takes.
- **Random** = 1 puts the same number of fills into random bars.

Compare Random = 0 with Random = 1 at the same settings. The amount of change is the same; only the order differs. The detector hears the difference as "period of N bars" against "no period".
