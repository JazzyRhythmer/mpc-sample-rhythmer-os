# Rhythmer OS 0.4.0-beta.1 UI and preset audit

Current scope: 20 plugin contexts and 36 Rhythmer Kit layouts. The current source banks are documented in ORIGINAL_PRESET_AUDIT_KO.md; all 36 kits and the six new Hortator MD layouts are listed in HORTATOR_KITS_KO.md.

## Edit and navigation

Controls are grouped by function with up to six per page, fixed native IDs, row A/B, current/total pages, progress line and a PAGES map. Reading/navigating these views does not change sound state. Single sounds show only their own voice controls and source-wide controls. Kit controls use the selected destination pad number and isolate edits from other shared voices. Empty pads have a clear selection marker and no stale controls.

Original names and presets remain visible. Native factory selectors are routed through PRESETS rather than competing with a second hidden preset choice. Dynamic model names/ranges and enum values come from source metadata. Engine main screens show the original name, preset, input-driven geometric art and common MIX/SENDS/SOURCE/SAVE controls; preset text has contrast plates. Source FX and whole-track controls remain distinct.

## Workflow

GEN retains FM-1 seeds and four-track sound/MIDI logic, target groups 1-4 / 5-8 / 9-12 / 13-16, and single-track MIDI generation. Acid and Break menus are contextual. The full Break performance screen exposes chops, rolls, A/B, Return, variation, grain and mix, and records/replays commands. Back returns to GEN when entered there. Acid settings, seed stream and Tie/Slide handling match the pinned source with documented host boundaries. GEN opens from PATTERNS with Shift+B3; pads audition without changing patterns while GEN is open. Full-song Tempo/Key/Scale and instrument assignment undo as one operation. Frozen tracks are guarded; Deep Freeze offers Unfreeze. Preset-folder Jump uses the current folder count, and noncontiguous controls map to their actual IDs.

## Observed checks

30,307 detailed states rendered with measured text and knob-binding checks, zero issues; 9,674 captured PNGs. This includes all 576 kit pads, 25 source views, dynamic model/factory layouts, 25 Pad-11 layouts, every preset cursor, page maps and empty-pad states. The new Patterns/Step Edit/Freeze and plugin-host workflow pages are included in the runtime checks recorded in VERIFICATION.md. All 20 engine graphics passed pitch/sustain/input/level/idle/uniqueness tests across 840 native frames (1,680 PNGs). The startup uses a solid interlocking monument and vector wordmark without a background plate. Native/library source data, host state and audio checks are detailed in VERIFICATION.md.

Original DX7 names containing literal dots, such as NOW-YOU..., keep their punctuation; the audit does not confuse these with inserted ellipsis truncation. Width and minimum-font checks still apply.

Device display contrast, knob feel, actual listening, CPU and long-session behavior remain physical owner-beta validation.
