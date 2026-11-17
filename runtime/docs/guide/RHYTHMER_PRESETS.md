# Rhythmer original presets

Prophet retains its original GPL Init state and adds 15 independently authored sounds. Elixir retains its original GPL Initkit and adds four independently authored seven-voice kits. These parameter edits are by jazzy rhythmer, GPL-3.0-only. They are not the upstream factory banks and do not reproduce Sequential, Erica Synths or Hrtl external patch records.

The standalone instruments still use one sound per track. Elixir exposes each kit's seven voices as individual sound selections. Rhythmer Kit supplies complete 16-pad hybrid layouts using the existing Sophie percussion for roles and additional pads not supplied by Elixir's seven native voices. No voice-allocation or DSP algorithm is changed.

## Prophet — 16 sounds including Init

INIT PROPHET
- Copper Brass: Rounded two-saw brass; quick response, restrained resonance.
- Muted Brass: Short muted brass for syncopated chords.
- Pulse Keys: Clean pulse/triangle keys with a gentle falling envelope.
- Soft Organ: Steady organ-like tone with a short release.
- Warm Strings: Warm detuned strings with a modest, playable attack.
- Wide Pad: Broad sustained chords with bounded attack and release.
- Bright Pluck: Fast bright pluck for melodic sequences.
- Round Bass: Solid pulse/sub bass without a long tail.
- Octave Bass: Saw bass with an octave foundation.
- Saw Lead: Focused two-voice lead with restrained detune.
- Sync Lead: Mild oscillator-sync lead, without extreme modulation.
- Fifth Chord: Open fifth interval for simple melodic chords.
- Soft Chord: Soft chord bed with a clear onset.
- Resonant Step: Controlled resonant sequencer tone; no self-oscillation.
- Air Keys: Lightly textured keys, keeping noise below the oscillators.

## Elixir — Initkit plus four new kits

- Initkit
- Dry Circuit
- Warm Machine
- Bright Logic
- Soft Pulse

Each contains Kick, Snare, Closed Hat, Open Hat, Low Tom, Cymbal and Percussion. The standalone sound list contains 35 choices. New voices use bounded decay and direct attacks; the complete kit layouts retain existing hybrid routing.

Raw edits are in `config/rhythmer-factory-presets.json`; `tools/rhythmer_presets.py` validates native parameter ranges and creates normalized host values. GEN uses the same catalogue. Preset reset returns to the loaded patch values, and sound/kit save restores edits using the normal host state.

The four Rhythmer Elixir kicks use a stronger short pitch envelope, modest native overdrive and a longer bounded body. Their native pitch is retained; non-kick parameters and original Initkit remain unchanged. Audio comparison preserves relative levels and applies no per-kit normalization.
