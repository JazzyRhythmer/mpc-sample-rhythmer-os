# Break workflow — beta.3 hotfix.2

## Load and play

Choose **Break Engine** in the instrument list. Before loading a loop, set browser **K1 LOAD BARS** to its actual length (1–4 bars in 4/4), select the file and press the encoder. The engine makes sixteen equal chops. Only an empty pattern receives Straight automatically. Replacing A preserves patterns, pattern lengths, performance and pad sound-design settings. It stays in **BREAK GEN**, with **BRK PERF** selected: press the encoder or **B3 OPEN**. During loading, **B1 CANCEL** or **SHIFT + encoder Push** cancels track assignment; the decoder may keep a cached copy of the file.

A rejected or undecodable source returns to the same browser for retry or cancellation, while keeping the previous instrument. Background failures do not change the current screen. If the target track is frozen during decoding, assignment is cancelled without opening a late Unfreeze dialog.

To reopen: select the Break track → **SEQ / PATTERNS → SHIFT + B3 GEN → BREAK GEN → BRK PERF**. B1 GEN in BRK PERF returns to the generator. BACK or SHIFT + Push returns from BREAK GEN to main GEN; repeat to close it. Switching tracks or leaving the menu during loading does not pull the screen back on completion.

## Six pages

Turn or press the encoder to change pages. Hardware pads are numbered bottom-left to top-right.

1. **CHOPS** — pads 1–16 play slices; Orbit and DJ Filter shape playback. Pattern Hold affects LOOP mode only.
2. **ROLLS / HOLD PADS** — hold a pad for Repeat, Build, Stretch, Echo, Up, Down or Shrink; release it to end that command. Pad 3 is STRETCH.
3. **SOURCE A / B** — Pad 1 selects A, Pad 2 selects B (load B with B2 LOAD B first), Pad 3 returns to straight playback. K1 selects CHOP or LOOP, K2 Pattern Hold, K3 DJ Filter. Both files use the declared source bar count.
4. **LOOP VARIATIONS** — PLAY with a populated pattern, select LOOP on page 3 and leave Pattern Hold OFF. Variation/Drift apply at internal bar boundaries. Tail Fill adds automatic rolls. In CHOP, the written slice sequence remains in charge.
5. **GRAIN / STRETCH** — changes stretched hits, not ordinary chops. With playback running, hold Pad 3 on ROLLS, keep holding while turning the encoder to this page, then adjust Grain/Splice/Slow. Release Pad 3 to finish. A recorded STRETCH command works too. Slow is a 2–4× stretch factor, not project tempo.
6. **TRACK MIX** — track level, pan and Send A. This page does not generate notes.

**Pattern Hold** was labelled **LOOP HOLD** in hotfix.1. It keeps the current internal pattern from regenerating. It is not audio sustain, a grain enable switch or track Freeze. With CHOP or Variation/Drift at zero its audible effect may be absent. It does not stop all live controls. RETURN resets Variation/Drift, not Hold or the recorded sequence. Release performance pads to end held commands.

## Record and save

With PLAY and SEQ RECORD enabled, use ROLLS and SOURCE pads. Command and held length are recorded into the current sequence. Stop recording before auditioning the result. Save the project to retain patterns, A/B sources and control values; reusable sound presets are a separate workflow. Keep your permitted source loops on the card. No break recording is included in the OS package.

The tutorial film demonstrates a session edited before this hotfix. Its audio and arrangement remain examples; use the written button paths and current screenshots for navigation. Random generation will not exactly reproduce its notes.

## Verification scope

The hotfix preserves DSP algorithms, preset banks, command IDs and project serialization. General GEN now also records the Acid RNG stream in the same Undo/Redo operation as its notes; the generation algorithm is unchanged. Software tests cover load/cancel/focus, Undo/Redo, saved hold/mode, held command release after paging, source A/B, recorded command replay, CHOP versus LOOP hold behavior, and grain changes with STRETCH. Physical-device installation, controls, listening and long sessions remain beta validation; software checks do not certify them.

## Replace a source without replacing your music

- BRK PERF pages 1, 2, 4, 5, 6: **B2 LOAD A**. Page 3 SOURCE A/B: **B2 LOAD B**. Its on-screen hint points back to CHOPS B2 for A.
- The browser header shows **LOAD A / N BARS** or **LOAD B / N BARS**. K1 LOAD BARS declares A's 1–4-bar audio length. B shares A's declared bars. Folders and CARD/INTERNAL/PREVIEW remain; non-audio instruments, kits, banks, MIDI and expansions are hidden only here. Shift+pad does not put a Break source on a random kit pad.
- Replacing A at the same length retains B. A changed bar count asks first: **B1 CANCEL** or **SHIFT+Push** cancels; **B3 LOAD A** keeps all pattern lengths and clears B. Undo restores the whole previous track. Source-relative slice trims are rebuilt for the new audio; filters, pitch, envelopes, sends and performance settings stay.
- **BREAK GEN K1 LENGTH** is the native sequence-length control. It is independent of browser LOAD BARS. Set LENGTH, then explicitly apply STRAIGHT or another generation action to write a new pattern.
- In folders B1 BACK goes up. At the root A returns to GEN, B to PERF, or CANCEL to the plug-in list for that entry route. SHIFT+encoder Push closes the browser. ORIGINAL is original-file audition; K2 AUDITION selects a separate SYNC preview using native Beats warp without assigning a source.
- Save with **SHIFT+Pad16 → PROJECT → SAVE**, reopen with OPEN, and retain the source audio files. This is project saving, separate from User Sound/User Kit.

## Audition and condition feedback

B3 PREVIEW enables audition; the physical middle knob **K2 AUDITION** selects ORIGINAL / SYNC. The top **B2** still selects CARD / INTERNAL. SYNC waits for complete audio and uses the actual host tempo with native pitch-preserving Beats warp. It starts when ready, not quantised to a bar. It is monitoring only: no track assignment, pattern edits, inserts/sends, prints/stems/input recording. The initial mode is ORIGINAL. SYNC requires a preview shorter than 30 s and a ¼–4× source/project ratio. CALC is based on duration and the declared bars; it is not beat detection. Failed decoding is shown as PREVIEW UNAVAILABLE.

LOOP VARIATIONS says INACTIVE in CHOP, PATTERN HOLD ON while regeneration is held, READY when it needs playback/amount, and ACTIVE when conditions are met. GRAIN / STRETCH distinguishes WAITING from an actual STRETCH command, including recorded commands. Live commands end when leaving BRK PERF; paging within it keeps a held command so the ROLLS-to-GRAIN gesture works. Other tracks' held notes are retained.

See the Break/Acid guide for outcomes, source preparation and “I hear no difference” checks. A first-time human/device walkthrough remains separate from scripted route and native-audio QA.
