# RHYTHMER OS 0.2.0 사용 설명서

이 문서는 **RHYTHMER OS 0.2.0**의 화면과 조작을 설명합니다. 기반 프로젝트 버전인 Melodee Sample 0.3.0과 구분하세요. 이전 영상과 버튼명이 다르면 이 문서의 0.2.0 설명을 기준으로 합니다.

처음에는 [First Groove 따라 하기](FIRST_GROOVE_020_KO.md)를 진행하세요. [필수 조작 안내](GETTING_STARTED_KO.md)에는 버튼 조합과 시스템 구조를 정리했습니다. 공개용 [영문 전체 매뉴얼](MANUAL_020_EN.md)도 같은 버전의 조작을 설명합니다.

## 1. 버튼 이름과 뒤로 가기

- **Push / 클릭:** 큰 로터리 인코더를 누른 뒤 놓습니다.
- **Turn / 회전:** 큰 인코더를 돌립니다.
- **B1 / B2 / B3:** 화면 위 세 버튼의 왼쪽 / 가운데 / 오른쪽입니다. 화면의 현재 버튼명을 확인하세요.
- **K1 / K2 / K3:** 화면 아래 세 노브이며, 화면 아래 카드의 값과 대응합니다.
- **뒤로 / 취소:** SHIFT를 누른 채 **인코더 클릭**. 확인창은 취소하고, GEN 하위 화면은 GEN 메인으로 돌아옵니다. MENU에서도 B1 BACK과 같습니다.
- **미세 조정:** K1–K3 중 대상 노브를 먼저 조작한 뒤 SHIFT + **인코더 회전**. 뒤로 가기와 다른 동작입니다.

NOTE REPEAT / ARP가 켜져 있으면 소프트 버튼이 반복 속도로 바뀔 수 있습니다. 메뉴를 조작하려면 해당 기능을 끄세요. 화면 위에 확인창이나 저장 도구가 떠 있으면 먼저 완료하거나 취소합니다.

## 2. 트랙 선택, 악기 화면, 패턴 화면

| 하려는 일 | 조작 | 확인할 것 |
| --- | --- | --- |
| 트랙 1–16 선택 | PAD BANK를 누른 채 대상 패드를 누르고 PAD BANK를 놓기 | 헤더의 트랙 번호 |
| 선택 트랙의 소리 연주 | SAMPLE | 패드를 누르면 노트·드럼·샘플이 연주됨 |
| 트랙 목록과 믹스 열기 | PAD FX + KNOB FX 동시에 | TRACKS, K1 Level / K2 Pan / K3 Send A |
| 한 트랙의 패턴 선택 | SEQ → B1을 눌러 PATTERNS | 패드가 현재 트랙의 패턴을 선택함 |
| 여러 트랙의 시퀀스 실행 | SEQ → B1을 눌러 SEQUENCES | 같은 번호의 패턴을 여러 트랙에서 실행함 |
| 스텝 편집 | SHIFT + SEQ | 선택 트랙·패턴의 Step Edit |
| GEN 열기 | PATTERNS → SHIFT + B3 GEN | 적용 대상 트랙과 악기 교체 여부 |

트랙을 선택해도 패턴 선택 화면의 패드가 자동으로 음표를 연주하는 것은 아닙니다. 연주·녹음하려면 **SAMPLE**로 돌아갑니다. 예전 문서에서 Stage라고 부르던 화면이 이 악기 화면입니다.

PAD BANK를 짧게 한 번 누르면 패드 뱅크가 바뀝니다. 누른 채 트랙을 선택한 동작에서는 뱅크를 넘기지 않습니다. PATTERNS / SEQUENCES에서 패드가 번호를 바꾸는 것은 악기 연주가 아닙니다.

## 3. 새 프로젝트와 악기 추가

새 프로젝트는 첫 트랙에 기기의 팩토리 킷을 불러옵니다. 빈 킷으로 시작하려면 **SHIFT + Pad 16 → B3 NEW → 확인창의 B2 EMPTY**를 선택합니다. NEW는 현재 프로젝트에 트랙을 추가하는 버튼이 아닙니다.

