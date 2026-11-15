# Rhythmer OS 사용 설명서

> **처음 사용하는 분:** [트랙 선택·진입·타입 변경부터 읽기](GETTING_STARTED_KO.md). SAMPLE은 Stage로, PAD FX + KNOB FX는 TRACKS로 갑니다. PATTERNS의 패드는 패턴 실행용이며, 연주 녹음은 SAMPLE로 Stage에 돌아와 진행합니다. 별도 PAD SOURCE / SAVE 편집창 진입은 현재 베타의 확인 과제로 표시합니다.

웹사이트 게재용 초안 · 대상 버전 0.4.0-beta.3

Rhythmer OS는 MPC Sample에서 샘플, 신스, 드럼킷과 시퀀서를 사용하는 음악 제작 환경입니다. 개발자는 **jazzy rhythmer**입니다. 실기기 조작·청취·성능은 별도 베타 검증 대상입니다. 아래 버튼 설명은 현재 구현을 기준으로 작성했습니다.

## 1. 소리 선택하기

### Sample Kit — 샘플과 MPC 킷

기존 샘플러 방식입니다. Samples에서 WAV·MP3·FLAC·Ogg Vorbis·AIFF를 패드에 넣거나, 지원되는 MPC `.xpm`·`.xty` 드럼 프로그램을 선택하고 Push로 킷을 로드합니다. MPC Sample `.xpj` 프로젝트에서는 `Load kit (no patterns)`로 킷만 가져올 수도 있습니다. 샘플과 관련 데이터 폴더를 함께 보관하세요. 모든 MPC 효과와 설정이 완전히 재현되는 것은 아닙니다.

### 악기·트랙 타입 바꾸기

PAD BANK + 번호 패드로 트랙을 선택합니다. PAD FX + KNOB FX를 함께 눌러 TRACKS를 열고 B1 **TRACK SETUP**를 누릅니다. 헤더의 트랙 번호를 확인하세요.

- **CHANGE PLUG-IN**: 현재 플러그인을 다른 악기로 교체합니다. 플러그인 프리셋 목록에서도 B2 **PLUG-INS**로 바로 교체할 수 있습니다.
- Sample Kit의 **LOAD SAMPLE**은 선택 패드에 소리를 넣고, MIDI의 **MIDI DEVICE**는 포트·채널 설정을 엽니다.
- **TRACK TYPE**: PLUG-IN / SAMPLE KIT / MIDI / EMPTY를 고릅니다. EMPTY는 악기만 비우고 패턴은 남깁니다. 타입 변경은 128개 패턴·현재 패턴·트랙 믹스·인서트를 유지합니다. 음표나 음역을 새 악기에 맞게 자동 변환하지는 않습니다.
- **LOAD MPC KIT**: 카드 또는 내부 드라이브의 프로젝트·드럼 프로그램에서 킷만 불러옵니다. 이 화면에서는 전체 프로젝트를 여는 대신 킷만 적용합니다.
- **DELETE TRACK**: 확인 후 소리와 모든 패턴을 지웁니다. 취소가 기본 선택입니다. Shift + Minus로 복원하고 Shift + Plus로 다시 적용합니다.

TRACK SETUP는 TRACKS의 B1 버튼으로만 엽니다. TRACKS에서 인코더를 누르면 악기가 있는 트랙은 기존 메인 화면으로, EMPTY로 비운 트랙은 PLUG-IN / KIT / MIDI 선택 화면으로 들어갑니다. Trim·Layers의 전용 Shift 조작과 Freeze 조작은 기존대로 유지합니다. 프리셋·플러그인·샘플 로드 화면에서 다른 트랙을 선택하면 그 트랙의 메인 화면으로 이동합니다. 악기를 확정하면 해당 트랙의 첫 화면으로 돌아오며, 취소하면 기존 악기가 유지됩니다. 버스·마스터 편집 화면은 공용 화면이므로 트랙을 바꿔도 유지합니다.

### 개별 엔진 — 한 트랙에 한 음색

