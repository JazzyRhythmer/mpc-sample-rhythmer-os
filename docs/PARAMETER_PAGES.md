# Rhythmer OS — functional edit pages

An instrument opens on MAIN. B3 EDIT SOUND / EDIT PAD or Push opens sound design. Existing native parameter IDs, values, preset selection, kit routes and saved engine chunks are retained; the pages provide a presentation map over those controls.

| Control | In sound design | In PAGES |
|---|---|---|
| Encoder, −/+ | Previous / next page, stops at either end | Move the page cursor |
| Push | Select row A/B when the second row exists | Open the highlighted page |
| K1–K3 | Edit the selected row's three controls | No sound edits |
| B1 / Back | Return to MAIN | Cancel the list and keep the current page/row |
| B2 | PRESETS; KIT PRESETS changes the whole kit | Not active |
| B3 | PAGES | SELECT |

The header always shows the functional page name and current/total page count. A group that spans multiple pages includes its own part count: FILTER 2/3 with 08/24 means the second Filter page, eighth page overall out of 24. A progress strip shows the overall position. PAGES lists the page numbers and names; the checkmark identifies the current edit page and the highlight identifies the page to open.

Up to six controls appear as two aligned rows of three. The selected row is highlighted; the large knob cards show that row's exact values. Small gauges also show the other row's positions. A/B letters identify the row. Push does nothing when there is only one row. Names remain readable at the existing minimum font size; redundant channel/operator/pad prefixes are removed only inside the cells, where the page and scope already provide them.

Only groups present in the current engine/model appear. OSC, FILTER, ENV, MOD, FX, MODEL and source-specific operator, channel or oscillator sections follow the available original controls. Large groups are split into six-control pages. Original advanced patch fields remain reachable in PATCH DATA; their native encoding/ranges are unchanged. Model changes rebuild the layout using the active controls. The current function is preserved when it still exists; otherwise the editor returns to a valid first page. Row B is cleared when the new page has no second row.

Rhythmer Kit design shows the selected destination pad, its actual source engine and sound. Hitting another pad updates the target and layout. Only that pad's controls appear. Empty pads show MAIN > SOURCE instructions and expose no design knobs. Whole-kit Level/Pan/Send A remain on MAIN MIX, with Send B/C/D on MAIN SENDS. MAIN SOURCE still assigns Pad / Engine / Sound, while MAIN SAVE stores the complete kit. Track mixer values are saved with the project.

PRESETS uses K1 or the encoder to browse, and Push or LOAD to apply. Browsing does not edit the sound behind the list. Returning restores the edit context; a newly loaded preset starts from its first design page, and a newly loaded kit also selects its first pad.

Break Engine uses its own six-page BRK PERF screen for chops, rolls, A/B sources, loop variation, grain/stretch and track mix. Native Sample Kit and MIDI retain their existing controls and page maps. See BREAK_ACID_GUIDE_KO.md for Break and Acid navigation.

The layout is cached on the control side until the focused sound/model changes. It adds no audio-thread work, allocation, file access or new audio lock. This does not certify the existing third-party DSP/wrappers or replace physical-device performance checks.
