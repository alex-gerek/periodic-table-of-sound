# Material request

*2026-11-10. What the next measurements need, in order of value.*

For every item: export **stems as WAV at 48 kHz**, the same way as the existing Suno exports. Put the tempo and meter you asked for in the folder name, for example `tempo_140_4-4`. The audio stays out of git; tell Claude where the folders are.

Every item below has a known answer that is fixed before measuring. This is ground truth by construction, not a listening test.

## 1. Tempo series (for the Z 16 border)

Six tracks in **4/4**, same style and same prompt, with only the tempo changed: **80, 100, 120, 140, 160, 174 BPM**. A steady electronic style with a clear kick is best.

- **Tests:** Meter crosses the Z 16 border at 120 BPM, and Z(Meter) − Z(Pulse) stays 2.00 at every tempo. See `docs/z16_border.md`.
- **Note:** Suno may not hit the exact tempo. That is fine, because we measure the tempo; the prompt only has to spread the tracks out.

## 2. Other meters

- **3/4** (a waltz), **6/8** (a shuffle or ballad), **5/4**, and **7/8** if Suno manages it.
- One track each, stems, with the meter in the folder name.
- **Tests:** Z(Meter) − Z(Pulse) should be log₂ 3 = 1.585 for 3/4, and so on. If Suno drifts back to 4/4, the measurement will show that too.

## 3. Natural vibrato

- **Two or three AI vocals with strong vibrato:** opera, soul ballad, classical crossover. Long held notes help.
- **Optional, the most valuable:** one human recording of any singer, even on a phone. Hold a few long notes **straight**, then the same notes **with vibrato**, and say in the file name which is which.
- **Tests:** the detector is now calibrated. It finds 15 cents of vibrato written into a real vocal (r = 0.33) and stays silent without it (r ≤ 0.09). It needs natural vibrato to measure the real rate and depth, and to tell whether AI vocals lack vibrato or only these three songs do.

## 4. A vocal with a usable level on Metro (optional)

The Metro lead vocal stem is almost silent: it is voiced in under 0.1% of frames. If there is a version with a louder vocal, its stems would let Metro count in the vocal measurements.

## 5. A loop with a known length (optional)

One track built in REAPER from a single loop of known length, for example 4 bars repeated, with parts muted and unmuted in sections. Note the loop length and tempo.

- **Tests:** the Loop element, which is not yet well defined. Claude can also build such tests by tiling a few bars of the existing stems, so this item is optional.

## What Claude does without new material

- Writes known effects into existing stems to check each detector: vibrato (done), echo at one beat, loops built by tiling.
- Checks the period borders against the perception literature.
- Investigates the beat-locked 2 Hz movement in the pitch of the GRAVITY vocal. One hypothesis is a vocal delay at one beat, which would be an Echo element (Space) showing up in the pitch track. This is not verified.