플러그인 목록에서 엔진을 선택합니다. Keys에서 Chromatic 또는 Scale과 원하는 루트·스케일을 설정합니다. 패드는 선택한 한 음색을 음높이에 맞춰 연주합니다. 드럼 엔진도 개별 엔진으로 선택하면 하나의 드럼 음색을 연주하며, C4를 기준으로 Tape 피치가 적용됩니다. 이 경우 길이와 기존 잔향도 함께 변합니다.

Stage의 B1 첫 화면은 **PRESETS**입니다. 엔진명·현재 프리셋·입력에 반응하는 그래픽을 함께 보여 줍니다. 인코더로 프리셋을 탐색하고 Push로 전체 목록을 엽니다. 목록에서는 인코더 또는 K1으로 선택하고 Push / B3 LOAD로 적용하며, B1 BACK으로 돌아갑니다. 프리셋이 없는 외부 플러그인은 같은 첫 화면이 PLUG-IN으로 표시됩니다.

Stage의 B1을 다시 눌러 **EDIT**로 이동합니다. 인코더 또는 −/+로 세 파라미터씩 이동하고 K1–K3으로 강조된 세 줄을 조절합니다. 화면에 앞뒤 제어까지 최대 여섯 줄을 표시합니다. 별도 Edit 화면도 같은 사운드 목록을 사용합니다. 원본 제어는 음색·필터·ENV·LFO·변조·FX 맥락을 이름 앞에 표시합니다. `EDIT 5/30`은 현재 조절할 세 값이 전체 30묶음 중 다섯 번째라는 뜻입니다. SOURCE와 SAVE 관리는 사운드 제어와 분리돼 있습니다.

PRESETS 하단은 해당 엔진의 실제 주 필터·레조넌스와 대표 음색 제어입니다. EDIT의 같은 값과 연동됩니다. Dexed·DRUM-X·Plaits·CS-1·MONO2K는 추가된 출력 전체 필터의 OUTPUT CUTOFF / OUTPUT RESONANCE를 표시합니다. 원본의 모델별 음색 제어와 CS-1 Brightness, MONO2K Filter Base/Width는 EDIT에 그대로 남습니다. 추가 필터와 원본 필터는 별개이며 이름으로 구분합니다.

**B2 PERFORM → ARP → CHORD**로 넘깁니다. PERFORM의 **DJ FILTER / ECHO / SPACE**는 OS가 각 플러그인 트랙에 제공하는 연주 효과입니다. DJ FILTER는 출력에 거는 LP/HP 스윕이며 엔진 컷오프와 다릅니다. ECHO는 템포 동기 딜레이, SPACE는 리버브의 입력 송신량입니다. 0%로 내려도 이미 발생한 잔향은 남고, STOP 더블탭은 내부·공통 효과의 잔향도 끊습니다. 엔진 내부 FX, 공용 SEND A–D, 트랙 인서트와 각각 별도이며 동시에 켜면 처리가 겹칩니다. 설정은 트랙/프로젝트에 저장되고, 프리셋 변경 시 자동으로 초기화되지 않습니다. 첫 화면의 PERFORM ON은 저장된 공통 연주 효과량이 켜져 있음을 알립니다. **B3 MIX → SENDS → FX**는 기존 위치입니다.

### Rhythmer Kit — 여러 엔진을 하나의 드럼킷으로

플러그인 목록 맨 위의 **Rhythmer Kit**을 선택합니다. PRESETS에서 36개 킷을 바꿀 수 있습니다. 모든 킷의 1–16번 패드가 채워져 있습니다. Hortator MD 추가 6종과 패드별 원본 사운드는 HORTATOR_KITS_KO.md에 정리했습니다.

첫 화면의 **KIT CUTOFF / KIT RESONANCE**는 Rhythmer Kit 엔진 내부의 전체 필터이며 모든 패드에 적용됩니다. K3은 트랙 음량입니다. EDIT 첫 묶음의 **KIT FILTER TYPE**에서 LP / BP / HP를 고릅니다. 컷오프·레조넌스는 첫 화면과 동일한 값입니다. 전체 필터는 트랙 인서트 슬롯을 쓰지 않으며 킷 프리셋과 프로젝트에 저장됩니다. 공장 킷의 기본값은 원래 소리를 그대로 통과시킵니다.

