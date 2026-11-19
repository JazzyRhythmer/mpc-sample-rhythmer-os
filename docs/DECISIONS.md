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


### Manual save and per-project recovery — 2026-11-19

DECIDED: SAVE chooses a folder/name on first save and updates the current file thereafter. SAVE AS chooses another destination and creates an independent project identity. Idle autosave updates one separate recovery entry per project under Rhythmer/Autosave; it never writes manual Project N files or overwrites an explicit save. OPEN/NEW use SAVE, DISCARD and CANCEL. This is a deliberate fork policy over the pinned Melodee saving model. See [Project saving and recovery](PROJECT_SAVE_RECOVERY.md) for the native-browser adaptation, state/media transaction boundaries and validation.


### Discoverable SENDS in BASIC — 2026-11-20

DECIDED: Keep MIX B2 SENDS visible in BASIC. Use the native confirmation to offer FULL; CANCEL preserves the mode and caller, ENABLE FULL persists the native FEATURES setting and opens track SENDS. Do not override repeat, shifted track actions or lesson restrictions. Existing FULL routes and native sampler pad-send cycling remain.
