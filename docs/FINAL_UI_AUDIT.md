# Native UI audit scope

This revision uses Melodee 0.2.0 PRESETS/EDIT, replacing the earlier functional-page/map presentation. Earlier beta.1 screenshot counts do not establish acceptance for this revision. See VERIFICATION.md for the current build's completed checks.

Coverage includes every selected plugin context; all 25 source views and their original named bank/model choices; all 36 complete Rhythmer Kits and 576 first-bank pad routes; selected-pad ownership, source replacement and save/restore; empty-pad and empty-track views; PRESETS names, EDIT labels/values/order and list position; and engine-specific dynamic algorithm controls.

GEN retains four target groups, original FM-1 seeded logic, kit/instrument assignment, single/range MIDI-only generation and atomic Undo/Redo. Acid and Break pages are contextual. Break BRK PERF includes A/B, Return and recorded/replayed commands. Back returns to the owning GEN screen. These paths are checked against actual host/shell fixtures rather than screenshots alone.

Factory bank data is independently compared to pinned sources. Prophet and Elixir's excluded external banks remain excluded; explicitly authorized independently authored patches are identified separately. Native parameter keys remain stable. Source-only sequencer/storage actions and packed bytes are not presented as sound controls. Synth and Track LFO labels distinguish different modulation layers. Motion does not claim arbitrary plugin-parameter learning.

All final acceptance passes must use the same catalog/native libraries and tested runtime. A correction invalidates acceptance for the affected behavior; extra final passes begin only after baseline problems are resolved. Software rendering/PCM does not establish MPC display contrast, knob feel, acoustic output, latency or USB/device installation behavior.