그 뒤의 **P01 … / P11 …** 항목은 선택 패드의 원본 엔진 제어입니다. KIT 항목은 전체 킷, P번호 항목은 해당 패드이므로 구분하여 조정하세요. 다른 패드를 눌러도 전체 필터 값은 유지됩니다. SAVE KIT에는 전체 필터와 패드별 소리가 함께 저장됩니다.

아래는 별도 전체 편집창의 제어 설명입니다. 현재 Stage에서 이 창으로 들어가는 경로는 [초기 안내의 베타 한계](GETTING_STARTED_KO.md)를 확인하세요. 별도 Edit 화면의 B3 **PAD SOURCE**를 열면 `Pad / Engine / Sound`가 나옵니다. B3은 SOURCE → SAVE → EDIT 순서로 전환합니다.

1. 패드를 누르거나 Pad를 돌려 편집할 패드를 선택합니다.
2. Engine으로 그 패드의 엔진을 선택합니다.
3. Sound로 해당 엔진의 음색을 선택합니다.
4. B3으로 EDIT에 돌아와 선택 패드의 실제 소리를 편집합니다. 목록과 K1–K3 카드의 P11 같은 표시는 실제 선택한 패드 번호입니다.

PRESETS는 킷 전체를, Engine / Sound는 선택한 패드만 바꿉니다. 독립적으로 교체·편집한 패드는 추가 엔진 인스턴스를 사용할 수 있으므로 무거운 엔진을 여러 패드에 사용할 때는 실기기 부하를 확인하세요.

### Sample Kit / Break / MIDI 입력

기존 Sample Kit과 Break의 첫 **SOUND** 화면은 샘플러의 전체 필터·레조넌스·킷 음량을 조절합니다. B1을 넘기면 TRIM / LAYERS / TUNE / AMP ENV로 이어집니다. 직접 Trim을 여는 단축 동작은 그대로 Trim으로 들어갑니다. 전체 타입은 B3의 KIT FILT, 개별 패드 필터는 FILTER에서 설정하며 새 인서트를 자동 추가하지 않습니다.

MIDI 출력에는 오디오 필터를 붙이지 않습니다. 입력은 독립 IN 엔진이 아니라 Input Config의 INPUT FX 또는 MIDI 트랙의 Audio In / Monitor를 사용합니다. 모니터링 오디오는 해당 트랙의 기존 인서트·센드 경로를 사용하며 이번 변경으로 필터를 자동 추가하지 않습니다.

## 2. GEN으로 패턴 만들기

SEQ → PATTERNS → Shift+B3 GEN으로 엽니다. K1 Energy, K2 Explore / Random / 장르, K3 Seed를 조절하고 인코더로 작업을 선택한 다음 Push 또는 APPLY를 누릅니다.

- GENERATE SONG: GEN SETUP에서 선택한 4트랙 묶음에 생성합니다. 첫 트랙에는 Rhythmer Kit, 나머지 세 트랙에는 원본 FM-1 GEN의 악기 역할·프리셋·MIDI를 배정합니다. 다른 묶음의 트랙과 패턴은 유지합니다. MONK는 자동 배정에서 제외합니다. 키·스케일·템포는 기존처럼 프로젝트 공통 설정에 반영됩니다.
- MUTATE SONG: 선택한 4트랙 묶음의 패턴을 변형하며 악기는 유지합니다.
- GENERATE T번호 / MUTATE T번호: 화면에 표시된 현재 트랙만 작업하고 악기를 유지합니다.
- GEN SETUP: K3 GEN MODE를 SOUND + MIDI로 두면 K1 SONG GROUP에서 **1–4 / 5–8 / 9–12 / 13–16**을 선택합니다. 예를 들어 9–12를 고르면 T9가 킷, T10–12가 악기입니다. MIDI ONLY로 바꾸면 K1 MIDI FROM / K2 MIDI TO로 자유 범위(1–16)를 설정합니다. 시작과 끝을 같게 하면 한 트랙만 지정됩니다. MIDI ONLY에서는 첫 두 항목이 GENERATE MIDI / MUTATE MIDI로 표시됩니다. 두 모드의 대상 설정은 별도로 기억하며 프로젝트에 저장됩니다.
- ENGINE GEN: 선택 트랙이 Break Engine이면 BREAK GEN, Acid Engine이면 ACID GEN이 표시됩니다. 다른 엔진에서는 기존 VARIATIONS를 엽니다.

