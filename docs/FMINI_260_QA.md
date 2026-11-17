# FMini-1 2.6.0 integration (local candidate)

Original source: https://github.com/ruppert/fmini-1/commit/02f5c53b09e85c132fba01132935218a5a737cff
Previous pin: 74375d3311889d8e28e6b2601d30f0df4faf70ab (2.5.13).

## Scope

- Original oscillator first-write/BLEP and voice-ramp optimisations, FX loop optimisations and delay-off-at-zero behavior.
- Original CA-72-calibrated biased ladder, linear mixer headroom, 6.3-octave contour taper and matching 200 factory records. DSP files are copied unchanged from upstream.
- Added the original bank generators and their level JSON to corresponding source provenance. Regenerating the complete preset header now matches the pinned header byte-for-byte. Names and order of all 200 presets are unchanged.
- Fixed an older adapter omission: hostsim's generic factory loader did not invoke FMini's separate factory-extras loader. The adapter now reuses the original `fa_factory_extras` sound assignments, including LFO, modulation, level, release settings, wheel/bend and 12 FX values. The original ARP assignments and device octave assignment are excluded: Rhythmer owns MIDI sequencing and pad layout. No preset is newly authored.
- 168 native control IDs/ranges/options, params.lock and source-panel order are unchanged. The host presents 112 editable sound controls; firmware sequencing/preset administration controls remain hidden. Defaults now reflect the correctly loaded first original preset.
- No legacy sound compensation or new state migration is added, per the user's direction. Raw contour values are retained; old edited sounds can sweep differently under the new upstream filter. Delay MIX zero now stops the delay and it restarts silent when raised, as upstream specifies.

## Software evidence

`/Volumes/SSD/Development/BuildCache/rhythmer-os/fmini-260-20261117/`

- Native ARM64 compilation and recovery/state/MIDI checks passed.
- Compiled original-table assertions cover all 200 factory patches, LFO/modulation/levels/12 FX assignments and state reloads.
- 600 PCM renders (200 programs × MIDI notes 36/60/84; 2.5-second hold plus release): no zero-output case, no clipped sample; maximum absolute sample 24344. All 600 hashes differ from 2.5.13, as expected from the upstream filter and restored extras. This is a numerical signal check, not listening acceptance.
- The same 600-case render/state suite passed with the original native DSP and adapter instrumented by AddressSanitizer (leak checking disabled).
- Actual Rhythmer rack: FMini-1 200 presets/112 controls; full host control round trips: 75 contexts, 4587 controls, zero issues. This host run used the existing instrumented host with the newly built native engine.
- Current original sources and the compiled candidate have hash receipts in `SOURCE.json` and the SSD candidate receipt. Local SD staging copies updated; public archives and release assets untouched. Full release acceptance receipts must be regenerated after the new-engine work is complete.

Not performed: hardware installation, sustained real-device CPU/polyphony stress, or human listening. Publication remains held.
