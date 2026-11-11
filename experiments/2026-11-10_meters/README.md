# 2026-11-10: meter test (answers that are not powers of two)

All the earlier tracks nested in powers of two. A method that leans towards doubling would give the same numbers, so these tracks have 3 as the right answer. Prompts are in `data/suno_prompts.md`, Series 2. Run `python run.py`; the numbers are in `results.md`.

## 3/4 waltz

- **Requested:** 120 BPM.
- **Generated:** a fast waltz at **182.4 BPM** (beat 0.3289 s). Suno ignored the tempo again, but not the meter.

Autocorrelation of the onset envelope at multiples of the beat:

| Beats | 1 | 2 | **3** | 4 | 5 | **6** | 8 | **9** | **12** |
|---|---|---|---|---|---|---|---|---|---|
| Drums | 0.40 | 0.39 | **0.83** | 0.37 | 0.38 | **0.78** | 0.35 | **0.71** | **0.64** |
| Bass | 0.05 | 0.00 | **0.23** | −0.02 | 0.00 | **0.23** | −0.03 | **0.20** | **0.22** |
| At 0.5 s (the requested 120 BPM) | | | | | | | | | drums −0.06, bass −0.08 |

- **Peaks stand only at multiples of 3.** There is no peak at 2, 4 or 8 beats. The drums and the bass are separate stems and agree.
- **The bar is 3 beats:** ΔZ(bar − beat) = log₂ 3 = 1.585.
- **The chords change every 1.967 s:** 6 beats, or 2 bars, ΔZ = log₂ 6 from the beat.
- **The method sees 3. It has no bias towards doubling.**

**A correction to the script.** The pulse rule picked the bar (0.987 s, 60.8 BPM) as the "pulse", because the bar repeats much more strongly (0.83) than the single beat (0.40). This is the same thing that happened with the 174 BPM breakbeat. The script then compared 2, 3 and 4 of *those* pulses, that is bars, and printed "drums say 2". That line is meaningless: it counts bars, not beats. The triple structure shows instead as the division of the pulse: 1/3 scores 0.49 against 0.37 for 1/2. The table above, at multiples of the beat, is the clean result.

**What this teaches about the pulse.** When the bar is much stronger than the beat, the "shortest strong period" rule returns the bar. A pulse needs a better definition: the finest level that is still regular, not the strongest one. This is now the second case after drum and bass.

## 6/8

- **Requested:** 6/8, about 60 dotted-quarter beats per minute, no vocals.
- **Generated:** a track with lead and backing vocals, despite the exclusion. The finest regular unit is 0.2337 s (256.7 per minute). The pulse rule gives 127.9 BPM, which is 2 units.

Autocorrelation of the onset envelope at multiples of the unit:

| Units | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 9 | 12 | 16 | 18 | 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Drums | 0.38 | 0.40 | **0.47** | 0.43 | 0.29 | 0.44 | 0.30 | 0.30 | 0.27 | 0.32 | 0.16 | 0.13 |
| Percussion | 0.42 | **0.51** | 0.41 | **0.50** | 0.37 | 0.46 | **0.46** | 0.34 | 0.40 | 0.35 | 0.31 | 0.27 |
| Bass, keyboard, guitar | flat, falling slowly: no grouping | | | | | | | | | | | |

- **Chord changes:** the strongest candidates are 7.50 s (32 units) and 3.76 s (16 units), both powers of two. The peak is weak (r = 0.23).

**Verdict: inconclusive, leaning binary.** Nothing in this track groups clearly in threes:
- The drums lean slightly towards 3 (0.47 at 3 units against 0.40 and 0.43 at 2 and 4), but not cleanly.
- The percussion groups in 2, 4 and 8.
- The chords change every 16 or 32 units.

The most likely reading is that Suno made a binary groove at about 128 BPM with some triplet figures, not a 6/8. This is the opposite situation from the waltz. There Suno ignored the tempo but kept the meter; here it seems to have ignored the meter.

This does **not** count against the method: a method that finds 3 in a waltz and 2 here is reporting what is there. It does mean that the 6/8 test (pulse divided into 3, bar of 2 pulses) is not done yet. A retake prompt is in `data/suno_prompts.md`.

## 6/8, retake (Irish jig prompt)

The largest drum period is B = 0.5715 s. A real 6/8 divides each beat into three eighths, so the autocorrelation must peak at B/3. A binary beat peaks at B/2.