빈 트랙에 플러그인을 넣는 순서:

1. **PAD BANK + 대상 패드**로 빈 트랙을 선택합니다. 헤더 번호를 확인합니다.
2. 필요하면 SAMPLE을 눌러 타입 카드를 엽니다.
3. 인코더로 **Plugin**을 선택하고 클릭합니다.
4. 플러그인 목록에서 엔진 이름을 선택하고 클릭합니다.
5. 로딩이 끝나면 SAMPLE에서 패드를 눌러 소리를 확인합니다.

| 타입 | 용도 |
| --- | --- |
| Drum | 패드마다 샘플을 넣는 네이티브 Sample Kit. 샘플·MPC 킷·입력 녹음을 사용합니다. |
| Keygroup | 한 샘플 또는 멀티샘플 악기를 여러 음높이로 연주합니다. |
| Plugin | 신스·퍼커션 엔진. Rhythmer Kit도 여기에 있습니다. |
| MIDI, FULL | 외부 악기로 노트·제어를 출력합니다. 외부 오디오 연결 없이는 소리가 나지 않습니다. |
| Audio, FULL | 입력 오디오를 패턴 길이만큼 녹음하는 트랙입니다. |

Basic의 타입 카드는 **Drum / Keygroup / Plugin**입니다. **SHIFT + Pad 8 → Settings → K1 FEATURES = FULL**로 바꾸면 MIDI / Audio와 고급 페이지가 보입니다. Basic/Full 전환은 기존 프로젝트의 트랙이나 노트를 삭제하지 않습니다.

Drum과 MIDI는 타입 다음에 소스를 선택합니다. B1 BACK / SHIFT + 인코더 클릭은 **소스 → 타입 → 이전 화면** 순서로 돌아갑니다.

**완전한 EMPTY와 빈 Sample Kit은 다릅니다.** 이미 만들어진 Sample Kit의 SOUND/TRIM에서 인코더를 클릭하면, 모든 패드·레이어가 비어 있을 때는 TRACK TYPE이 열립니다. 다른 패드에 샘플이 있으면 선택한 빈 패드의 샘플 브라우저가 열립니다.

## 4. 악기 교체, 타입 변경, 삭제

**시작 경로:** 대상 트랙 선택 → **PAD FX + KNOB FX → B1 TRACK SETUP**.

| 항목 | 바뀌는 것 | 유지 / 주의 |
| --- | --- | --- |
| CHANGE PLUG-IN | 선택 트랙의 악기 | 패턴과 트랙 믹스 유지. 교체 확인창에서 확정해야 함 |
| LOAD SAMPLE | 선택 샘플 패드 | 다른 패드와 패턴 유지 |
| TRACK TYPE | Plugin / Sample Kit / Keygroup / Empty, FULL에서는 MIDI / Audio도 표시 | 128개 패턴·선택 패턴·트랙 믹스 유지. 기존 타입의 사운드 상태는 교체됨 |
| LOAD MPC KIT | 다른 MPC 프로젝트·프로그램의 킷 | 대상 트랙의 패턴 유지. 프로젝트 전체를 여는 것과 다름 |
| DELETE TRACK | 트랙의 소리와 패턴 | 별도 확인 후 삭제. 지원되는 Undo로 복원 |

플러그인 프리셋 목록의 **B2 PLUG-INS**, 또는 플러그인 트랙의 **SAMPLE SELECT**로도 악기 브라우저를 열 수 있습니다. 확정 전 Back은 기존 악기를 유지합니다. 녹음 중에는 먼저 녹음을 끝내고, Freeze 트랙은 해제 확인을 따릅니다.

악기·프리셋·샘플 브라우저에서 다른 트랙을 고르면 이전 트랙의 브라우저를 닫고 새 트랙의 악기 화면으로 이동합니다. 공용 버스·마스터 FX 화면은 트랙별 화면이 아니므로 유지됩니다.

## 5. 프리셋 선택과 사운드 편집

