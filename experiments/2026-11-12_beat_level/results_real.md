# Beat level: real drum stems

The tempo written in a Suno prompt is not a label: a generation can differ from it. A track is scored only when its beat is **verified** in `labels.json`. **Ambiguous** tracks are listed apart. **Unverified** tracks show the level each rule returns and are not scored.

| Track | Label | Old rule | New rule | Same level |
|---|---|---|---|---|
| gravity | unverified | 119.0 BPM | 119.0 BPM | yes |
| pure_voltage | unverified | 111.5 BPM | 111.4 BPM | yes |
| tempo_080_4-4 | unverified | 122.0 BPM | 121.9 BPM | yes |
| tempo_080_4-4_retake | unverified | 80.5 BPM | 160.9 BPM | **no** |
| tempo_100_4-4 | unverified | 100.0 BPM | 100.0 BPM | yes |
| tempo_120_4-4 | unverified | 121.1 BPM | 121.0 BPM | yes |
| tempo_140_4-4 | unverified | 141.6 BPM | 141.2 BPM | yes |
| tempo_160_4-4 | unverified | 164.1 BPM | 164.0 BPM | yes |
| tempo_174_4-4 | ambiguous: 174.0, 87.0 BPM | 43.5 BPM | 174.0 BPM | **no** |
| meter_3-4 | unverified | 60.8 BPM | 181.9 BPM | **no** |
| meter_6-8 | unverified | 127.9 BPM | 128.2 BPM | yes |
| meter_6-8_retake | ambiguous: 105.0, 210.1 BPM | 210.1 BPM | 210.1 BPM | yes |
| metro | unverified | 132.0 BPM | 132.1 BPM | yes |

**Verified:** none yet.

**Ambiguous:** tempo_174_4-4: old multiple, new exact, meter_6-8_retake: old exact, new exact
