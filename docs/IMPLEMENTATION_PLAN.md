# Implementation scope

See [current inventory](ENGINE_REGISTRY.md) and [verification](VERIFICATION.md) for 0.4.0-beta.3.

Engine home uses original names, named preset, selected pad, common MIX/SENDS/SOURCE/SAVE pages and input-reactive monochrome graphics. EDIT opens paged original controls. Kit controls show KIT MIX and the selected destination pad only; parameter names start with its pad number. Per-pad replacement forks the source on demand. Original engine selectors and Sound/PRESETS remain synchronized.

GEN retains the original FM-1 four-track role and seed logic with 1–4/5–8/9–12/13–16 targets, one-track/range MIDI ONLY, Undo/Redo and engine-specific Acid/Break views. Source assignment is generated exclusively from the selected catalogue. Excluded engine implementations are absent. Real-device validation is pending.

Track management now has native TRACK SETUP, focused kit loading and pattern-preserving instrument/type replacement. Browser ownership, cancellation, Undo/Redo, empty-track input gating and late-load target isolation are described in TRACK_WORKFLOW.md. Local host validation is complete; release and physical installation remain held.
