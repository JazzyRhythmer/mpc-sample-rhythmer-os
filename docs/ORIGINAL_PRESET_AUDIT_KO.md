# Preset and library provenance

The release contains 20 picker entries, 25 source views, 36 complete Rhythmer Kit layouts and 2,563 sound/model selections. Of these, 2,520 are retained source selections and 43 are explicitly identified Rhythmer originals: 15 Prophet sounds and four Elixir kits split into 28 native voices. Original preset names and source values remain for all other engines. No hidden envelope overrides are applied.

| Engine / source view | Selections | Basis |
|---|---:|---|
| CS-1  | 69 | Original factory bank / voice or model palette |
| DRUM-X  | 72 | Original factory bank / voice or model palette |
| Elixir  | 35 | GPL Initkit + four Rhythmer kits, each seven voices; external Erica/Hrtl banks excluded |
| FM-106  | 128 | Original factory bank / voice or model palette |
| FMini-1  | 200 | Original factory bank / voice or model palette |
| Guru-600  | 255 | Original factory bank / voice or model palette |
| Hortator  | 147 | Original factory bank / voice or model palette |
| K-WASUB  | 97 | Original factory bank / voice or model palette |
| K-WASUB Drum mode | 32 | Original factory bank / voice or model palette |
| MONO2K  | 112 | Original factory bank / voice or model palette |
| OberVave  | 64 | Original factory bank / voice or model palette |
| Prophet  | 16 | GPL Init + 15 Rhythmer originals; Sequential external bank excluded |
| S1Vave  | 64 | Original factory bank / voice or model palette |
| Aphex  | 41 | Original factory bank / voice or model palette |
| Braids  | 10 | Original factory bank / voice or model palette |
| Dexed  | 1056 | Original factory bank / voice or model palette |
| Hera  | 56 | Original factory bank / voice or model palette |
| Plaits  | 24 | Original factory bank / voice or model palette |
| Sophie  | 16 | Original 16 default voices; no separate factory bank |
| 6W6  | 8 | Original factory bank / voice or model palette |
| 8W8  | 16 | Original factory bank / voice or model palette |
| 9W9  | 11 | Original factory bank / voice or model palette |
| CW-78  | 14 | Original factory bank / voice or model palette |
| TR-MPC  | 16 | Original factory bank / voice or model palette |
| Acid Engine  | 4 | Original factory bank / voice or model palette |

The 200-program Sequential bank and 117 Erica/Hrtl kit files are absent from this public build, corresponding source exports and rebuilt modules. The original software has GPL Init implementations, which remain. External-bank exclusion records 118 file fingerprints without redistributing the files. The software license is not treated as a blanket license for external bank data. The Elixir notice describes permission for the original project; extension of that permission to this port has not been established. This is not a finding that personal use is prohibited.

Four sample-dependent Hortator presets and three input-only MONO2K models are excluded with reasons. Empty library slots are not duplicated as presets. The remaining original banks, native names, bank selectors and generated tables are independently compared with pinned sources. Dexed retains 33 original SysEx banks / 1,056 programs. Full numerical records are in `config/preset-coverage.json`.

See [Rhythmer originals](RHYTHMER_PRESETS.md), [source notices](../THIRD_PARTY_NOTICES.md), and [verification](VERIFICATION.md). Source attributions and notices remain even when external data is omitted.
