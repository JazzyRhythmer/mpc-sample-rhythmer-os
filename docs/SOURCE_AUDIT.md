# Source audit

The runtime and port sources are pinned in SOURCE_LOCK.json. Prebuilt artifact identity, download size and checksum are recorded in config/releases.lock.json. Port-specific changes are documented in ports/*/VENDORED.md.

The runtime supports sixteen tracks. The sampler's original per-track pool has 32 live and eight spare/fade slots. No new global 32-voice policy is introduced. Plugin voice counts remain engine-specific.

Existing sample-base startup/recovery, bounded command paths and plugin lifecycle boundaries are retained. The third-party Open MPC wrapper uses its original mutex; hard real-time compliance is not asserted.

Rhythmer musical source snapshots, GPL notice and hashes are in third_party/jiant-gen. Native adaptation coverage is described in GEN8_BREAK.md. No proprietary ROM or bundled break audio is supplied.

Offline validation results are in VERIFICATION.md. Full asset/dependency redistribution review and real-device validation remain separate gates.

Track navigation was compared with pinned Melodee v0.2.0 (`8880d16116ccb3c69f75fb46bf2166b16c51ef0c`). Its TRACKS page contains no replacement/type menu. The fork adds that menu using native load/undo/Freeze primitives, fixes empty-track input gating, and captures asynchronous kit/bank/Break destinations. See TRACK_WORKFLOW.md for source findings and host/device evidence boundaries.

Acid GEN seed visibility is an interface-only adaptation. Native TB-3PO generation, the FM-1 bridge, runtime random-policy code and project serialization remain unchanged. Two Acid settings pages retain Density/Accent/Slide and Octaves/Base Octave/Auto Mutate.


### Manual save and per-project recovery — 2026-11-19

DECIDED: SAVE chooses a folder/name on first save and updates the current file thereafter. SAVE AS chooses another destination and creates an independent project identity. Idle autosave updates one separate recovery entry per project under Rhythmer/Autosave; it never writes manual Project N files or overwrites an explicit save. OPEN/NEW use SAVE, DISCARD and CANCEL. This is a deliberate fork policy over the pinned Melodee saving model. See [Project saving and recovery](PROJECT_SAVE_RECOVERY.md) for the native-browser adaptation, state/media transaction boundaries and validation.


### BASIC SENDS doorway — 2026-11-20

The pinned Melodee v0.3.0 mixer hides B2 SENDS outside Full. The fork keeps its caption visible and offers the existing confirmation sheet to enable the native FEATURES setting. Full access, bus routing and source DSP are unchanged; other Basic gates remain. `tests/test_sends_access.py` exercises the actual surface dispatcher, cancel/back priority, shifted/repeat controls, native setting roundtrip and project-byte preservation.


### Rhythmer Kit pad mute — 2026-11-21

Rhythmer Kit reuses native MUTE tap/hold, SHIFT pad solo and SHIFT MUTE global reset, with existing Track.pad_mutes project persistence. Only the mute context recognizes its drum-note slots; sampler loading, copying, erase, sends, track selection and standalone plug-ins retain native classification. TRACKS remains track mute. The audio host caches the first 64 slots across load/late attachment and passes a lock-free mask to the internal kit rack. Muted note-ons are blocked at original note positions; note-offs and existing release/effect tails continue, avoiding cuts to other pads that share original DSP. No new preset data, per-pad DSP clone, parameter-volume edits or project format is introduced. Native mute/solo remain performance state rather than undo steps.