설정을 바꾸지 않고 GENERATE SONG을 다시 누르면 원본처럼 최근 8개 랜덤 시드를 피해서 새 Seed를 선택합니다. 이전 Seed를 수동으로 넣으면 해당 조건의 생성 결과를 재현합니다. Mutate는 기존 패턴도 입력으로 사용합니다. 한 번의 Undo로 패턴·악기·프리셋·전체 생성 시의 키와 템포를 함께 복원합니다. 하위 생성 화면의 BACK은 GEN 메인으로, 메인의 BACK은 PATTERNS로 돌아갑니다.

B2는 다음 화면 이름(VARY / SETUP / GEN)을 표시하며 GEN → VARIATIONS → GEN SETUP → GEN 순서로 이동합니다. 닫았다가 다시 Shift+B3 GEN을 누르면 GEN 첫 항목에서 시작합니다. 하단 OPEN은 하위 화면 진입, APPLY는 실행, SELECT는 선택한 트랙 묶음 적용, DONE은 MIDI 범위 설정에서 GEN 복귀를 뜻합니다. 상단의 NEW SOUNDS / KEEP SOUNDS / KEEP SOUND로 악기 교체 여부를 구분합니다.

Acid Engine은 Hortator ACID의 단일 음색 뷰입니다. ACID GEN에서는 원본 TB-3PO의 스케일·악센트·슬라이드·타이 및 Mutate를 사용합니다.

## 3. BREAK로 루프 재구성하기

BREAK는 사용자가 준비한 샘플 조각을 시퀀싱하는 기능입니다. 기본 브레이크 음원은 포함되지 않습니다.

### 루프 준비

1. 플러그인 목록에서 Break Engine을 선택하면 루프 브라우저가 열립니다.
2. 브라우저의 K1 **LOAD BARS**로 원본 4/4 루프의 길이 **1·2·3·4마디**를 지정합니다.
3. 오디오 루프를 선택하고 Push를 누릅니다. Break GEN으로 돌아오며 로드 중에는 진행 메시지를 표시합니다. 브라우저 최상위의 B1 GEN은 선택을 취소하고 Break GEN으로 돌아갑니다.
4. 로드가 끝나면 선택 뱅크 1–16번 패드에 루프 전체의 16개 구간이 자동 배치됩니다. 기존 해당 패드와 현재 패턴은 교체됩니다.
5. 원본 길이로 계산한 템포와 기존 Follow/Beats 기능으로 프로젝트 템포에 맞추고 Straight 패턴을 만듭니다. Undo로 되돌릴 수 있습니다.

16개 구간은 원본 전체를 균등 분할한 것입니다. 특히 3마디는 고정 8분음표 슬라이스가 아닙니다. 트랜지언트를 자동 탐지하는 기능으로 표시하지 않습니다. 수동 Chop도 계속 사용할 수 있습니다.

### 실행 순서

Break 트랙에서 SEQ → PATTERNS → Shift+B3 GEN → **BREAK GEN**으로 들어갑니다. K2 Genre, K3 Seed를 설정하고 인코더로 작업을 고른 뒤 Push 또는 APPLY로 실행합니다. LOAD BARS는 다음 샘플 로드의 마디 수입니다. 이미 로드한 루프를 다르게 해석하려면 마디 수를 지정하고 BROWSE SAMPLE로 같은 파일을 다시 선택하세요. Random/Mutate 강도는 메인 GEN의 ENERGY를 사용합니다.

