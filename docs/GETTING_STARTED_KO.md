# 처음 시작하는 트랙 워크플로우 — Rhythmer OS 0.4.0-beta.3

첫 공개 베타용 안내입니다. B1/B2/B3는 화면 위쪽의 소프트 버튼, K1/K2/K3는 화면 아래 값과 연결되는 노브입니다. Push는 큰 로터리 인코더를 누르는 동작입니다.



### 빈 트랙·빈 패드에서 시작하기

**SAMPLE → SOUND 또는 TRIM → 큰 인코더 클릭(Push)** 으로 시작합니다.

- **악기가 없는 EMPTY 트랙:** 기존 PLUG-IN / KIT / MIDI 선택 카드를 사용합니다.
- **Sample Kit의 모든 패드가 비어 있음:** `TRACK TYPE`이 열립니다. `PLUG-IN`은 악기 브라우저, `SAMPLE KIT`은 첫 샘플 브라우저로 이어집니다. MIDI·EMPTY도 선택할 수 있습니다.
- **다른 패드에 샘플이 있고 선택한 패드만 비어 있음:** `SAMPLES`에서 파일을 고르고 Push하면 선택한 패드에 로드합니다. 브라우저에서 다른 패드를 누르면 로드 대상도 그 패드로 바뀌므로 헤더와 패드 번호를 확인하세요.
- 판정은 **A–H 전체 128패드와 추가 레이어**를 포함합니다. 레이어에 소리가 있는 패드는 빈 패드로 취급하지 않습니다. Rhythmer Kit 플러그인의 PAD SOURCE와는 별도인 네이티브 Sample Kit 동작입니다.
- 화면에 `PUSH: TRACK TYPE` / `PUSH: LOAD SAMPLE` 안내가 표시됩니다. **SHIFT + 인코더 클릭**은 브라우저를 닫고 이전 화면으로 돌아갑니다. 브라우저의 **B1**은 폴더 안에서는 상위 폴더로, 최상위에서는 이전 화면으로 돌아갑니다. 샘플 로드는 **SHIFT + −**로 되돌릴 수 있습니다.

샘플이 있는 패드, 다른 편집 페이지, Break의 루프 로드 경로는 기존 조작을 유지합니다. 녹음 중이나 Freeze 상태에서는 기존 보호 안내를 따르세요. 악기 교체·삭제는 **TRACKS → B1 TRACK SETUP**을 사용합니다.



### 프리셋 순환 탐색과 Acid Engine의 Aphex 사운드

프리셋 목록과 메인 PRESETS 화면에서 **인코더 또는 −/+**로 탐색하면 마지막 다음은 첫 항목, 첫 항목 이전은 마지막 항목입니다. 목록 화면은 현재 폴더 안에서 순환하고, 메인 PRESETS는 기존의 전체 프리셋 탐색 범위를 유지합니다. User Sound / User Kit도 포함합니다. K1 같은 절대 위치 노브의 범위, 목록의 Push / LOAD 확정, 메인 화면의 기존 적용 타이밍은 유지합니다. 프리셋이 없는 엔진에서는 새 프리셋을 만들거나 다른 기능을 실행하지 않습니다.

Acid Engine에는 기존 Hortator의 **SQUELCH / DEEPBASS / SCREAMER / SQUAREAC** 외에 Aphex 원본의 **Acid Squelch / Lead Scream / Whistle Lead / Resonant Spike / Acid Seq / Reso Bass / Filter Cry / Techno Pulse**를 추가했습니다. 원본 이름·패치 선택값을 유지하며 Aphex 사운드는 실제 Aphex DSP로 재생합니다. 첫 화면의 컷오프·레조넌스와 EDIT의 ENV·LFO 등은 선택된 소스의 실제 제어를 사용합니다. ACID GEN은 같은 Acid Engine 트랙에서 계속 사용할 수 있고, 프로젝트와 User Sound에 선택한 소스·편집값이 함께 저장됩니다.


## 꼭 알아야 할 키 조합

| 목적 | 조작 | 알아둘 점 |
| --- | --- | --- |
| 뒤로 / 취소 | **SHIFT + 인코더 클릭** | 확인창에서는 취소. GEN 하위 화면은 GEN 메인으로 복귀 |
| TRACKS 진입 | **PAD FX + KNOB FX 동시 누르기** | 트랙 선택 후 클릭은 악기 화면. B1 TRACK SETUP은 악기·타입 변경 |
| 트랙 선택 | **PAD BANK 누른 채 Pad 1–16** | 선택 후 PAD BANK를 놓고 헤더의 트랙 번호 확인 |
| 악기 / 패턴 화면 | **SAMPLE / SEQ** | SAMPLE은 소리 연주, PATTERNS에서는 패드로 패턴 선택 |
| 미세 조정 | **K1–K3 중 대상 노브 조작 → SHIFT + 인코더 회전** | SHIFT 없이 회전하면 EDIT 파라미터 행 이동 |
| 프로젝트 저장 | **SHIFT + Pad 16 → B1 SAVE** | User Sound / User Kit 저장과 별개 |
| GEN | **PATTERNS → SHIFT + B3 GEN** | 적용 대상과 NEW SOUNDS / KEEP SOUNDS를 확인 |
| Undo / Redo | **SHIFT + − / +** | 지원되는 프로젝트 편집에 적용 |
| 오디오 끊기 | **STOP 두 번, 400ms 이내** | SHIFT + STOP은 All Notes Off |

