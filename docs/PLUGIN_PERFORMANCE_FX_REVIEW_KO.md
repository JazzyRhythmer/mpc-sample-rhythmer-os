# 첫 화면 필터와 PERFORM 검토

0.4.0-beta.3의 필터·연주 효과 구조다. 실제 검증 범위는 VERIFICATION.md를 참고한다.

## 적용 구조

- 개별 엔진 PRESETS: 원본 주 필터와 대표 음색 제어를 EDIT와 같은 실제 파라미터에 연결한다. Dexed·DRUM-X·Plaits·CS-1·MONO2K에는 엔진 출력 전체에 적용하는 OUTPUT FILTER를 추가한다. PRESETS의 K1/K2는 OUTPUT CUTOFF/OUTPUT RESONANCE이고 K3는 원본 대표 파라미터를 유지한다. LP/BP/HP 타입은 EDIT 첫 행의 OUTPUT FILTER TYPE으로 조정한다. 원본 내부 필터·모델별 음색 제어는 별도로 그대로 보존한다. Prophet의 합성 필터와 FX Tone 필터를 혼동하지 않도록 고정 소스 ID를 명시한다. CS-1 Brightness, MONO2K Filter Width, Plaits 모델별 명칭도 원래 의미를 유지한다.
- Rhythmer Kit: 엔진 내부에 전체 SVF 하나를 기본 제공한다. 기존 Melodee Filter DSP를 재사용하며, 트랙 인서트나 외부 버스에 의존하지 않는다. KIT CUTOFF / KIT RESONANCE를 첫 화면에, 타입 LP/BP/HP를 EDIT에 둔다. 글로벌 설정과 저장된 리셋 기준은 킷 프리셋·프로젝트에 포함한다. 다른 패드·소스를 고르더라도 같은 전체 필터다. 기본 LP/100/0은 정확한 dry 우회이며 지연 메모리 블록을 쓰지 않는다. 소스 패치값은 재작성하지 않는다.
- Kit EDIT의 KIT 항목은 전체, P11 같은 항목은 선택 패드다. 글로벌 필터 행은 ALL PADS로 명시한다. 빈 패드에도 전체 필터만 남고, 이전 패드의 소리 제어가 남지 않는다.
- Sample Kit / Break: 기존 샘플러 전체 필터·레조넌스·음량을 첫 SOUND 페이지에 둔다. Trim 직접 진입과 패드별 필터·전체 타입 설정은 유지한다.
- MIDI에는 오디오 필터를 자동 추가하지 않는다. 독립 IN 엔진은 없고 Input Config의 INPUT FX와 MIDI Audio In / Monitor 경로를 사용한다. 기존 모니터링과 인서트·센드는 유지한다.

## ECHO / SPACE의 원래 의도와 새 위치

Melodee 0.2.0은 모든 PLUGIN 트랙에 같은 FILTER / ECHO / SPACE 연주 노브를 제공했다. 엔진 VCF나 믹서 A/B를 원격 조절하는 값이 아니라 트랙마다 독립된 OS 효과 인스턴스다. FILTER는 LP/HP DJ 스윕이며 이를 DJ FILTER로 명시한다. ECHO는 1/8D 동기 딜레이, SPACE는 리버브의 입력 송신량이다.

B1 PRESETS / EDIT, **B2 PERFORM / ARP / CHORD**, B3 MIX / SENDS / FX로 배치한다. PERFORM에 기존 세 연주 노브를 유지한다. 저장된 제어 ID와 Motion의 의미는 바꾸지 않는다. 첫 화면은 저장된 연주 효과량이 켜져 있으면 PERFORM ON을 표시한다.

신호는 엔진 출력(원본 내부 FX 포함, Kit는 소스 합산 뒤 내부 전체 필터 포함) → OS DJ FILTER → ECHO dry+wet → SPACE dry+wet → 트랙 레벨·팬·인서트 → 직접 출력과 버스 A–D다. SPACE는 ECHO도 받는다. 엔진/인서트/버스 설정값을 덮어쓰지는 않지만, 동시에 사용하면 레벨과 잔향 처리가 겹친다.

ECHO/SPACE는 0으로 내려도 기존 잔향을 남기며, 각 활성 효과는 공유 DelayPool의 한 블록을 쓴다. 자원이 부족하면 해당 공통 wet만 빠지고 dry는 남는다. Kit 내부 필터는 그 풀을 점유하지 않는다. 공통 효과량은 트랙·프로젝트에 저장되고 엔진 프리셋 변경 시 자동 초기화되지 않는다.

기존 강제 정지에서는 공통 잔향 버퍼가 남는 결함을 별도 출력 시험으로 재현했다. PluginEngine::silence()가 MacroStage도 비우도록 보완했다. Kit 내부 필터도 MIDI AllSoundOff의 정확한 프레임에서 상태를 비운다.

## 검증 경계

주 필터의 첫 화면과 EDIT가 같은 값인지, 저장·복원과 패드 전환을 실제 플러그인으로 확인한다. 원본 Melodee의 모델 데이터 Undo와 플러그인 내부 파라미터는 범위가 다르다. 플러그인 내부 노브의 Undo를 새 기능으로 제공하거나 검증됐다고 표현하지 않는다. GEN·Acid·Break의 기존 Undo/Redo는 별도 검사한다. Kit 내부 필터는 factory neutral PCM, 모든 패드의 대상 범위, 실제 발음, 두 인스턴스 독립성, 원본 패치 보존, 사용자 킷·프로젝트·리셋, 빈 패드와 강제 정지를 검사한다.

엔진 내부 값과 Kit 내부 필터는 opaque PluginParam이며, 원본 호스트 MOD의 임의 파라미터 학습 대상은 아니다. 기존 PERFORM·트랙 믹서·FX의 MOD/기록은 유지한다. 물리 기기의 CPU·조작성·청취·설치/복구는 별도 검증이다. 현재 검증 결과는 VERIFICATION.md와 final-validation.lock.json에 기록한다.

킷 패드 EDIT 제목은 `P11 / CS-1 / 사운드명`처럼 선택 패드·실제 엔진·소리를 표시합니다. 킷 전체 필터 행은 `킷 이름 / ALL PADS`를 표시합니다. 패드 소스를 교체해도 킷 프리셋 이름을 현재 소스 엔진으로 오해하지 않도록 구분합니다.
