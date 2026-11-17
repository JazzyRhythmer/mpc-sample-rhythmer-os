# Break library and workflow improvement backlog

Status: **P0 and P1 implemented in a local candidate; hardware listening and human novice validation remain open.** Reused the native browser, confirmation sheet, pattern-length binding and atomic TrackState Undo. No Break DSP or MIDI sync algorithm changes. Public release, installer replacement and hardware installation have not been performed.

### P0 result

- A replacement retains every pattern and its length, pad sound-design controls and performance values. Same-length replacement retains B; changed source bars require confirmation and clear B with atomic Undo/Redo. Source-relative trims are rebuilt. First load only creates Straight when the selected pattern contains no notes, motion, lanes or punches.
- The Break-only file projection is shared by drawing, file counts, cursor audition and assignment; folders and native drive/PREVIEW controls remain. Shift+pad cannot accidentally load a loop into an unrelated pad here. Browser LOAD BARS is local UI state and does not alter general GEN settings. BREAK GEN K1 LENGTH uses the existing native pattern control.
- Existing B2 LOAD A (pages 1/2/4/5/6) and LOAD B (page 3) are retained. SOURCE A/B now points to the A entry. No new shortcut. Owned decode completion, failed-load retry, cancellation, frozen tracks and track changes retain their safeguards.
- Manual and First Groove written lessons now lead with separate play / generate / replace / perform / save routes, real UI renders and exact Back destinations. The film remains a historical example; written instructions take precedence.
- Approved Kit v6 geometry was already present. Pad-specific preset labels were resetting motion; only the kit motion identity now ignores the changing Pad suffix/edit marker. Fixed vs changing pad labels produce identical output for all 96 replayed frames at 1× and 2×.

Evidence: `docs/BREAK_P0_QA.md`; detailed logs and before snapshots on the SSD. Software tests do not constitute physical-device listening or installation.

## Confirmed baseline

Inspected against the shipped `v0.4.0-beta.3-hotfix.3` source archive. This is the historical pre-P0 baseline. The local candidate now differs as described in the P0/P1 QA reports.

- `runtime/src/rhythmer/pages/samples_page.cpp`: Break reuses the native file browser with drive selection and PREVIEW. Non-audio bank/kit/MIDI/expansion items remain visible, then Push rejects them in Break context. This is a context-filter opportunity, not a missing browser implementation.
- `runtime/src/rhythmer/shell/bindings.cpp`: source A browsing exposes LOAD BARS 1–4; source B inherits the existing declared length. Bar count is manual, not a confidently detected property.
- `runtime/src/rhythmer/shell/sample_files.cpp`: cursor preview stops the previous audition and passes the path to the library. This path does not request project-tempo-synchronised Break audition. This is not a claim that native preview is absent.
- `runtime/src/rhythmer/shell/gen_break_jobs.cpp`: source A loading creates 16 equally sized slices and a Straight pattern, including on the replacement path. It also reinitialises the source track. The implications for existing sequence/performance edits need an explicit replacement contract.
- Load completion already respects track ownership/cancellation/frozen tracks and keeps BREAK GEN open. These are existing safeguards to retain, not features to reimplement.
- Current docs provide six-page operating conditions, but the First Groove film predates some workflow changes. The written guide explicitly warns of this mismatch. `BREAK_ACID_GUIDE_KO.md` still contains obsolete statements that the release labels Pattern Hold as LOOP HOLD; reconcile with the actual shipped screen.

## Development tasks

