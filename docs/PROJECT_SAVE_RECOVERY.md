# Project saving and recovery

## Contract

- Manual SAVE and background recovery are separate. Autosave never assigns a manual file path, clears manual dirty status or overwrites a manually saved project.
- Each project has a persistent 128-bit recovery identity in optional `RID1` project data. Older project files still load. Legacy projects derive a stable initial identity from their normalized full path until a manual save persists it.
- A new unsaved session has one recovery entry. Its first SAVE keeps that identity. SAVE AS to a different file and Duplicate create independent identities; SAVE AS to the current file keeps its identity; renaming or moving a saved project retains its identity.
- Recovery entries live in `Rhythmer/Autosave/<id>.mldp`, outside the normal Projects list. There is no numbered recovery history. Display names come from project data rather than ID filenames.
- Each recovery manifest selects one of two bounded hidden media staging slots, using optional `RCMP` metadata. The inactive slot receives current loop audio, takes and prints before the manifest is atomically replaced. These are transaction staging data, not additional project/recovery entries. The previous active slot is not overwritten while preparing the next checkpoint.
- Original path metadata (`RCVR`) helps initialize the save destination after recovery. Opening a recovery copy does not change the original project.

## Controls

Project is **SHIFT + Pad 16**.

| Control | Result |
| --- | --- |
| B1 SAVE | Update current manual file; if new/recovered, choose destination and name |
| SHIFT + B1 SAVE AS | Choose a destination/name for a separate project |
| B2 OPEN | Native project browser with SAVE / DISCARD / CANCEL protection |
| B3 NEW | Unsaved-change protection, then normal / EMPTY choice |
| SHIFT + B3 RECOVERY | Read-only recovery-entry list; LOAD or Load kit |

The save destination browser reuses the native Project list. Encoder push enters folders; SHIFT + push goes up; B3 USE FOLDER opens native name entry. B2 NEW FOLDER creates a folder in that exact directory. B1 CANCEL leaves saving without changing the current manual path or identity. Existing names require REPLACE confirmation. Read-only/internal, stock, system and recovery destinations never silently redirect to Projects.

## Completion and failure

- A bounded service queue reports save success/failure to Context. Rename/Move path changes are acknowledged once; cached listings cannot redirect a later SAVE AS. Only successful completion adopts the new manual path/name/ID. An edit arriving during a write leaves the project dirty and cancels an attempted project switch.
- The serializer captures supported plug-in state, patterns, sample references and print records. Used source samples remain referenced; this does not introduce automatic sample collection.
- Audio recording and project-bound print/Freeze jobs wait while a manual SAVE AS changes the working path; queued refreezes defer until the new path is committed. Pending print work must finish before snapshot capture.
- Loop-file jobs must finish successfully before the project manifest is queued. Media copy errors abort manifest publication. Temporary-file writes check completion, synchronize data and replace the manifest by rename; settings/resume pointers use the same mechanism.
- Idle timing and existing playback/record/print/load exclusions remain. Unchanged state is not repeatedly written. Exit/update checkpoint requests wait for transport stop before capturing plug-in state and cannot invent manual Project N files. Errors leave the exit/update cancellable or abort the update.
- An unresolved startup recovery offer blocks automatic checkpoint replacement until the user chooses RECOVER/LATER or explicitly saves.
- Startup offers the last active checkpoint separately from native manual-project resume. RECOVER opens an unsaved working copy. LATER suppresses the next automatic offer; the recovery entry remains in the list. DISCARD on OPEN/NEW leaves the manual file unchanged and dismisses the automatic offer.
- Existing numbered projects and user files are not migrated, moved or deleted.

## Verification

The `--rhythmer-project-save-check DIR` runtime harness exercises actual Context, native page input dispatch, serializer and ProjectStore service requests. `tests/recovery_file.cpp` separately exercises real short-write failure, interrupted temporary writes, ID isolation and same-size changed audio copies. Runtime screenshots are rendered from the states reached by those controls.

Host/Linux verification and physical SD power-loss behavior are separate. The implementation does not claim a physical-device power-cut test; removable filesystem/controller behavior requires separate device confirmation.

### Local verification result

- Linux ARM64 runtime compiled with warnings treated as errors, version 0.2.0.
- Project saving harness: **75 assertions passed**. It covers repeated single-entry checkpoints, manual file byte preservation, first SAVE/Save As folder choice, real soft-key/encoder dispatch, cancellation, replacement confirmation, write failure, concurrent edits, restart/LATER, media copies, legacy Rename/Move identity, Duplicate, corrupt LOAD reporting and failed-exit recovery preservation and rename/name-reuse path isolation.
- File-safety tests passed on macOS and Linux; Linux runtime-control and file tests: **2 tests passed**.
- Native navigation: **1,248 contexts / 9,538 assertions**; track workflow: **315 assertions**.
- Existing four-track/single-track GEN, Acid/Break routing and save/restore checks passed. Random input: **8 seeds × 250 moves, zero failures**.
- Existing model/engine test passed; upstream-state/control-ID test passed with address/undefined-behavior sanitizers.
- Manual and First Groove source text and relevant project-screen assets were updated. The release assembler includes the matching illustrated guides, source and signed installation/update packages.

Physical-device installation and power-cut testing were not performed in this session.
