# Empty-pad Push validation

Local Linux ARM64 validation, 2026-11-16. No deployment or installation performed. 

## Before the change

Actual surface-button dispatch confirmed that an empty sampler SOUND face cycles knob focus. It does so both after TRACKS → Push and after SAMPLE entry. TRIM stays on its face with no empty-sample binding to focus. Legacy TUNE and LAYERS Push opens the sampler page map; MIX retains its native controls. These are distinct from the never-assigned/intentional EMPTY track carousel.

## Implemented scope

See [Track workflow](TRACK_WORKFLOW.md#empty-pad-encoder-push). Both an entirely empty sample kit and a selected empty pad in a populated sample kit open the sample browser. Secondary layers count as playable pad content. Only ordinary sampler SOUND/TRIM intercept empty-pad Push. Track type changes remain in TRACKS → TRACK SETUP → TRACK TYPE. Other editor clicks and Break retain their existing roles.

## Evidence

- Final ARM64 application build passed with warnings treated as errors; version unchanged.
- Track workflow suite passed **192 assertions**, including the new cases and existing real plug-in replacement, Undo/Redo, all-pattern retention, asynchronous target ownership, contextual controls and safe dialog Back checks.
- Direct choice tested for PLUG-IN, SAMPLE KIT, MIDI and EMPTY; cancellation returns to the caller.
- Selected-pad sample assignment and Undo checked at model level; no new audio/DSP behavior is introduced.
- Loaded and layered pads, samples in bank H, legacy maps, recording/Freeze guards and Break loop entry covered.
- Complete integration patch replay passed; the four changed sources reproduce exactly and all locked integration input hashes match.

Runtime logs and before/after route traces are retained in the SSD QA directory `empty-pad-qa-20261116`. This evidence does not establish physical panel behavior or an SD installation.

The expanded release candidate additionally covers preset list and main-face wrapping on all 19 preset-bearing instrument entries (Break retains its loop browser), bringing the track suite to 290 assertions. Acid Engine’s eight Aphex source aliases have separate host/control/state checks.
