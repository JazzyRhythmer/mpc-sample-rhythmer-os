# RHYTHMER OS 0.2.0 — Sounds and Rhythmer Kit

The full SD package supplies **22 instrument entries**, **36 complete Rhythmer Kits** and **2,888 factory sound selections across 27 source views**. This includes kit voices and shared Acid choices, not 2,888 unique synth patches. Frodhes supplies 57 original programs; Tenebrae supplies 164 including Init. FMini-1 uses its original 2.6.0 engine and 200 programs.

## Load and replace an instrument

Select a track with **PAD BANK + its pad**, then press **SAMPLE**. On an entirely EMPTY track, choose **Plugin** from the type cards. On a populated track, use **PAD FX + KNOB FX → B1 TRACK SETUP → CHANGE PLUG-IN**. From an instrument's preset list, **B2 PLUG-INS** opens the same instrument browser. Patterns are retained when changing the instrument; DELETE TRACK is a separate confirmed action.

Individual engines use **one selected sound per track**. Melodic sounds play chromatically or in scale. A single percussion sound uses **C4 / MIDI 60** as its original pitch; other keys transpose that sound with the tape-rate bridge. Transposition changes its duration and existing tail; it does not add independent pitched drum voices.

## Select a preset and edit it

On **SAMPLE → B1 PRESETS**, turn the encoder to change the sound, or push for the full list and push / B3 LOAD to load a selection. Encoder and −/+ navigation wrap within the current list. Save edits before loading another factory sound.

Press **B1 EDIT** for sound-design controls. Turn the encoder to reach another row; use **K1–K3** to adjust its values. Source-native filter, oscillator/model, envelope, LFO, modulation and effects controls depend on the selected engine. The PRESETS filter controls stay linked to EDIT. If you see SLOT / SAVE / STATUS, use **SHIFT + encoder push** to return from saving to sound editing.

## Work with Rhythmer Kit

Rhythmer Kit is first in the plug-in picker. Its preset changes the **whole kit**, with every factory kit filling pads **1–16**. Select a pad before editing: its **native Volume** comes first, followed by its supported Pan, Tune or Decay controls. The next row holds the separate whole-kit filter.

**P01, P11, etc.** identify the selected destination pad. **KIT / ALL PADS** identifies a kit-wide control. The selected source's original lane number is not the destination pad number. Banks A–D extend the editable routing to pads 1–64; factory layouts fill the first 16 pads.

From EDIT, push the encoder to open **PAD SOURCE**. Choose the destination pad, engine and sound. **B3** cycles **PAD SOURCE → SAVE → EDIT**. Pad sources are the curated 27 views backed by 26 native VST2 instruments; arbitrary external VST3/CLAP/LV2 plug-ins are not promised as Rhythmer Kit pad sources. Seven percussion-only variants stay inside the kit picker; Elixir also remains a standalone instrument.

## Save a reusable sound or kit

On an individual engine's EDIT screen, push to open SAVE. In Rhythmer Kit, open the tools and press **B3** until SAVE appears. Set **K1 SLOT**, use **K2 SAVE**, and wait for Ready. There are 64 User Sound / User Kit slots; saving to an occupied slot replaces it. Reload saved entries from PRESETS, including in another project.

User Kit stores pad assignments, source edits and the kit filter. Save the **project separately** to retain patterns, arrangement and track mix: **SHIFT + Pad 16 → B1 SAVE AS → enter name → B3 SAVE**.

## Keep the scopes separate

- Engine filters affect that instrument; Rhythmer Kit's own filter affects the combined kit output.
- **B2 PERFORM** contains the separate track DJ FILTER / ECHO / SPACE macros, alongside ARP / CHORD pages.
- MIX / SENDS / FX control track mixing, sends and inserts. Source-native effects are separate from these host effects.
- A native **Drum / Sample Kit** is a separate track type for audio files and MPC kits. TRACK SETUP → LOAD MPC KIT retains this workflow. Native sample pads have their own send buses; Rhythmer Kit uses track-level sends.

Use the full **0.2.0 SD ZIP**, including its plug-ins and catalogue. UPDATE alone does not install the engine collection.

[Practical manual](MANUAL_020_EN.md) · [Your first groove](FIRST_GROOVE_020_EN.md) · [Essential controls](QUICK_REFERENCE_020_EN.md) · [Preset provenance](ORIGINAL_PRESET_AUDIT_KO.md)
