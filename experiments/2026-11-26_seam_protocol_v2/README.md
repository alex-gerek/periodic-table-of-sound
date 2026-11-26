# 2026-11-26: seam protocol v2

Issue #34, journal step `2026-11-26-seam-002`. The protocol for Suno tracks with known extend points is in [`PROTOCOL.md`](PROTOCOL.md) and is frozen: `seam_features.py` (SHA-256 `b7243441…`) and the one-shot scorer `score_joins.py`, which refuses to run if the features changed.

## Development sweep (run `20261126T145945Z-dev-f91c371fc8cf`)

Joins written into 21 Suno mixes from Lex's archive at known times; each join is compared with the other places of the same track. Share of 42 joins with p ≤ 0.05:

| Join | envelope | floor | bandwidth | level | click |
|---|---|---|---|---|---|
| none (calibration) | 5% | 5% | 2% | 7% | 2% |
| splice, no crossfade | 19% | 29% | 10% | 17% | 14% |
| splice, 50 ms crossfade | 14% | 21% | 14% | 26% | 0% |
| low-pass 16 kHz | 5% | 5% | 19% | 7% | 2% |
| low-pass 12 kHz | 2% | 5% | **67%** | 7% | 2% |
| high shelf +4 dB | 2% | 7% | 2% | 7% | 2% |
| level step +2 dB | 2% | 5% | 2% | 10% | 2% |
| noise −50 dB | 7% | 5% | 14% | 7% | 2% |

Calibration holds. The features see a bandwidth change and, weakly, a splice; level, tilt and noise joins of these sizes are smaller than the music's own movement. Full table: `runs/…/results.md`.