1. 대상 플러그인 트랙을 선택하고 **SAMPLE**을 누릅니다.
2. **B1**을 반복해 **PRESETS**를 선택합니다. 엔진명과 현재 프리셋명을 확인합니다.
3. 메인 PRESETS에서 인코더를 돌리면 프리셋을 순서대로 바꿉니다. 클릭하면 목록이 열립니다.
4. 목록에서는 이동만으로 로드되지 않습니다. 항목 선택 후 **클릭 / B3 LOAD**로 로드합니다.
5. B1 BACK은 폴더 위로, 최상위에서는 호출 화면으로 돌아갑니다. SHIFT + 인코더 클릭도 뒤로 가기입니다.

인코더·−/+ 탐색은 마지막 다음에 처음, 처음 이전에 마지막으로 이어집니다. 목록은 현재 폴더 안에서 순환합니다. 공장 프리셋을 로드하면 저장하지 않은 사운드 편집값이 바뀔 수 있으므로 필요한 음색은 먼저 User Sound/Kit으로 저장합니다.

**개별 엔진은 한 음색을 여러 음높이로 연주합니다.** 패드마다 다른 프리셋이 들어가는 구조가 아닙니다. 여러 소리를 한 트랙에서 쓰려면 Rhythmer Kit을 선택합니다.

사운드 편집은 **SAMPLE → B1 EDIT**입니다. 인코더를 돌려 세 개 단위의 파라미터 행을 이동하고 K1–K3으로 표시된 값을 바꿉니다. ENV/LFO/FX는 원본 엔진에 해당 기능이 있을 때 표시됩니다. 첫 PRESETS 화면의 메인 컷오프·레조넌스와 EDIT의 같은 제어는 하나의 값입니다.

**Save Slot / Save Sound 또는 Save Kit / Status가 보이면 사운드 편집 행이 아니라 저장 도구입니다.** SHIFT + 인코더 클릭으로 원래 악기의 EDIT에 돌아가세요.

## 6. Rhythmer Kit: 전체 킷과 패드 한 개 구분

플러그인 목록 맨 위의 **Rhythmer Kit**을 로드합니다. 기본 킷 36종은 패드 1–16이 모두 채워져 있습니다. 처음에는 bank A를 사용하세요.

| 목표 | 조작 | 확인 |
| --- | --- | --- |
| 킷 전체 교체 | PRESETS에서 킷 선택 | 여러 패드의 소리가 함께 바뀜 |
| 한 패드의 엔진·소리 교체 | 악기 EDIT → 인코더 클릭 → PAD SOURCE. 패드 선택 후 K2 ENGINE / K3 SOUND | P번호와 엔진·소리명이 대상 패드와 일치 |
| 한 패드 볼륨 | 악기 EDIT에서 대상 패드 누르기 → 첫 행 K1 Pxx Volume | 해당 패드 음량만 바뀜 |
| 전체 킷 필터 | PRESETS의 KIT CUTOFF / KIT RESONANCE | 모든 패드에 적용 |
| 킷 저장 | 도구 B3 SAVE → K1 슬롯 → K2 SAVE KIT → STATUS READY | User Kit 목록에서 다시 로드 가능 |

도구의 B3은 **PAD SOURCE → SAVE → EDIT**를 순환합니다. B2 KIT PRESETS는 킷 목록을 엽니다. SHIFT + 인코더 클릭으로 원래 악기 편집 위치에 돌아갑니다.

**KIT …**은 전체 킷, **P11 …**은 선택한 11번 패드의 값입니다. 다른 패드를 눌러도 KIT 필터 값은 그대로입니다. 패드 엔진 자체 필터와 전체 킷 필터는 별개입니다.

User Sound는 개별 엔진의 EDIT에서 인코더 클릭으로 저장 도구를 연 뒤, **K1 슬롯 → K2 SAVE SOUND → STATUS READY** 순으로 저장합니다. PRESETS의 User Sound 항목을 선택하고 클릭/LOAD로 복원하세요. 같은 슬롯은 덮어씁니다.

