# Rhythmer OS 0.4.0-beta.1 — Sounds and Rhythmer Kit

## Individual sounds

Select an engine from the plugin picker. Individually selectable engines represent one selected sound on a track. On Keys, select Chromatic or Scale and the required root/scale. Melodic engines keep their original MIDI and polyphony. Drum engines select one original source voice: C4/MIDI 60 is its original pitch, and other keys transpose that sound with the existing band-limited tape-rate bridge. This changes duration and transposes existing tails together, within three octaves of C4; it is not an independent pitched drum voice allocator.



The home SAVE page has Save slot, Save Sound and Status. Choose slot 1–64, turn Save Sound to save, and wait for Ready. User Sound entries appear in PRESETS and survive a restart. Saving to an occupied slot replaces that slot.

## Rhythmer Kit

Rhythmer Kit is pinned first in the plugin picker. B2 PRESETS changes the entire kit. There are 36 named whole-kit selections, including DRUM-X, Hortator, Elixir and K-WASUB. These include original and Rhythmer-authored arrangements; see DRUM_KITS.md. The original Move drum presets, Sophie and classic drum machines are retained. Every factory selection fills pads 1–16. Smaller original kits retain their voices and gain complementary original Sophie percussion. Additional original voices remain available on later banks when needed. No recorded break or proprietary ROM is supplied.

The home SOURCE page is Pad / Engine / Sound. Hit a physical pad, or turn Pad, to choose the pad being edited. Engine changes only that pad's source; Sound selects that source's named sound. A melodic source uses C4 as its trigger. Original drum voices retain their original source notes. EDIT PAD opens functional pages for that sound's original parameters. Editing a shared factory voice forks that pad's state, leaving the remaining pad routes in place.

Kits share their original engine instance while unedited, preserving original choke groups and avoiding one engine instance per pad. Replaced or independently edited pads need their own original instance. Cross-engine choke groups are not added. Only selected engines are staged, from the card to RAM, by a worker. There is no new file access, allocation or host mutex in the audio callback. The original third-party VST wrapper mutex remains a device-performance consideration.

Save slot / Save Kit stores the complete kit into one of 64 user slots. User Kit entries appear in PRESETS. Files are under Rhythmer/Presets/Kits; individual sounds are under Rhythmer/Presets/Sounds. Project save/load independently stores every pad's engine identity, selected sound, complete engine chunk and persistent parameter values. Keep the Plugins folder and user preset files on the card.

GEN drum roles use the canonical first eight Rhythmer Kit roles (kick, snare, clap, closed hat, open hat, tom, rim/percussion, cymbal). An individual engine used on a GEN percussion track instead triggers its C4 reference, so one track continues to play one sound.

## Updating the beta

Back up the current card and projects. Copy the complete 0.4.0-beta.1 SD package, including Rhythmer/Plugins/RHYTHMER - Rhythmer Kit, rather than updating autorun alone. The original engine folders, IDs and mandatory notices remain. Existing sampler/WAV workflows remain available in the sample-kit track.


This is a device-test beta. CPU, latency, repeated card access and long performances with many independently loaded heavy pad engines need owner testing on MPC Sample. The kit source catalogue covers the bundled aarch64 VST2 instruments; it does not promise every external VST3 or armv7 plugin as a pad source.


GEN의 트랙 범위·악기 자동 배정·MIDI 전용 모드와 1–4마디 Break 자동 준비는 [GEN_WORKFLOW.md](GEN_WORKFLOW.md)를 참고하세요.


Edit labels use the focused destination pad, never the original engine lane number. Pad focus is applied before another knob edit. P01–P16 identify bank A; P17–P32 bank B, P33–P48 bank C and P49–P64 bank D. The Sound selector and PRESETS share the current factory or user slot. Native duplicate whole-bank selectors are hidden; model-specific controls and enum values remain editable.


Seven percussion-only source variants live in Rhythmer Kit instead of the track picker; Elixir stays individually selectable. MAIN MIX controls the complete kit; EDIT PAD uses B3 PAGES for its selected-pad controls. Save Kit stores pad designs; the project retains whole-track mixer values.


## Engine MAIN and controls

An engine opens on MAIN. Turn the encoder or −/+ through MIX, SENDS B/C/D, SOURCE and SAVE. B3/Push opens sound design; B1/Back returns to MAIN. B2 opens PRESETS. In Rhythmer Kit, PRESETS changes the entire kit; MAIN → SOURCE uses K1 Pad / K2 Engine / K3 Sound for only the selected pad. The SAVE page stores the whole kit or the single sound, as labelled. Track MIX and sends are saved with the project.

BANK A–D / PAD 1–64 identifies the edit target. Source FX labels identify the chosen original engine's common effect controls, separate from whole-track MIX. Original Init presets retain their source names; redundant host Default entries are removed. Dexed exposes all 33 original published banks (1,056 programs), with bank context and original names. See ORIGINAL_PRESET_AUDIT_KO.md for source data coverage, separate asset terms and documented exclusions.

Functional page navigation, row A/B and page position are described in [PARAMETER_PAGES.md](PARAMETER_PAGES.md).
