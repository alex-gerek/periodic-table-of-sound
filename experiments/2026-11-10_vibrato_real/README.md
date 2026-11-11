# 2026-11-10: natural vibrato in real recordings

The first measurement of natural vibrato: two Suno operatic voices (lead vocal stems), a historic solo violin, two string recordings with accompaniment, and a piano as negative control.

- Code: `run.py`, using `pts/periodicity.py`. A test of the partial tracker is in `pts/partials.py` and `tests/`.
- Full numbers: `results.md`, `results.json`. Sources and licences: `data/material/arias/SOURCES.txt`.
- Pictures: `suno_voices_spectrogram.png`, `violin_vs_piano_spectrogram.png`.

## Method

The single-voice pitch tracker is used. Held notes (voiced runs of at least 0.6 s) are cut into **1-second windows**, with a step of 0.5 s. In each window the note is removed with a running median and the remaining swing is autocorrelated. A window counts as vibrato if r ≥ 0.5, the depth is at least 8 cents and the rate is 4 to 8.5 Hz.

The windows are needed because **vibrato is local in time**. The Suno soprano holds a note at about 1150 Hz perfectly straight for about 6 s and starts to swing only near its end (see the spectrogram). Judging whole notes hid that.

## Result

| Recording | Kind | Held-note time | Share with vibrato | Rate, median (10–90%) | Depth in cents, median (10–90%) | Z | Row |
|---|---|---|---|---|---|---|---|
| Soprano, Suno | solo stem | 58 s | 16% | 5.67 Hz (5.48–6.05) | ±30 (24–34) | 12.50 | 3 ✓ |
| Baritone, Suno | solo stem | 43 s | 11% | 5.84 Hz (5.50–6.47) | ±40 (30–65) | 12.45 | 3 ✓ |
| Violin, Bach Partita 3 (Telmányi, historic) | solo | 389 s | 13% | 6.54 Hz (6.05–6.96) | ±13 (9–21) | 12.29 | 3 ✓ |
| Violin, Salut d'amour (with piano) | mix | 0 s | – | – | – | – | – |
| Cello, The Swan (with orchestra) | mix | 12 s | 0% | – | – | – | – |
| **Piano (control)** | control | 79 s | **0%** | – | – | – | – |
| Piano + 15 cents at 5.5 Hz written in | control | 75 s | 26% | **5.51 Hz** | ±14 | 12.54 | 3 |

## What this shows

1. **The controls hold.** The piano gives no false alarms. Vibrato written into the same recording is found at the written rate (5.51 Hz for 5.5) and depth (±14 cents for 15). Only 26% of the time with written vibrato is caught, so the shares above are **lower bounds**.
2. **Natural vibrato lands in the predicted cell.** Every solo recording gives a vibrato period at Z 12.3 to 12.5, in row 3 (Event), where the second edition put Vibrato (Z 12.4). This is real evidence, because the search window (3 to 10 Hz) covers both rows 3 and 4.
3. **Voices and the violin differ the way they should.** The voices swing 2 to 3 times wider (±30 to 40 cents) than the violin (±13), and slightly slower (5.7 to 5.8 Hz against 6.5 Hz).
4. **Suno voices start straight and add vibrato late.** Only 11 to 16% of held-note time has vibrato, typically at the end of long notes. Whether this differs from human singers needs a human reference recording, which we do not have yet. This is a candidate fingerprint of generated vocals, not a finding.
5. Depth on synthetic tones reads about 20% low with this method, so true depths are somewhat larger.

## What did not work

- **Recordings with accompaniment.** The violin with piano and the cello with orchestra show clear vibrato in the spectrogram, but the single-voice tracker loses the melody under the accompaniment (0 to 12 s of held notes found). A partial tracker (`pts/partials.py`) passes its synthetic test but does not yet separate the violin from the piano control on real recordings. Tuning its thresholds further on these two recordings would be fitting the answer, so it was stopped. Measuring vibrato inside a mix is its own task.
- The earlier claim "no vibrato in AI vocals" was withdrawn before this step. With the windowed method, the GRAVITY and Pure voltage vocals should be measured again.

## Next

- A human singer recording, straight and with vibrato, as the reference for point 4.
- Re-measure the GRAVITY, Metro and Pure voltage vocals with windows.
- Vibrato in a mix: melody extraction by partial grouping, as a separate step.
