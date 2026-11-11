# The Z 16 border and the two time axes

*Open question, 2026-11-10.*

## The problem

The second edition cuts the Beat and Bar rows at Z 16, which is 2 s. Metro runs at 132 BPM, so its 4/4 bar is 1.82 s long, Z 15.86. By the Z rule that bar sits in the Beat row. A 4/4 bar at 100 to 140 BPM lasts 1.7 to 2.4 s, so in ordinary club music the bar lands right on the border.

## What we had missed: there are two time axes

The rows are an **absolute** axis. Z is measured in seconds, and the borders come from hearing: what can be tapped as a pulse, the length of the present moment.

Metric levels are **relative**. A subdivision, a beat, a bar and a phrase are defined by counting the track's own pulse, whatever its tempo. The first edition named rows after metric levels (Beat, Bar, Phrase) and then cut them at absolute times. The conflict comes from mixing the two axes.

The measurements show the relative axis clearly. Differences of Z between metric levels are logarithms of whole numbers, independent of tempo:

| Track | Tempo | Z(Pulse) − Z(Subdivision) | Z(Meter) − Z(Pulse) | Z(Loop) − Z(Meter) |
|---|---|---|---|---|
| GRAVITY | 119 BPM | 2.009 (= log₂ 4) | 2.000 (= log₂ 4) | 2.805 (≈ log₂ 7, suspicious) |
| Metro | 132 BPM | 1.001 (= log₂ 2) | 3.000 (= log₂ 8, two bars) | 1.997 (= log₂ 4) |
| Pure voltage | 111 BPM | not found | 1.992 (= log₂ 4) | 2.006 (= log₂ 4) |

This is the same arithmetic as musical intervals. An octave is ΔZ = 1 (ratio 2). A bar of 3/4 over its pulse would be ΔZ = log₂ 3 = 1.585, the ratio of an octave plus a fifth. The idea that rhythm ratios and pitch ratios are one system is not new. Henry Cowell described it in *New Musical Resources* (1930), and Karlheinz Stockhausen built on it in "…wie die Zeit vergeht…" (1957). What is new here is that we measure it on the stems, element by element.

## Options

**A. Keep the absolute rows and give metric elements a second coordinate (recommended).**
- Z stays the physical axis. The compression test only makes sense on it.
- Borders are drawn as zones about ±0.3 Z wide, because perception has no sharp line. The exact values are taken from the literature.
- Meter, Subdivision, Loop and Phrase are elements whose Z depends on tempo. Meter spans rows 4 and 5.
- Each metric element also carries its **metric interval**, ΔZ to the pulse: 2 for a 4/4 bar, 1.585 for 3/4, 1 for 8ths, 2 for 16ths.
- No detector is ever limited by row borders.

**B. Make rows 3 to 6 relative to the track's pulse.**
The rows would then follow music theory. The table would lose its physical axis, and the compression test would lose its meaning. Not recommended.

**C. Move the border to Z 16.5 (about 2.8 s).**
This would only move the conflict to slower tempos: a 4/4 bar at 85 BPM is 2.8 s. Not recommended.

## Testable predictions of option A

1. In a series of 4/4 tracks from about 80 to 175 BPM, Z(Pulse) moves with tempo, but Z(Meter) − Z(Pulse) stays 2.00 ± 0.01. Meter crosses Z 16 at 120 BPM.
2. In 3/4 tracks, Z(Meter) − Z(Pulse) = 1.585. In 6/8 and 7/8 the intervals follow the counted grouping.
3. The perceptual borders, checked against the literature, stay where hearing puts them, independent of any track.

Predictions 1 and 2 need new material: a tempo series and tracks in other meters. See [`data/material_request.md`](../data/material_request.md).