## 7. 샘플과 기존 MPC 킷 불러오기

샘플 한 개를 넣는 순서:

1. Sample Kit 트랙을 선택하고 SAMPLE에서 대상 패드를 누릅니다.
2. **SAMPLE SELECT**를 누르고 브라우저 헤더의 트랙·패드 번호를 확인합니다.
3. 인코더로 폴더·파일을 고릅니다. B2 CARD / INTERNAL은 저장소, B3 PREVIEW는 미리듣기입니다.
4. 파일에서 인코더를 클릭해 로드합니다. SAMPLE로 돌아와 대상 패드를 눌러 확인합니다.

WAV / MP3 / FLAC / Ogg Vorbis / AIFF를 지원합니다. 긴 파일의 변환·캐시 준비가 끝날 때까지 기다리세요. 파일 브라우저에서 다른 패드를 누르면 로드 대상도 바뀌므로 헤더를 다시 확인합니다.

MPC 프로젝트의 킷만 넣으려면 **TRACKS → TRACK SETUP → LOAD MPC KIT**를 사용합니다. **Project → OPEN**은 현재 프로젝트 전체를 바꾸는 경로입니다. 두 작업을 구분하세요.

Sample Kit의 B1/B2/B3은 반복해서 누르면 하위 페이지를 순환합니다. **필요한 페이지명(SOUND, TRIM, TUNE, AMP ENV, PLAY, MIX, FILTER, FILT ENV)이 보일 때 멈추세요.** FULL에서는 LAYERS, COLOUR, SENDS, FOLLOW, CLOUD, KIT FILT도 표시됩니다. 직접 Trim을 여는 단축 동작은 SOUND가 아닌 TRIM으로 들어갈 수 있습니다.

## 8. 패턴 녹음과 시퀀스 실행

트랙별 패턴은 서로 다른 노트입니다. 시퀀스 1은 여러 트랙의 패턴 1을 함께 실행합니다. 트랙별 길이가 같을 필요는 없습니다.

1. 대상 트랙을 선택합니다. **SEQ → B1 PATTERNS**로 갑니다. Roll 등이 먼저 열리면 B1으로 SEQUENCES를 거쳐 PATTERNS로 이동합니다.
2. 사용할 패턴 패드를 고릅니다. bank A의 pad 1은 패턴 1입니다.
3. 패턴 설정 행에서 **K1 LENGTH / K2 Q / K3 SWING**을 설정합니다. 처음에는 4마디 / 1/16 / 50%를 사용합니다.
4. **SAMPLE**로 돌아갑니다.
5. **SEQ RECORD → PLAY**, 카운트인이 있으면 기다린 뒤 패드를 연주합니다.
6. SEQ RECORD를 다시 눌러 녹음만 끄고, STOP으로 재생을 멈춥니다.

패드가 패턴 번호를 바꾼다면 SAMPLE로 돌아오지 않은 것입니다. 카운트인은 **SHIFT + Pad 4**로 켜고 끕니다. 노트 수정은 SHIFT + SEQ의 Step Edit 또는 Roll을 사용하며, 헤더의 트랙·패턴 번호를 먼저 확인합니다.

SEQUENCES는 여러 트랙을 함께 바꿉니다. 노트가 없는 번호를 실행한 트랙은 무음입니다. 한 트랙만 바꾸려면 PATTERNS에서 선택하세요.

## 9. GEN: 악기까지 교체할지, 노트만 만들지

진입: **대상 트랙 선택 → SEQ → B1 PATTERNS → SHIFT + B3 GEN**.

| 메뉴 | 대상 / 결과 |
| --- | --- |
| GENERATE SONG | 선택한 4트랙 그룹에 생성. SOUND + MIDI는 첫 트랙에 킷, 다음 세 트랙에 악기·프리셋·노트 배정 |
| MUTATE SONG | 그 그룹의 패턴 변형. 기존 악기 유지 |
| GENERATE T번호 / MUTATE T번호 | 현재 선택 트랙만 생성·변형. 악기 유지 |
| GENERATE MIDI / MUTATE MIDI | GEN SETUP의 MIDI FROM / TO 범위에 노트 생성. 악기 유지 |
| ACID GEN / BREAK GEN | 해당 엔진이 선택됐을 때만 전용 생성 화면 표시 |

