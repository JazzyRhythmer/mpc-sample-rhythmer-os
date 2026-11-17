# Chord GEN verification — development build

Date: 2026-11-17. Base: pinned Melodee v0.3.0. Product version remains 0.2.0. No public deployment.

- Model: 11,895 deterministic cases across 61 genre menu choices, 13 scales, 5 play styles and 3 seeds; varying bars, chord counts, colors, voicings, time signatures and mono/poly behavior. AddressSanitizer and UndefinedBehaviorSanitizer enabled. Passed.
- Context: explicit tests for project-follow/local key selection, scale adaptation, pitch bounds, duplicate events, mono overlap and project-file round-trip. Passed in model tests.
- Shell: five-page navigation, physical Shift+encoder back, independent single-track/chord dispatch, project-global preservation, one-step Undo/Redo, local overrides and project-key/length mapping are covered by the development shell test. Passed in the final ARM64 build.
- Canonical patch: replay check against the mechanically renamed pinned upstream passed; final refreshed patch also checked against the pinned upstream.
- Full ARM64 application build: passed with -Wall -Wextra -Werror.
- Existing GEN/Break model regression: passed with AddressSanitizer / UndefinedBehaviorSanitizer.
- Final shell regression: passed, including the existing Acid and Break workflows.
- All five native 320×240 chord pages: rendered and visually inspected. Text audit reported zero issues. The optional 2× renderer omitted the large single-letter key in one output; the native-resolution page correctly shows it, so use the native-resolution screenshots as device UI evidence.

Artifacts: /Volumes/SSD/Development/BuildCache/rhythmer-os/chord-gen-qa-20261117. Original source remains under the project checkout; all compiled/test output is SSD-backed.

Physical hardware playback and subjective evaluation of the generated musical phrases are not established by these automated tests.

Follow-up: removed GEN TYPE switching from the existing single-track rows. GENERATE Tn / MUTATE Tn retain their prior engine-adapted route; CHORD GEN is independent. Added an all-59-genre kit-track check using canonical pad keys 36–43, plus a same-genre fallback for original arrangements that omit drums.

Final follow-up result: ARM64 build and complete shell regression passed. All 59 explicit genre selections were tested from empty kit patterns: 58 produced drum events (56 distinct patterns at the chosen fixed seed/settings); Neo Classic had no drum vocabulary, displayed no drum part, and preserved an existing-pattern marker. Single-track generation remains independent even with an older stored chord-type flag.
