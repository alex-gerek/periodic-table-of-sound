# suno_vibrato_01: a Suno track requested with vibrato

- **File:** `data/material/vibrato/suno_vibrato_01.wav`, 13.6 s, stereo, 48 kHz, a full mix (not a stem).
- **Request:** the user generated it in Suno, asking for vibrato.

## Result

| Signal | Rate found | r | Verdict |
|---|---|---|---|
| The file as it is | 1.28 Hz | 0.06 | no vibrato (noise level) |
| Control: 15 cents at 5.5 Hz written in | 5.49 Hz | 0.63 | found |
| Control: 30 cents at 5.5 Hz written in | 5.49 Hz | 0.82 | found |

The detector is the one calibrated in `vibrato_injection.py`, with a free search over 30 ms to 1 s of the pitch track. The controls show that it sees small vibrato in this very file, so the empty result for the original is a real result, not blindness.

## What the file contains

The spectrogram (`suno_vibrato_01_spectrogram.png`) shows steady, flat lines. The texture is sustained notes that pile up into chords: C4 (262 Hz), then G4 (392 Hz), then more notes. No line wiggles. Vibrato of ±30 cents at 392 Hz would swing the line by about ±7 Hz, which is visible at this resolution.

Around 600 to 625 Hz between 4.7 and 6.5 s two close notes overlap. Their beating gives an irregular wobble in level and apparent pitch (r ≈ 0.2, not periodic). In the table this is the Beating element, not vibrato.

## Conclusion

This generation contains no pitch vibrato, even though it was requested. One generation is not enough to say that Suno cannot produce vibrato. The next attempt should ask for a solo **voice** with long held notes and export the **stems**, so that the vocal can be measured without the chords around it.

A spectral-line tracker was also tried as an independent check. It returned zero movement even with vibrato written in, so it has a bug. Its numbers are not used here.