| Stem | B/3 (6/8 sign) | B/2 (binary sign) | B | 2B | 3B | 4B |
|---|---|---|---|---|---|---|
| Drums | −0.06 | 0.56 | 0.80 | 0.71 | 0.64 | 0.60 |
| Percussion | −0.08 | 0.58 | 0.77 | 0.69 | 0.65 | 0.62 |
| Strings (fiddle) | 0.01 | 0.44 | 0.44 | 0.39 | 0.35 | 0.32 |
| Woodwinds (whistle) | 0.00 | 0.38 | 0.35 | 0.31 | 0.30 | 0.26 |
| Guitar | 0.01 | 0.28 | 0.30 | 0.25 | 0.23 | 0.25 |

**Verdict: binary.** No stem shows a third of the beat; every one shows the half. Suno produced a straight, reel-like groove twice when asked for 6/8, even with a genre that is 6/8 by nature. The method agrees with itself across eight stems. The 6/8 test stays open, because Suno does not deliver 6/8 reliably. The waltz already shows that the method finds 3 when 3 is there.

## Real 6/8 attempt: Bach Partita No. 3 (Telmányi)

The recording splits at its 7 silences into the 7 movements, whose meters are known from the score (Preludio 3/4, Loure 6/4, Gavotte 2/2, Menuets 3/4, Bourrée 2/2, Gigue 6/8).

**Result: no meter is visible in any movement.** Only the note rate shows (for example 0.140 and 0.274 s in the Gigue). Correlations are weak (0.1 to 0.25) and fade within a few notes. A live soloist bends the tempo, so a repeat smears after a few beats. The fixed-lag autocorrelation needs a steady tempo. Live music needs beat tracking that follows the tempo, which is a separate task.

## Real 6/8 attempt: guitar phrase from Freesound

- **File:** `data/material/meters/meter_6-8_real/guitar_aede_6-8_llf0.wav`, 8.1 s, CC BY 3.0, by llf0. Classical guitar recorded on a phone.
- **Result: too short and too irregular to show a meter.** Each strum spreads its strings over 0.1 to 0.5 s, and the phrase ends in a fast tremolo. The gaps between strums are about 0.32 to 0.35 s, which is probably the eighth. The autocorrelation has no structure beyond 0.75 s.
- **What would work:** at least a minute of steady 6/8. The "March in 6/8" on Freesound (by JoshKayLowf) looks suitable; check that its licence is CC0 or CC BY.

## Real 6/8: "March In 6/8" (Freesound, CC BY 4.0)

- **File:** `data/material/meters/meter_6-8_real/march_6-8_joshkeylowf.wav`, 59.4 s, a solo-instrument piece composed in 6/8 by JoshKeyLowF. The first 53 s are used; the tail is silence.
- The eighth is u = 0.1377 s (the strongest repeat between 0.7 and 1.0 s, 0.8264 s, divided by 6). The dotted-quarter beat is 3u = 0.413 s, 145.2 per minute.

Autocorrelation of the onset envelope at multiples of the eighth:

| Eighths | 1 | 2 | **3** | 4 | 5 | **6** | 7 | 8 | **9** | 10 | 11 | **12** | **15** | **18** | **24** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r | 0.20 | 0.17 | **0.26** | 0.19 | 0.13 | **0.35** | 0.13 | 0.13 | **0.24** | 0.11 | 0.11 | **0.32** | **0.20** | **0.22** | **0.29** |

1. **The beat is divided into 3.** Every multiple of 3 eighths stands above its neighbours (3, 6, 9, 12, 15, 18, 24), while 2, 4, 8 and 10 do not.
2. **The bar is 2 beats.** 6 eighths (0.35) is stronger than 3 (0.26), and 12 (0.32) is stronger than 9 (0.24). The even numbers of beats win.
3. **This is 6/8 as written:** a beat of 3 eighths (ΔZ = log₂ 3 = 1.585) and a bar of 2 beats (ΔZ = 1).

The ΔZ values in point 3 follow from the grid; the evidence is the pattern of peaks in the table. The bar (0.826 s, Z 14.72) lies in row 4 at this tempo.

**The 6/8 test passes on a real recording.** Together with the waltz, the method finds 3 at both levels where it can occur: in the bar (3/4) and in the beat (6/8). It also finds 2 where Suno played 2. The metric interval is a measurable property, so it can go into the table.
