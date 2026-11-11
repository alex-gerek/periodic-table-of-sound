# Periodic Table of Sound

A research project into what music is made of. Sound is broken down into elements, each element gets its own measurement math, and every claim is checked against ground truth.

The project started inside PHARMAKON, a mastering and restoration tool for AI-generated music. On 2026-11-10 it became a project of its own. Results that prove themselves here may later return to PHARMAKON as new modules.

## The table

The current table is the **third edition**: [`table/edition3.html`](table/edition3.html). To view it, open `table/standalone/Periodic_Table_of_Sound_edition3.html` in a browser. It adds the first measurements on real stems (marked ✓), the tempo-dependent bar and the metric interval. The second edition ([`table/edition2.html`](table/edition2.html)) and the first ([`table/edition1.html`](table/edition1.html)) are kept for comparison.

The table is ordered by two measurable criteria. The full rules are in [`docs/ordering_criteria.md`](docs/ordering_criteria.md).

- **Order: time octave Z.** Every element has its own characteristic time τ. Its position is Z = log₂(τ / 1 s) + 15. A pulse at 120 BPM is Z 14; a whole song is about Z 23.
- **Group: the question asked of the signal.** There are six questions: Level, Periodicity, Irregularity, Change, Makeup and Space. One column asks the same question at every time scale.
- **Periods** are cut where hearing changes how it treats time, at Z 6, 10.7, 13, 16, 18 and 20.
- **Defects are unstable forms** of normal elements. They sit in their element's group and carry a mark; they are not a column of their own.

## Layout

| Path | What it holds |
|---|---|
| `table/` | The table pages, one file per edition |
| `docs/` | Rules of the table and notes on the method |
| `docs/research/` | Literature reviews (classical stem separation, patents) |
| `elements/` | One study per element: definition, math, tests, demo |
| `experiments/` | Dated experiments with their scripts and results |
| `data/` | Ground-truth stems and how to get them (audio is not in git) |
| `ROADMAP.md` | Phases of the work and what comes next |

## Ground rules

- **Own math only.** No third-party code or pretrained models in anything we ship. Papers may be studied and their math re-derived and implemented from scratch. Check patents before shipping.
- **Measure, don't guess.** Every claim gets a number, a ground-truth test on synthetic signals with known answers and on real stems, and a held-out check on data the method never saw. Listening is not the deciding argument.
- **Name things ourselves.** Element names come from physics, in our own words.
- **English** for everything written in the project.
- **A commit and a backup bundle after every finished step.**

## Status

Phase 0 (project setup) is done. Next: Phase 1 continues the table; the first task is to measure τ for each element on the stems and check that every element falls into its predicted cell. See [`ROADMAP.md`](ROADMAP.md).

An earlier kick-and-bass separation experiment depends on [PHARMAKON](https://github.com/alex-gerek/PHARMAKON), the author's open-source mastering tool. It is not part of this repository yet; it will be added once its functions are ported into `pts/`.

## Licence

MIT, see [`LICENSE`](LICENSE). The recordings used in the experiments keep their own licences; see the credits in `articles/01_the_periodic_table_of_sound.md` and the `SOURCES.txt` files under `data/material/`.

This project is developed by Lex Gerek together with Claude (Anthropic), credited as co-author in the commits.
