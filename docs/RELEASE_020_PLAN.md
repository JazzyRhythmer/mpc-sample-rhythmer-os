# RHYTHMER OS 0.2.0 — working release plan

User-confirmed next RHYTHMER version: **0.2.0**, independent of the Melodee 0.2.0 foundation. Publication and installer replacement remain held pending notification. Historical beta tags keep their names. The local installation candidate is now version 0.2.0.

## Changes after the first public beta

Historical GitHub records include beta.1 and beta.3; the user identifies the first user-facing launch with the current beta.3 series. Do not assume every earlier staged GitHub asset had users.

Already published in beta.3 follow-ups: confirmed-delete cancellation, consistent GEN Back hierarchy, all-empty mixer entry, contextual Note Repeat keys; User Sound/User Kit save and PAD SOURCE entry; clearer Break load/BRK PERF/Pattern Hold/Stretch guidance; empty-track type selection versus selected-empty-pad sample loading; wrapping preset lists; original Aphex acid choices. Refer to the actual release records for their exact asset/source associations.

Local subsequent candidate: display-only MIDI tempo stabilisation, source replacement with preserved patterns/atomic Undo and length confirmation, independent original/synchronised Break preview, actual-activity feedback and held-command cleanup, prevention of audition resetting the playing Break, Kit motion continuity across pad labels, matching task-oriented written guides. See BREAK_P0_QA.md and BREAK_P1_QA.md.

## Engine work

- FMini-1 2.6.0 integrated and numerically checked: original filter/contour/bank/CPU updates, plus correction of the older missing original factory-extras loader. See FMINI_260_QA.md. No legacy tone compensation requested.
- Frodhes: original 0.9.12 ARM MPC VST2 source built and integrated, retaining its 57 factory programs and native parameters. GPL-3.0-only with original notices/MPC SDK MIT provenance.
- Tenebrae: preferred second candidate from Schwung (Move Everything's successor): original MIT engine/presets, eight oscillator models, Init +163 presets, filter/envelopes/LFO/effects. The original ARM64 module is source-built and integrated through the existing wrapper. Sample-dependent Quark was not prioritised; broader Surge XT overlaps more and requires a larger integration.

Both new engines passed bank/audio, host, state and parameter checks in the local candidate; final package/source hashes bind the installable handoff. No fabricated presets. Do not market source upstream's Move/MPC benchmarks as MPC Sample measurements. Include actual CPU, peak block, instance limits and memory findings in acceptance.

## Release gates

Complete both engine integrations, preserve current workflow and 36 kits, refresh original-source and acceptance receipts, rebuild matching app/catalogue/full SD installation candidate, verify package contents/hash/source/license/privacy and updated offline/online guide sources. User notification precedes any publication. 
