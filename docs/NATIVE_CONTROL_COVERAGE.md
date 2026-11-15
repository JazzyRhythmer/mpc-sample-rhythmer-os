# Native sound-control coverage

The native boundary and presentation are checked separately. `check_control_coverage.py` compares every port contract key, in its original order, with the sound catalog and compiled source-panel membership. `audit_control_api.py` reads those keys from the actual native module. Compiled factory, state, MIDI and audio-effect tests verify behavior beyond metadata.

| Source | Restored sound controls / adaptation |
|---|---|
| FMini-1 | 168 controls. Original EDIT/ENV/LFO/FX order, fine oscillator detune, named switch bits, filter release/link, drive/chorus/reverb type, MIDI expression/pressure and original value formatting. Packed duplicate bytes stay hidden. |
| Prophet | 201 controls. Original synth envelope/LFO/poly-mod, distinct Track LFO/matrix, shared FX routing/return and three audio-FX slots with algorithm-specific labels/units. Retired and note-only shared FX choices stay hidden. |
| Guru-600 | 126 controls. Original visible synth/ENV/LFO/FX panels, reverb type, expression/pressure and source value/units formatting. |
| Hortator / Acid | 517 native controls. Per-voice dual LFO, four modulation slots, filter/envelope, resonator, insert/SRR, slicer, distortion and chorus/delay/reverb paths. Pad ownership filters the edit list. Acid keeps its ACID model fixed while retaining its resonator/filter/LFO/FX controls. |
| FM-106 | 42 controls, original 128-program bank, native arp enable, sustain and pitch bend. |
| MONO2K | 73 controls, original 16 audio machines and 96 library sounds. Three LFOs target this single-sound instance. Internal destination-track selectors are hidden and fixed to that instance. Destination bounds and value/units formatting follow the original UI. |
| CS-1, OberVave, S1Vave, K-WASUB, Elixir | Full mutable sound/patch structures or native parameter tables are exposed, with source voice ownership, enums and model labels. OberVave/S1Vave receive host tempo. Elixir's source formatter remains active. |
| Sophie | Original 16 percussion voices and their published sound controls. There is no invented internal LFO/matrix. Common host Motion targets remain available separately. |
| Aphex, Braids, Dexed, Hera, Plaits | Published native contracts, original parameter keys, modulation controls and banks/models. The Move GUI is replaced by the common host presentation; its DSP and available native controls are retained. |
| DRUM-X and classic drum packages | Original voice controls, selected-pad ownership and shared source controls. Kit-only variants remain accessible through Rhythmer Kit. |

Source sequencer, storage and hardware actions are handled by the Rhythmer host and are not presented as independent sound controls. Reserved FM4 operator envelopes do not control these non-FM4 engines and are hidden. Original programs are not silently rewritten to fit the interface. The excluded external Prophet/Elixir banks and the explicitly authorized new Rhythmer sounds are documented separately in ORIGINAL_PRESET_AUDIT_KO.md.

Appended controls retain earlier native IDs. The adapters accept the earlier FMini/Guru/Prophet/FM-106 state lengths and Hortator HKT2 state; new state includes the recovered controls. MONO2K keeps its native M2K2 state. Source Init/factory assertions and state tests exercise these boundaries.

Engine-native LFO/matrices and the host Motion MOD system are different layers. Motion learns supported host targets such as FILTER/ECHO/SPACE, not arbitrary internal plugin parameters. Software checks do not establish hardware timing, listening or full timbral equivalence with the original device.

## Saved sound reset and enum readback

Decorated numeric enum labels (for example 8′, 1/16 and 16T) are matched as labels before numeric-index fallback in rebuilt port wrappers. Bare integer indices keep the native API convention. DSP kernels and original bank data are unchanged.

Loading a User Sound/Kit establishes its saved parameter values as the reset baseline. Projects persist that baseline separately from later edits. Saved writable control values supplement native chunks where a module omits an edited control, while factory/bank selectors are not replayed over those edits.

## Control write stability and value formatting

Hortator's dynamic 0–127 control bridge uses nearest rounding in both directions. Every model's original integer range is checked for identity under read/write. Re-selecting its existing model preserves edits. FMini Filter Release retains its decay link when written with the current value; the separate link control still works. Exact repeated host edits are skipped on the worker and do not mark a sound as modified.

S1Vave and OberVave now use the original value-formatting functions from their pinned source, including envelope times, Hz/cutoff, signed offsets, percentages and S1 tempo-sync values. SOURCE.json records the source and fragment hashes; native sweeps cover every value. S1 abbreviations identify LFO, filter, riser and chord voices explicitly. TR-MPC labels distinguish Reverb/Delay Send from internal source FX and host track effects.

Plaits model controls follow the pinned 24-model label table. Its 96 embedded 6-Op programs are available by original bank/name, in the common PRESETS browser. Mapping compensates for the original SixOpEngine's 1.02 quantizer factor so names and selected programs agree, including the high bank indices. The duplicate internal preset selector and inactive FM Amount are hidden in EDIT for those three models; continuous model controls remain available for other models. Original DSP/banks remain unchanged.

The kit write-isolation audit changes a real control on each of 576 destination pads, compares all other routes before/after, and reloads the edited state to verify the same destination. This supplements prefix/render tests rather than inferring isolation from a label alone.

DRUM-X labels omit internal lane indices: Voice controls and Morph A/B controls identify the selected pad's source functions without L0/L1 or repeated A/A prefixes. The Hands macro is exposed only for the clap source, matching DV_CLAP in the original. The kit ownership probe additionally lowers the selected voice's actual gain, measures the resulting audio, and checks that the other routes retain their values.