| 작업 | 용도 |
|---|---|
| STRAIGHT | 지정한 원본 마디 길이의 조각 순서를 현재 패턴 길이에 맞춰 반복 |
| GENRE CHOPS | 선택한 장르에 맞는 조각 배치와 필인 생성 |
| RANDOM CHOPS | 첫 다운비트를 유지하며 랜덤 재배치; Amount가 높으면 재트리거 증가 |
| MUTATE CHOPS | 기존 패턴의 오프비트 조각 변경; 4분음표 기준점과 자동화 유지 |
| TAIL FILL | 패턴 끝 4/8스텝에 조각과 2배/4배 래칫으로 필인 구성 |

추천 순서: **STRAIGHT로 정렬 확인 → GENRE CHOPS → MUTATE CHOPS → 필요할 때 TAIL FILL**. Mutate는 빈 패턴을 채우는 작업이 아니므로 먼저 Straight나 Generate 계열로 패턴을 만드세요. 래칫은 같은 조각을 빠르게 반복하는 기능입니다.

BREAK는 입력한 마디 수와 파일 길이로 원본 BPM을 계산하고 균등 슬라이스를 배치합니다. 마디 수를 자동 인식하거나 트랜지언트를 분석하지는 않습니다. 잘못된 슬라이스 순서, 원본 길이 또는 템포 설정은 먼저 샘플러에서 조정해야 합니다. Follow의 Beats/Tones/Tape, Tune/Warp, # Beats 등 기존 기능을 사용할 수 있습니다.

## 4. VARY와 기존 생성 기능

같은 생성 화면에서 B2 **VARY**를 누르면 기존 variation 작업을 사용할 수 있습니다. 기존 Euclid 기능도 유지됩니다. GEN은 원본 FM-1의 장르 기반 생성, BREAK는 준비한 16개 샘플 조각의 재구성에 사용합니다.

## 5. 저장과 다시 열기

Edit 화면의 B3 SAVE에서 Save slot을 1–64 중 선택하고 Save Sound 또는 Save Kit을 실행합니다. Status가 Ready가 될 때까지 기다립니다. 저장한 항목은 PRESETS의 User Sound / User Kit으로 나타납니다. 같은 슬롯에 저장하면 이전 항목을 교체합니다.

프로젝트 저장은 패턴과 플러그인·킷 상태를 보존합니다. 사용자 프리셋은 SD의 `Rhythmer/Presets`에 저장됩니다. 사용한 샘플, Plugins와 관련 데이터 폴더도 함께 보관하세요.

## 6. 자주 묻는 질문

**GEN을 실행해도 소리가 없어요.** MIDI ONLY에서는 음색이 자동 배정되지 않습니다. 트랙에 악기가 로드됐는지, 그룹 내 역할과 맞는지, 현재 패턴과 믹서 음량이 올바른지 확인하세요.

**킥 대신 다른 소리가 나요.** Sample Kit의 패드 번호와 각 패드에 배정된 샘플을 확인하세요. 개별 엔진은 선택한 한 음색만 연주합니다. 여러 드럼 음색을 한 트랙에서 쓰려면 Rhythmer Kit 또는 Sample Kit을 선택하세요.

**Break가 박자에서 밀려요.** 입력한 Source Bars가 원본 4/4 루프 길이와 맞는지 확인하세요. 16개 조각은 원본 전체의 균등 구간입니다. STRAIGHT로 원래 순서를 재생해 정렬을 점검합니다.


## 크레딧과 채널

