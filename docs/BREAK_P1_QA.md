# Break P1 integration — local candidate

P0 source replacement and Kit motion fixes remain included. P1 reuses a native SamplerEngine monitor for dry ORIGINAL/SYNC browsing, calculated source tempo from declared 1–4 bars, and pitch-preserving Beats warp. Preview does not assign a track, alter patterns/effects or enter prints/stems/input recordings. Limits: complete decode, under 30 seconds, speed ¼×–4×; otherwise ORIGINAL only. It starts when ready, not on a bar boundary. The displayed target uses the stabilised tempo text; audio follows the actual tempo.

Actual audio activity drives Variation READY/ACTIVE and STRETCH feedback. Exiting BRK PERF releases its held command keys only on that track; internal paging retains them. Sample replacement notifications now reset a Break engine only for its own A/B sources, preventing audition from restarting the playing break.

## Completed software checks

Evidence: `/Volumes/SSD/Development/BuildCache/rhythmer-os/break-p1-20261116/`.

- P1 route/decoder/preview suite and 384 native musical renders: 1–4 bars × aligned/offset/tail/trim × 90/140/175 BPM × four generators × CHOP/LOOP, alternating source A/B. Nonzero finite output, valid anchors/events; no new generation algorithm. Synthetic fixtures have no third-party recording rights dependency.
- Real WAV, FLAC, Ogg, MP3 and AIFF decode, rapid changes/cancel and invalid-file feedback. Preview audible on None/MIDI/Plugin/Break without project or track mutation; cancel/panic and isolation verified. Source continuity matches control PCM bit-for-bit when unrelated samples are offered.
- Guide scripted load/perform/generate/Undo/Redo/B/replace/confirm/cancel/actual project-file save/reopen/Back route passed. Decoder completion in this route is replayed from decoded fixtures; this is not a human novice trial.
- 290 track assertions; GEN/Acid/Break regression; 20 runtime unit tests; base-unit/self-test; 12 monkey seeds ×3000 moves, zero failures. Original Break parity max error 0 and Acid 2400-case regression retained.
- 438 production UI states, no text issues. Final presentation-only footer change rendered on its four affected screens with zero issues.
- AddressSanitizer execution of P1 checks plus all 384 renders passed with seven changed engine/shell/decoder units newly instrumented. Leak detection disabled; hardware performance not inferred.
- Fresh actual host checks: singles, labels, all 36 kits, and 75 contexts/4587 control round trips, zero issues. No original synth DSP was changed by P1.
- Runtime patch refreshed against pinned Melodee 0.2.0. Source manual, first-groove written guide, packaged guide source and screenshot receipts updated locally.

## Remaining acceptance

Human novice timing/wrong-turn study and actual MPC listening/CPU/USB behavior are not completed. The blank beta-test sheet is provided for those tests. No install ZIP replacement or publication has been performed. The next release plan is 0.2.0; this does not rename the previously published beta assets.
