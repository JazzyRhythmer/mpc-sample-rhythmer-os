# Track instruments, types and navigation

Rhythmer OS uses the sampler, sequencing, browser, mixer, Freeze and undo foundations of Melodee 0.2.0 by Kerem Kiliç (Ellic Studio). These changes add visible track actions and scope browser navigation to the selected track; they do not replace those foundations.

## Changing what a track plays

1. Select the track with PAD BANK + its numbered pad.
2. Open TRACKS with PAD FX + KNOB FX, then press B1 **TRACK SETUP**. The header identifies the target track. TRACK SETUP opens only from B1 on TRACKS. Ordinary encoder Push still opens the selected track; on EMPTY it opens the native type carousel. Existing Stage Shift controls are unchanged.
3. **CHANGE PLUG-IN** opens the instrument browser. On Sample Kit this reads **LOAD SAMPLE** and loads onto the selected kit pad. On MIDI it reads **MIDI DEVICE** and opens its port/channel controls. An empty track reads **ADD INSTRUMENT** and offers its types.
4. **TRACK TYPE** offers **PLUG-IN / SAMPLE KIT / MIDI / EMPTY**. Type changes keep all 128 patterns, the selected pattern, playback speed, mixer strip and track inserts. Engine-specific pad and modulation state is reset when changing type. EMPTY removes the instrument while keeping the sequence; DELETE TRACK is the separate destructive operation.
5. **LOAD MPC KIT** opens the native project/kit browser in a focused mode. Push loads only the selected project's/program's kit, preserving the destination patterns. B2 switches card/internal storage as before. This mode cannot accidentally open the whole project.
6. **DELETE TRACK** asks for confirmation before clearing its sound and all patterns. Cancel starts selected. Shift + Minus undoes deletion or an instrument/type change; Shift + Plus redoes it. Existing native clear-track behavior retains the mixer strip.

The instrument PRESETS list also exposes B2 **PLUG-INS**. Cancel returns to the invoking list or menu without changing its sound; an accepted instrument replacement opens the selected track's Stage. Effect preset lists keep their existing controls. A Break Engine selected in the picker does not replace the current instrument until a loop has been chosen and decoded successfully. Cancelling its loop browser preserves the current instrument.

Changing a kit to a melodic instrument retains the same note events; it does not transpose or rewrite them. Type changes do not convert note mappings or engine-specific automation into a different engine's parameters.

## Screen ownership

| Context | Track change behavior |
| --- | --- |
| Instrument preset list, instrument picker, track-effect picker, sample browser, track actions | Close the former track's context and show the selected track's Stage. Back cannot reopen the previous instrument's browser. |
| Engine Edit, Chop, pad sound/filter/envelope/layers editors, Freeze/Print sheet | Return to the selected track's Stage; obsolete selection sheets and focused notes are cleared. Background print jobs retain their explicitly captured target. |
| Focused LOAD MPC KIT browser | A track change leaves focused kit loading and opens the new track. A file read already started retains its original destination. |
| Patterns, Roll, Motion and Tracks/Sends/track FX | Keep the working page, retarget the track and close obsolete modal selections. Held-pad note releases still reach the original note's track. Roll marks already carry native track/pattern ownership. |
| Bus/master effects and their plugin/preset browsers | Keep the shared effect context. Global Back navigation is retained. |
| Project manager, settings, MIDI configuration, card access, input/recording/looper and global FX controls | Retain native global or operation-specific ownership; no track selection silently changes an in-progress recording target. |

Delayed preset turns commit on the former track before selection changes. The selected track is then changed once, using the common selection path used by track pads, track wheels and MIDI remote selection.

## Asynchronous loads

Whole-kit reads capture their destination track. Bank reads capture both track and bank. A late result cannot land on the track/bank selected afterwards. If the destination instrument is changed or deleted, the queued kit/bank load is discarded. A project switch invalidates outstanding kit/bank results rather than treating them as a whole-project open.

Break loads retain independent job metadata for track, bank, loop bars, A/B and picker origin. Later browsing cannot retarget an earlier decode. A result never forces the screen back from another selected track or an unrelated page. Changing/deleting its destination cancels the queued Break operation.

Changing instruments/types while recording is blocked with a short explanation. Frozen tracks use the native Unfreeze confirmation; browsing folders itself does not alter a frozen instrument. No transport-wide panic or additional audio-thread work is added.

## Design reference and verification

The [Ableton Move manual, Browsing and Swapping Presets](https://www.ableton.com/en/move/manual/#browsing-and-swapping-presets) describes entering the browser from the selected device and returning through its Back hierarchy. This informs the current-track browser ownership and explicit replacement entry. Rhythmer keeps Melodee's existing load/undo/Freeze mechanisms and adds a separate confirmed deletion rather than using deletion as a replacement workflow.

The pinned Melodee v0.2.0 TRACKS page had no instrument/type action menu; the fork had not removed one. The fork's added empty-track shortcuts were, however, inconsistent with the native empty-track button lock. KIT, MIDI, Back and Undo/Redo are now enabled through that lock.

The local ARM64 build passes track workflow assertions; five native menu previews had zero text issues. Host checks exercise real plugin replacement and state restoration, all-pattern preservation, new/used/empty track transitions, scoped Back behavior, PAD BANK selection, delete cancel/confirm, recording/Freeze guards and asynchronous target ownership. Physical-device validation remains separate. Physical installation remains separate from published early-beta software evidence.

An intentional EMPTY retains its patterns and uses the same native PLUG-IN / KIT / MIDI carousel as a never-assigned track. Push from its TRACKS cell or a stranded empty Edit screen opens that carousel; it does not open TRACK SETUP. Sample Kit with no loaded samples is still a Sample Kit, not EMPTY.

## Contextual keys and all-empty navigation

The selected track's active Note Repeat/arp retains the native rate overlay on TRACKS: B1/B2/B3 choose 1/8, 1/16 and 1/32 (B1/B3 again: 1/4 and 1/64; Shift: triplets). Tap NOTE REPEAT to turn it off and restore TRACK SETUP / SENDS / FX. Enabling arp on its ARP page uses the same state. PAD BANK held, track copy/move and modal questions retain their native higher-priority controls. TRACK SETUP is the normal unmodified TRACKS B1 action, not an override of these modes.

Even when every track is EMPTY, unshifted PAD FX + KNOB FX opens TRACKS, in either order. Each key alone stays blocked on the empty carousel, as upstream; their Shift functions are not newly enabled. This allows track/project management without first creating an instrument. No sound, pattern or track is automatically created.

The instrument preset list's B2 PLUG-INS is an additional route to the same instrument picker as SAMPLE SELECT and CHANGE PLUG-IN. Effect preset lists do not expose this replacement route. The new routes check recording/freeze before opening; SAMPLE SELECT can still browse before its common load-time guard. This is a difference in guard timing, not permission to replace a recording/frozen instrument.

GEN subpages use one Back hierarchy for screen BACK and Shift + Push: subpage → GEN main → Patterns. This applies to Vary, Break, Setup and Acid; it does not change generation, seed or note data. Sample-browser folder traversal remains distinct from cancelling the browser to its caller.

## Confirmation cancellation

Shift + Push cancels a confirmation dialog even if its affirmative action is selected. Plain Push and B3 still confirm; B1 still cancels. Cancel preserves the sound, patterns, pending target and undo history.