| ID / Priority | Deliverable | Acceptance / side-effect checks |
| --- | --- | --- |
| BRK-UX-01 / P0 | Define and implement separate **initial load**, **replace Source A**, **load/replace Source B** and **generate pattern** operations using the current async loader. Propose preserving compatible existing notes/performance edits for source replacement and keeping Straight as an explicit generation choice. | Merely browsing/pre-listening never changes the project. Initial empty-track setup remains quick. Existing music is not silently replaced. A bar-length change has an explicit length/pattern choice. Undo/Redo restores source, pattern, performance and track state as one coherent operation. |
| BRK-UX-02 / P0 | Add an audio-loop view of the existing library only when browsing for Break. Preserve folders, CARD/INTERNAL and native PREVIEW; suppress entries the Break loader cannot accept. Display selected source/target and the declared 1–4 bar length clearly. | No generic Sample Kit/MPC program/expansion browser regression. All formats the actual Break decoder supports are handled consistently. Metadata that is inferred from declared bars is labelled as calculated, not automatically detected. Original sample files are not rewritten. |
| BRK-UX-03 / P0 | Make source replacement/re-entry visible near Source A/B, then audit the complete Track → Browse → Load → Generate → Perform → Return navigation. Review existing soft-key jobs before choosing a visible Source action/menu. | Keep pad A/B/Return performance commands and contextual transport/Note Repeat behavior. Retain captured async target ownership. Back, Cancel, track changes and decode errors have a documented destination for each entry route. No hidden new shortcut or unsolicited focus takeover. |
| BRK-UX-04 / P1 | Show why controls are currently inactive: Pattern Hold/Variation/Drift depend on LOOP and generation state; Grain/Splice/Slow affect STRETCH. First add concise mode/condition feedback; evaluate a simpler effect-audition gesture only if needed. | Values can be prepared without silently changing modes or recording commands. Leaving a page/releasing a control cannot leave a held command active. Do not imply that Pattern Hold sustains audio. |
| BRK-UX-05 / P1 | Evaluate optional in-tempo loop audition using existing preview/analysis facilities. Show original versus project-synced audition clearly; investigate suggested BPM/bar metadata with a manual override. | A preview does not assign a track, alter notes, change the project BPM or modify MIDI sync. Rapid browsing cancels stale previews. Master audio/transport continue normally. Estimate uncertainty and half/double-tempo ambiguity remain visible. |
| BRK-QA-01 / P1 | Reproduce the reported musical limitations before changing generation: use permitted 1/2/3/4-bar fixtures, offset downbeats, imperfect trims, several source/project tempos, CHOP/LOOP and A/B. Compare Straight, Genre, Random and Mutate with repeatable settings. | Separate loading/length/first-downbeat problems from generation quality. Record settings, expected result, actual sound and user actions. Prefer existing trim/beat-analysis capabilities before considering a new algorithm. Physical listening remains a separate gate. |

## Manual and guide tasks

| ID / Priority | Deliverable | Acceptance |
| --- | --- | --- |
| DOC-BRK-01 / P0 | Lead with short **goal-based routes**: play a loop; write a break pattern; replace a source; perform rolls; save and reopen. Keep six-page parameter reference as a secondary lookup. | Each lesson identifies the starting screen, numbered buttons, visible labels, an expected audible result and a return path. A beginner can complete one goal without reading all six pages or watching the film. |
| DOC-BRK-02 / P0 | Put a compact route map and recovery cues beside the Break instructions. Distinguish native Sample Kit, Break source loading, CHOP sequencing and LOOP variations. | Explicitly distinguish B1 folder-up from SHIFT + encoder Push closing a browser. Cover the EMPTY carousel root and SONG/name-entry exceptions instead of presenting a universal Back rule. Do not describe unimplemented proposed menus as available. |
| DOC-BRK-03 / P0 | Replace the current version-dependent contradictions and reconcile the First Groove written steps/screens with the release. Remove stale LOOP HOLD wording; label historical video examples clearly until the film is regenerated. | Every stated control name and path is verified against the same shipped tag. Setup/re-entry and mode requirements appear before instructions that need them. Random output is not presented as guaranteed to match the edited musical example. |
| DOC-BRK-04 / P1 | Create an outcome/condition reference: control → required mode/state → what should change → what it does not do → how to stop/revert it. Include a short “I hear no difference” troubleshooting route. | Pattern Hold, Variation/Drift, Grain/Stretch and saving have concrete audible/action examples. State source-file location and permitted formats only after checking the browser’s actual roots and decoder support. Distinguish project save from User Sound/User Kit. |
| DOC-QA-01 / P1 | Run task-based novice checks using only the published guide. Record wrong turns, terminology confusion and time to first loop/first variation; update the guide and UI together. | Static screenshot rendering alone is insufficient. Verify sample placement, browser target, 1–4-bar selection, first playback, regeneration, undo, reopen, source replacement, save and restore. Keep software and physical-device results separate. |

## Suggested order

1. Reproduce the supplied workflow and agree the source-replacement contract; fix factual documentation contradictions in parallel.
2. Improve the existing Break browser and visible source entry; preserve the current loader/Undo/ownership guards.
3. Rewrite the short goal-based guide against that reviewed flow, then verify it with a first-time user.
4. Evaluate tempo-synced audition and generation-quality changes only after concrete failures are identified.

This backlog is not a release announcement. Public homepage/README content should be updated inside its existing descriptions only when the corresponding behavior is available.
