# RHYTHMER monochrome geometric design

A restrained black/white interface with OP-XY as a visual reference. RHYTHMER uses original code-drawn assets and existing layout/rendering infrastructure.

- Black background, white primary text/selection, neutral greys for panels and secondary information.
- Official MPC Sample outline/solid device wordmark above the original solid pixel RHYTHMER OS wordmark matching the developer signature. The SVG outlines are drawn directly at the destination scale, outside the cached pixel animation. Small by prefix before JAZZY RHYTHMER, aligned on the same baseline.
- Solid interlocking rectangular blocks form a large architectural startup sculpture. The vector wordmark enters without a background plate; four unlabelled abstract engine sculptures settle underneath. The existing startup duration, skip and transition API are retained.
- Square panel edges, square small markers and sixteen-segment knob gauges.
- Original 5×7 numeric glyphs for primary knob values where they fit. Long labels retain the existing readable text system, fitting within their own name/value columns.
- Outlines, position markers, labels and transport icons communicate state alongside brightness. Track numbers remain explicit.
- No additional graphics library, font download, background animation or audio-thread work.

`tools/branding.py` generates original CC0 RHYTHMER layers. The official device wordmark is a separate attributed vector asset (assets/device/NOTICE.md), compiled into native JUCE Paths. No additional graphics library or framebuffer is required. `tools/skin.py` applies the native UI skin after runtime naming. Physical pad-light mapping remains the original hardware implementation. Pages render at 320×240 and undergo text overflow checks; hardware display/lighting validation remains outstanding.


## Rhythmer identity

Rhythmer OS uses a destination-scale pixel vector wordmark matching the small by jazzy rhythmer signature. The startup shares the engine screens' monochrome geometric material and depth: seven thick rectangular blocks move into an interlocked monument before the official vector MPC Sample mark and RHYTHMER OS letters enter. The product letters have no black backplate. Four miniature engine sculptures (Sophie, Aphex, Plaits, Break) remain without captions; READY and SOUND INTO MOTION are absent. All geometry is native JUCE drawing, with no new graphics dependency or synthesis/session-state change.


## Engine-specific performance graphics

The visual reference is the motion of OP-XY performance effects, rather than its step-component icons: [official product](https://teenage.engineering/products/op-xy), [punch-in FX guide](https://teenage.engineering/guides/op-xy/auxiliary), [FX guide](https://teenage.engineering/guides/op-xy/fx). These are design references; no Teenage Engineering artwork, icons, screen recordings or firmware assets are bundled.

Twenty original geometric sculptures fill the main instrument canvas: a struck bell for Sophie, fractured monoliths for Aphex, six resonators for Elixir, a six-voice chorus veil for FM-106, three oscillator towers for FMini-1, intertwined layers for CS-1, an analog fan for OberVave, bass rings for K-WASUB, pulse gates for Hera, woven ribbons for Braids, faceted models for Plaits, a drum cam for Hortator, a saw sculpture for MONO2K, voice pillars for Prophet, a wave surface for S1Vave, six operator pipes for Dexed, an iris for Guru-600, a resonant tunnel for Acid, sixteen radial pillars for Rhythmer Kit and a segmented tape loop for Break.

[Robert Henke Lumiere](https://roberthenke.com/concerts/lumiere.html) informed the sense of large geometric audiovisual space. [OP-XY synth engines](https://teenage.engineering/guides/op-xy/synth-engines) informed instrument-specific visual identity. All geometry is original native JUCE drawing; no reference product artwork is copied.

Existing track meters, held notes, pitch, pan, preset identity and selected kit pad drive symbolic motion. These are not measured spectra, sampled waveforms or per-pad meters. Idle is stable; input activates movement. Pitch changes articulation speed and orbit. A note strike expands the sculpture; holding develops its tilt, roll and breathing over several seconds. Release follows the existing track meter. Only sixteen bounded screen-thread gesture records are retained; original meshes and preset/DSP values stay unchanged. Drawing is capped at 384 depth-sorted faces with a 20 Hz phase cadence, on the screen thread, with no added audio-thread work, taps, locks or allocations. Titles and presets have contrast plates. The original control pages, navigation and preset selection remain. Physical-device graphics performance remains owner-beta validation.

Startup miniatures reuse the production engine renderer. Each projected silhouette fits inside its cell with a three-pixel inset, including during rotation. Instrument-page framing is unchanged.
