# Data

Audio is not stored in git. Stems live in `data/stems/<track>/`, which is listed in `.gitignore`.

## Ground-truth stems

These are the user's own Suno stem exports. They are the reference for every separation and measurement test.

| Track | Stems | Source | Local folder |
|---|---|---|---|
| Metro | 8 | the author's archive (not published) | `data/stems/metro/`, or set `PTS_METRO_STEMS` |
| GRAVITY HAS AN ADDRESS | 10 | the author's archive (not published) | `data/stems/gravity/` |
| Pure voltage | 12, including guitar | the author's archive (not published) | `data/stems/pure_voltage/` |

- Metro has a quiet vocal; it is good for drums and bass.
- GRAVITY is vocal-heavy.
- Pure voltage is the held-out track. Methods are tuned on the other two and checked on this one.

## Not valid as ground truth

The Bronze Psalter and Vector Pulse demo stems were produced by PHARMAKON's own splitter. Scoring a splitter against its own output proves nothing.

## Restoring the local copies

Unzip the original archive into the matching folder under `data/stems/`. File names stay as exported, for example `2 Drums.wav`.
