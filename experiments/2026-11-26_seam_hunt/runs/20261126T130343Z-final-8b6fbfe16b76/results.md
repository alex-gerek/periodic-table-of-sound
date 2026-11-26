# Seam hunt, pilot: results

Run `20261126T130343Z-final-8b6fbfe16b76`. Windows of 30 s, change of the median over 6 s on each side, flagged at conformal p <= 0.05. Rates with exact 95% intervals.

## P1: live windows flagged (leave one recording out)

- S_all: 4 of 95 (4.2%, 95% CI 1.2 to 10.4%)
- S_bw: 5 of 95 (5.3%, 95% CI 1.7 to 11.9%)

| Recording | Windows | Flagged by S_all | Flagged by S_bw |
|---|---|---|---|
| 110333__tomlija__traditional-eastern-instrument-macedonian-t | 5 | 0 | 0 |
| 171092__ondrosik__body_rhythm.wav | 7 | 0 | 0 |
| 173210__felixblume__a-young-girl-singing-while-crushing-mill | 2 | 0 | 0 |
| 185552__rtb45__brass-wedding-band-china.wav | 13 | 0 | 1 |
| 276887__christopherbrooks__violin-improv.wav | 1 | 0 | 0 |
| 391806__martineerok__folkfestival-indoors.wav | 6 | 0 | 0 |
| 451425__kyles__ganpati-celebration-on-beach-night-singing-cl | 10 | 0 | 1 |
| 486407__martineerok__ottoman-taksim-music-soundcheck.wav | 3 | 0 | 0 |
| 651551__kevp888__voc_220924-2106-1_fr_bagpipes.wav | 7 | 0 | 0 |
| 755187__kevp888__240815_140056_fr_marching_band_in_metzerral | 7 | 1 | 3 |
| 772213__kevp888__241130_153241_fr_marching_band_outdoor.wav | 8 | 0 | 0 |
| 812937__zachrau__school-marching-band-in-central-america.wav | 1 | 0 | 0 |
| 819225__studioste__irish-trad-music-navvy-on-the-shore-fast. | 1 | 1 | 0 |
| king-oliver_working-man-blues_1923.flac | 6 | 2 | 0 |
| nork_da-da-strain_1923.flac | 5 | 0 | 0 |
| nork_tin-root-blues_1923.flac | 6 | 0 | 0 |
| tsalapishko_krivo_horo_gerganov.ogg | 7 | 0 | 0 |

## P2: known seams found (flagged and within 1 s of the join)

| Seam | Cases (excluded) | Found by S_all | Found by S_bw | Flagged by S_all, any time |
|---|---|---|---|---|
| bandwidth | 95 (0) | 9 of 95 (9.5%, 95% CI 4.4 to 17.2%) | 43 of 95 (45.3%, 95% CI 35.0 to 55.8%) | 17 of 95 (17.9%, 95% CI 10.8 to 27.1%) |
| floor | 95 (0) | 1 of 95 (1.1%, 95% CI 0.0 to 5.7%) | 5 of 95 (5.3%, 95% CI 1.7 to 11.9%) | 5 of 95 (5.3%, 95% CI 1.7 to 11.9%) |
| tilt | 95 (0) | 1 of 95 (1.1%, 95% CI 0.0 to 5.7%) | 0 of 95 (0.0%, 95% CI 0.0 to 3.8%) | 4 of 95 (4.2%, 95% CI 1.2 to 10.4%) |
| splice | 89 (6) | 0 of 89 (0.0%, 95% CI 0.0 to 4.1%) | 3 of 89 (3.4%, 95% CI 0.7 to 9.5%) | 3 of 89 (3.4%, 95% CI 0.7 to 9.5%) |

## P3: Suno windows flagged (against all live windows; a comparison, not a calibrated test)

- S_all: Suno 5 of 65 (7.7%, 95% CI 2.5 to 17.0%); live 4 of 95 (4.2%, 95% CI 1.2 to 10.4%)
- S_bw: Suno 13 of 65 (20.0%, 95% CI 11.1 to 31.8%); live 5 of 95 (5.3%, 95% CI 1.7 to 11.9%)

Candidates for a test with known join times (not counted as seams):

| Track | Window start | S_all time | S_all | p_all | Feature | S_bw time | S_bw | p_bw |
|---|---|---|---|---|---|---|---|---|
| gravity | 240 s | 258 s | 24.0 | 0.010 | floor 100-188 Hz | 246 s | 1.4 | 0.510 |
| tempo_080_4-4_retake | 120 s | 138 s | 9.6 | 0.125 | bandwidth ratio | 138 s | 9.6 | 0.010 |
| tempo_120_4-4 | 0 s | 13 s | 10.8 | 0.083 | floor 8484-16000 Hz | 10 s | 9.3 | 0.010 |
| vibrato_baritone_01 | 30 s | 45 s | 11.1 | 0.083 | bandwidth ratio | 45 s | 11.1 | 0.010 |
| vibrato_soprano_01 | 0 s | 10 s | 9.6 | 0.125 | floor 2385-4498 Hz | 8 s | 9.3 | 0.010 |
| tempo_120_4-4 | 120 s | 143 s | 6.8 | 0.240 | bandwidth ratio | 143 s | 6.8 | 0.021 |
| tempo_140_4-4 | 90 s | 114 s | 8.7 | 0.177 | floor 4498-8484 Hz | 97 s | 6.2 | 0.021 |
| tempo_160_4-4 | 0 s | 20 s | 7.4 | 0.198 | floor 8484-16000 Hz | 8 s | 5.8 | 0.021 |
| tempo_160_4-4 | 120 s | 127 s | 9.3 | 0.146 | floor 2385-4498 Hz | 133 s | 7.4 | 0.021 |
| vibrato_baritone_01 | 0 s | 9 s | 20.0 | 0.021 | floor 8484-16000 Hz | 7 s | 5.5 | 0.021 |
| vibrato_soprano_01 | 30 s | 46 s | 15.9 | 0.021 | floor 8484-16000 Hz | 44 s | 5.8 | 0.021 |
| tempo_100_4-4 | 0 s | 22 s | 15.0 | 0.031 | floor 2385-4498 Hz | 22 s | 1.2 | 0.625 |
| tempo_160_4-4 | 90 s | 108 s | 9.1 | 0.167 | floor 8484-16000 Hz | 107 s | 4.6 | 0.031 |
| meter_6-8 | 120 s | 134 s | 13.9 | 0.031 | floor 4498-8484 Hz | 133 s | 3.5 | 0.104 |
| gravity | 60 s | 76 s | 12.4 | 0.073 | floor 100-188 Hz | 84 s | 4.6 | 0.042 |
| pure_voltage | 90 s | 96 s | 4.6 | 0.458 | bandwidth ratio | 96 s | 4.6 | 0.042 |

## Score medians

| Set | S_all | S_bw |
|---|---|---|
| live | 4.26 | 1.37 |
| Suno | 6.51 | 1.82 |

Run time: 107 s.