GEN SETUP의 **K3 GEN MODE = SOUND + MIDI**에서는 **K1 SONG GROUP = 1–4 / 5–8 / 9–12 / 13–16**을 고릅니다. 기존 작업을 보존하려면 사용하지 않는 그룹을 선택하세요. 이 모드의 GENERATE SONG은 대상 악기를 바꿉니다.

**MIDI ONLY**에서는 MIDI FROM / TO를 고릅니다. 시작과 끝을 같게 하면 한 트랙만 지정합니다. GENERATE T번호도 현재 트랙만 대상으로 합니다. 적용 전에 화면의 NEW SOUNDS / KEEP SOUNDS / KEEP SOUND를 확인하세요.

하위 생성 화면의 Back → GEN 메인 → PATTERNS 순서로 돌아갑니다. 생성은 지원되는 SHIFT + − / + Undo/Redo로 비교합니다. 일반 GEN의 Seed와 Acid GEN 내부 시드는 별개입니다.

## 10. Acid GEN

1. Acid Engine을 로드하고 SQUELCH 또는 Acid Squelch 등의 프리셋을 고릅니다.
2. **PATTERNS → SHIFT + B3 GEN → ACID GEN**으로 갑니다.
3. SETTINGS 1 OF 2에서 **DENSITY / ACCENT / SLIDE**를 설정합니다.
4. B2 SETTINGS로 2 OF 2의 **OCTAVES / BASE OCTAVE / AUTO MUTATE**를 봅니다. 처음에는 AUTO MUTATE를 OFF로 둡니다.
5. GENERATE ACID → 클릭 / B3 APPLY로 적용하고 PLAY합니다. MUTATE ACID는 현재 라인을 변형합니다.

키·스케일은 프로젝트 설정을 사용합니다. Seed는 내부에서 관리하므로 SEED 노브·숫자·REPLAY 메뉴가 없습니다. AUTO MUTATE는 지원되는 패턴 재생 중 지정한 마디마다 라인을 바꾸며 녹음·Song 재생 중에는 실행하지 않습니다. 고정된 연주를 녹음하려면 끄세요.

## 11. Break: 소스 로드, 재진입, 여섯 연주 화면

먼저 사용 권한이 있고 실제 마디 수를 아는 루프를 준비합니다. 처음에는 **2마디**를 사용하세요.

1. 빈 트랙에서 Plugin → Break Engine을 고릅니다.
2. 브라우저의 **LOAD A**를 확인하고 **K1 LOAD BARS = 2**로 지정한 뒤 파일을 선택·클릭합니다.
3. 준비가 끝날 때까지 기다립니다. BREAK GEN 메뉴는 유지됩니다. 비어 있던 패턴에만 Straight가 준비됩니다.
4. PLAY로 재생합니다. 의도보다 절반·두 배 속도라면 생성보다 먼저 소스의 마디 수를 확인합니다.
5. BRK PERF를 고르면 연주 화면입니다. 다시 생성 설정으로 갈 때는 **선택 Break 트랙 → SEQ → B1 PATTERNS → SHIFT + B3 GEN → BREAK GEN**을 사용합니다.

로드 중 **B1 CANCEL / SHIFT + 인코더 클릭**은 배정을 취소합니다. 다른 트랙으로 이동한 뒤 늦게 끝난 로딩이 새 트랙을 덮어쓰면 안 됩니다. 로드 완료 후에는 Undo/Redo로 교체를 비교할 수 있습니다.

인코더를 돌려 1–6페이지를 넘깁니다.

