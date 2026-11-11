# Suno prompts for the measurement material

Rule for every series: **the same prompt, and only the measured parameter changes.** Export the **stems** (WAV) and keep the requested value in the folder name.

## Series 1: tempo (6 tracks, 4/4)

**Style** (the same for all six; only the BPM number changes):

```
instrumental electronic groove, 4/4 time, steady tempo at 120 BPM, four-on-the-floor kick on every beat from start to end, closed hi-hat on every eighth note, clap on beats 2 and 4, one bass note per beat, simple warm chord pad changing once per bar, 8-bar phrases, clean mix, no tempo changes
```

**Exclude styles:**

```
vocals, singing, half-time, double-time, swing, tempo change, ritardando, rubato, breakdown without drums
```

| Track | Folder name | Number in the prompt |
|---|---|---|
| 1 | `tempo_080_4-4` | `steady tempo at 80 BPM` |
| 2 | `tempo_100_4-4` | `steady tempo at 100 BPM` |
| 3 | `tempo_120_4-4` | `steady tempo at 120 BPM` |
| 4 | `tempo_140_4-4` | `steady tempo at 140 BPM` |
| 5 | `tempo_160_4-4` | `steady tempo at 160 BPM` |
| 6 | `tempo_174_4-4` | `steady tempo at 174 BPM` |

**Title:** the folder name, for example `tempo_080_4-4`.

The exact tempo does not matter, because we measure it. If a track comes out at half or double the requested speed, keep it and note that in a text file next to it. It is useful data in its own right.

## Vibrato, second attempt

**Style:**

```
solo female classical soprano, slow aria, long sustained notes held for several seconds, wide expressive operatic vibrato on every held note, very sparse piano accompaniment, slow tempo, lots of space between phrases
```

**Exclude styles:**

```
choir, backing vocals, autotune, vocoder, drums, pads, synth
```

**Lyrics:** a few long vowels are enough, for example:

```
[Verse]
Aaaa... ooo...
Lu-naaa... a-mo-re...
```

**Folder:** `vibrato_soprano_01`, with **stems** so that the vocal can be measured on its own.

A male voice for comparison: replace the first words of the style with `solo male operatic baritone` and name the folder `vibrato_baritone_01`.

## Series 1, retake of 80 BPM

The first 80 BPM request came out at about 122 BPM: the electronic-groove style pulls Suno towards dance tempos. The retake names a slow genre and excludes fast ones.

**Style:**

```
instrumental downtempo hip hop, 4/4 time, slow laid-back groove at 80 BPM, kick and snare boom-bap pattern with snare on beats 2 and 4, closed hi-hat on every eighth note, one bass note per beat, warm Rhodes chords changing once per bar, 8-bar phrases, steady tempo throughout, clean mix
```

**Exclude styles:**

```
vocals, singing, rap, fast, dance, house, techno, drum and bass, 120 BPM, double-time, half-time, tempo change, swing
```

**Lyrics:** the same structure tags as the rest of the series. **Folder:** `tempo_080_4-4_retake`.

## Series 2: meters (the test that is not a power of two)

All the earlier tracks nest in powers of two. A waltz and a 6/8 piece are cases where the right answer is 3. If the method finds 3 here, it measures the music and not its own bias.

### 3/4 waltz

**Style:**

```
instrumental waltz in 3/4 time, 120 BPM, strong oom-pah-pah: bass note on beat 1, chord stabs on beats 2 and 3, light drum kit with kick on beat 1 and soft snare on beats 2 and 3, piano and strings, chords changing once per bar, steady tempo throughout, clean mix
```

**Exclude styles:**

```
vocals, singing, 4/4, common time, four on the floor, backbeat, swing, half-time, double-time, tempo change, rubato
```

**Folder:** `meter_3-4`. Expected: bar = 3 beats, ΔZ = log2 3 = 1.585.

### 6/8

**Style:**

```
instrumental piece in 6/8 time, two dotted-quarter beats per bar, each beat clearly divided into three eighth notes, drum kit with kick on beat 1 and snare on beat 4 of the six eighths, hi-hat on every eighth note, acoustic guitar arpeggios in groups of three, chords changing once per bar, steady tempo, about 60 dotted-quarter beats per minute
```

**Exclude styles:**

```
vocals, singing, 4/4, straight eighths, four on the floor, half-time, double-time, tempo change, rubato
```

**Folder:** `meter_6-8`. Expected: beat = 3 eighths (ΔZ = 1.585 from the eighths), bar = 2 beats (ΔZ = 1 from the beat).

### 6/8, retake

The first 6/8 came out binary (about 128 BPM, groups of 2, 4 and 8) and with vocals. The retake names a genre that is 6/8 by nature.

**Style:**

```
instrumental Irish jig in 6/8 time, fiddle and tin whistle playing running triplets, every beat divided into three eighth notes, bodhran drum accenting beats 1 and 4 of each six-eighth bar, acoustic guitar strumming in groups of three, lively steady tempo, chords changing once per bar
```

**Exclude styles:**

```
vocals, singing, choir, 4/4, straight eighths, backbeat, rock, pop, electronic, four on the floor, half-time, double-time, tempo change
```

**Folder:** `meter_6-8_retake`.
