# Chord GEN and generation context

Status: implemented in the development runtime; automated model and shell validation recorded in the QA report. No public release is implied.

## Confirmed Melodee v0.3.0 ownership

- Project owns global tempo, time signature, swing, key root and scale. `seq_tempo` enables one tempo per pattern number, shared across tracks, not one independent tempo per track.
- Actual tempo priority: external MIDI clock; active Song tempo lane; lead pattern-number tempo; global tempo. Scene launch can also update the global tempo at the launch boundary.
- Each track/pattern pair owns length in ticks, Q division, notes, motion and Feel. Track speed is a separate local multiplier. A displayed bar count uses the project's time signature.
- Project swing changes the shared sequencer clock. Pattern Feel and written microtiming can add further offsets. A generator must avoid unintentionally applying swing twice.
- Root/scale guide pad pitch and harmonic operations; changing them does not rewrite existing absolute note events.

## Confirmed current Rhythmer behaviour

- Sound + MIDI Generate Song writes four track patterns and instrument assignments; it does not construct a Song-page arrangement.
- That action changes project root, scale and global tempo; in SEQ BPM mode it additionally sets the lead pattern's tempo. This can affect tracks outside the four generated tracks.
- Full new generation uses FM-1 generated part lengths, Q and baked timing; it resets Feel. MIDI-only and selected-track generation retain the old pattern length.
- Selected-track/MIDI-only generation now adapts imported FM-1 absolute pitches to the existing project key/scale.
- Full pattern comparison is needed when deciding whether generation changed a pattern: notes alone do not capture length, Q or Feel changes.

## Accepted context policy

- Selected-track / MIDI-only generation follows the current project tempo, signature, key/scale and global swing. Chord GEN follows project key/scale unless LOCAL is selected.
- Only the selected track/pattern or four selected track patterns are changed. GEN length changes belong there, not to unrelated tracks or the project time signature.
- The existing Sound + MIDI / Generate Song action continues applying generated global tempo, root and scale; the owner explicitly accepted its effect on other tracks. SEQ BPM also receives the generated tempo at the lead pattern number. Song automation and external clock retain playback priority.
- Chord GEN never changes global tempo, signature, swing, root or scale. LOCAL changes apply only to generated notes. Advanced/borrowed/chromatic harmony may deliberately use chromatic tones.
- New Chord GEN belongs to eligible instrument/MIDI/keygroup tracks, excludes Acid Engine, Break and Rhythmer Kit. Monophonic voices use successive chord tones and identify this as chord arpeggiation.
- Chord controls: genre, progression family, chord changes, bars, rhythm complexity, gate, colour, voicing and register. Native project signature defines bars. New and Mutate have one undo including notes and random state.
- Jazz/neo-soul profiles use guide tones, controlled extensions, rootless/open/quartal voicings, resolving altered dominants, modal interchange, shared tones and minimum-motion voice leading. Existing genre progression tables remain the vocabulary basis.

## Musical references

Reference recordings are listening/design references, not bundled audio or verbatim song reconstructions. Harmony rules are original adaptations of common musical techniques.

- Herbie Hancock, Maiden Voyage: modal space and suspended/quartal voicing direction. Artist discography: https://www.herbiehancock.com/music/discography/album/maiden-voyage/
- Robert Glasper Experiment, Black Radio / Afro Blue: contemporary jazz/R&B texture and shared-tone voicing direction. Label source: https://www.bluenote.com/robert-glasper-black-radio-10th-anniversary-deluxe-edition/
- Berklee Harmony: guide tones, close/spread voice leading, secondary/substitute dominants and modal interchange. https://college.berklee.edu/harmony and https://online.berklee.edu/takenote/voice-leading-paradigms-for-harmony-in-music-composition/

Required validation: all genre menus, major/minor/other scales, all keys, 1-16 bars, non-4/4 signatures, event bounds/duplicates, poly/mono rendering, project round-trip, undo/redo, freeze/recording guards, selected-track navigation and existing Acid/Break/Kit flows. No release is implied.

## Controls and navigation

GEN main: GENERATE Tn / MUTATE Tn preserve engine-adapted single-track generation. CHORD GEN is an independent entry with its own NEW / MUTATE commands and five groups of three controls. B2 PAGE cycles; dots and “n OF 5” show position. B1 BACK or Shift + encoder click returns to GEN.

1. Genre / Progression / Chords (1–8 changes over the complete phrase)
2. Bars (1–16) / Pattern complexity / Chord color (triad, 7th, 9th, advanced)
3. Energy (accent/dynamics) / Play style (block, arp up/down/up-down, strum) / Gate
4. Voicing / Register / Play rate (arp subdivision or strum spacing; inactive for block)
5. Key source PROJECT or LOCAL / Key / Scale

NEW chooses a new harmony seed. MUTATE retains harmony while varying articulation. Mono instruments use arpeggiation instead of block chords. Notes, settings and seed changes are one undo; sound and unrelated tracks stay intact.

Song GEN SETUP adds LENGTH: AUTO retains original FM-1 part lengths for new Sound + MIDI and existing lengths for MIDI-only; a chosen 1–16-bar length applies only to target patterns. Non-4/4 imports preserve quarter-note timing, crop excess beats in shorter bars, and leave remaining beats empty in longer bars. Project swing takes precedence over source swing; small human microtiming remains.
