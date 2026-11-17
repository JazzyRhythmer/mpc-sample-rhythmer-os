# Foundation tracking

RHYTHMER OS 0.2.0 uses the pinned Melodee Sample v0.3.0 foundation, commit `6d6ad5efff4cef9b7b04f3aee3c3f386ee717c16`. The sample-base pin is `7e2d15d9ca086608b942599f6471a82f48c139f7`. These are separate product and foundation versions.

`config/upstream-integration.lock.json` records the reviewed downstream patch and its inputs. `tools/audit_upstream_030.py` checks the pinned sources and the paths for audio/keygroup tracks, auto sampling, Stems, native-rate streaming, long recordings, MPC 3 import/export, chords, sequences, autosave, menus, lessons, Basic/Full, browser dialogs, fonts, loading, USB services and updates. Source coverage does not establish physical-device operation.

RHYTHMER retains its own engine filter controls on PRESETS, separate PERFORM macros, Rhythmer Kit, four-track GEN, Acid/Break workflows, TRACK SETUP, empty-track/pad entry, User Sound/Kit tools and artwork. In Menu, SHIFT + encoder push follows B1 BACK; ordinary push still selects. Native lessons use their original TRIM/TUNE order, while ordinary sample editing retains RHYTHMER's filter-first SOUND page.

The unchanged Stems helper and model are checked against `config/upstream-stems.lock.json`. Their original notices accompany the installation; their source companions accompany the matching SOURCE archive. The application uses RHYTHMER's update signing key. Melodee is credited in the application and source notices.

Local installation candidates remain beta builds. Hardware listening, timing, inputs, USB networking/camera behavior and power-cycle installation require owner testing. Preparing or verifying an archive does not publish it.
