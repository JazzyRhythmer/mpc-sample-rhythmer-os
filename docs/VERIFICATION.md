# Rhythmer OS 0.4.0-beta.3 verification

This public beta is built from the pinned Melodee 0.2.0 foundation and current RHYTHMER integration patch. Physical MPC Sample validation remains pending.

The release build runs runtime unit tests, self-test, GEN/Acid/Break card fixtures, input monkey checks and standard screen checks before stripping and stamping the exact executable. One fresh ASan/UBSan host pass validates the release generation: transport, user preset/reset state, labels, Plaits controls, preset values, parameter roundtrip, single sounds, complete kits, whole-kit and engine filters, selected-pad isolation, original preset audio and authored presets.

The catalogue contains 20 track entries, 36 populated 16-pad kits, 2,616 retained original source selections and 43 separately identified authored selections. Original names, DSP attribution and permitted bank data are retained. External Prophet and Erica/Hrtl Elixir banks remain excluded. The source and notice inventory, excluded-bank checks, archive integrity and signed-update identity/tamper checks accompany packaging.

Historical beta.3 QA completed one additional full pass with 28,166 UI states and zero measured text issues. Additional historical repeats were not completed. These results are not represented as three completed release passes. Current receipt files bind the exact release runtime and source inputs. Continuous parameter combinations are not exhaustively tested.

Use the complete SD ZIP for beta.2 → beta.3: plugin binaries, parameter metadata and the preset catalogue changed. UPDATE replaces only the application.

Device installation/recovery, physical controls, listening, CPU/latency, USB networking/UVC and long sessions remain owner beta tests. Offline checks do not certify hardware performance or timbral equivalence. Original source audio can vary considerably in level; the website demos are separately level-matched examples. This is an early beta, not a hardware-validated stable release.

Based on Melodee by Kerem Kiliç (Ellic Studio) and contributors. Original licences and corresponding source are retained per component.
