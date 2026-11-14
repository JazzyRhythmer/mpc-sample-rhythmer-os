# Rhythmer OS 사용 설명서

웹사이트 게재용 초안 · 대상 버전 0.4.0-beta.1

Rhythmer OS는 MPC Sample에서 샘플, 신스, 드럼킷과 시퀀서를 사용하는 음악 제작 환경입니다. 개발자는 **jazzy rhythmer**입니다. 현재 베타는 오프라인 검증을 마쳤으며 실기기 조작·청취·성능 검증은 진행 전입니다. 아래 버튼 설명은 현재 구현을 기준으로 작성했습니다.

## 1. 소리 선택하기

### Sample Kit — 샘플과 MPC 킷

기존 샘플러 방식입니다. Samples에서 WAV를 패드에 넣거나, 지원되는 MPC `.xpm`·`.xty` 드럼 프로그램을 선택하고 Push로 킷을 로드합니다. MPC Sample `.xpj` 프로젝트에서는 `Load kit (no patterns)`로 킷만 가져올 수도 있습니다. 샘플과 관련 데이터 폴더를 함께 보관하세요. 모든 MPC 효과와 설정이 완전히 재현되는 것은 아닙니다.

### 개별 엔진 — 한 트랙에 한 음색

플러그인 목록에서 엔진을 선택합니다. Keys에서 Chromatic 또는 Scale과 원하는 루트·스케일을 설정합니다. 패드는 선택한 한 음색을 음높이에 맞춰 연주합니다. 드럼 엔진도 개별 엔진으로 선택하면 하나의 드럼 음색을 연주하며, C4를 기준으로 Tape 피치가 적용됩니다. 이 경우 길이와 기존 잔향도 함께 변합니다.

Stage/Keys에서 Push로 엔진 메인을 열고, B2 PRESETS에서 인코더로 음색을 고른 뒤 Push로 로드합니다. 현재 프리셋 이름은 메인과 편집 상단에 표시됩니다. 메인에서 B3 EDIT SOUND 또는 Push로 상세 편집에 들어가고, 인코더 또는 −/+로 기능별 페이지를 이동하고 Push로 A/B 줄을 선택해 K1–K3으로 조절합니다. B3 PAGES에서 원하는 기능으로 바로 이동합니다.

### Rhythmer Kit — 여러 엔진을 하나의 드럼킷으로

플러그인 목록 맨 위의 **Rhythmer Kit**을 선택합니다. PRESETS에서 36개 킷을 바꿀 수 있습니다. 모든 킷의 1–16번 패드가 채워져 있습니다. Hortator MD 추가 6종과 패드별 원본 사운드는 HORTATOR_KITS_KO.md에 정리했습니다.

메인의 SOURCE 페이지는 `Pad / Engine / Sound`입니다.

1. 패드를 누르거나 Pad를 돌려 편집할 패드를 선택합니다.
2. Engine으로 그 패드의 엔진을 선택합니다.
3. Sound로 해당 엔진의 음색을 선택합니다.
4. B3 EDIT PAD 또는 Push로 선택 패드의 상세 편집에 들어갑니다.

PRESETS는 킷 전체를, Engine / Sound는 선택한 패드만 바꿉니다. 독립적으로 교체·편집한 패드는 추가 엔진 인스턴스를 사용할 수 있으므로 무거운 엔진을 여러 패드에 사용할 때는 실기기 부하를 확인하세요.

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

MAIN의 SAVE 페이지에서 Save slot을 1–64 중 선택하고 Save Sound 또는 Save Kit을 실행합니다. Status가 Ready가 될 때까지 기다립니다. 저장한 항목은 PRESETS의 User Sound / User Kit으로 나타납니다. 같은 슬롯에 저장하면 이전 항목을 교체합니다.

프로젝트 저장은 패턴과 플러그인·킷 상태를 보존합니다. 사용자 프리셋은 SD의 `Rhythmer/Presets`에 저장됩니다. 사용한 샘플, Plugins와 관련 데이터 폴더도 함께 보관하세요.

## 6. 자주 묻는 질문

**GEN을 실행해도 소리가 없어요.** MIDI ONLY에서는 음색이 자동 배정되지 않습니다. 트랙에 악기가 로드됐는지, 그룹 내 역할과 맞는지, 현재 패턴과 믹서 음량이 올바른지 확인하세요.

