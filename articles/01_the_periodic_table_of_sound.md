# The Periodic Table of Sound: ordering music by time, and a collider to test it

*Lex Gerek, with Claude. November 2026.*

Mendeleev did not set out to describe every substance in the world. He looked for the few numbers that put the elements in order, and then he trusted that order enough to leave gaps in it. Three of those gaps were later filled by gallium, scandium and germanium, with almost exactly the properties he had predicted.

This project asks whether music can be ordered the same way. We do not mean genres, instruments or moods. We mean the elementary quantities that every piece of music is made of, such as a pitch, a pulse, a vibrato, a bar or a phrase. Can those be ordered by numbers that a machine can measure, and does the resulting order predict something we have not heard yet?

After two days of measurement, our answer is a careful yes. This article describes the table, how we tested it, and what the tests showed. It also describes a small "collider" in which new elements can be built from scratch and checked. Finally, it tries to convey how large the space of possible combinations is.

## 1. One number for order: the time octave Z

Mendeleev first ordered the elements by atomic mass, and a few pairs landed the wrong way round. Moseley later found the true key by measuring a frequency, the X-ray line of each element, and that frequency gave the atomic number.

Our key is also a frequency, or rather its inverse. Every element of sound has its own characteristic time τ: the period of a vibration, the spacing of a pulse, or the length of a bar or a phrase. We place it on a logarithmic axis:

**Z = log₂(τ / 1 s) + 15**

One step of Z doubles the time. The whole of music fits into about 23 steps:

| Landmark | τ | Z |
|---|---|---|
| The top of hearing, 20 kHz | 50 µs | 0.6 |
| The note A4, 440 Hz | 2.27 ms | 6.2 |
| 20 Hz, where repeats turn into pitch | 50 ms | 10.7 |
| A pulse at 120 BPM | 0.5 s | 14 |
| A 4/4 bar at 120 BPM | 2 s | 16 |
| A song of four minutes | 240 s | 22.9 |

## 2. Six questions instead of eight families

In chemistry, properties repeat because the outer electron shells repeat. In sound, what repeats is the kind of question you can ask of a signal. The question stays the same at every time scale:

| Group | Question |
|---|---|
| Level | How strong is it? |
| Periodicity | What repeats, and how often? |
| Irregularity | How far from regular is it? |
| Change | Where does it start, end or turn? |
| Makeup | Which components, in what proportions? |
| Space | Where is it, and how do signals relate? |

Read a column from top to bottom and the same question returns at slower and slower scales. In the Periodicity column, for example, the sequence runs frequency, pitch, subdivision, pulse, meter, loop, repetition. This is the periodic law of our table, and it can be tested. **Compress an element in time and it must turn into another element of its own column.** We played 32 seconds of a real drum stem 32 times faster. A pitch detector, a tool that knows nothing about rhythm, found a note whose period, multiplied back by 32, was exactly 2.00, 2.00 and 1.00 pulses of the original on three tracks (within 0.3%). The rhythm had turned into pitch in the same column, exactly five octaves of Z lower.

Elements can also ask their question of another element's track rather than of the raw sound. Vibrato is the periodicity of the pitch track. A sidechain pump is the periodicity of the level track. We call these second-order elements.

Defects are not a family of their own. Radioactivity is a property, not a column of Mendeleev's table, and in the same way a defect sits in the group of the healthy element it corrupts. Clipping is a broken level, a smear is a broken attack, and a seam is a false boundary. All eleven defects we know found a home this way.

## 3. What we measured, and how we kept ourselves honest

The rule of the project is *measure, don't guess*. Every claim needs a number, a test against a known answer, and a check on data the method has not seen. Listening is never the deciding argument. All measuring code is our own and depends only on numpy for arrays and the FFT.

| Claim | How it was tested | Result |
|---|---|---|
| The bar is an element whose Z moves with tempo | Six Suno tracks in 4/4. The Z values for 80.5 and 100 BPM were written down **before** measuring | Z 16.58 and 16.26 as predicted. Above about 120 BPM the bar falls below Z 16, into the Beat row |
| Metric levels nest as logarithms of whole numbers | Chord changes, measured independently of the drums | ΔZ = log₂ 4 or log₂ 8 within 0.003, on the four of seven tracks where the chord-change period is confirmed |
| A best peak is not yet a period | A confirmation test on held-out noise and on real drums whose beat was destroyed | 0% false periods, where the bare peak rule gave 100% |
| The method has no hidden bias towards doubling | A waltz, and a real 6/8 march from Freesound | Three beats per bar in the waltz; three eighths per beat and two beats per bar in the march |
| Natural vibrato lives in the Event row | Two operatic voices and a historic solo violin, with a piano as a control | Z 12.3 to 12.5. The piano gave no false alarms, and vibrato we wrote into it was found at the written rate |
| The detector can say no | Two Suno tracks requested in 6/8 | Both came out binary, and the method said so |

Some results surprised us. Asked for 80 BPM, Suno returned a track at 122 BPM; asked for a 6/8 jig, it twice returned a straight groove. In the Suno voices, vibrato often starts only at the end of a long note. This is a candidate fingerprint of generated singing, not yet a finding, because we still need a human reference recording.

