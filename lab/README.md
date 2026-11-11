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

- **Pulse:** correct at every setting without fills, from 60 to 200 BPM. With loud fills the pulse may come out as the half-beat (100/4 and 80/4). The bar and phrase lengths are still right.
- **Meter:** correct at 8 of 8 settings (2, 3, 4, 5, 6 and 7 beats, 66 to 200 BPM). No meter is reported for the 3 rhythms without accents.
- **Variation, fills at the end of each phrase:** the period is found at 6 of 7 settings (2, 3, 4 and 8 bars, 100 to 174 BPM). The one miss is an 8-bar phrase at 90 BPM, where fewer than three phrases fit into the sound.
- **Variation, random fills:** reported as variation without a period at 4 of 4 settings, so no false periods.
- **No fills:** no variation at 2 of 2 settings.
- **Vibrato, Spatial motion and Width arc** are found at the set rate or length at every setting.
- **Controls:** each of the six elements disappears when it is removed.

## How to hear Variation

- **Phrase** = how many bars until the fill comes back.
- **Fill length** = how many beats the fill takes.
- **Random** = 1 puts the same number of fills into random bars.

Compare Random = 0 with Random = 1 at the same settings. The amount of change is the same; only the order differs. The detector hears the difference as "period of N bars" against "no period".