설치 ZIP의 오프라인 이미지: `Documentation/essential-controls.png`와 `Documentation/os-structure.png`.

한 장짜리 비주얼 안내: [필수 조작](https://jazzyrhythmer.github.io/mpc-sample/manual/essentials.html) · [OS 구조](https://jazzyrhythmer.github.io/mpc-sample/manual/structure.html).

프로젝트 안에 16트랙이 있고 각 트랙은 악기·패턴·믹스를 갖습니다. EMPTY에서 PLUG-IN / KIT / MIDI를 선택합니다. Rhythmer Kit은 PLUG-IN 안에 있는 16패드 악기이고, KIT은 샘플을 넣는 네이티브 Sample Kit입니다. 트랙마다 최대 128패턴을 만들고 Scenes로 묶어 연주하거나 Song에 배열합니다. SAMPLE은 소리, SEQ는 패턴, TRACKS는 트랙과 믹스의 출발점입니다.

## 1. 트랙 선택과 트랙 화면 열기는 다릅니다

1. **PAD BANK를 누른 채 번호 패드 1–16**을 누릅니다. PAD BANK를 놓고 헤더의 트랙 번호를 확인합니다.
2. **SAMPLE을 짧게 한 번** 누르면 선택 트랙의 **Stage(악기 메인 화면)**로 갑니다. 이미 Stage에 있으면 첫 음색 페이지로 돌아갑니다.
3. 전체 트랙을 보려면 **PAD FX + KNOB FX를 함께** 눌러 **TRACKS**를 엽니다. 인코더나 번호 패드로 트랙을 고르고 **Push**하면 그 트랙의 Stage가 열립니다.
4. **SAMPLE을 길게 누르는 동안**에는 Pads / Keys와 관련 노브를 볼 수 있습니다. SAMPLE을 여러 번 눌러 Stage → Tracks → Keys를 순환하는 이전 안내는 현재 구조와 다릅니다.

PATTERNS에서 트랙을 선택하면 작업 화면을 유지합니다. 선택한 악기로 들어가려면 SAMPLE을 누릅니다. 프리셋·악기·샘플 로드 화면에서 다른 트랙을 선택하면 이전 트랙의 브라우저를 닫고 새 트랙의 Stage로 이동합니다. 버스·마스터 화면은 공용 화면이므로 그대로 유지합니다.

## 2. 처음 악기 넣기

EMPTY 트랙의 Stage에서 인코더를 돌려 PLUG-IN / KIT / MIDI 계열 카드를 고른 뒤 Push합니다. B2 KIT와 B3 MIDI도 사용할 수 있습니다. 의도적으로 EMPTY로 비운 트랙도 같은 선택 화면을 사용합니다.

- **PLUG-IN → Rhythmer Kit**: 한 트랙에 여러 드럼 사운드를 담습니다. PRESETS에서 킷 전체를 바꿉니다.
- **PLUG-IN → 개별 엔진**: 한 트랙에서 선택한 한 음색을 연주합니다. 크로매틱/스케일 설정에 따라 패드 음높이가 달라집니다.
- **KIT → Sample Kit**: 오디오 샘플용 네이티브 킷입니다. SAMPLE SELECT로 선택 패드에 파일을 넣습니다. 샘플이 없는 Sample Kit도 EMPTY 트랙과는 다릅니다.
- **MIDI**: 외부 악기용 포트·채널을 설정합니다. 외부 악기/오디오 연결 없이 MIDI 트랙 자체에서 소리가 나지는 않습니다.

## 3. 이미 있는 악기 교체 / 트랙 타입 변경

**PAD BANK + 대상 번호 패드 → PAD FX + KNOB FX → B1 TRACK SETUP**

1. 헤더의 대상 트랙을 확인합니다.
2. **CHANGE PLUG-IN**은 다른 악기를 엽니다. 플러그인 프리셋 목록의 **B2 PLUG-INS**, 또는 플러그인 트랙의 **SAMPLE SELECT**로도 악기 브라우저에 들어갈 수 있습니다.
3. **TRACK TYPE**에서 PLUG-IN / SAMPLE KIT / MIDI / EMPTY를 고르고 Push / SELECT로 확정합니다.
4. 변경 완료 후 해당 트랙의 Stage로 돌아옵니다. Break Engine 교체는 실제 루프 파일을 선택하고 디코딩에 성공해야 확정됩니다.

타입 변경은 128개 패턴·현재 패턴·트랙 믹스·인서트를 유지합니다. 기존 노트를 새 악기의 음역/드럼 배치에 맞게 자동으로 바꾸지는 않습니다. 타입별 패드·모듈레이션 상태는 초기화될 수 있습니다.

**EMPTY는 악기만 비우고 패턴을 남깁니다. DELETE TRACK은 확인 후 악기와 모든 패턴을 지우는 별도 동작입니다.**

- **LOAD MPC KIT**: 프로젝트나 프로그램의 킷만 이 트랙에 불러옵니다. 패턴은 유지합니다.
- **SHIFT + Pad 16 → OPEN**: 프로젝트 전체를 엽니다. LOAD MPC KIT와 구분하세요.
- Sample Kit에서는 첫 항목이 LOAD SAMPLE, MIDI에서는 MIDI DEVICE, EMPTY에서는 ADD INSTRUMENT로 달라집니다.
- B1에 TRACK SETUP 대신 반복 속도가 보이면 NOTE REPEAT / ARP가 켜진 상태입니다. 해당 기능을 끄고 SHIFT·PAD BANK를 놓으면 원래 메뉴가 보입니다. 녹음 중 교체는 막히며 Freeze 트랙은 Unfreeze 확인이 나옵니다.

## 4. 프리셋 탐색과 사운드 편집

플러그인 Stage에서 B1은 **PRESETS ↔ EDIT**를 순환합니다. PRESETS의 인코더는 음색을 탐색/적용할 수 있습니다. Push로 연 프리셋 목록에서는 선택만 한 뒤 Push / B3 LOAD로 적용합니다. 두 화면의 동작을 구분하세요.

Stage EDIT에서는 인코더 또는 −/+로 세 파라미터씩 이동하고 K1–K3으로 조절합니다. 킷에서는 실제 패드를 눌러 편집 대상을 고르고 P01–P16과 ALL PADS 표시를 확인합니다. 엔진 원본 필터·ENV·LFO·FX는 이 사운드 목록의 이름과 단위로 구분합니다.

### User Sound / User Kit 저장과 다시 불러오기

**SAMPLE → B1 EDIT → 인코더 Push**로 사운드 도구를 엽니다. EDIT 화면의 PUSH 안내를 확인하세요. 외부 플러그인은 기존 동작을 유지하며, 이 도구는 Rhythmer 저장/킷 기능을 지원하는 엔진에서만 표시됩니다.

- **개별 엔진**은 SAVE 화면으로 바로 들어갑니다. **K1 Save slot**에서 1–64번 슬롯을 선택하고 **K2 Save Sound**를 오른쪽으로 돌립니다. **K3 Status**가 Ready인지 확인하세요. 같은 슬롯에 저장하면 그 슬롯을 덮어씁니다.
- **Rhythmer Kit**은 PAD SOURCE로 들어갑니다. 실제 패드 또는 **K1 Pad**로 대상을 고른 다음 **K2 Engine / K3 Sound**로 그 패드만 바꿉니다. P01–P16과 엔진·사운드 이름을 확인하세요.
- 킷 도구에서 **B3 SAVE**로 이동하고 K1 슬롯 → K2 Save Kit → Status Ready 순으로 전체 킷을 저장합니다. B3은 PAD SOURCE → SAVE → EDIT를 순환합니다. 도구 EDIT에서 B3 PAD SOURCE를 누르면 다시 패드 설정으로 갑니다.
- **B2 PRESETS / KIT PRESETS**를 열고 목록의 **User Sound 01… / User Kit 01…** 항목을 골라 Push / LOAD합니다. 인코더로 목록을 움직이는 것만으로는 로드되지 않습니다. 새 프로젝트에서도 같은 엔진 또는 Rhythmer Kit을 로드하면 저장한 항목을 다시 사용할 수 있습니다.
- **SHIFT + Push**로 돌아가면 악기 메인 화면의 원래 EDIT 위치를 복원합니다. 화면을 연 상태에서 다른 트랙을 고르면 새 트랙의 메인 화면으로 갑니다.

NOTE REPEAT / ARP가 켜져 소프트 버튼에 반복 속도가 보이면 해당 기능을 끄고 도구 조작을 계속하세요. 반복 속도 버튼의 기존 우선순위는 유지합니다.

저장 위치는 `Rhythmer/Presets/Sounds/<engine>/` 또는 `Rhythmer/Presets/Kits/`입니다. 이 프리셋 파일은 패턴·곡 구성·원본 샘플을 대신 저장하지 않습니다. 편곡은 프로젝트 SAVE로 별도 보관합니다. 원래 Melodee의 SHIFT + SAMPLE SELECT 사운드 파일은 이 플러그인 전체 상태 프리셋과 다른 형식입니다.

## 5. 패턴 고르기와 연주는 별도 화면입니다

- **SEQ → PATTERNS**: 패드가 패턴을 선택/실행합니다. K1 Length, K2 Q(그리드), K3 Swing을 설정합니다. 인코더 Push는 씬을 실행합니다.
- **SAMPLE → Stage**: 패드로 실제 악기를 연주합니다. 패턴 설정 후 여기로 돌아와 **SEQ RECORD → PLAY**로 녹음하세요. 다시 SEQ RECORD를 누르면 재생을 유지하며 녹음을 끝냅니다.
- **STEPS / ROLL / MOTION**: 스텝·노트·노브 동작 편집용입니다. 녹음하려는데 소리가 아니라 패턴 번호가 바뀌면 PATTERNS에 있는지 확인합니다.
- **SHIFT + Pad 16 → B1 SAVE**: 프로젝트·패턴·악기·킷 상태를 저장합니다. 사용한 원본 샘플도 카드에 보관합니다.

## 6. GEN과 뒤로 가기

PATTERNS에서 **SHIFT + B3 GEN**을 엽니다. SOUND + MIDI는 1–4 / 5–8 / 9–12 / 13–16 중 선택 그룹의 악기와 패턴을 새로 배정하므로 사용하지 않는 그룹이나 새 프로젝트에서 시작하세요. MIDI ONLY는 지정 범위의 노트만 생성합니다. 같은 시작/끝 트랙 번호로 한 트랙만 지정할 수 있습니다. 프로젝트의 키·스케일·템포는 공통입니다.

Acid 트랙에서는 ENGINE GEN → ACID GEN, Break 트랙에서는 ENGINE GEN → BREAK GEN을 사용합니다. Break 연주 화면은 **BREAK GEN → BRK PERF**로 엽니다. 소스 루프의 1–4마디 수를 먼저 지정하고 파일을 로드하세요. Acid의 Seed는 내부에서 관리하며 노브나 REPLAY SEED 메뉴가 없습니다.

- GEN 하위 페이지의 BACK / SHIFT + Push → GEN 메인 → PATTERNS.
- 일반 브라우저의 BACK은 폴더 위로 이동한 뒤 호출 화면으로 돌아갑니다. 선택을 취소하면 현재 소리를 유지합니다.
- TRACK TYPE의 BACK → TRACK SETUP → TRACKS.
- 확인창의 B1 CANCEL / SHIFT + Push는 취소합니다. 일반 Push / B3는 확정합니다.
- **SHIFT + − / +**: 지원되는 작업 Undo / Redo. 내부 플러그인의 모든 노브에 Undo가 적용된다는 뜻은 아닙니다.
- **STOP 더블탭(400ms 이내)**: 오디오를 끊습니다. 일반 STOP은 재생 정지, SHIFT + STOP은 All Notes Off입니다.

## 먼저 읽을 안내

- [웹 매뉴얼](https://jazzyrhythmer.github.io/mpc-sample/manual/#track-basics)
- [첫 패턴 튜토리얼](https://jazzyrhythmer.github.io/mpc-sample/manual/quickstart.html)
- [트랙 타입과 비동기 로드 상세](TRACK_WORKFLOW.md)

Melodee by Kerem Kiliç (Ellic Studio)의 기반 조작을 유지한 Rhythmer OS 안내입니다. 소스에서 확인한 동작과 실기기 검증은 구분하며, 실기기 조작·설치·복구 검증은 아직 소유자 베타 테스트 범위입니다.

## 플러그인 TRANSPORT와 EDIT 미세 조정

사운드 도구에서 SHIFT를 누르면 B3 TRANSPORT가 나타납니다. ON은 OS의 PLAY·STOP 상태를 해당 플러그인에 전달하고 OFF는 정지 상태로 전달합니다. 내부 시퀀서·아르페지에이터 등 이 정보를 사용하는 엔진에만 효과가 있으며, 트랙 음소거·노트 차단·곡 전체 재생 제어는 아닙니다.

원본 Melodee의 Stage EDIT 클릭은 K1–K3 선택을 순환하고 SHIFT + 인코더 회전의 미세 조정 대상을 정했습니다. 이번 지원 엔진은 클릭을 저장 도구 진입으로 바꿨습니다. 미세 조정은 K1–K3 중 대상 노브를 조작한 뒤 SHIFT + 인코더 회전으로 계속 사용할 수 있습니다. 외부 플러그인의 원래 클릭 동작은 유지합니다.
