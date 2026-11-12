# Plan: element cards and the prediction scoreboard

*Status: plan, nothing built yet. Owner: Claude. 2026-11-12.*

Clicking an element in the table should open a large card about it:
- what it is;
- where you hear it;
- why it sits in its row and column;
- how we found it, with the picture from our own experiment;
- and, if the ear can hear it, a button that plays it in the Sound Collider, with and without it.

Predictions get a section of their own and a public score, because a prediction that can fail is the most interesting part of the table.

## 1. The card

The card opens over the table, at full width on a phone. Its sections, from top to bottom:

1. **Header.** Symbol and name in the group colour, row and column, Z (typical value and range), and one status badge:
   - ✓ measured in this project;
   - 🔮 predicted, waiting for a test;
   - defect (an unstable form);
   - not yet measured.
2. **In one sentence.** Plain words, no formulas.
3. **Where you hear it.** Two to four examples: instruments, genres, moments in a track.
   - These are descriptions, not measurements. They are shown as "typically" and kept visually apart from anything we measured.
4. **Its place in the table:**
   - why this row (its time τ) and this column (the question it asks);
   - its neighbours in the column;
   - what it turns into when time is compressed or stretched;
   - the elements it is built on (vibrato is the periodicity of the pitch track).
5. **Listen:**
   - **if the ear can hear it:** "Open in the collider", with a ready recipe and a with / without switch;
   - **if not** (phase, channel correlation, true peak): "Not heard directly", what it does to the sound, and a picture instead.
6. **How we found it** (measured elements):
   - one picture drawn from the experiment's own results, for example:
     - Envelope: the true and the measured envelope on one plot;
     - Pulse: the autocorrelation with its confirmed peak and the dip before it;
     - Vibrato: the rates found in two voices and a violin;
   - two or three key numbers in plain words;
   - the limits: where the method does not work;
   - links to the experiment and to its entry in the research journal.
7. **Our prediction:**
   - **what we expect:** where on which graph, or what it should sound like, stated before the test;
   - **how it could fail:** the result that would prove us wrong;
   - **status:** 🔮 waiting, ✓ came true (with the evidence), or ✗ did not come true (with what we learned).

   Measured elements show the predictions they passed. Predicted cells show the prediction they are waiting on.
8. **In PHARMAKON:** where the element is used or treated, if it is.

## 2. The prediction scoreboard

A strip above the table: **made N predictions · came true · did not · waiting**. Clicking it opens the list. It starts with what has already been tested:

| Prediction | Status | Evidence |
|---|---|---|
| The 4/4 bar lands at Z 16.58 (80.5 BPM) and Z 16.26 (100 BPM), written before measuring | ✓ came true | tempo series |
| Chord changes nest at log₂ of a whole number of pulses | ✓ partly: on the 4 of 7 tracks where the chord period is confirmed | tempo series, issue #7 |
| Vibrato lives in the Event row | ✓ came true | real vibrato |
| Envelope is a Level element near Z 8 | ✓ for tonal sounds, under stated conditions | issue #21 |
| Loop is an element of the Phrase row | ✗ not confirmed: Loop is not yet well-posed | periodicity column, issue #7 |
| The pulse rule returns the beat | 🔮 open: candidate at 94 to 95% on held-out sets, not yet tested on real labels | issue #15 |
| Variation, Spatial motion, Width arc exist as elements | 🔮 built and detected in the collider; not yet found in real music | collider |
| Novelty, Tonal palette, Stereo form exist as elements | 🔮 waiting | — |
| AI-generated audio has fingerprints (late vibrato, rigid harmonic rhythm, little variation) | 🔮 hypotheses | article, section 7 |

A prediction is only counted if it was written down before the test, and its row links to that record.

## 3. Waves

**Wave 1: ten elements.** First one sample card, Envelope or Vibrato, for Lex to review before the other nine are built.

| Element | Status | "How we found it" picture | Listen |
|---|---|---|---|
| Pitch (F0) | ✓ | pitch of bass and vocal stems over time | collider melody: notes on a dial (new) |
| Vibrato (Vb) | ✓ | vibrato rates of the voices and the violin | collider: Vibrato on / off (exists) |
| Pulse (Pu) | ✓ | autocorrelation with the confirmed peak and the dip before it | collider: Pulse (exists) |
| Sidechain pump (Sc) | ✓ | the level track of the bass ducking on every kick | collider: a new Sidechain element |
| Meter (Me) | ✓ | measured bars against tempo, with the Z 16 border | collider: beats per bar (exists) |
| Harmonic rhythm (Hr) | ✓ | chord-change curve with its period | collider: a new chord-change element |
| Envelope (Ev) | ✓ | true and measured envelopes; the valid region | collider: a new attack and decay element |
| Variation | 🔮 | detector output: the bars that differ, on a grid or at random | collider: fills (exists) |
| Spatial motion | 🔮 | the left–right balance over time with its period | collider (exists) |
| Width arc | 🔮 | side-to-mid energy over a phrase | collider (exists) |

**Wave 2: defects you can hear.** Clipping, Harsh burst and Aliasing, with clean against defective. This is the most direct way to show what PHARMAKON treats.

**Wave 3: elements you cannot hear, with pictures.** Phase, Channel correlation, True peak.

**Wave 4: the rest,** as each one is measured. Unmeasured elements get a short card with "not measured yet".

## 4. How it is built

- **Card texts** live in a data file (`table/cards.json`), not inside the table page, so they can be reviewed and checked on their own.
- **Pictures** are drawn by a script from the experiments' stored results, as for the article (`articles/make_01_figures.py`), so a picture always matches its data.
- **Collider links:**
  - the collider learns to open from a link with a recipe: `lab/collider.html?recipe=vibrato`;
  - a with / without switch is added;
  - new elements: Envelope (attack and decay), Sidechain pump, chord changes.
- **No audio files:** every sound is synthesised in the browser, as the collider does now. Audio stays out of git.
- **Checks before each merge:**
  - every link opens and every recipe loads;
  - for every recipe, the collider's own detector finds the element, and stops finding it when the element is switched off. This is the control the collider already runs;
  - every claim on a card that says "measured" links to its evidence;
  - every prediction links to the record written before its test.
- **Workflow:** one issue per wave, work through a pull request, a research-journal entry for each new collider element.

## 5. Risks

- **Volume.** Seventy cards hold many claims, and each must be checked against the evidence. That is why the work goes in waves.
- **Descriptions that sound like measurements.** "Where you hear it" is description; the card keeps it visually apart from measured claims.
- **Predictions stay predictions until tested.** They are shown with pride, as predictions, and never presented as results. A prediction that fails stays on the scoreboard with what it taught us.
