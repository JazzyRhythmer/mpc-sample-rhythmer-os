# Rhythmer OS

Developed by **jazzy rhythmer**. [Instagram](https://www.instagram.com/jazzyrhythmer/) · [YouTube](https://www.youtube.com/@jazzyrhythmer)

**0.4.0-beta.3**, an MPC Sample beta for owner device testing, based on **Melodee 0.2.0 by Kerem Kiliç (Ellic Studio)**. Existing sampler, sequencer, mixer, effects, driver and recovery foundations are retained.

Revision 2 adds safe confirmation cancellation with Shift + Push, consistent GEN Back navigation and MIX access from all-empty projects. Note Repeat rate-key behavior is preserved.

The plugin picker contains 20 entries: Rhythmer Kit, Acid Engine, Break Engine, Sophie, Elixir, Aphex, FM-106, FMini-1, CS-1, OberVave, K-WASUB, Hera, Braids, Plaits, Hortator, MONO2K, Prophet, S1Vave, Dexed, Guru-600. The original Sample Kit remains available through the native sampler. See [engine inventory](docs/ENGINE_REGISTRY.md).

Rhythmer Kit has 36 named kit presets with pads 1–16 filled. Kit-wide switching, pad-specific engine/sound editing, user presets and project saving are supported. Individual instruments play one selected sound through chromatic/scale pads, with named presets and native control lists with current/total position. The native Melodee PRESETS/EDIT workflow is used, with original sound controls in the native parameter list; Kit source and save controls are separate from sound design. PRESETS mirrors the main native filter; Dexed, DRUM-X, Plaits, CS-1 and MONO2K additionally have an engine-owned OUTPUT FILTER while retaining original tone controls; B2 PERFORM keeps the track DJ FILTER / ECHO / SPACE. Rhythmer Kit has its own whole-kit LP/BP/HP filter, saved with Kit presets, with no insert slot consumed. Sample Kit and Break front the existing sampler-wide filter. See [native plugin workflow](docs/NATIVE_PLUGIN_WORKFLOW.md).

GEN uses the original FM-1 Rhythmer generator: choose tracks 1–4, 5–8, 9–12 or 13–16. The first track receives a kit, the remaining three instruments and MIDI. MIDI ONLY supports a range or one track. Acid/Break actions follow the selected engine. Break audio is browsed from user storage; 1–4 declared source bars are synchronized and sliced. No break recordings are bundled.

[Track changes and navigation](docs/TRACK_WORKFLOW.md) · [Build](docs/BUILD.md) · [Sound and kits](docs/SOUND_KIT_GUIDE.md) · [GEN](docs/GEN_WORKFLOW.md) · [Installation and recovery](docs/SD_CARD_GUIDE.md) · [Validation](docs/VERIFICATION.md) · [Credits](THIRD_PARTY_NOTICES.md).

Excluded engine source folders and package resources are removed from this release. Shared dependencies, upstream authorship and license notices are preserved. Public source exports omit private history and conversations. Offline builds and host tests do not establish physical-device behavior; physical-device validation remains pending.

Current beta UI/preset audit: [FINAL_UI_AUDIT.md](docs/FINAL_UI_AUDIT.md), observed checks: [VERIFICATION.md](docs/VERIFICATION.md).

Break Engine includes the pinned FM-1 Rhythmer Amenity/Jungle performance DSP, BRK PERF controls and recorded performance commands. Acid GEN uses the original TB-3PO laws with per-track settings, 32-bit seeds and sustained ties. See [Break and Acid guide](docs/BREAK_ACID_GUIDE_KO.md).

The 0.4 integration adds the new upstream 128-pattern Patterns home, Freeze/Deep Freeze, LV2/CLAP hosting, native pad sends, USB web/files and screen mirroring. GEN moves to Shift+B3 on PATTERNS. The integration and limitations are in [UPSTREAM_020.md](docs/UPSTREAM_020.md). Updates use a separate Rhythmer signature; an upstream Melodee ZIP is not a Rhythmer update.

Plaits exposes the original 24 models and 96 embedded 6-Op programs, with model-specific control names and named FM choices. The curated sound catalogue contains 2,616 retained original selections plus 43 explicitly authored Rhythmer selections: 15 Prophet sounds and four seven-voice Elixir kits. External Sequential/Erica/Hrtl banks are excluded. See [Rhythmer presets](docs/RHYTHMER_PRESETS.md) and [bank provenance](docs/ORIGINAL_PRESET_AUDIT_KO.md).

## Install the beta

[Download the latest beta](https://github.com/JazzyRhythmer/mpc-sample-rhythmer-os/releases) · [Installation and recovery guide](docs/SD_CARD_GUIDE.md) · [Website and web manual](https://jazzyrhythmer.github.io/mpc-sample/) · [Engine port sources](https://github.com/JazzyRhythmer/mpc-sample-engine-ports)

Use the complete **SD.zip** for first installation, the 0.4 transition, beta.2 → beta.3, and beta.3 revision 1 → revision 2: this revision also changes plugin binaries and the preset catalog. **Revision 2 retains the beta.3 version number, so revision 1 does not automatically offer the same-version update. Use the full SD package for that transition.** [Current installation steps](https://jazzyrhythmer.github.io/mpc-sample/installer/). **UPDATE.zip** updates only a compatible Rhythmer application; it does not replace plugin/kit data. Back up projects, samples and the card first. Verify the release checksums and the AC50 / stock firmware 1.3.0.12 requirement in the installation guide. SOURCE, MOVE-SOURCE and SUPPORT-SOURCE archives contain corresponding source, not installers.

This is an unofficial project, not affiliated with or endorsed by AKAI Professional or inMusic. Product names and logos belong to their respective owners. Provided without warranty under the applicable licenses. This beta has offline build, audio-host and UI checks; physical-device behavior, latency and recovery still require owner testing.

<!-- JAZZY-RHYTHMER-PORTFOLIO:START -->
## More from Jazzy Rhythmer

**For MPC Sample:** [RHYTHMER OS](https://jazzyrhythmer.github.io/mpc-sample/) · **For FM-1:** [JAZZY](https://jazzyrhythmer.github.io/Jazzy/) / [RHYTHMER](https://jazzyrhythmer.github.io/Rhythmer/)

**JR Audio Software** — in development, expected in 2027: [JR ACID](https://jazzyrhythmer.github.io/software.html#jr-acid) · [JR FX](https://jazzyrhythmer.github.io/software.html#jr-fx) · [JR SMPL](https://jazzyrhythmer.github.io/software.html#jr-smpl) · [JR RYTM](https://jazzyrhythmer.github.io/software.html#jr-rytm) · [JR DRAW](https://jazzyrhythmer.github.io/software.html#jr-draw) · [JR PLAY](https://jazzyrhythmer.github.io/software.html#jr-play) · [JR TREK](https://jazzyrhythmer.github.io/software.html#jr-trek).

[Main website](https://jazzyrhythmer.github.io/) · [Ko-fi](https://ko-fi.com/jazzyrhythmer) · [Patreon](https://www.patreon.com/JazzyRhythmer/) · [Studio Notes & email updates](https://jazzyrhythmer.github.io/#notes) · [YouTube](https://www.youtube.com/@jazzyrhythmer) · [Instagram](https://www.instagram.com/jazzyrhythmer/)

Voluntary support helps me keep making music, instruments and open-source tools. Thank you for being part of it.
<!-- JAZZY-RHYTHMER-PORTFOLIO:END -->
