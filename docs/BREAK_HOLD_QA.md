# Break PERF hold correction

Scope: RHYTHMER OS for MPC Sample. No MPC 3 plug-in changes or public deployment.

- Page order: ROLLS / HOLD PADS, CHOPS, SOURCE A/B, LOOP VARIATIONS, GRAIN / STRETCH, TRACK MIX. All existing entry points still open page zero.
- Physical commands have their own bounded priority stack and EngineCall provenance. Sequenced chop events and recorded command note-offs cannot clear a physical hold. The last held effect wins; releasing it restores a still-held earlier effect.
- Performance commands bypass Note Repeat and Arp gates. Chop playing keeps the existing sampler path. Recorded command numbers and file format are unchanged.
- The separate recorded-command stack retains a gated effect across incoming chops. The pinned original FM-1 DSP is unchanged.
- Page changes inside BRK PERF preserve the hold. Back, GEN and track changes release it using existing pad ownership cleanup.

## Verification

- Pre-fix reproducer: STRETCH activity changed from 7 to 3 on the next sequenced chop.
- Address/undefined-behavior sanitizers: all 16 effects, varying incoming chop velocities, recorded releases of the same effect, overlapping holds and duplicate downs passed.
- Original reference: 16 effects, maximum sample error zero; three sample rates, four source lengths; 2,400 Acid reference cases passed.
- Full build, 50 unit tests, 1,248 navigation contexts / 9,538 assertions, track workflow check, GEN shell check, 12-seed / 3,000-move random interaction check and self-test passed.
- Native Shell Break P1: direct, Note Repeat and Arp contexts; paging hold, GEN/back/track release, source/save/load/undo/redo routes; 384 finite nonzero audio cases passed.
- Preview: 511 pages, zero text issues. Manual and first-groove page order and first two screen captures updated locally.

These are software/native-host results. Physical-device behavior remains to be confirmed. No new public release or installer upload was performed.

## FX command pressure

Live and recorded effect commands preserve the sounding chop gain. Their pad/MIDI velocity does not act as a second master volume. The first live hold captures the current chop level; overlapping holds retain it. Chop MIDI velocity and the original effect envelopes remain unchanged. Comparing the same repeat command at velocities 32 and 127 reproduced a -11.973 dB difference before correction and 0 dB after it. The 16-command sanitizer regression now compares different pad pressures as well as overlapping holds and sequencer events.
