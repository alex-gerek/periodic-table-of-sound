<div align="center">

# Periodic Table of Sound

**The elements of music, ordered by a number you can measure.**

[![License: MIT](https://img.shields.io/badge/license-MIT-0f9e8e.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-1f8fd0.svg)](requirements.txt)

[The table](table/standalone/Periodic_Table_of_Sound_edition3.html) · [The collider](lab/collider.html) · [The article](articles/01_the_periodic_table_of_sound.md) · [How it is ordered](docs/ordering_criteria.md)

</div>

---

Mendeleev did not describe every substance. He found the numbers that put the elements in order, and he trusted that order enough to leave gaps in it. Three of those gaps were later filled by gallium, scandium and germanium, with almost the properties he had predicted.

This project does the same for music. Pitch, pulse, vibrato, bar and phrase are treated as **elements**. Each one is placed by its characteristic time, grouped by the question it asks of the signal, and **measured on real recordings**. The empty cells of the table are predictions, and a small **collider** builds those predicted elements from scratch so they can be heard and checked.

## The idea in one table

| Rule | Chemistry | Sound |
|---|---|---|
| **Order** | atomic number | time octave **Z = log₂(τ / 1 s) + 15**, from 20 kHz (Z 0.6) to a whole song (Z 23) |
| **Group** | valence electrons | six questions asked at every time scale: *Level, Periodicity, Irregularity, Change, Makeup, Space* |
| **Period** | electron shell | borders of hearing at Z 6, 10.7, 13, 16, 18 and 20, drawn as ±0.3 zones |
| **Stability** | radioactivity | a defect is an unstable form of a healthy element, not a family of its own |
| **Bonds** | bond lengths | the **metric interval**: ΔZ to the pulse, log₂ of a whole number |

The periodic law can be tested. **Compress an element in time, and it must become another element of its own column.** A real drum stem played 32 times faster turns into a pitch whose period is exactly 2.00, 2.00 and 1.00 pulses of the original, on three tracks, within 0.3%.

## What has been measured

Every claim needs a number, a control with a known answer, and a check on data the method has not seen. Listening is never the deciding argument.

| Finding | Evidence |
|---|---|
| The bar is an element whose Z moves with tempo | At 80.5 and 100 BPM the bar landed at Z **16.58** and **16.26**, the values written down *before* measuring |
| Metric levels nest as whole numbers | Chord changes sit at ΔZ = log₂ 4 or log₂ 8 from the pulse, **within 0.003**, at every tempo |
| No hidden bias towards doubling | A waltz gives **3** beats per bar; a real 6/8 march gives **3** eighths per beat and **2** beats per bar |
| Natural vibrato lives in the predicted cell | Voices and a solo violin land at **Z 12.3–12.5**; a piano control gives **no** false alarms |
| The method can say no | Two tracks requested in 6/8 came out binary, and the method reported that |

The open questions are listed just as plainly: a clean definition of the pulse, meter in tempo-bending live music, and vibrato inside a mix. See the [article](articles/01_the_periodic_table_of_sound.md).

## How large is the space?

The third edition holds **59** stable elements.

| | Combinations |
|---|---|
| Any set of elements | 2⁵⁹ ≈ **5.8 × 10¹⁷**, about the number of seconds since the Big Bang |
| Every element with a five-position dial | 6⁵⁹ ≈ **8.1 × 10⁴⁵** |
| Compounds of 8 elements, five positions each | **8.7 × 10¹⁴**, about **800 million years** of listening at 30 s each |
| Second-order elements (a question asked of another element's track) | **354**, of which the table holds 10 so far |

## Open it

- **The table:** open [`table/standalone/Periodic_Table_of_Sound_edition3.html`](table/standalone/Periodic_Table_of_Sound_edition3.html) in a browser. Click any tile for its time octave, its measured range and its metric interval.
- **The collider:** open [`lab/collider.html`](lab/collider.html). Choose elements, set their dials and press *Collide*. The sound is synthesised from scratch, the detectors search the stems without seeing the recipe, and *Run controls* removes each element in turn.
- **Everything at once:** [`index.html`](index.html) is the landing page, ready for GitHub Pages.

## Quick start

```bash
git clone https://github.com/alex-gerek/periodic-table-of-sound.git
cd periodic-table-of-sound
python -m pip install -r requirements.txt
python -m pytest tests
```

The measuring code in [`pts/`](pts) depends only on numpy. The experiments in [`experiments/`](experiments) read stems with `soundfile`. The ground-truth audio is not published; [`data/README.md`](data/README.md) explains which material each experiment expects.

## Repository

| Path | Contents |
|---|---|
| [`table/`](table) | The three editions of the table, with standalone copies |
| [`lab/`](lab) | The Sound Collider |
| [`pts/`](pts) | The measuring code: time octaves, periodicity, partial tracks |
| [`tests/`](tests) | Ground-truth tests on synthetic signals |
| [`experiments/`](experiments) | Dated experiments with scripts, results and write-ups |
| [`docs/`](docs) | The ordering rules, the two time axes, literature notes |
| [`articles/`](articles) | Articles about the project |
| [`data/`](data) | Material notes, sources and licences (no audio) |
| [`ROADMAP.md`](ROADMAP.md) | The progress log and the plan |

## Principles

- **Measure, don't guess.** A ground-truth test, a number and a held-out check for every claim.
- **Our own mathematics.** Methods from papers are re-derived and implemented from scratch; no third-party models.
- **Our own names.** Elements are named from physics, in our own words.
- **English** for everything written in the repository.

## Relatives

Henry Cowell (*New Musical Resources*, 1930) and Karlheinz Stockhausen ("…wie die Zeit vergeht…", 1957) treated rhythm and pitch as one continuum. The dice game attributed to Mozart and the algorithmic music of Iannis Xenakis generated music by combination. What is new here is the combination: one measured axis, six questions, a falsification test for every column, and a collider for predicted elements.

## Credits

Recordings used in the experiments keep their own licences. The full list is in the [article](articles/01_the_periodic_table_of_sound.md#credits-for-material) and in the `SOURCES.txt` files under [`data/material/`](data/material). The project grew out of [PHARMAKON](https://github.com/alex-gerek/PHARMAKON), an open-source mastering and restoration tool for AI-generated music.

## Authors and licence

Created by **Lex Gerek** together with **Claude** (Anthropic), who is credited as co-author in the commits.

Released under the [MIT licence](LICENSE). To cite the project, see [`CITATION.cff`](CITATION.cff).
