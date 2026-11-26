# Seam protocol v2 (frozen)

Issue #34, journal step `2026-11-26-seam-002`. This file states how the tracks with known extend points will be scored. It is written before any of them exists.

## Material

Suno tracks made as asked in `data/material_request.md`, section 7: a first part, then one or two **Extend** steps, with the time of every extend point written down as Suno shows it.

- Each track is a folder `data/material/seams/<track>/` with `joins.txt` (one time per line, seconds or m:ss) and one full-track audio file. Stems, if exported, go to `stems/` and are kept for the held-out check of the stem-leakage estimator (issue #38). They are not used here.
- `joins.txt` is written by Lex before the folder is given to Claude. Claude does not open, play or analyse the audio before scoring.
- Joins less than 10 s from either end cannot be scored with the ±10 s exclusion; they are listed and excluded.

## Stage 1: is a join visible?

The code is `seam_features.py`, frozen at SHA-256 `b7243441c4a70367c9f49c7857e6ae98d7985e0c44048587b201a040da63bbc5`; `score_joins.py` refuses to run if it changed.

- Five features, each a value every 0.25 s: `envelope`, `floor`, `bandwidth`, `level` and `click` (definitions in the code and in the journal step).
- Per join and feature: the largest value within ±2 s of the join, against the largest values in ±2 s windows centred on every whole second of **the same track** that is more than 10 s from any join and from the ends. Conformal p.
- Per feature: k joins with p ≤ 0.05 out of n; one-sided binomial tail P(X ≥ k) at rate 0.05; Holm correction over the five features at 0.05. A feature that survives is **visible at joins**.
- One run: `python score_joins.py final`. No rerun with other settings. A defect in the code found after the run is recorded as a correction, and its rerun is labelled as such.

## How to read the result

The development sweep on 21 Suno mixes from Lex's archive (`runs/…-dev-…/results.md`) gives each feature's sensitivity to joins of known kind and size: hard and crossfaded splices, low-pass, high shelf, level steps and added noise. If no feature is visible at the real joins, they are smaller than those limits in every feature. If one is, the sweep says which kinds of join that feature can see.

## Stage 2 (not yet designed)

Blind detection (finding joins without their times) is designed only after Stage 1 shows a visible feature, and is tested on tracks not used in Stage 1.