Some things did not work, and we have kept them in the record. A live violinist bends the tempo so much that our fixed-lag method cannot see the meter. Vibrato inside a mix, such as a violin over a piano, is still unsolved. The pulse itself still lacks a clean definition: in a breakbeat or a fast waltz the strongest repeat is the bar, not the beat.

## 4. Predicted cells and the collider

The grid of six questions by seven time scales has empty cells. Mendeleev wrote down the expected properties of his gaps. We go one step further: we build the predicted element from scratch, then check by measurement that it lands in its cell.

The **Sound Collider** is a single web page. You choose elements and set their dials, such as tempo, beats per bar, vibrato rate, phrase length or the cycle of a stereo movement. The page synthesises the sound from first principles, with no samples, and plays it. Detectors then search the separate stems without being told the recipe, and a control run removes each element in turn, after which the detector must stop finding it.

Three predicted cells can already be heard:
- **Variation:** a drum fill closes every phrase. The detector finds a period of exactly 2, 3, 4 or 8 bars. When the same fills are scattered at random, it reports variation without a period, and no false periods appear.
- **Spatial motion:** the melody travels from left to right once per cycle.
- **Width arc:** the stereo image opens from mono to wide over a set number of bars.

In the browser check, the pulse was correct at every setting without fills. The meter was correct at 8 of 8 settings (2 to 7 beats), the variation period at 6 of 7, and every control passed. The collider is a sandbox. Official results come only from the Python code, and the provisional rules inside the page are marked as provisional.

## 5. How large is the space?

The third edition of the table holds 70 elements. Eleven are defects; we leave them out, and 59 stable elements remain. If each element can be present or absent, the number of possible sets is

**2⁵⁹ ≈ 5.8 × 10¹⁷**

which is about the number of seconds since the Big Bang (≈ 4.4 × 10¹⁷).

Compounds of a few elements:

| Elements in the compound | Possible compounds |
|---|---|
| 2 | 1,711 |
| 3 | 32,509 |
| 5 | 5,006,386 |
| 8 | 2,217,471,399 |
| 10 | 62,828,356,305 |

Now give every element a dial. With five settings each, plus "off", the count becomes

**6⁵⁹ ≈ 8.1 × 10⁴⁵**

With ten settings it becomes about 2.8 × 10⁶¹. For scale, the observable universe contains roughly 10⁸⁰ atoms.

A more modest "molecule" has a few elements with five settings each. Allowing thirty seconds of listening per variant:

| Compound | Variants | Listening time |
|---|---|---|
| 3 elements | 4,063,625 | about 4 years |
| 5 elements | 15,644,956,250 | about 15,000 years |
| 8 elements | 866,199,765,234,375 | about 800 million years |

And each of these is only a formula. The formula "waltz, vibrato, fills every four bars" can be realised by countless different melodies, so the number of distinct sounds is larger still by many orders of magnitude.

Two conclusions follow. First, nobody will ever explore this space by trying everything. Its value lies in the rules that cut it down, such as consonance through the harmonic series and metric levels that nest as whole numbers, and in measurements that show where real music actually lives. Second, some parts of it are small enough to explore completely. Six questions asked of the tracks of 59 elements give 354 possible second-order elements, and the table contains only ten of them so far.

## 6. Relatives and prior work

None of the individual ideas here is entirely new, and we want to name their relatives:
- Henry Cowell (*New Musical Resources*, 1930) treated rhythm ratios and pitch ratios as one system. Karlheinz Stockhausen ("…wie die Zeit vergeht…", 1957) built a continuum from rhythm to pitch.
- The musical dice game attributed to Mozart, and later the algorithmic music of Iannis Xenakis, generated music by combination.
- The perceptual borders of our rows come from the literature on the limits of pulse and the perceived present. They still have to be checked properly against those sources.

What is our own is the combination: a single measured axis, six questions, defects as unstable forms, a falsification test for every column, and a collider that builds and checks elements predicted by the table.

## 7. What is not proven yet

- Most τ values in the table are typical estimates. Only the elements marked ✓ have been measured.
- The period borders are drawn as zones about ±0.3 Z wide, and they need checking against the perception literature.
- The pulse needs a definition that returns the beat rather than the strongest repeat.
- Meter in live, tempo-bending performance, and vibrato inside a mix, are open problems.
- The idea that generated audio has its own fingerprints (late vibrato, rigid harmonic rhythm, little variation) is a set of hypotheses to test, not results.

## Credits for material

- "March In 6/8" by JoshKeyLowF, Freesound, CC BY 4.0.
- "A E D E chord progression in 6 8 time" by llf0, Freesound, CC BY 3.0.
- Elgar, *Salut d'amour*, performed by Emanuel Salvador, via Musopen, CC BY.
- Saint-Saëns, *The Swan*, Seattle Youth Symphony Orchestra, via Musopen, CC BY-SA.
- Bach, Partita No. 3, performed by Emil Telmányi, via Musopen, public domain.
- Beethoven, Sonata Op. 27 No. 2, I. Adagio sostenuto, via Musopen, public domain.
- Suno tracks and stems: generated by the author for this research.
