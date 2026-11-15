# Native UI and workflow verification

Rhythmer OS retains Melodee 0.2.0 by Kerem Kiliç (Ellic Studio) as its sampler, sequencer, mixer and recovery foundation.

The release uses 20 plugin picker entries, 25 native source views and 36 complete 16-pad kits. Original named presets and stable native parameter keys are retained. External Prophet Sequential and Elixir Erica/Hrtl banks remain excluded; authorized authored selections are identified separately. No break recordings are bundled.

## Track and browser behavior

SAMPLE SELECT remains the inherited instrument-browser entry. Instrument PRESETS adds B2 PLUG-INS; TRACKS adds B1 TRACK SETUP. Both use the same instrument picker and load lifecycle. TRACK TYPE preserves all 128 patterns, the selected pattern and mixer state. DELETE TRACK separately confirms removal of sound and patterns; Undo restores them. EMPTY retains patterns and opens the native type carousel. Instrument-owned browsers follow PAD BANK track changes; shared bus/master contexts remain global.

Active Note Repeat/arp intentionally replaces TRACKS soft keys with rate choices. Turning it off restores TRACK SETUP / SENDS / FX. Held PAD BANK, copy/move and Shift keep their native precedence. Effect preset lists do not expose instrument replacement. Pad-source changes inside Rhythmer Kit remain separate from whole-track replacement.

GEN screen BACK and Shift + Push share one hierarchy: Vary, Break, Setup or Acid → GEN main → Patterns. Going back changes neither patterns nor seed. All-empty projects can open TRACKS using the native PAD FX + KNOB FX chord in either order; solo FX keys and their Shift functions keep the empty-track lock.

Confirmation dialogs treat Shift + Push as Cancel, even when an affirmative answer is selected. Its Shift gesture is consumed so releasing Shift does not clear Roll note selection. Plain Push and B3 still confirm; B1 still cancels. The existing cancellation branch also preserves update deferral. Name, exit and in-progress-update handlers are separate and unchanged.

## Validation scope

Finite software checks cover original source controls, preset/control correspondence, pad ownership and state restoration, track replacement/Undo, contextual navigation and async load ownership. The recorded sound audit covers 2,659 selections, 272,711 preset/control comparisons and 37,226 note probes. The 576 kit pad voice-gain checks report no ownership or audio-routing failures. Native DSP libraries are not all sanitizer-instrumented.

The UI review covers 11 renderer groups, 1,895 input states and 5,176 captures. Post-fix standard previews cover 426 pages. Text-fit measurements and software PCM output do not establish physical display contrast, knob feel, acoustic output, latency, USB/UVC, internal-drive access or installation/recovery behavior. These remain owner beta tests. Exact release checks are described in VERIFICATION.md.
