# Periodic Table of Sound: Roadmap

*Started 2026-11-10. Owner: Lex Gerek. Project name decided on 2026-11-10: **Periodic Table of Sound**. The research line is the "chemistry of music".*

## 0. Progress log

- **2026-11-10. Phase 0 done.** The project repository, README, layout, the table (both editions), the stem separation report, the kick portrait experiment, and local copies of the ground-truth stems.
- **2026-11-10. Table, second edition** ([`table/edition2.html`](table/edition2.html)). It is ordered by time octave Z = log₂(τ / 1 s) + 15 and has six groups (Level, Periodicity, Irregularity, Change, Makeup, Space). Periods are cut at Z 6, 10.7, 13, 16, 18 and 20. Defects are marks of instability, and second-order elements are marked. Rules: [`docs/ordering_criteria.md`](docs/ordering_criteria.md). The edition-3 description in section 3 below is the **first edition** of the table (file `table/edition1.html`).
- **2026-11-10. Phase 1, step 1: the Periodicity column measured** ([`experiments/2026-11-10_periodicity_column/`](experiments/2026-11-10_periodicity_column/README.md)). Our own code is in `pts/`, with 10 synthetic ground-truth tests passing. The compression test passes on the real drums of all three tracks (period × 32 = 2.00 / 2.00 / 1.00 pulses, within 0.3%). Sidechain pump nests in whole pulses where pumping exists: one pulse on GRAVITY, two on Pure voltage, within 0.5% (corrected in issue #5). Periods nest as integers within 0.6%. Problems found: the Z 16 border cuts 4/4 bars faster than 120 BPM (Metro); no vibrato found in these AI vocals; Loop needs a better definition; the repetition search has an edge bias.
- **2026-11-10. Vibrato detector calibrated on real voices** by writing known vibrato into the stems. The old tracker was blind, so the earlier claim "no vibrato in AI vocals" is withdrawn. Pure voltage has no natural vibrato (now a valid result). The GRAVITY vocal pitch moves with the pulse (1.99 Hz). **Z 16 border:** the cause is two time axes, absolute Z and metric level, which are related by ΔZ = log₂ of whole numbers. Options are in `docs/z16_border.md`. New material is requested in `data/material_request.md` (tempo series, other meters, natural vibrato).
- **2026-11-10. Natural vibrato measured** ([`experiments/2026-11-10_vibrato_real/`](experiments/2026-11-10_vibrato_real/README.md)). A Suno soprano and baritone (stems), a historic solo violin, and a piano as control. Analysis uses 1 s windows, because vibrato is local in time. The piano gives 0% false alarms, and 15 cents written in is found at 5.51 Hz. The vibrato period lands at Z 12.3 to 12.5 (row 3, as predicted) for every solo recording. Voices are wider than the violin (±30 to 40 cents against ±13). Suno voices start straight and swing only late in long notes (11 to 16% of held time); this is a candidate fingerprint, and a human reference is needed. Vibrato inside a mix (violin with piano, cello with orchestra) is not solved yet.
- **2026-11-10. Tempo series, 6 tracks** ([`experiments/2026-11-10_tempo_series/`](experiments/2026-11-10_tempo_series/README.md)). The 4/4 bar moves with tempo: Z 16.26 at 100 BPM (row 5, exactly as predicted before measuring), Z 15.99 at 121 BPM, then 15.76, 15.55 and 15.46 at 142, 164 and 174 BPM, all in row 4. This supports option A of `docs/z16_border.md`. The harmonic rhythm nests at ΔZ = log₂ 4 or log₂ 8 within 0.003 on the four tracks where it is confirmed (100, 120, 140 and 160 BPM; corrected in issue #7). At 174 BPM the breakbeat makes the pulse ambiguous (bar, 87 or 174 BPM). The first 80 BPM request came out at 122 BPM; a slow-genre retake hit 80.5 BPM, and its bar landed at Z 16.58, row 5, exactly as predicted. **The Z 16 question is answered by data: the bar is a tempo-dependent element that crosses the border near 120 BPM (option A).** Still missing: tracks in other meters (3/4, 6/8).
- **2026-11-10. Meter test, 3/4** ([`experiments/2026-11-10_meters/`](experiments/2026-11-10_meters/README.md)). A Suno waltz, generated at 182.4 BPM instead of the requested 120. Drums and bass, two separate stems, peak only at multiples of 3 beats (0.83, 0.78, 0.71 and 0.64 against about 0.37 at 2, 4 and 8). The bar is 3 beats, ΔZ = log₂ 3: **the method sees 3 and has no doubling bias.** The pulse rule picked the bar as the pulse, the second such case after the 174 BPM breakbeat, so the pulse needs a better definition. The 6/8 track came out binary (about 128 BPM, groups of 2, 4 and 8, with vocals despite the exclusion), so the method correctly found no triple grouping there and the 6/8 test is still open. The Irish jig retake also came out binary: no stem shows a third of the beat, every one shows the half. Suno does not deliver 6/8 reliably, so the 6/8 test stays open; the waltz already shows the method finds 3. Telmányi's Bach Partita (real meters from the score) shows no meter at all, because a live soloist bends the tempo: live music needs tempo-following beat tracking. **A real 6/8 from Freesound ("March In 6/8", CC BY 4.0) passes:** peaks at every multiple of 3 eighths, and 6 beats 3 and 12 beats 9, so the beat is 3 eighths and the bar is 2 beats. With the waltz, the method finds 3 in both the bar and the beat. The metric interval is measurable and can go into the table.
- **2026-11-11. Table, third edition** ([`table/edition3.html`](table/edition3.html)). Option A is adopted. It adds ✓ checks with measured Z ranges (Pitch, Vibrato, Pulse, Sidechain pump, Meter, and the new Harmonic rhythm), the metric interval as a second coordinate, borders drawn as ±0.3 Z zones, and a chart of measured bars against tempo for 4/4, 3/4 and 6/8.
- **2026-11-12. Confirming a period** ([`experiments/2026-11-12_periodicity_confirmation/`](experiments/2026-11-12_periodicity_confirmation/README.md), issue #7). A candidate period is now confirmed only if it is significant against Bartlett's noise level (≥ 5 σ), repeats at least 4 times and stays significant in both halves. The thresholds were chosen on a training set. On held-out noise, grooves and real drum stems: 0% false periods and 0% misses, where the bare peak rule gave 100% false periods. Earlier results re-checked: pulse, meter and sidechain are confirmed; Loop and Repetition are not; the harmonic rhythm is confirmed on 4 of 7 tempo tracks, which corrects the claim "at every tempo". After review, a fourth test (return: the correlation must fall after half the lag and rise back) stops smooth swells from being confirmed (25 of 40 before, 0 after). Reports now show unconfirmed periods as candidates, and the wrong-period rate on real stems is marked as not evaluated.
- **2026-11-12. Choosing the beat level** ([`experiments/2026-11-12_beat_level/`](experiments/2026-11-12_beat_level/README.md), issue #15). The old metric counted bars as right. A strict benchmark scores the exact beat apart from its subdivision and its multiples. On two held-out sets the old pulse rule gets 80% and 76.5% of beats exact; a candidate that reads the strong events (kick and snare) gets 95% and 94%. It fails where a kick on the "and" makes the half beat regular (rock, boom-bap), and there the old rule is right. **The rule in `pts/` is not replaced yet. Open stage: real recordings with verified beat labels.**
- **2026-11-12. Band split: a negative result** ([`experiments/2026-11-12_band_split/`](experiments/2026-11-12_band_split/README.md), issue #15). Separate envelopes for kick, snare and hats looked like they told the beat from its half (98% against 93%). A fair control showed that the gain came from hat conventions in the generator (a louder hat on the beat, hats that divide the beat into 2 or 4). Without them, and with the features, classifiers and generator tested, the bands added nothing (95.7% against 95.5%, McNemar χ² = 0.1). The algorithm was not made more complex.
- **2026-11-12. Collider: equal bars render equal** ([`lab/README.md`](lab/README.md), issues #8 and #10). Runs work on a snapshot of the recipe, and the noise is seeded. The false Variation at 150 BPM in 3/4 had four causes:
  - Web Audio rendered the same hit differently depending on its place in a 128-frame block;
  - the bar grid drifted;
  - the pulse depended on the frame phase;
  - the meter median was biased.

  With hits rendered once and copied, a robust grid cut from the downbeat, a smoothed onset curve and a true median, the battery of 360 settings passes 359 times (before: 304).
- **Next:** a pulse rule that returns the beat, not the strongest repeat; the Level column; vibrato inside a mix; a human singer as the vibrato reference. Meanwhile Claude checks the borders against the literature, runs the echo and loop injection tests, and starts the Level column.

## 1. Why a separate project

PHARMAKON 3.2 is released and works well. Its research has gone further than a mastering tool: we want to understand what sound is made of, element by element, and build our own mathematics on top of that. This project develops that research on its own. Proven results may be merged back into PHARMAKON later (new Antidote modules, a better stem splitter), but the research is no longer tied to its release cycle.

The name PHARMAKON already fits the direction: in Greek it means both remedy and poison. The same engine that removes an artifact can isolate it and turn it into material.

## 2. Ground rules

- **Own math only.** No third-party code, libraries for the core, or pretrained models (including open-source separators such as Demucs) inside anything we ship. Published papers may be studied and their math re-derived and implemented from scratch.
- **Check patents before shipping.** Known risks: REPET / REPET-SIM (US 9,093,056, active to 2033), Fraunhofer structure-tensor HPR (US 10,770,051, to 2037), Celemony note objects (US 8,022,286, to 2029). Expired or lapsed: ADRess, DUET, Creative panning, MERL NMF. Not legal advice.
- **Measure, don't guess.** Every claim gets a ground-truth test, a number, and a held-out check on data the method never saw. No subjective listening tests on Lex as the deciding argument.
- **Name things ourselves.** Do not borrow other researchers' category names (for example Schaeffer's typology terms). Name elements from physics, in our own words.
- **English for everything written** in the project (code, docs, articles). Conversation with Claude is in Russian.
- **Backups and commits after every step.**

## 3. What exists today

**Periodic Table of Sound, first edition (called version 3 while it was being built).**
- File: `table/edition1.html`; a standalone copy is in `table/standalone/`.
- Rows are 7 time scales: Vibration, Tone, Event, Beat, Bar, Phrase, Form.
- Columns are 8 families:
  - Tonal ("metals")
  - Noise ("noble gases")
  - Transient ("alkali")
  - Color
  - Energy
  - Space
  - Order
  - Defects ("radioactive")
- Row 8, Texture: Grit, Swarm, Flutter, Beating, Shimmer, Drift, Breath pulse, Bloom.
- Row 9, unstable generated-audio artifacts: Warble, Smear, Ghost partials, Fizz, Seam.
- 66 elements, each with a status: measured by PHARMAKON, partly, or not yet.
- Six excitation families (struck, plucked, bowed, blown, sung, electronic) with about 24 instrument fingerprints.
- "Rhythm becomes pitch" bridge: around 20 repetitions per second, hits fuse into a tone.

**Research report.**
- File: `docs/research/classical_dsp_stem_separation.md`.
- The kick-portrait scripts depend on a local PHARMAKON checkout and are kept in the private working copy for now. Ground-truth stems: see `data/README.md`.
- Covers classical (non-neural) separation methods, voice-vs-lead cues, the recommended pipeline and patents.

**Ground-truth stems.** These are the user's own Suno exports, used as reference.

| Track | Stems | Notes |
|---|---|---|
| Metro | 8 | quiet vocal; good for drums and bass |
| GRAVITY HAS AN ADDRESS | 10 | vocal-heavy |
| Pure voltage | 12, incl. guitar | held-out track |

- Not valid as ground truth: the Bronze Psalter and Vector Pulse demo stems. They were produced by PHARMAKON's own splitter.

**Stem separation experiments.**
- The task is to split the low band below 200 Hz into kick and bass. Scores are SI-SDR in dB, higher is better.

| Track | Current splitter (kick / bass) | Kick portrait (kick / bass) |
|---|---|---|
| Gravity | no kick / +1.8 | +7.0 / +8.4 |
| Metro | no kick / +3.5 | +5.1 / +9.2 |
| Pure voltage | no kick / +1.4 | +6.6 / +7.8 |

- How the kick portrait works:
  - Kicks generated by AI are not identical samples, so we average magnitude spectra, not waveforms.
  - The portrait cleans its own onset list.
  - Subtract-and-search finds double kicks.
- The stems sum back to the mix exactly.
- Remaining gap: on Pure voltage only 63% of kicks are found. The rest are masked by the bass.

## 4. Core ideas: the chemistry of music

1. **Element vs amount.** An element is a kind of thing (Pitch, Pulse, Kick). A measurement is how much of it and what value: Hz, BPM, ms, dB. **Decibels are the concentration of an element in the mix.** Every element gets a unit and a typical range, like the atomic mass in the corner of a cell.
2. **Protons and neutrons of a note.** The pitch class is the identity, the "protons": C, C#, ... B, 0 to 11. The octave is the weight, the "neutrons". The note number is 12 × octave + pitch class, the "mass number", and the frequency follows from it: f = 440 · 2^((n − 69)/12). Everything about a note can be computed from this passport.
3. **Isotopes** are the same note in another octave.
4. **Allotropes** are the same elements in a different arrangement, like diamond and graphite, or oxygen and ozone. A chord versus an arpeggio of the same notes. The same hits in a different groove. 4/4 versus 2/4.
5. **Atomic number of an interval** is the harmonic number where it first appears:

   | Harmonic | Interval |
   |---|---|
   | 2 | octave |
   | 3 | fifth |
   | 5 | major third |
   | 7 | blues seventh |
   | 11, 13 | microtones |

   Light elements (2, 3, 5) are stable and consonant. Heavy ones (7, 11, 13) are rare and reactive.
6. **Valence** is how many stable (consonant) links a note can make with others.
7. **Instruments are alloys with recipes.** Like steel (iron plus a proportion of carbon), an instrument is defined by the **proportions** of its elements, not just the list. Variants are "grades" of one alloy: acoustic versus electric guitar, a fine violin versus a cheap one. Recognising an instrument means measuring its composition and comparing it with the recipes, like spectroscopy identifies a steel grade.
8. **Mixture versus alloy.** A track is a **mixture** of alloys. Its instruments sit side by side, like salt in water, and can be separated physically: that is stem separation. Inside an instrument the elements are **alloyed**. They are not separated; they are **analysed** for the recipe.
9. **Rhythm becomes pitch.** A pulse and a pitch are one periodicity at two time scales. The border is near 20 Hz. The Flutter element lives there.
10. **Audible table.** Every element should be heard:
    - Level 1: a synthesised demo in the page, for example sine vs saw vs square, two beating tones, a click accelerating into a tone.
    - Level 2: "solo this element" from the user's own track.
11. **Music from AI artifacts.** Use the unstable row deliberately as material: Warble, Smear, Ghost partials, Fizz, Seam. This is a possible path to a genre of our own. Historical parallel: Oval and the glitch music of the 1990s used CD errors.
12. **Predicted gaps.** Find truly empty cells systematically, by enumerating element combinations and checking what exists, not by guessing. The first three candidates (Eka-Groove, Eka-Chord, Eka-Meter) turned out to have relatives: Brian Eno's tape loops, noise through tuned resonators, and sidechained noise grooves.

## 5. Roadmap

**Phase 0: set up the new project. Done 2026-11-10.**
- Create the repository and folder structure: research notes, bench data, element studies, demos.
- Copy the table, the report and the experiment scripts in.
- Write a short README in English.
- Decide the working name together.

**Phase 1: the table, next editions.**
- Measure τ of every element on the ground-truth stems and check that each falls into its predicted cell.
- Run the time-compression test for each group on synthetic signals.
- Check the period borders against the perception literature.
- Add a unit to every element. Typical τ and its range are already in the second edition.
- Add isotopes (octaves) and allotropes (arrangements).
- Add atomic numbers of intervals from the harmonic series, and valence.
- ~~Rename row 9~~: done differently in the second edition; defects are now marks of instability inside their groups.
- Turn instrument fingerprints into alloy recipes with proportions and grades.
- Add the mixture-vs-alloy explanation.
- Keep it a standalone page; nothing goes into PHARMAKON.

**Phase 2: research the elements one by one.**
- For each element: a definition in our own words, the measurement math, a ground-truth test (synthetic signals with known values plus real stems), a held-out check, an audible demo, and an updated status in the table.
- Suggested order: Harmonic pattern → Body → Formant and Timbre motion → Vibrato and Glide → Register → Excitation → Grit → Flutter → Beating → Shimmer → Drift → the unstable row.

**Phase 3: instrument recognition by composition.**
- Build a library of recipes measured from our own stems.
- Classify a sound by comparing its measured composition with the recipes.
- Report how confident the match is.

**Phase 4: separation through elements.**
- Continue the kick work: kicks masked by bass (use the kick click at 1 to 5 kHz as second evidence; per-section portraits).
- Then other percussion (snare, hats, claps) with the same portrait idea.
- Bass harmonics via pitch tracking.
- Vocals and leads last.
- Every step: stems sum to the mix exactly, scored against ground truth and held-out tracks.
- Patent check before anything ships.

**Phase 5: the audible table.**
- Synthesised demos in the page.
- Then "solo this element" from a real track.

**Phase 6: creative work.**
- Music from AI artifacts.
- Systematic search for empty cells.
- Experiments toward our own genre.

**Phase 7: back into PHARMAKON when proven.**
- New Antidote modules (for example Warble and Smear removal).
- Stem splitter v2.
- One release and one article in English.
