# Rhythmer OS

Developed by **jazzy rhythmer**. [Instagram](https://www.instagram.com/jazzyrhythmer/) · [YouTube](https://www.youtube.com/@jazzyrhythmer)

**0.4.0-beta.3**, an MPC Sample beta for owner device testing, based on **Melodee 0.2.0 by Kerem Kiliç (Ellic Studio)**. Existing sampler, sequencer, mixer, effects, driver and recovery foundations are retained.

The plugin picker contains 20 entries: Rhythmer Kit, Acid Engine, Break Engine, Sophie, Elixir, Aphex, FM-106, FMini-1, CS-1, OberVave, K-WASUB, Hera, Braids, Plaits, Hortator, MONO2K, Prophet, S1Vave, Dexed, Guru-600. The original Sample Kit remains available through the native sampler. See [engine inventory](docs/ENGINE_REGISTRY.md).

Rhythmer Kit has 36 named kit presets with pads 1–16 filled. Kit-wide switching, pad-specific engine/sound editing, user presets and project saving are supported. Individual instruments play one selected sound through chromatic/scale pads, with named presets and native control lists with current/total position. The native Melodee PRESETS/EDIT workflow is used, with original sound controls in the native parameter list; Kit source and save controls are separate from sound design. PRESETS mirrors the main native filter; Dexed, DRUM-X, Plaits, CS-1 and MONO2K additionally have an engine-owned OUTPUT FILTER while retaining original tone controls; B2 PERFORM keeps the track DJ FILTER / ECHO / SPACE. Rhythmer Kit has its own whole-kit LP/BP/HP filter, saved with Kit presets, with no insert slot consumed. Sample Kit and Break front the existing sampler-wide filter. See [native plugin workflow](docs/NATIVE_PLUGIN_WORKFLOW.md).

GEN uses the original FM-1 Rhythmer generator: choose tracks 1–4, 5–8, 9–12 or 13–16. The first track receives a kit, the remaining three instruments and MIDI. MIDI ONLY supports a range or one track. Acid/Break actions follow the selected engine. Break audio is browsed from user storage; 1–4 declared source bars are synchronized and sliced. No break recordings are bundled.

[Build](docs/BUILD.md) · [Sound and kits](docs/SOUND_KIT_GUIDE.md) · [GEN](docs/GEN_WORKFLOW.md) · [Installation and recovery](docs/SD_CARD_GUIDE.md) · [Validation](docs/VERIFICATION.md) · [Credits](THIRD_PARTY_NOTICES.md).

Excluded engine source folders and package resources are removed from this release. Shared dependencies, upstream authorship and license notices are preserved. Public source exports omit private history and conversations. Offline builds and host tests do not establish physical-device behavior; physical-device validation remains pending.

Current beta UI/preset audit: [FINAL_UI_AUDIT.md](docs/FINAL_UI_AUDIT.md), observed checks: [VERIFICATION.md](docs/VERIFICATION.md).

Break Engine includes the pinned FM-1 Rhythmer Amenity/Jungle performance DSP, BRK PERF controls and recorded performance commands. Acid GEN uses the original TB-3PO laws with per-track settings, 32-bit seeds and sustained ties. See [Break and Acid guide](docs/BREAK_ACID_GUIDE_KO.md).

The 0.4 integration adds the new upstream 128-pattern Patterns home, Freeze/Deep Freeze, LV2/CLAP hosting, native pad sends, USB web/files and screen mirroring. GEN moves to Shift+B3 on PATTERNS. The integration and limitations are in [UPSTREAM_020.md](docs/UPSTREAM_020.md). Updates use a separate Rhythmer signature; an upstream Melodee ZIP is not a Rhythmer update.

Plaits exposes the original 24 models and 96 embedded 6-Op programs, with model-specific control names and named FM choices. The curated sound catalogue contains 2,616 retained original selections plus 43 explicitly authored Rhythmer selections: 15 Prophet sounds and four seven-voice Elixir kits. External Sequential/Erica/Hrtl banks are excluded. See [Rhythmer presets](docs/RHYTHMER_PRESETS.md) and [bank provenance](docs/ORIGINAL_PRESET_AUDIT_KO.md).

## Install the beta

Use the full **0.4.0-beta.3 SD ZIP** when updating from beta.2. App-only UPDATE does not install the revised plug-ins and catalogue.

[Install page](https://jazzyrhythmer.github.io/mpc-sample/installer/) · [First groove](https://jazzyrhythmer.github.io/mpc-sample/manual/quickstart.html)

![Acid Engine native preview](assets/preview/acid-engine.gif)


[Download the latest beta](https://github.com/JazzyRhythmer/mpc-sample-rhythmer-os/releases) · [Installation and recovery guide](docs/SD_CARD_GUIDE.md) · [Website and web manual](https://jazzyrhythmer.github.io/mpc-sample/) · [Engine port sources](https://github.com/JazzyRhythmer/mpc-sample-engine-ports)

Use the complete **SD.zip** for first installation, the 0.4 transition, and beta.2 → beta.3: this revision also changes plugin binaries and the preset catalog. **UPDATE.zip** updates only a compatible Rhythmer application; it does not replace plugin/kit data. Back up projects, samples and the card first. Verify the release checksums and the AC50 / stock firmware 1.3.0.12 requirement in the installation guide. SOURCE, MOVE-SOURCE and SUPPORT-SOURCE archives contain corresponding source, not installers.

This is an unofficial project, not affiliated with or endorsed by AKAI Professional or inMusic. Product names and logos belong to their respective owners. Provided without warranty under the applicable licenses. This beta has offline build, audio-host and UI checks; physical-device behavior, latency and recovery still require owner testing.

## Stay in touch

RHYTHMER OS is free and open source, and will always be free. Your support helps me keep working on this project and other open-source tools.

[Support on Ko-fi](https://ko-fi.com/jazzyrhythmer) · [Patreon](https://www.patreon.com/JazzyRhythmer/) · [Email updates](https://jazzy-rhythmer.kit.com/6dd4006c7c) · [Main website](https://jazzyrhythmer.github.io/) · [Instagram](https://www.instagram.com/jazzyrhythmer/) · [YouTube](https://www.youtube.com/@jazzyrhythmer)
