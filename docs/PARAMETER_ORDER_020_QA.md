# Parameter names and selected-pad mix — local 0.2.0 candidate

This is a local development change. No release asset, public installer or website has been published for this work.

## User-facing result

- Rhythmer Kit EDIT starts with the selected destination pad's existing native Volume. Pan, Tune and Decay follow in that priority, only when the source exposes them.
- Whole-kit Cutoff / Resonance / Filter Type occupy the next row. PRESETS retains the same whole-kit filter and track-level K3.
- Related source controls stay in rows of three. An unavailable third control is unassigned, rather than borrowing another pad's or source-wide output control.
- Every selected-pad control uses the physical destination prefix P01–P16. Source-wide output and FX remain separately named.
- FMini-1 oscillator enable switches belong to their OSC group; oscillator levels and noise have their own groups. Modulation rows preserve Source / Destination / Amount order.
- Filter Key Tracking and LFO Polarity have named choices. Prophet's extra/track LFO is distinct from its synth LFO. Its source BPM is hidden because the wrapper follows project tempo each audio block.
- New Frodhes labels follow the original instrument TYPE, including Marimba Hand Mute. Its motor controls are visible for Vibraphone only. Tenebrae native percentage values include the correct bipolar sign/range.

## Runtime integration

Changing the legacy design-page map alone did not reorder Melodee's Stage EDIT list. This was caught during integration review and corrected: `PluginRack::panel` consumes `sound_rack_edit_order`, keeps the six source/save controls in place and maps grouped edit slots to existing native control IDs. Blank slots are rejected by `set_param`. Quick controls resolve their display positions from the same mapping. The Kit header identifies the selected pad on the first mix row and ALL PADS on the kit-filter row.

No additional volume DSP, factory preset rewrite or source-parameter range change is part of the mix move. Native states and parameter IDs remain the authority. Source-based naming/visibility refinements can change visible list positions.

## Verification evidence

SSD evidence root: `/Volumes/SSD/Development/BuildCache/rhythmer-os/new-engines-020-20261117`.

- Preset controls: 2,888 selections, 284,523 visible value checks, zero issues (`host-preset-controls-final.log`). This covers the staged 27 source views, including the two local new-engine candidates.
- Existing all-kit ownership/audio scan: 576 pads, all native voice gains checked, zero issues (`host-ownership.log`).
- Runtime build: `runtime-ui-order-rebuild.log`.
- Mechanical patch replay: 141 files match the pinned upstream plus recorded integration patch (`parameter-order-patch-replay.json`).

Final display-order, state-roundtrip and rendered UI results are recorded below after execution. Software renders and signal checks do not establish physical-device listening or installation.

## Final display/order checks

- Actual EDIT inventories: all 576 factory pads start at the selected pad's Volume; every control appears exactly once; display slots align in groups of three. The host test now asserts the actual `sound_rack_edit_order` consumed by Stage, not only the legacy design-page map.
- `host-kits-final.log`: 36 factory kits / 576 pads, plus every source swapped into a custom pad; mixed-engine independent control, user preset file, complete state and project roundtrip passed under ASan/UBSan (leak detection disabled).
- `host-controlroundtrip-order-final.log`: 81 contexts, 4,917 controls, zero issues.
- `parameter-order-ui.log`: production renderer, 6 host-inspected states / 133 edit positions, 24 captures, zero text issues. Inspected first/second rows for P11 Hortator and confirmed the selected-pad vs ALL PADS headers and knob cards.
- Screens: `parameter-order-ui/engine-05-row-002@2x.png` and `engine-05-row-003@2x.png`.

The all-factory-pad guarantee covers the 36 supplied kits. A custom source such as Plaits without a native output-level parameter is not given a synthetic volume DSP by this reordering change; its original controls remain available.

- Final native audio/ownership rerun: all 576 pads checked, zero issues; all 16 drum↔Acid model routing checks passed (`host-kitownership-order-final.log`). All 27 source views passed final name/value/page inspection (`host-inspect-order-final.log`).
