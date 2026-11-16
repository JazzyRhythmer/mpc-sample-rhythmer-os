# Rhythmer OS 0.4.0-beta.3 — Sound / Kit save hotfix verification

Built on Melodee by Kerem Kiliç (Ellic Studio) and contributors. The retained workflow fixes correct confirmation cancellation, GEN Back navigation and all-empty MIX access while preserving active Note Repeat rate keys.

The release receipts bind the tested runtime, exact source inputs and corresponding source archives. Current runtime checks include the unit suite, 161 track-workflow assertions, GEN/Acid/Break integration, audio self-test, random surface inputs and 426 standard page previews. Confirmation tests cover both selected answers for all 12 Ask dialog types, retained plain-Push/B3 confirmation, B1 cancellation and Undo. Shift release also preserves Roll note selection.

The retained sound review covers 25 source views, 2,659 preset selections, 272,711 preset/control comparisons, 37,226 note probes, 576 pad gain/ownership checks and 4,567 control round trips. Engine/plugin/model source is compared byte-for-byte to the reviewed sound snapshot before retaining this evidence. ASan/UBSan covers the host wrapper, not every native DSP library. The three-pass release campaign is not claimed by these finite checks.

There are 20 picker entries and 36 complete 16-pad kits, 2,616 original and 43 separately identified authored selections. Excluded external banks remain excluded. Original credits, licences and corresponding source accompany the release; no break recordings are bundled.

Use the full SD ZIP for installation and the complete beta.3 update. UPDATE replaces the app only. Back up the entire card first. Physical-device installation/recovery, controls, listening, load/latency, USB/UVC and long sessions remain pending owner beta testing. Software validation does not certify hardware performance.


## Sound-tools entry hotfix — verified locally

Owned plug-ins now open PAD SOURCE / SAVE (kit) or SAVE SOUND (single instrument) from Stage EDIT encoder Push, with an on-screen prompt. Native PRESETS Push, external plug-in Push, Note Repeat/ARP soft-key priority and the frozen-track confirmation remain unchanged.

The hotfix passes 161 track-workflow assertions, 19 runtime unit tests, audio self-test, GEN/Acid/Break integration, 12 random-input seeds of 3,000 moves, 426 standard UI states and 535 source/save/edit states with zero reported text issues. Fresh-rack disk reload preserves edited controls for all 26 source configurations; mixed-engine kit save/reload preserves full pad overrides and the whole-kit filter. Unwritable storage reports an error without adding a phantom preset. These finite checks do not claim a new three-pass campaign or physical-device validation.

Installation and corresponding-source ZIPs use the same app version, 0.4.0-beta.3. The hotfix includes the updated first-session guide and save/load manual. Existing instrument DSP payloads are retained unchanged from the reviewed baseline.


## Break workflow hotfix.2 — 16 November 2026

The focused runtime changes retain BREAK GEN after an initial source load, expose pending-load cancellation through B1 and Shift + Push, prevent late source A/B completion from reclaiming a dismissed screen, and clarify Pattern Hold / Grain operating conditions. The serialized controls and DSP are unchanged. General GEN also restores Acid RNG state together with notes during Undo/Redo.

The hotfix includes regression fixtures for A/B completion ownership, cancellation, undo/redo, saved hold/mode values and held STRETCH release after paging. Offline DSP tests distinguish CHOP from LOOP hold and ordinary chops from stretched grain processing. Test results are bound to the final runtime in the validation receipt. Existing engine/preset acceptance is retained only for byte-identical source and payloads; it is not presented as a new hardware listening test.

App version: 0.4.0-beta.3. Distribution record: v0.4.0-beta.3-hotfix.2. Physical-device testing remains pending; install the full SD package for this same-version hotfix.
