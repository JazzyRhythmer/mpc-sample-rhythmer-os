# Native sound controls

Sound editing follows Melodee 0.2.0 PRESETS → EDIT. PRESETS combines the engine name, named sound and animation with source-authoritative primary filter or representative controls. B2 PERFORM holds the retained DJ FILTER / ECHO / SPACE, before ARP / CHORD. EDIT lists six controls with three active knob cards. Turn the encoder or use −/+ to move by three controls; EDIT current/total identifies the position. Labels retain source groups such as oscillator, filter, envelope, LFO and FX, ordered from the original sound panels.

K1–K3 change the highlighted row. The list displays full names; the cards display values and knob identities. In Rhythmer Kit, KIT CUTOFF / KIT RESONANCE / KIT FILTER TYPE are the engine-owned whole-kit filter and are saved with the Kit; subsequent P01–P16 rows identify the selected destination pad. Hit another pad to change the edit target. Shared factory voices are isolated on the first independent edit. Empty pads retain only the three whole-kit filter controls, with no stale source controls.

B3 cycles SAVE / EDIT for an instrument and PAD SOURCE / SAVE / EDIT for Rhythmer Kit. PAD SOURCE is Pad / Engine / Sound. PRESETS changes the whole kit; PAD SOURCE changes only the focused pad. Host mix/sends use the mixer. The saved project retains these host values separately from the kit preset.

The source ENV/LFO matrices remain inside each instrument. Motion MOD controls common host targets; it does not automatically learn arbitrary internal plugin parameters. Source-specific sequencer/storage actions and packed patch bytes are hidden where they have no direct sound-design meaning. Native IDs and original presets stay stable.

Break retains its six-page BRK PERF flow. Sample Kit and MIDI use their native Melodee screens. See NATIVE_PLUGIN_WORKFLOW.md and USER_MANUAL_KO_DRAFT.md for current controls. Older functional-page/map screenshots are development history and do not describe this revision.


### 추가 출력 필터 — Dexed·DRUM-X·Plaits·CS-1·MONO2K

이 다섯 엔진의 PRESETS 첫 두 노브는 **OUTPUT CUTOFF / OUTPUT RESONANCE**입니다. EDIT의 첫 세 줄에서 같은 컷오프·레조넌스와 **OUTPUT FILTER TYPE (LP/BP/HP)**을 조절합니다. OUTPUT FILTER는 이 제어 묶음의 이름이며 별도의 메뉴 버튼이 아닙니다. 세 번째 노브에는 원본의 대표 음색 파라미터가 남습니다.

추가 필터는 엔진의 원래 합성·내장 이펙트 뒤, OS PERFORM·트랙 인서트·센드 앞에서 출력 전체를 처리합니다. 인서트 슬롯이나 버스는 사용하지 않습니다. 기본값은 Cutoff 100%, Resonance 0%, LP이며 이 조합에서는 원본 오디오를 그대로 통과합니다. 원본 프리셋을 선택하면 이 중립값으로 시작하고, Save Sound와 프로젝트 저장에는 추가 필터 설정도 포함됩니다. 원본 필터·ENV·LFO·FX 설정은 변경하지 않습니다. Rhythmer Kit 안에서는 패드 원본의 필터와 별도로 킷 자체의 KIT FILTER가 전체 합산 출력을 처리합니다.
