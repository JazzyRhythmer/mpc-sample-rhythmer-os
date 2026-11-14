# Open MPC compatibility

Catalog: https://open-mpc.github.io/#plat=sample. Snapshot checked 2026-11-13. Catalog snapshot identity and Sample entries: `config/open-mpc-sample.json`. Catalog listings and upstream device tests do not establish RHYTHMER compatibility.

RHYTHMER is a standalone application on sample-base. Open MPC's Sample addins generally attach to Akai's running MPC process. A shared device/CPU does not establish a shared host API.

| Surface | Policy / actual state |
|---|---|
| VST2 / Open MPC instruments | Reuse original plugin IDs, module folders, `plugin-meta.xml`, parameter identity, state and licenses. Existing host supports aarch64, and armv7 through its original bridge. Ten packaged instruments passed local host/state tests before GEN changes. This is not a promise that every catalog plugin works. |
| VST3 | Preserve original host support. An MPC touchscreen skin or Sample custom page does not automatically become a RHYTHMER page. |
| `VST2 Plugins`, legacy `Synths`, RHYTHMER `Plugins` | Preserve user folders. Use the existing browser to select an external plugin. Do not run stock-MPC installers or migrate user's content as part of a RHYTHMER build. |
| WAV, samples, MIDI and banks | Reuse existing import/export paths and original sample files. RHYTHMER's `MELODEE1` files and Akai project files are distinct; do not label them interchangeable. |
| Sample Draw Handler / Sample Scale Mode | Stock-MPC page/input hooks; existing RHYTHMER rendering and scale controls provide their own path. Direct addin loading is unimplemented. |
| MPC Sample Rack | Stock-MPC insert/restart integration; preserve RHYTHMER's existing plugin rack. Direct addin loading is unimplemented. |
| MPC Commander / MPC Remote | Need a specific transport/UI bridge for RHYTHMER. Do not claim their stock-MPC control protocol is implemented. |
| MPC File Browser | A separate file service may be useful, but service packaging, paths and save/write ownership require device tests. Not bundled/enabled. |
| Co-installation / stock switching | Preserve sample-base's existing stock transition and recovery. Do not add a second audio/display/input owner or import global LD_PRELOAD hooks. Device coexistence is unverified. |

The catalog records hook overlap between Commander and Sample Rack (`dlsym`), and Remote and Draw Handler/Scale Mode (`poll`). Those components need deliberate chaining even in their intended stock-MPC host. No system patch, device installer, remote service or credentials were configured here.

New engine acceptance still requires source/asset licenses, correct architecture, metadata, audible MIDI notes, parameters, bounded state and project round-trip. Plugin identity/compat versions must remain stable when an engine is renamed in RHYTHMER's own UI. New GEN profiles are note/range capabilities, not alternate DSP implementations.