| 페이지 | 직접 해볼 조작 | 작동 조건과 결과 |
| --- | --- | --- |
| 1 CHOPS | pad 1–16 누르기 | 16개 슬라이스 연주. B2 LOAD A는 A 소스 선택 |
| 2 ROLLS / HOLD PADS | 재생 중 반복 패드를 누른 채 유지했다 놓기 | 누른 동안 명령 적용, 놓으면 종료. pad 3은 STRETCH |
| 3 SOURCE A / B | B2 LOAD B로 B를 로드한 후 pad 1/2로 A/B 선택 | B가 없으면 먼저 로드. pad 3 / RETURN은 Straight 복귀 |
| 4 LOOP VARIATIONS | SOURCE에서 PLAY MODE = LOOP, PATTERN HOLD = OFF, 재생 후 Variation/Drift 올리기 | CHOP 재생에는 내부 LOOP 변형이 적용되지 않음 |
| 5 GRAIN / STRETCH | 2페이지 pad 3 STRETCH를 계속 누른 채 인코더로 5페이지 이동 | STRETCH가 활성화된 동안 Grain을 조절. 노브만 돌려서는 시작되지 않음 |
| 6 TRACK MIX | Level / Pan / Send A | Break 트랙 믹스 조절 |

**PATTERN HOLD는 내부 LOOP 패턴의 재생성을 멈추는 값입니다.** 오디오 Freeze, 지속음, Grain 켜기가 아닙니다. INACTIVE / WAITING / READY 상태에서는 그 조건부터 확인하세요. Grain은 STRETCH, LOOP VARIATIONS는 LOOP·재생·Hold OFF가 필요합니다.

BREAK GEN의 Straight / Genre / Random / Mutate / Tail Fill은 패턴의 슬라이스 순서를 생성합니다. 이를 누르는 것과 LOOP 모드·STRETCH 명령을 활성화하는 것은 다릅니다. 다른 마디 수의 A를 교체할 때 나타나는 길이 확인창은 Back으로 취소할 수 있습니다.

## 12. 필터, 효과, 센드 구분

| 제어 | 적용 대상 |
| --- | --- |
| 플러그인 PRESETS의 CUTOFF / RESONANCE | 해당 엔진의 메인 필터. EDIT의 동일 제어와 연동 |
| Rhythmer Kit의 KIT CUTOFF / KIT RESONANCE | 전체 킷 |
| Pxx의 필터·볼륨 | 선택한 킷 패드 |
| Sample Kit의 B3 FILTER | 개별 샘플 패드 |
| Sample Kit의 SOUND / KIT FILT | 네이티브 킷 전체 필터 |
| 플러그인 B2 PERFORM의 DJ FILTER / ECHO / SPACE | 별도의 OS 트랙 연주 효과 |
| SEND A–D | 공용 버스로 보내는 양 |
| 엔진 FX / 트랙 인서트 / 버스 FX | 각각 다른 처리 단계 |

**ECHO = SEND A, SPACE = SEND B가 아닙니다.** 효과가 과하면 PERFORM ECHO/SPACE와 센드를 낮추고 엔진 자체 FX·인서트를 확인합니다. 송신량을 0으로 내려도 기존 잔향은 남을 수 있습니다. 바로 끊으려면 STOP 두 번입니다.

## 13. 프로젝트와 User Sound/Kit 저장

재생·녹음·프린트가 멈춘 유휴 상태에서는 약 3초 뒤 별도 복구본이 갱신됩니다. **SAVED / UNSAVED**는 수동 저장 기준이며, **Recovery saved HH:MM**은 복구 저장 기준입니다. 수동 SAVE가 끝난 뒤 전원을 끄거나 카드를 분리합니다.

수동 저장: **SHIFT + Pad 16 → B1 SAVE**. 첫 저장은 폴더 선택 → B3 USE FOLDER → 이름 → B3 SAVE이며 이후에는 같은 파일을 갱신합니다. 다른 이름·폴더의 독립 프로젝트는 프로젝트 화면의 **SHIFT + B1 SAVE AS**를 사용합니다. 자동저장은 Rhythmer/Autosave의 프로젝트별 복구본 하나만 갱신하며 원래 수동 저장 파일은 보존합니다. 복구는 프로젝트 화면의 **SHIFT + B3 RECOVERY**입니다. 다시 열기: Project → B2 OPEN → 프로젝트 선택 → LOAD. 미저장 변경이 있으면 SAVE·DISCARD·CANCEL을 선택합니다.