**킥 대신 다른 소리가 나요.** Sample Kit의 첫 여덟 패드 배치를 확인하세요. 개별 엔진은 선택한 한 음색만 연주합니다. 여러 드럼 음색을 한 트랙에서 쓰려면 Rhythmer Kit 또는 Sample Kit을 선택하세요.

**Break가 박자에서 밀려요.** 입력한 Source Bars가 원본 4/4 루프 길이와 맞는지 확인하세요. 16개 조각은 원본 전체의 균등 구간입니다. STRAIGHT로 원래 순서를 재생해 정렬을 점검합니다.

**이전 베타의 드럼 프로젝트가 다르게 들려요.** beta.1에서 개별 드럼 플러그인에 여러 노트를 사용한 프로젝트는 beta.2에서 한 음색의 피치로 해석됩니다. 원본 프로젝트를 보관하고 Rhythmer Kit으로 다시 구성한 뒤 새 이름으로 저장하세요.

## 크레딧과 채널

Developed by **jazzy rhythmer** · [Instagram](https://www.instagram.com/jazzyrhythmer/) · [YouTube](https://www.youtube.com/@jazzyrhythmer)

Based on **Melodee by Kerem Kiliç (Ellic Studio)** and sample-base, AGPL-3.0-only. 각 엔진의 원저작권·라이선스·출처 고지는 배포물에 유지됩니다.

Beta.4: [sound fixes and preset coverage](SOUND_FIXES_BETA4.md). Stop twice within 400 ms cuts all audio; the next note or Play resumes.

## Beta.4 악기 선택과 편집

- 플러그인 목록 최상단의 Rhythmer Kit은 여러 드럼 사운드를 패드별로 배치한다. 개별 엔진은 한 음색을 크로매틱/스케일로 연주한다.
- Acid Engine은 Hortator ACID 전용 뷰다. Break Engine을 선택하면 샘플 브라우저가 열리며, 루프와 원본 길이 1–4바를 지정하면 16찹과 템포 싱크를 준비한다.
- 개별 드럼 엔진을 새로 고르면 패드 시작 옥타브를 C4(기본 C키에서 MIDI 60)로 맞춘다. 구형 플러그인 트랙의 Drums/기본 옥타브 2 조합은 Scale/C4로 보정하며, 명시적으로 설정한 크로매틱/스케일 옥타브는 유지한다.
- Hortator는 킷별 음색 48개와 원본 합성 모델 44개를 제공한다. ACID, MD TRX/EFM 등을 Sound/Presets에서 고를 수 있다.
- 킷 편집 파라미터의 P01/P02는 실제 선택한 패드 번호다. Model 값은 숫자 대신 실제 모델명으로 보인다. 전체 프로그램을 바꾸는 원본의 중복 노브는 숨기고 Sound/Presets 선택을 사용한다.
- Stop을 400ms 이내에 두 번 누르면 모든 오디오를 끊는다. 새 노트 또는 Play로 다시 소리를 낼 수 있다.

## Beta.4 GEN 개편

8개 역할을 8트랙에 나누던 자동 생성 방식은 종료했습니다. [GEN_WORKFLOW.md](GEN_WORKFLOW.md)의 4트랙 원본 GEN이 현재 동작입니다. T1 Rhythmer Kit, T2–4 악기·프리셋·MIDI를 원본 FM-1 시드 로직으로 만듭니다. MIDI ONLY 범위 1–16과 한 트랙 지정은 유지합니다. Break/Acid 전용 화면은 해당 엔진에서만 표시하고 Back은 GEN 메인으로 돌아옵니다. Acid Engine은 Hortator ACID입니다.


### 킷 편집 범위와 트랙 묶음 선택

Rhythmer Kit의 EDIT PAD는 누른 패드의 소리만 편집합니다. B3 PAGES는 기능별 페이지 목록입니다. 모든 패드의 레벨·팬·Send A는 MAIN MIX에서 조절합니다. 킷 공용 믹서 값은 프로젝트에 저장됩니다. `Save Kit`에는 패드별 엔진·사운드 디자인이 저장됩니다. 소리 이름 뒤 `*`는 값을 수정했다는 표시입니다.

GEN SETUP에서 `T1–T4`, `T5–T8`, `T9–T12`, `T13–T16` 행을 고르고 SELECT를 누릅니다. 첫 트랙은 킷, 나머지 셋은 악기를 받습니다. MIDI ONLY의 FROM/TO는 별도 범위이며 같은 번호를 지정하면 한 트랙에만 생성됩니다.

### 엔진 메인 화면

플러그인을 열면 공통 메인 화면이 먼저 표시됩니다. 원본 엔진명과 현재 프리셋, Rhythmer Kit의 선택 패드를 확인할 수 있습니다. 휠 또는 −/+로 공통 조절 페이지를 넘깁니다.

1. MIX: 트랙 Level / Pan / Send A
2. SENDS: 트랙 Send B / C / D
3. SOURCE: 선택 패드·엔진·사운드 또는 개별 엔진의 사운드 선택
4. SAVE: 저장 슬롯 / Save Kit 또는 Save Sound / 상태

B2는 프리셋 목록, B3 또는 Push는 EDIT PAD / EDIT SOUND입니다. 편집에서 B1 MAIN 또는 Back을 누르면 메인으로 돌아옵니다. Rhythmer Kit의 세부 편집은 누른 패드를 따라갑니다. 일반 악기는 모든 패드가 같은 사운드를 크로매틱 또는 스케일로 연주합니다. 별도로 설치한 일반 VST는 공통 믹스·센드 두 페이지와 원래 파라미터 편집을 사용합니다.

흑백 픽셀 애니메이션은 기존 트랙 음량과 눌린 음에 반응합니다. 킷의 막대는 입력 반응 그래픽이며 패드별 독립 음량 미터를 뜻하지 않습니다. 소리가 멈추면 움직임도 멈춥니다. 공통 믹서 값은 프로젝트에, 사운드 디자인은 Save Sound / Save Kit에 저장됩니다.


### 엔진 MAIN 화면

엔진을 열면 MAIN에서 시작합니다. 인코더 또는 −/+로 MIX → SENDS → SOURCE → SAVE를 넘깁니다. B3/Push로 소리 편집에 들어가고 B1/Back으로 MAIN에 돌아옵니다. B2 PRESETS는 개별 엔진의 소리 또는 Rhythmer Kit 전체를 바꿉니다. 킷의 개별 패드는 MAIN → SOURCE에서 Pad / Engine / Sound로 교체합니다. 뱅크와 패드 번호는 함께 표시됩니다.

Default는 호스트의 초기 상태이며 원본 Init과 구분됩니다. Dexed는 같은 음색이 반복된 슬롯을 숨겨 고유 FM 음색 8개와 Default를 제공합니다. 킷별·엔진별 프리셋 대조 및 현재 검증 범위는 FINAL_UI_AUDIT.md와 VERIFICATION.md를 참고하세요.

프리셋 목록에서는 인코더로 고른 뒤 Push 또는 B3 LOAD로 불러옵니다. Break에 아직 루프가 없으면 Browse Sample부터 선택됩니다. Aphex 드론 4종은 긴 발음 전 지연을 제거해 패드·짧은 시퀀스에서도 발음되도록 조정했습니다.

단일 소리의 Pitch mode에서 Key Pitch는 악기의 음높이 제어, Pitch + Length는 음높이와 재생 길이가 함께 바뀌는 타악기 재생을 뜻합니다. C4 / MIDI 60은 타악기 원래 속도의 기준입니다.

### 기능별 편집 페이지와 현재 위치

편집 상단의 `FILTER 2/3 · 08/24`는 Filter의 두 번째 페이지이며 전체 24페이지 중 8번째라는 뜻입니다. 전체 위치 막대도 함께 표시됩니다. 한 페이지의 최대 여섯 파라미터는 A/B 두 줄이며, 밝은 줄의 세 값을 아래 큰 노브 카드에서 조정합니다. 인코더·−/+는 페이지, Push는 A/B 줄, B3 PAGES는 페이지 바로 가기입니다. 목록에서 Back은 선택을 취소하고, 편집에서 Back은 MAIN으로 돌아옵니다.

킷에서는 패드 번호·해당 엔진·사운드가 함께 표시됩니다. 다른 패드를 누르면 해당 패드의 항목으로 바뀝니다. 빈 패드에서는 MAIN SOURCE에서 엔진·사운드를 넣으라는 안내가 나옵니다. B2 KIT PRESETS는 킷 전체를 바꾸므로, 한 패드의 소리만 바꾸려면 MAIN SOURCE를 사용합니다. 프리셋 목록의 K1은 위치 선택이며 소리 파라미터를 편집하지 않습니다.

## Break Manipulator와 Acid의 상세 조작

새 Break 연주 화면, 명령 녹음·편집, LOOP/CHOP과 Acid의 세 설정 페이지·Seed·Tie는 [Break/Acid 사용 안내](BREAK_ACID_GUIDE_KO.md)를 참고한다.


## 0.4.0: Melodee 0.2.0 기반 변경

- SEQ 홈은 **PATTERNS**입니다. 트랙별 128개 패턴을 A–H 뱅크에서 선택합니다. Step 편집은 **STEP EDIT**를 사용합니다.
- **Shift+B3 GEN**으로 생성 화면을 엽니다. 생성 화면에서 패드는 현재 악기를 연주하며 패턴을 바꾸지 않습니다. 하위 화면의 BACK은 GEN으로, GEN의 BACK은 PATTERNS로 돌아갑니다.
- 플러그인 편집 화면의 **Shift+B3 TRANSPORT**는 엔진 내부 시퀀서에 Play/Stop을 전달할지 정합니다. EDIT/PAGES 버튼은 기존처럼 사용합니다.
- Erase+노브는 Rhythmer 악기의 해당 파라미터를 불러온 원본 프리셋 값으로 초기화합니다. Shift+인코더의 미세 조정은 선택형 값에서 한 항목씩 이동합니다.
- 새 플러그인은 **Rhythmer/Plugins**에 넣습니다. 기존 최상위 Plugins 경로도 읽습니다. VST2/3 외에 호환되는 Linux ARM64 LV2/CLAP 플러그인을 지원하며, 외부 플러그인은 Rhythmer Kit 내부 엔진으로 자동 추가되지 않습니다.
- 원본 Sample Kit의 패드별 Send A–D를 지원합니다. Rhythmer Kit은 기존 트랙 공용 Send를 사용합니다.
- Freeze/Deep Freeze, USB 화면 미러링, 파일 전송, 오디오 형식 확장은 새 기반의 기능입니다. USB 연결 후 **http://rhythmer.local**에서 기기 페이지와 파일을 엽니다. 실제 기기의 USB·네트워크·성능 검증은 별도입니다.
- 자동 업데이트는 Rhythmer OS 서명 파일만 수락합니다. 0.3 베타에서 처음 넘어올 때는 전체 SD ZIP을 수동 복사합니다. UPDATE ZIP은 이후 호환되는 Rhythmer 0.4 빌드의 실행 파일만 교체하고 프로젝트·플러그인을 보존합니다.

Deep Freeze로 메모리에서 내려간 악기는 편집 화면에 DEEP FROZEN으로 표시합니다. UNFREEZE를 선택하면 원래 사운드를 다시 불러온 후 편집합니다. Freeze 중에는 프리셋·TRANSPORT 변경도 먼저 Unfreeze를 요청합니다. 폴더형 프리셋에서 K1 JUMP는 현재 폴더의 목록 범위 안에서 이동합니다.


## Rhythmer 자체 프리셋

Prophet은 원본 Init 1개와 jazzy rhythmer가 제작한 새 사운드 15개를 제공합니다. Elixir는 원본 Initkit과 자체 킷 Dry Circuit, Warm Machine, Bright Logic, Soft Pulse를 제공합니다. Elixir의 개별 악기 목록에서는 킷별 7개 보이스를 선택하고, Rhythmer Kit에서는 패드 1–16을 채운 전체 킷을 선택합니다. 네 자체 킷의 킥은 짧은 피치 어택과 드라이브, 충분한 저역 몸통을 갖도록 조정했습니다.

Sequential의 외부 Prophet 뱅크와 Erica/Hrtl 외부 Elixir 뱅크는 배포본에 포함하지 않습니다. 이들의 재배포 허가 범위가 확인되지 않았기 때문이며, 개인 사용 금지 판정을 뜻하지 않습니다. 원본 Init과 자체 프리셋은 구분해 표시합니다.
