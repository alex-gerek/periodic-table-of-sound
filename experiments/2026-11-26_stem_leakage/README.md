# 2026-11-26: stem leakage with the other stem as a witness

Issue #38, journal step `2026-11-26-leak-001` (hypotheses, decision rule and three pre-data amendments written before the run).

For a target stem and a witness stem: one complex gain per log band (16 bands, 100 Hz to 12 kHz) fitted over all STFT frames; the share of the target's energy that the witness explains, minus its chance level; significance against 199 circular shifts of the witness. This is the witness-channel regression used to subtract known noise in gravitational-wave detectors, re-derived.

## Ground truth across songs (run `20261126T135152Z-final-30531db5f2eb`)

The lead vocal of song B written into the drums of song A (7 Suno songs, 42 pairs; before writing, the true leak is zero):

| Leak (dB of drum energy) | Linear: detected | Linear: median abs. error | Masked: detected |
|---|---|---|---|
| none | 1 of 42 (false alarm) | | |
| −40 | 1 of 42 | 3.1 dB | 1 of 42 |
| −35 | 6 of 42 | 1.0 dB | 4 of 42 |
| −30 | 35 of 42 | 0.5 dB | 30 of 42 |
| −25 | 41 of 42 | 0.2 dB | 41 of 42 |
| −20 | 42 of 42 | 0.1 dB | 42 of 42 |

**Measured limit:** reliable detection from −25 dB; level within 1 dB from −35 dB. The pre-registered targets (90% at −35 dB linear and −30 dB masked; 1 dB error at −40 dB) were not met, so nothing is adopted into `pts/`. Chance level on real drums: −39 dB (−47 dB on white noise).

## Within songs (exploration)

- Voice in the drum stem: GRAVITY −21.8 dB, Pure voltage −21.5 dB (inside the reliable range), EVERYTHINGS ALRIGHT −29.8 dB (detected; in the 71–83% range); not detected in the other four.
- Stems sharing the same audio: Keyboard and Synth at −1 dB in two songs; Lead and Backing Vocals at −5 to −7 dB in four songs.
- Pure voltage's twelve stems are mixed into each other almost everywhere.

Full matrices: `runs/…/results.md`. Audio stays outside git (Lex's archive and `data/stems/`).