Developed by **jazzy rhythmer** · [Instagram](https://www.instagram.com/jazzyrhythmer/) · [YouTube](https://www.youtube.com/@jazzyrhythmer)

Based on **Melodee by Kerem Kiliç (Ellic Studio)** and sample-base, AGPL-3.0-only. 각 엔진의 원저작권·라이선스·출처 고지는 배포물에 유지됩니다.


## 빈 트랙에서 시작하기

프로젝트를 열면 원래의 선택 트랙을 유지합니다. 빈 트랙은 **PLUG-IN / SAMPLE KIT / MIDI** 선택 화면을 보여 줍니다. 인코더를 돌려 종류를 선택하고 Push로 엽니다. 플러그인은 목록에서 악기를 선택할 때 실제 트랙이 만들어집니다. 킷은 빈 패드, 카드의 샘플, 입력 녹음을 선택할 수 있고 MIDI는 출력 포트를 선택할 수 있습니다. B2 SAMPLE KIT / B3 MIDI는 빠른 진입입니다. PAD BANK를 누른 채 패드로 트랙을 선택합니다.

## 저장과 편집 범위

개별 엔진의 B3은 SAVE / EDIT를 전환합니다. Rhythmer Kit은 SOURCE / SAVE / EDIT를 전환합니다. Save Sound / Save Kit은 사운드 디자인과 패드 구성을 저장하고, 프로젝트 저장은 패턴·트랙 믹서·FX·모듈레이션도 함께 보존합니다. 프로젝트를 다시 열면 선택한 프리셋 이름도 복원합니다. ERASE + 해당 노브는 불러온 사운드의 그 값을 초기화합니다. 일반 플러그인 내부 노브의 편집은 프로젝트 공통 Undo 대상이 아니며, GEN·Acid·Break 작업의 Undo/Redo와 구분해야 합니다. STOP을 400 ms 이내에 두 번 누르면 모든 오디오를 끊으며 다음 노트 또는 PLAY로 다시 연주합니다.

## LFO와 MOD

EDIT의 LFO·변조 슬롯은 원본 엔진 자체 기능입니다. 엔진마다 제공하는 제어가 다릅니다. `LFO Settings`는 같은 LFO의 Sync·Trigger·Polarity 설정이며 LFO가 하나 더 생긴다는 뜻이 아닙니다. Sophie 등 내부 LFO가 없는 원본에는 임의의 내부 LFO를 추가해 표시하지 않습니다.

프로젝트 공통 MOD에서는 마지막으로 돌린 **Motion 지원 제어**를 ADD로 연결합니다. PERFORM의 DJ FILTER / ECHO / SPACE, 트랙 믹서·FX 등을 LFO·Envelope Follower·Macro로 움직일 수 있습니다. PRESETS의 엔진 필터와 Rhythmer Kit 내부 전체 필터를 포함한 플러그인 내부 임의 파라미터는 원본 Melodee의 Motion 타깃에 포함되지 않습니다. 내부 노브를 돌린 뒤 ADD하면 이전의 다른 타깃을 잘못 추가하지 않고 안내를 표시합니다. 엔진 내부 LFO 또는 공통 FX의 MOD를 사용하세요. 변조 범위는 해당 노브에 표시된 범위 안에서 적용됩니다.

## 패드 색상과 흑백 화면

Sample Kit의 COLOUR는 **실제 패드 조명 색상**을 지정합니다. 화면은 흑백을 유지하며 색상 이름·패드 번호·선택 테두리로 구분합니다. MPC 킷에서 읽은 RGB 값과 실제 조명, 프로젝트 저장 값은 유지합니다. 이 기능은 native Sample Kit의 기능입니다. Rhythmer Kit은 플러그인 트랙이며 자체 패드 엔진·사운드 편집을 사용합니다.

## Break Manipulator와 Acid 상세

[Break/Acid 사용 안내](BREAK_ACID_GUIDE_KO.md)에 BRK PERF, 19개 연주 명령·녹음·재생·A/B/Return, Acid의 두 설정 페이지·내부 난수 상태·Tie와 진입·복귀 경로를 정리했습니다. 루프가 없는 Break 트랙의 Stage에서 Push로 다시 샘플을 고를 수 있습니다.

## Melodee 0.2.0 기반 기능

- SEQ 홈은 PATTERNS입니다. 트랙마다 128개 패턴을 A–H 뱅크에서 선택합니다. Step 편집은 STEP EDIT를 사용합니다.
- Shift+B3 GEN의 하위 화면 BACK은 GEN으로, GEN의 BACK은 PATTERNS로 돌아갑니다.
- 플러그인 Edit의 Shift+B3 TRANSPORT는 플러그인에 PLAY·STOP을 전달할지 설정합니다.
- 새 플러그인은 `Rhythmer/Plugins`에 넣습니다. 호환 Linux ARM64 VST2·VST3·CLAP·LV2를 지원합니다. 외부 플러그인이 Rhythmer Kit의 내부 소스로 자동 추가되지는 않습니다.
- Native Sample Kit은 패드별 SEND A–D를 사용하며 Rhythmer Kit은 트랙 공용 SEND를 사용합니다.
- Freeze는 패턴을 오디오로 출력해 재생하고 Deep Freeze는 플러그인을 메모리에서도 내립니다. DEEP FROZEN 트랙은 UNFREEZE 후 편집합니다.
- USB-C 연결 후 `http://rhythmer.local`에서 Files·업데이트·플러그인 업로드·매뉴얼을 엽니다. 기기 USB·네트워크·성능은 실기기 검증 대상입니다.
- Settings → SCREEN의 Screen mirror는 USB 카메라로 화면을 보냅니다. 기준 릴리스의 선택 해상도는 320×240, 640×480, 1280×720, 1280×960, 프레임률은 30/60 fps입니다. 실제 달성률은 기기·연결에 따라 확인해야 합니다.
- 초기 전체 설치는 SD ZIP을 수동 복사합니다. 이후 UPDATE ZIP은 서명된 Rhythmer OS 파일만 받으며 실행 파일을 교체하고 프로젝트·플러그인을 보존합니다.

## Rhythmer 자체 프리셋

Prophet은 원본 Init 1개와 jazzy rhythmer가 제작한 새 사운드 15개를 제공합니다. Elixir는 원본 Initkit과 자체 킷 Dry Circuit, Warm Machine, Bright Logic, Soft Pulse를 제공합니다. Elixir의 개별 악기 목록에서는 킷별 7개 보이스를 선택하고, Rhythmer Kit에서는 패드 1–16을 채운 전체 킷을 선택합니다. 네 자체 킷의 킥은 짧은 피치 어택과 드라이브, 충분한 저역 몸통을 갖도록 조정했습니다.

Sequential의 외부 Prophet 뱅크와 Erica/Hrtl 외부 Elixir 뱅크는 배포본에 포함하지 않습니다. 이들의 재배포 허가 범위가 확인되지 않았기 때문이며, 개인 사용 금지 판정을 뜻하지 않습니다. 원본 Init과 자체 프리셋은 구분해 표시합니다.


### 추가 출력 필터 — Dexed·DRUM-X·Plaits·CS-1·MONO2K

이 다섯 엔진의 PRESETS 첫 두 노브는 **OUTPUT CUTOFF / OUTPUT RESONANCE**입니다. EDIT의 첫 세 줄에서 같은 컷오프·레조넌스와 **OUTPUT FILTER TYPE (LP/BP/HP)**을 조절합니다. OUTPUT FILTER는 이 제어 묶음의 이름이며 별도의 메뉴 버튼이 아닙니다. 세 번째 노브에는 원본의 대표 음색 파라미터가 남습니다.

추가 필터는 엔진의 원래 합성·내장 이펙트 뒤, OS PERFORM·트랙 인서트·센드 앞에서 출력 전체를 처리합니다. 인서트 슬롯이나 버스는 사용하지 않습니다. 기본값은 Cutoff 100%, Resonance 0%, LP이며 이 조합에서는 원본 오디오를 그대로 통과합니다. 원본 프리셋을 선택하면 이 중립값으로 시작하고, Save Sound와 프로젝트 저장에는 추가 필터 설정도 포함됩니다. 원본 필터·ENV·LFO·FX 설정은 변경하지 않습니다. Rhythmer Kit 안에서는 패드 원본의 필터와 별도로 킷 자체의 KIT FILTER가 전체 합산 출력을 처리합니다.

킷 패드 EDIT 제목은 `P11 / CS-1 / 사운드명`처럼 선택 패드·실제 엔진·소리를 표시합니다. 킷 전체 필터 행은 `킷 이름 / ALL PADS`를 표시합니다. 패드 소스를 교체해도 킷 프리셋 이름을 현재 소스 엔진으로 오해하지 않도록 구분합니다.
