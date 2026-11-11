# How the table is ordered

*Second edition, 2026-11-10.*

Mendeleev first ordered the chemical elements by atomic mass. The order was nearly right, but a few pairs landed in the wrong place, for example tellurium and iodine. Moseley later found the true key by measuring the frequency of each element's X-rays. That measurement gave the atomic number Z, a single integer that can be read off an instrument.

The Periodic Table of Sound follows the same path. Its first edition named rows after music theory (tone, beat, bar). The second edition replaces those names with a number measured on the signal.

## 1. Order: time octave Z

Every element has its own characteristic time τ: the period of its vibration, the length of its pattern, or the spacing of its repeats.

    Z = log2(τ / 1 s) + 15

One step of Z doubles τ.

| Landmark | τ | Z |
|---|---|---|
| Upper limit of hearing, 20 kHz | 50 µs | 0.6 |
| A4, 440 Hz | 2.27 ms | 6.2 |
| 20 Hz, where rhythm turns into pitch | 50 ms | 10.7 |
| Vibrato, 6 Hz | 167 ms | 12.4 |
| Pulse at 120 BPM | 0.5 s | 14 |
| 4/4 bar at 120 BPM | 2 s | 16 |
| Phrase of 8 bars | 16 s | 19 |
| Song of 4 minutes | 240 s | 22.9 |

Music spans about 23 octaves of time. Elements that live in a range, such as pitch (20 Hz to 5 kHz), are placed by their typical τ. The range is recorded next to it.

The elements are numbered in order of increasing Z, like atomic numbers. When two elements share the same Z, the order of the groups below decides.

## 2. Group: the question asked of the signal

In chemistry, properties repeat because the outer electron configuration repeats from shell to shell. In sound, what repeats is the **kind of quantity**: the same question can be asked of a signal at any time scale.

| Group | Question | Examples from fast to slow |
|---|---|---|
| Level | How strong is it? | amplitude, envelope, crest, momentary loudness, groove, energy arc, integrated loudness |
| Periodicity | What repeats, and how often? | frequency, pitch, subdivision, pulse, meter, loop, repetition |
| Irregularity | How far from regular is it? | white noise, grit, consonant, swing, drift |
| Change | Where does it start, end or turn? | click, attack, decay, kick hit, downbeat, phrase boundary, section |
| Makeup | Which components, in what proportions? | formant, harmonic pattern, shimmer, chord, key |
| Space | Where is it, and how do signals relate? | channel correlation, pan, echo, reverb tail |

**Test of the grouping.** Compress an element in time by 2^k. It must turn into another element of its own column. For example, a 120 BPM pulse sped up 32 times becomes a 64 Hz tone, five rows higher in Periodicity. This test can be run on synthetic signals with a known answer, without listening.

## 3. Periods: borders of hearing

Rows end where hearing changes how it treats time. The values below are approximate and still have to be checked against the literature.

| Period | τ | Z | Why the border is there |
|---|---|---|---|
| 1. Wave | < 2 ms | < 6 | Two clicks closer than about 2 ms fuse into one; time is heard as color. |
| 2. Tone | 2 – 50 ms | 6 – 10.7 | Repeats faster than about 20 per second are heard as pitch. |
| 3. Event | 50 – 250 ms | 10.7 – 13 | Single notes, syllables and fast rhythms: too slow for pitch, too fast to tap. |
| 4. Beat | 0.25 – 2 s | 13 – 16 | The range in which a pulse can be felt and tapped. |
| 5. Bar | 2 – 8 s | 16 – 18 | About the length of the perceived present moment. |
| 6. Phrase | 8 – 32 s | 18 – 20 | Held in short-term memory as one musical sentence. |
| 7. Form | > 32 s | ≥ 20 | Only memory connects it: sections, returns, the whole song. |

## 4. Stability: defects are unstable forms

A defect is not a group of its own. Radioactivity is a property, not a column of Mendeleev's table, and in the same way a defect sits in the group of the healthy element it corrupts and is marked as unstable. All 11 known defects fit:

| Defect | Group | Corrupted element |
|---|---|---|
| Clipping | Level | amplitude hitting the ceiling |
| Harsh burst | Level | a short level spike in the presence band |
| Aliasing | Makeup | false components folded back from above Nyquist |
| Resonance | Makeup | a narrow bump that rings over every note |
| Intermodulation | Makeup | sum and difference tones from a nonlinearity |
| Ghost partials | Makeup | tones that belong to no note |
| Fizz | Irregularity | noise that follows the music instead of the room |
| Warble | Irregularity | unstable pitch and phase in sustained notes |
| Smear | Change | an attack blurred over tens of milliseconds |
| Seam | Change | a false boundary where two generated segments meet |
| Kick-bass clash | Space | kick and bass in opposite phase in one band |

This also serves the idea of making music from AI artifacts: each artifact has a healthy neighbour from which it can be told apart by measurement.

## 5. Second-order elements

Some elements ask their question of another element's track instead of the raw signal. Vibrato is the periodicity of the pitch track. Sidechain pump is the periodicity of the level track. Swing is the irregularity of the pulse. Drift is the irregularity of pitch at slow scales. Glide, timbre motion and modulation are changes of pitch, formants and key.

The group follows the question. The inner element is recorded with the element and marked with a superscript 2 in the table.

## 6. Predicted cells

Empty cells of the grid are predictions, because the grid was not drawn around the known elements. The second edition has six:

| Cell | Group, period | Relatives in practice |
|---|---|---|
| Variation | Irregularity, Phrase | drum fills, humanization |
| Novelty | Irregularity, Form | computable from the repetition clusters of PHARMAKON's Track Map |
| Tonal palette | Makeup, Form | key-finding profiles |
| Spatial motion | Space, Bar | tempo-synced auto-pan |
| Width arc | Space, Phrase | build-ups that widen into a drop |
| Stereo form | Space, Form | narrow verse, wide chorus |

## 7. What is not proven yet

- The τ values are typical estimates, not measurements. Phase 1 measures them on the ground-truth stems.
- The period borders come from the perception literature and need to be checked against sources.
- The time-compression test has not been run yet.

The table is confirmed when measured elements fall into their predicted cells and the compression test passes in every column.
