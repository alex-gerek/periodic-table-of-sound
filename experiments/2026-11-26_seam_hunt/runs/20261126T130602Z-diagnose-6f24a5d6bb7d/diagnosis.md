# Seam hunt: post-hoc diagnosis

Source: `runs\20261126T130343Z-final-8b6fbfe16b76\results.json`. Exploratory, written after the results.

## 1. Bandwidth seams by the energy above 16 kHz before the join

| Energy above 16 kHz against 8-16 kHz (window median) | Seams | Found by S_bw |
|---|---|---|
| -200 to -40 dB | 7 | 0 |
| -40 to -30 dB | 0 | 0 |
| -30 to -20 dB | 16 | 11 |
| -20 to -10 dB | 55 | 22 |
| -10 to 100 dB | 17 | 10 |

| Recording | Median energy above 16 kHz (dB re 8-16 kHz) |
|---|---|
| tsalapishko_krivo_horo_gerganov.ogg | -55.2 |
| 451425__kyles__ganpati-celebration-on-beach-night-singing-cl | -22.2 |
| 755187__kevp888__240815_140056_fr_marching_band_in_metzerral | -21.8 |
| 651551__kevp888__voc_220924-2106-1_fr_bagpipes.wav | -19.3 |
| 819225__studioste__irish-trad-music-navvy-on-the-shore-fast. | -19.2 |
| 185552__rtb45__brass-wedding-band-china.wav | -18.8 |
| 391806__martineerok__folkfestival-indoors.wav | -18.4 |
| 772213__kevp888__241130_153241_fr_marching_band_outdoor.wav | -17.2 |
| 110333__tomlija__traditional-eastern-instrument-macedonian-t | -16.1 |
| 171092__ondrosik__body_rhythm.wav | -15.3 |
| 486407__martineerok__ottoman-taksim-music-soundcheck.wav | -15.3 |
| 173210__felixblume__a-young-girl-singing-while-crushing-mill | -13.3 |
| 812937__zachrau__school-marching-band-in-central-america.wav | -12.8 |
| 276887__christopherbrooks__violin-improv.wav | -12.3 |
| king-oliver_working-man-blues_1923.flac | -7.1 |
| nork_da-da-strain_1923.flac | -3.3 |
| nork_tin-root-blues_1923.flac | -3.1 |

## 2. Thresholds set by the live null

95th percentile of live window scores: S_all 12.7, S_bw 4.2.

| Seam | Median S_all with the seam | Median S_bw with the seam |
|---|---|---|
| bandwidth | 8.8 | 7.8 |
| floor | 4.4 | 1.5 |
| tilt | 4.4 | 1.4 |
| splice | 5.1 | 1.6 |
