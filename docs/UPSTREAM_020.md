# Melodee 0.2.0 integration — Rhythmer OS 0.4.0-beta.3

Origin: Melodee by Kerem Kiliç (Ellic Studio), tag v0.2.0, commit 8880d16116ccb3c69f75fb46bf2166b16c51ef0c. Untouched sample-base: 7e2d15d9ca086608b942599f6471a82f48c139f7. Official release: https://github.com/keremimo/melodee-sample/releases/tag/v0.2.0.

The original source changed 357 files. The complete pinned source is adopted, then the reviewed custom diff is replayed onto an SSD snapshot. Original vendor/base files stay unchanged. Existing 20 picker entries, 25 source views, 36 kits and 2,659 selections (2,616 retained source selections and 43 Rhythmer originals) are retained. Native engine DSP and factory banks are not rewritten.

| New foundation | Rhythmer integration |
|---|---|
| 128 patterns per track, Patterns/Scenes home, Step Edit | PATTERNS is SEQ home. Shift+B3 opens the existing 4-track/single/range GEN menus; original VARY stays inside GEN. Pads audition the selected sound while GEN is open. Native Step Edit and pattern launch remain. |
| LV2/CLAP instruments, effects and preset folders | New upstream hosts/preset discovery retained alongside the curated VST2/3 instruments; K1 Jump follows the current folder row count. External plugins do not become Rhythmer Kit sources automatically. |
| Plug-in transport | Outer transport reaches Rhythmer child engines. Shift+B3 on Edit toggles TRANSPORT; native PRESETS/EDIT remains. Child clocks are cleared before release. |
| Parameter reset / discrete fine adjustment | The native list maps actual shown IDs. Erase+pot resets to the loaded source preset value because VST2 provides no default-value ABI. Source preset values are not changed. |
| Freeze / Deep Freeze | Original print/stream/unload architecture retained. Manual GEN/Break edits ask to Unfreeze first; automatic Acid skips frozen tracks. Pending Break loads recheck freeze state. Preset/transport edits of frozen instrument/track/pad-effect entries are guarded; Deep Freeze has an explicit Unfreeze edit screen. |
| Pad Send A-D | Native Sample Kit pad sends retained, including project/import/print data. Rhythmer Kit remains a stereo instrument using track sends; it does not expose native sample-pad send buses. |
| Plugin storage | New SD packages use Rhythmer/Plugins. Existing top-level Plugins paths and existing project identity remain readable. User data is not moved/deleted automatically. |
| Signed card/USB updates | Rhythmer package/app identity and separate Ed25519 public key. Official Melodee updates are rejected. UPDATE installs autorun only; full SD packages also provide plugin data. Previous executable folder/recovery flow retained. |
| USB web/files, screen mirror | Rhythmer local hostname and monochrome web skin; own wordmark, explicit upstream credit. USB service, driver and device performance validation remains physical-device work. |
| Decoder/chop/MIDI/panic/core fixes | New upstream implementation retained, including the native sampler's linear velocity response; custom Break performance DSP, Acid seed/ties, kit state and double-Stop panic remain. |

Initial 0.3-to-0.4 installation requires the full SD package. Preserve existing projects/samples and back up autorun first. Later signed UPDATE packages preserve plugins and user data. New 128-pattern/Freeze projects should not be overwritten by an older beta. See SD_CARD_GUIDE.md and USER_MANUAL_KO_DRAFT.md.

Verification results are recorded in VERIFICATION.md after the integration checks finish. Physical listening, USB networking/screen mirroring, installer restart/rollback and sustained MPC performance require owner device testing. This is an owner beta, not a claim of device validation or public redistribution clearance.

The sixteen official release features are traced in `tools/audit_upstream_020.py`: audio formats/preview, Chop Beats/fine edit/zoom, empty-track families, MPC kit imports/colour, per-pad sends, Freeze, plugin formats/folders, PRESETS macros, pattern banks/scenes, Roll multiselect, Zones, MIDI, gestures, USB web/Files, UVC mirror and signed updates. Hardware-dependent behavior is not inferred from source equality.

A reviewed post-release preset-name persistence fix is listed in `config/upstream-backports.json`. Other unreleased changes are not merged automatically. The video demonstrates higher mirror sizes in one scene, but the pinned stable release/source caps this build at 1280×960; no unverified higher limit is advertised. Pad colours remain RGB in project data and real pad lights, while the on-screen picker shows grayscale with colour names.
