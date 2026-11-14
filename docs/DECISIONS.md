# Technical contracts

- Rhythmer OS is a standalone MPC Sample groovebox based on pinned Melodee/sample-base sources.
- Existing sampler voice allocation, sequencer, audio drivers and recovery remain the runtime foundation.
- Original engine DSP, stable plugin identity and required copyright/license notices are retained.
- Project compatibility retains MELODEE1 and legacy plugin state keys.
- GEN8 writes native patterns on the control thread. Engine profiles describe ranges, monophony and drum notes.
- User break audio stays on the user's storage. No factory break library or proprietary ROM is included.
- Source builds, offline tests and real-device validation are reported separately.
- Public documentation describes the software, build procedure and evidence. Private development material is excluded.
