# Technical contracts

- Rhythmer OS is a standalone MPC Sample groovebox based on pinned Melodee/sample-base sources.
- Existing sampler voice allocation, sequencer, audio drivers and recovery remain the runtime foundation.
- Original engine DSP, stable plugin identity and required copyright/license notices are retained.
- Project compatibility retains MELODEE1 and legacy plugin state keys.
- GEN8 writes native patterns on the control thread. Engine profiles describe ranges, monophony and drum notes.
- User break audio stays on the user's storage. No factory break library or proprietary ROM is included.
- Source builds, offline tests and real-device validation are reported separately.
- Public documentation describes the software, build procedure and evidence. Private development material is excluded.

- Track instrument/type replacement retains all patterns and uses native undo; track deletion is separately confirmed. Track-owned browsers follow the selected track, while shared bus/master editors retain global ownership. See TRACK_WORKFLOW.md.

- TRACK SETUP opens only with B1 TRACK SETUP on TRACKS. Encoder Push retains native track opening; intentional EMPTY tracks use the native type carousel, preserving patterns. Stage Shift shortcuts retain native behavior.

- Acid GEN keeps its original NEW/MUTATE random policy and saved state. Only its seed knob/readout and Replay menu are removed; six musical settings occupy two pages. General GEN and Break seed controls retain their behavior.


### Empty sampler source shortcut — 2026-11-16

DECIDED: On SOUND/TRIM only, encoder Push on a completely empty Sample Kit opens TRACK TYPE. If other pads contain primary or layered samples, Push on an empty pad opens the native SAMPLES browser for that pad. Keep native clicks on loaded/layered pads and other editor pages; preserve recording/Freeze and Break-specific entry. SAMPLE KIT from the direct chooser begins sample loading; cancelling returns to the source face. No release or installation is implied by this source change.
