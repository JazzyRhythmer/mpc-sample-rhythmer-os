# Build Rhythmer OS

The release source contains the complete reviewed runtime and populated sample-base source under `runtime/`. It also includes the pinned JUCE, CLAP, Rubik, additional font, SpleeterRT and OpenBLAS sources under `third_party/runtime/`. Original native DSP dependencies accompany the MOVE-SOURCE archive and the engine-port repository. The Debian support-library sources accompany SUPPORT-SOURCE.

## Build the exported runtime

Use a Linux ARM64 machine or an ARM64 Docker environment. From the exported source root:

```sh
docker build -t sample-base-builder -f runtime/base/tools/Dockerfile runtime/base
docker build -t rhythmer-builder -f runtime/tools/plugin_support/Dockerfile runtime
mkdir -p runtime/build/deps
ln -s ../../../third_party/runtime/JUCE runtime/build/deps/JUCE
ln -s ../../../third_party/runtime/clap runtime/build/deps/clap
ln -s ../../../third_party/runtime/rubik runtime/build/deps/rubik
ln -s ../../../third_party/runtime/fonts runtime/build/deps/fonts
ln -s ../../../third_party/runtime/spleeterrt runtime/build/deps/spleeterrt
ln -s ../../../third_party/runtime/openblas runtime/build/deps/openblas
docker run --rm --platform linux/arm64 -v "$PWD":/source -w /source/runtime rhythmer-builder sh -ec 'make -j1 && python3 -m unittest discover -s tests -v && build/rhythmer --self-test build/test.wav'
```

These links use the included sources; do not run the Git-based dependency fetcher over links to history-free exported trees. Alternatively, an empty `runtime/build/deps` can be populated by `python3 runtime/tools/dependencies.py`, which fetches and checks the pinned original Git repositories. The runtime Makefile builds the plug-in support pack and armhf bridge. Stems uses the separately supplied helper and model: maintainer builds verify the official upstream release bytes against `config/upstream-stems.lock.json` with `tools/prepare_runtime_assets.py`. Corresponding SpleeterRT and OpenBLAS sources and their notices are included; `make stems` can build the helper from source. Ordinary source builds are unsigned; the private release key is not distributed. A modified executable can be installed manually using the documented SD workflow; creating an official signed UPDATE requires the release key.

## Maintainer workspace

The macOS workspace helpers stop if `/Volumes/SSD` is absent. Build/SDK/cache/test/archive/VM data stays below `/Volumes/SSD/Development`.

```sh
. tools/environment.sh
python3 tools/build.py custom
```

`custom` copies the unmodified pinned Melodee v0.3.0 foundation, mechanically renames the generated snapshot and replays `extensions/runtime-v030.patch`. `config/upstream-integration.lock.json` binds the patch and reviewed inputs. It retains 128 patterns, Freeze, native sample-pad sends, LV2/CLAP and USB services while restoring Rhythmer's GEN, Acid, Break and single-sound/kit interface. Legacy anchor-based apply scripts are not reapplied over the new architecture.

The build runs unit/model/sanitizer checks, self-test, GEN, monkey input and screen checks before stripping/stamping. A complete staged SD root is supplied as `RHYTHMER_GEN_CARD` for real-plugin assignment, bank and Undo/Redo checks. Card metadata is written atomically after accepted native-library hashes are checked, so an old library cannot silently be paired with a new bank map.

## Native engines and preset data

The selected port variants and native source trees are specified in `config/first-release-candidates.json`. Fetch and prepare the pinned original sources, then compile the native ports in the ARM64 builder. `tools/prepare_fm1_ports.py` excludes the external Prophet and Elixir bank assets; `tools/public_factory_data.py` generates zero-count external-bank declarations. The original GPL Init implementations remain. `tools/rhythmer_presets.py` adds the independently authored host-side presets from `config/rhythmer-factory-presets.json`.

After compilation, stage required notices and run the real host tests. `config/native-engines.lock.json` records accepted native files. Generate `config/sound-catalog.json` with `tools/sound_catalog.py`, then run `tools/gen_engine_catalog.py`, the independent bank checks, authored audio checks and full native/host playback. Actual host inspections drive the paged UI audits. Changing a native file or accepted host input invalidates packaging.

## Exports and packages

Run the source exporters and package assembler after acceptance:

```sh
python3 tools/export_support_sources.py
python3 tools/export_move_sources.py
python3 tools/export_public.py
python3 tools/package.py
```

The SD ZIP includes the app, curated plugins, source references, required notices and file hashes. UPDATE contains only the signed autorun update and preserves plugins/projects. SOURCE, MOVE-SOURCE and SUPPORT-SOURCE are corresponding-source companions. Public repositories are created from reviewed exports with new history; the private development checkout is never pushed. Physical-device listening, timing, USB services and restart/recovery remain owner beta tests.
