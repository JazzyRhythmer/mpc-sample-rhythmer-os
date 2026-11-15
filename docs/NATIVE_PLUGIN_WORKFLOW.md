# Native plugin workflow

The plugin browser and PRESETS list follow Melodee 0.2.0 by Kerem Kiliç (Ellic Studio), commit `8880d16116ccb3c69f75fb46bf2166b16c51ef0c`. Encoder/K1 selects a preset; Push/LOAD applies it. The Stage PRESETS encoder retains the upstream audition behavior.

Stage PRESETS displays the engine, named preset and input-responsive animation, above its real primary filter/resonance or representative source controls. These mirror EDIT, not separate values. B2 opens PERFORM (DJ FILTER / ECHO / SPACE), then ARP / CHORD; B3 retains MIX / SENDS / FX. Performance effects are per-track and separate from engine effects and SEND A–D. EDIT uses Melodee's six-line list and three knob cards. Encoder/−/+ moves by three controls; row position and total remain visible. There is no extra MAIN/PAGES navigation layer.

Original sound controls are ordered from the source's EDIT, ENV, LFO and FX panels. Display order never renumbers native parameter IDs or rewrites factory programs. Wrapper Pitch reference, Pitch mode, Save slot and Status are not synthesis controls and do not appear in the sound-design list. Synth LFO and Track LFO are distinguished. Packed switch bytes have individual named switches; unsupported source-only sequencer, FM4-operator and internal track selectors are hidden rather than presented as functioning sound controls.

Rhythmer Kit has its own whole-kit SVF: KIT CUTOFF / KIT RESONANCE on PRESETS, and KIT FILTER TYPE (LP/BP/HP) on the first EDIT row. It uses no insert slot or delay block and is saved in Kit presets, projects and their reset baselines. Its factory setting is a bit-exact bypass. Subsequent EDIT rows show the focused pad's controls, labelled P01–P16. Source-local effects stay attached to that pad's engine instance; the host mixer and its track sends remain separate. B3 cycles PAD SOURCE → SAVE → EDIT. Ordinary instruments cycle SAVE / EDIT. Kit PRESETS replaces the complete kit; PAD SOURCE replaces only the selected sound. Acid Engine follows the instrument flow and exposes Hortator ACID controls, including its source LFO/filter/FX; its drum-model selector is hidden. Break retains native browsing, slicing, BRK PERF, GEN and Return.

Loading a project retains its initial track selection. Hold PAD BANK and press a pad to select a track. An empty track offers three families: PLUG-IN, KIT and MIDI, using the upstream carousel of seven choices. Turn the encoder to choose, then Push to enter. B2 selects Sample Kit; B3 selects MIDI. Closing a browser returns to the same empty track.

Native sound racks apply requested programs directly and retain the pending requested selection while loading. The generic VST3 alternate-program workaround does not run for these racks. The optional selected preset name is saved with projects using the reviewed upstream backport listed in `config/upstream-backports.json`.

The native engine LFO/modulation matrices are distinct from Motion MOD. Melodee Motion learns common host controls such as DJ FILTER/ECHO/SPACE on PERFORM; arbitrary internal plugin parameters are not supported Motion targets. Turning an unsupported plugin control clears the previous learn candidate, preventing accidental reuse of a stale target.

Sample Kit and Break land on SOUND with the existing sampler-wide filter/resonance/level. TRIM remains a direct shortcut and the next B1 page. Pad filters and whole-track filter type remain separate. MIDI routing and existing input monitoring/INPUT FX are retained; no audio filter is invented for external MIDI.

The Kit reserves shown controls 6–8 for its internal filter; source controls begin at 9. Individual racks retain their source controls from 6. Original DSP parameter IDs and child state data are unchanged.

Physical-device behavior remains a separate validation step. The beta installation uses the complete SD package; hardware validation is pending. Current acceptance evidence is recorded in VERIFICATION.md; an older build's counts are not acceptance for this revision.


### 추가 출력 필터 — Dexed·DRUM-X·Plaits·CS-1·MONO2K

이 다섯 엔진의 PRESETS 첫 두 노브는 **OUTPUT CUTOFF / OUTPUT RESONANCE**입니다. EDIT의 첫 세 줄에서 같은 컷오프·레조넌스와 **OUTPUT FILTER TYPE (LP/BP/HP)**을 조절합니다. OUTPUT FILTER는 이 제어 묶음의 이름이며 별도의 메뉴 버튼이 아닙니다. 세 번째 노브에는 원본의 대표 음색 파라미터가 남습니다.

추가 필터는 엔진의 원래 합성·내장 이펙트 뒤, OS PERFORM·트랙 인서트·센드 앞에서 출력 전체를 처리합니다. 인서트 슬롯이나 버스는 사용하지 않습니다. 기본값은 Cutoff 100%, Resonance 0%, LP이며 이 조합에서는 원본 오디오를 그대로 통과합니다. 원본 프리셋을 선택하면 이 중립값으로 시작하고, Save Sound와 프로젝트 저장에는 추가 필터 설정도 포함됩니다. 원본 필터·ENV·LFO·FX 설정은 변경하지 않습니다. Rhythmer Kit 안에서는 패드 원본의 필터와 별도로 킷 자체의 KIT FILTER가 전체 합산 출력을 처리합니다.

## Replacing instruments and changing track families

For another plug-in, press SAMPLE until Pads / Keys, then encoder Push to open the full editor and B1 PLUG-INS. Stage EDIT is a quick subpage with different soft-key labels.

There is currently no visible dedicated track-family conversion menu. KIT / Empty creates an empty Sample Kit. To change Plug-in / Sample Kit / MIDI families, clear the track with PAD BANK + ERASE + its track pad, confirm B3 CLEAR, and choose a new card on the empty Stage. **This clears the sound and patterns together.** Save/copy the project first; SHIFT + Minus undoes the clear. A visible type-change command that preserves compatible patterns is a proposed improvement, not a feature of beta.3.
