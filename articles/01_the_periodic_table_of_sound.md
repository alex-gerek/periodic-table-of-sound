# The Periodic Table of Sound: ordering music by time, and a collider to test it

*Lex Gerek, with Claude. November 2026.*

Mendeleev did not set out to describe every substance in the world. He looked for the few numbers that put the elements in order, and then he trusted that order enough to leave gaps in it. Three of those gaps were later filled by gallium, scandium and germanium, with almost exactly the properties he had predicted.

This project asks whether music can be ordered the same way. We do not mean genres, instruments or moods. We mean the elementary quantities that every piece of music is made of, such as a pitch, a pulse, a vibrato, a bar or a phrase. Can those be ordered by numbers that a machine can measure, and does the resulting order predict something we have not heard yet?

After three days of measurement, our answer is a careful yes. This article describes the table, how we tested it, and what the tests showed. It also describes a small "collider" in which new elements can be built from scratch and checked. Finally, it tries to convey how large the space of possible combinations is.

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
| A best peak is not yet a period | Four tests on every candidate: significance against the noise level, enough repetitions, stability in both halves, and a correlation that falls and then returns. Checked on held-out noise, on smooth swells, and on real drums whose beat was destroyed | 0% false periods and 0% misses on held-out signals, where the bare peak rule gave 100% false periods. Without the fourth test, 25 of 40 smooth swells passed as periods; with it, none |
| The method has no hidden bias towards doubling | A waltz, and a real 6/8 march from Freesound | Three beats per bar in the waltz; three eighths per beat and two beats per bar in the march |
| Natural vibrato lives in the Event row | Two operatic voices and a historic solo violin, with a piano as a control | Z 12.3 to 12.5. The piano gave no false alarms, and vibrato we wrote into it was found at the written rate |
| The detector can say no | Two Suno tracks requested in 6/8 | Both came out binary, and the method said so |

Some results surprised us. Asked for 80 BPM, Suno returned a track at 122 BPM; asked for a 6/8 jig, it twice returned a straight groove. In the Suno voices, vibrato often starts only at the end of a long note. This is a candidate fingerprint of generated singing, not yet a finding, because we still need a human reference recording.

Some things did not work, and we have kept them in the record. A live violinist bends the tempo so much that our fixed-lag method cannot see the meter. Vibrato inside a mix, such as a violin over a piano, is still unsolved.

Review found errors in our own checks, and we corrected them in public:
- A single smooth swell in a long recording was accepted as periodic. That led to the fourth test above.
- Reports printed rejected candidates as if they were measurements.
- A rate of wrong periods on real recordings counted every result as right by default, where no independent labels existed.

### Is the pulse the beat?

A detector that finds a regular repetition can still pick the wrong level of it: the bar instead of the beat, or the eighth notes instead of the beat. Our first metric hid this, because it counted the beat or any multiple of it as right.

We built a strict benchmark:
- **Classes.** The returned period counts as the beat itself, a precision error, a subdivision (1/2, 1/3 or 1/4 of the beat) or a multiple (2 to 8 beats).
- **Signals.** Synthetic drum patterns with a known beat: meters of 2 to 7 beats and compound meters, hats in eighths, triplets and sixteenths, accented downbeats, and several patterns.
- **Honesty.** Every rule was tuned on development data only. It was then run once on two sets it had never seen. The second set came from a generator written after development had finished, with other timbres, patterns and noise.

| Rule | First held-out set | Second held-out set |
|---|---|---|
| The rule in our core code | 80% of beats exact; the rest are multiples (bars and half bars) | 76.5% exact |
| A candidate that reads only the strong events (kick and snare, below 2.5 kHz), takes each period from its first four multiples, and keeps the shortest level that repeats and is confirmed | 95% exact | 94% exact |

The candidate is better, but it is not better everywhere, and we report where it is worse:
- On the two held-out sets it improved 34 and 42 signals and made 4 and 7 worse.
- In the first set, three of the four new errors came from heavy noise. The beat was found but failed the stability test, so a confirmed multiple won.
- In the second set, all seven new errors are rock with a kick on the "and" between beats. That kick makes the half beat a regular period of strong events, and the candidate returns the eighths. The old rule is right there.
- A second version of the candidate fixed the noise errors in development, but it gave no measurable gain on the second held-out set, so we report the first version.
- On real recordings the two rules agree on 10 of 13 drum stems. They disagree on a waltz and on a 174 BPM breakbeat, where the candidate is probably right, and on an 80 BPM boom-bap track, where it is probably wrong.

The candidate is not yet in the core code. First it has to pass a check on real recordings whose beats are verified independently. The tempo written in a generation prompt is not such a label, because the generated track can differ from it.

## 4. Predicted cells and the collider

The grid of six questions by seven time scales has empty cells. Mendeleev wrote down the expected properties of his gaps. We go one step further: we build the predicted element from scratch, then check by measurement that it lands in its cell.

The **Sound Collider** is a single web page. You choose elements and set their dials, such as tempo, beats per bar, vibrato rate, phrase length or the cycle of a stereo movement. The page synthesises the sound from first principles, with no samples, and plays it. Detectors then search the separate stems without being told the recipe, and a control run removes each element in turn, after which the detector must stop finding it.

Three predicted cells can already be heard:
- **Variation:** a drum fill closes every phrase. The detector finds a period of exactly 2, 3, 4 or 8 bars. When the same fills are scattered at random, it reports variation without a period, and no false periods appear.
- **Spatial motion:** the melody travels from left to right once per cycle.
- **Width arc:** the stereo image opens from mono to wide over a set number of bars.

The browser check is a battery of 360 settings: 15 tempos from 60 to 200 BPM, meters of 2 to 7 beats, and four kinds of fills. Pulse, meter and variation must all be right for a setting to pass. **359 of 360 pass, up from 304.**

The earlier failures had four causes, two in the sound and two in the detector:
- **The same hit did not render the same.** Web Audio renders in blocks of 128 frames, so a hit sounded slightly different depending on where it fell inside its block. Every distinct hit is now rendered once and copied, which makes bars written the same equal sample for sample.
- **The bar grid drifted.** It now comes from a robust fit.
- **The pulse depended on how a beat fell on the analysis frames.** The onset curve is now smoothed before the pulse search.
- **The meter used a biased median.** It now uses a true one.

When any element is removed, it disappears from the results. The collider is a sandbox. Official results come only from the Python code, and the provisional rules inside the page are marked as provisional.

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
- The pulse rule in the core code returns a bar or a half bar for about one signal in five on our strict benchmark. A better candidate exists (94 to 95%), but it fails when a kick falls between the beats, and it has not yet been checked on real recordings with verified beat labels.
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