| 저장 종류 | 저장 내용 | 별도로 보관할 것 |
| --- | --- | --- |
| 프로젝트 | 트랙·패턴·믹스·지원 변조·악기 상태 | 원본 샘플과 카드 백업 |
| User Sound | 재사용할 악기 음색 | 패턴·곡 구성 |
| User Kit | 전체 킷과 패드별 편집 | 패턴·곡 구성·원본 샘플 |

Rhythmer, Samples와 다른 원본 오디오 폴더를 함께 백업하세요. 프리셋을 저장했다고 소스 파일을 지워도 되는 것은 아닙니다.

## 14. 추가 작업의 진입점

| 작업 | 경로와 첫 조작 |
| --- | --- |
| 오디오 트랙 녹음 | FULL → 빈 트랙 Audio → INPUT 설정 → SEQ RECORD + PLAY |
| Auto Sample | Song 밖의 Plugin/MIDI 트랙 → SHIFT + Pad 11 → 자동 검사 완료 → B2로 키·노트·사운드 행 설정 → B3 SAMPLE |
| Stems 분리 | 네이티브 킷 TRIM → SHIFT + B3 STEMS 또는 MENU HERE → STEMS. 소스 다음 네 패드는 비워 두기 |
| Freeze | FULL → 인코더 길게 → HERE → FREEZE. 출력 옵션 확인 후 실행. Deep Freeze는 플러그인을 내려놓으므로 다시 편집할 때 Thaw 필요 |
| MPC 3 내보내기 | Song → B1 EXPORT → MPC 3. FX·센드·곡 템포 변화·WAV 아닌 소스 등은 내보내기 한계 확인 |
| USB 웹 | USB-C 네트워크 연결 후 rhythmer.local. Files / 가이드 / 업데이트는 악기 편집과 별도 |
| 화면 미러 | Settings → SCREEN의 미러 설정 후 컴퓨터 카메라 앱에서 MPC Sample 선택 |

## 15. 문제가 생겼을 때 먼저 확인할 것

| 증상 | 확인 / 조치 |
| --- | --- |
| 패드를 눌러도 패턴만 바뀜 | SEQ를 놓고 SAMPLE |
| 플러그인 목록이 비어 있음 | 전체 SD ZIP 설치와 Rhythmer/Plugins 확인 |
| 편집할 노브 대신 Save Slot이 보임 | SHIFT + 인코더 클릭으로 악기 EDIT에 복귀 |
| 킷 노브가 다른 소리를 바꾸는 것 같음 | 대상 패드를 누르고 P번호 확인 |
| 소리가 안 나거나 작음 | 트랙·패드 Level, Mute, 메인 컷오프, 출력, MIDI 포트·입력 확인. 알려진 공장 프리셋으로 비교 |
| STOP 후에도 잔향이 남음 | 400ms 이내 STOP 두 번 |
| B1이 TRACK SETUP이 아니라 반복 속도 | NOTE REPEAT / ARP를 끄고 TRACKS 재진입 |
| Break 속도가 절반·두 배 | 파일의 실제 마디 수와 LOAD BARS 확인 |
| Variation / Grain을 바꿔도 변화 없음 | 11절의 LOOP / Hold / STRETCH 조건 확인 |
| 저장 오류 / User 프리셋 누락 | 카드 여유·쓰기 권한 해결 후 다시 저장. STATUS READY 전에는 성공으로 간주하지 않기 |

## 크레딧과 베타 확인 범위

개발자 jazzy rhythmer. 기반은 Melodee by Kerem Kiliç (Ellic Studio), sample-base와 고지된 원본 엔진들입니다. 각 라이선스·출처 고지는 설치·소스 파일에 유지합니다. 소프트웨어 검증과 실제 기기 설치·청취·타이밍·USB·장시간 사용 검증은 구분합니다.
