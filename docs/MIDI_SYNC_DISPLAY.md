# External MIDI tempo display

Local implementation; no release or device installation is implied.

The display reads a separate `Snapshot.display_tempo` value. `Snapshot.tempo` and the project tempo retain their existing numerical meaning. MIDI pulse timing, ClockFollower, transport, clock output, recording, sample/loop lengths, automation and tempo-synced effects do not read the display value.

Only MIDI Clock input uses the presentation filter. It has a 750 ms time constant for small fluctuations and a 150 ms time constant when the incoming estimate differs by at least 1 BPM. Display changes are limited to once per 250 ms for a continuing source. Small decimal changes use a 0.075 BPM hysteresis boundary and must persist for 500 ms. These are UI rules, not musical clock rules.

Acquisition, input-port changes and a screen gap longer than two seconds reset presentation state. Internal tempo editing and MTC keep their original display behavior. External whole-number tempos omit the redundant .0 (120 rather than 120.0); genuine fractional tempos retain one decimal place (119.9, 120.1, 127.5). The header reserves 50 px so adjacent status and track labels do not move with the number width. The same presentation formatter is used by the header, Tempo face, tempo card and sequence tempo labels.

Validation: the standalone filter tests cover jitter, rounding-boundary oscillation, real fractional changes, update frequency, larger tempo steps, frame-rate independence, source changes and timer wrap. The runtime track suite and standard UI preview are retained. Physical-device MIDI input and listening tests remain separate.

Local ARM64 validation passed: 26 display-filter checks (ASan/UBSan), 12 formatter/pixel checks, 290 track assertions and 430 preview states with no text issues. All 115 protected MIDI/audio/model/control source files retain their pre-change SHA-256 hashes. The locked runtime patch replays exactly. No public deployment or device installation was performed.
