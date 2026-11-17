# Your first groove with RHYTHMER OS. — 0.2.0 따라 하기

이 가이드는 **RHYTHMER OS 0.2.0**에서 4마디 드럼·베이스·코드 패턴을 만들고 저장합니다. Acid와 Break는 마지막 선택 과제입니다. 이전 영상은 이전 UI로 제작됐으므로 현재 버튼과 순서는 이 문서를 따르세요.

## 준비

전체 SD ZIP과 Rhythmer/Plugins를 설치하고 헤드폰·스피커 음량을 낮춥니다. 이번 연습에서는 외부 MIDI Clock을 분리해 Sample에서 템포를 설정합니다. 큰 인코더를 누르는 것은 클릭, 돌리는 것은 회전입니다. 뒤로는 **SHIFT + 인코더 클릭**입니다.

| 트랙 | 악기 / 프리셋 | 패턴 |
| --- | --- | --- |
| 1 | Rhythmer Kit / DRUM-X | 4마디, 패턴 1 |
| 2 | FMini-1 / MOOG BASS | 4마디, 패턴 1 |
| 3 | FM-106 / A11 Brass | 4마디, 패턴 1 |

## 1. 새 빈 프로젝트 만들기

1. SHIFT + Pad 16으로 Project를 엽니다.
2. B3 NEW → 확인창의 **B2 EMPTY**를 누릅니다.
3. PAD BANK를 누른 채 pad 1을 눌렀다 놓고, 헤더의 트랙 1을 확인합니다.

**확인:** 보존할 기존 곡이 없는 새 프로젝트입니다. NEW는 기존 곡에 악기를 추가하는 버튼이 아닙니다.

## 2. 트랙 1에 Rhythmer Kit 넣기

1. PAD FX + KNOB FX를 동시에 눌러 TRACKS로 갑니다.
2. B1 TRACK SETUP → TRACK TYPE → PLUG-IN을 선택합니다.
3. 플러그인 목록 맨 위 **Rhythmer Kit**을 선택하고 클릭합니다.
4. SAMPLE → B1을 눌러 PRESETS → 인코더 클릭으로 목록을 엽니다.
5. **DRUM-X**를 골라 클릭 / B3 LOAD합니다.
6. SAMPLE로 돌아가 bank A에서 **pad 1 킥 / pad 2 스네어 / pad 4 닫힌 하이햇**을 확인합니다.

모든 패드가 같은 소리의 음높이만 바꾼다면 Rhythmer Kit이 아닌 개별 악기를 로드했는지 확인합니다. 목록이 비어 있으면 전체 설치와 Rhythmer/Plugins부터 확인합니다.

## 3. 140 BPM과 4마디 설정

1. TAP TEMPO를 누른 채 인코더를 돌려 **140 BPM**으로 맞추고 놓습니다.
2. SEQ를 누릅니다. Roll 등이 열리면 B1으로 SEQUENCES를 거쳐 **PATTERNS**로 갑니다.
3. bank A의 pad 1을 눌러 패턴 1을 선택합니다.
4. 패턴 설정의 **K1 LENGTH = 4마디 / K2 Q = 1/16 / K3 SWING = 50%**로 맞춥니다.
5. **SAMPLE**로 돌아갑니다.

**확인:** 헤더는 트랙 1이고 패드가 드럼을 연주합니다. 길이는 현재 트랙의 패턴에 적용됩니다. 트랙 2와 3에서도 따로 설정합니다.

## 4. 드럼 녹음

1. 필요하면 SHIFT + Pad 4로 카운트인을 켭니다.
2. SEQ RECORD → PLAY를 누르고 카운트인을 기다립니다.
3. 각 마디를 1·2·3·4로 세며 **1과 3에 킥 pad 1**을 칩니다. 4마디 녹음합니다.
4. 루프가 돌아오면 **2와 4에 스네어 pad 2**를 추가합니다.
5. 다음 루프에서 **1-&-2-&-3-&-4-&**에 하이햇 pad 4를 추가합니다.
6. SEQ RECORD를 다시 눌러 녹음을 끕니다. STOP으로 재생을 멈춥니다.

**확인:** 패드를 누르지 않아도 드럼이 반복됩니다. 녹음 중 패턴 번호만 바뀌면 SAMPLE로 돌아오지 않은 것입니다. 지원되는 녹음 편집은 SHIFT + −로 되돌립니다.

## 5. 트랙 2 베이스

1. PAD BANK + pad 2로 트랙 2를 선택합니다. 필요하면 SAMPLE을 누릅니다.
2. 빈 트랙 카드에서 Plugin → **FMini-1**을 로드합니다.
3. PRESETS 목록에서 **MOOG BASS**를 선택하고 LOAD합니다.
4. SAMPLE을 길게 눌러 Keys를 열고 **K1 C / K2 Minor / K3 Scale**로 설정한 뒤 놓습니다.
5. PATTERNS의 패턴 1을 선택하고 **4마디 / 1/16 / 50%**로 맞춥니다.
6. SAMPLE에서 pad 1·3·5로 짧은 베이스 구절을 연습합니다. 음역은 −/+로 조절합니다.
7. SEQ RECORD → PLAY로 녹음하고, SEQ RECORD를 다시 눌러 녹음을 끕니다.

**확인:** 트랙 1 드럼은 계속 재생하고 지금 패드는 트랙 2의 베이스를 연주합니다. 패드는 프리셋이 아니라 음높이를 바꿉니다.

## 6. 트랙 3 코드

1. PAD BANK + pad 3 → Plugin → **FM-106**을 로드합니다.
2. PRESETS 목록에서 원본 **A11 Brass**를 선택하고 LOAD합니다.
3. Keys의 C / Minor / Scale을 확인하고 패턴 1을 **4마디 / 1/16 / 50%**로 설정합니다.
4. SAMPLE에서 **pad 1·3·5를 동시에** 눌러 마이너 코드를 연주합니다.
5. SEQ RECORD → PLAY로 짧은 코드 연주를 녹음하고 녹음을 끕니다.

**확인:** 프리셋명은 A11 Brass입니다. 이 가이드에서는 이를 패드 음색이나 별도 제작 프리셋이라고 설명하지 않습니다.

## 7. 음량과 킷 편집

1. PAD FX + KNOB FX로 TRACKS를 엽니다.
2. 트랙 1·2·3을 선택하며 **K1 LEVEL**로 밸런스를 맞춥니다. K2 PAN, K3 SEND A는 필요할 때만 조절합니다.
3. 전체 드럼 필터는 트랙 1 → SAMPLE → PRESETS의 **KIT CUTOFF / KIT RESONANCE**입니다.
4. 킥만 줄이려면 트랙 1 → SAMPLE → EDIT → pad 1 → 첫 행 **K1 P01 Volume**입니다.

**확인:** KIT 필터는 전체 킷, P01 Volume은 pad 1에만 적용됩니다. PERFORM의 ECHO/SPACE는 엔진 필터나 센드 A/B와 다른 효과입니다.

## 8. 프로젝트 저장

1. STOP 후 약 3초간 조작하지 않고 자동 저장을 기다립니다.
2. SHIFT + Pad 16 → **B1 SAVE AS**를 누릅니다.
3. FIRST GROOVE 020 같은 이름을 입력하고 **B3 SAVE**합니다.
4. SAVED를 확인합니다. 이후 Project → B2 OPEN → 이름 선택 → 클릭으로 다시 엽니다.

User Sound/Kit이 아니라 **프로젝트**를 저장해야 세 트랙의 노트와 구성이 함께 보존됩니다. 원본 샘플과 SD 카드도 별도로 백업합니다.

## 선택 과제: 트랙 4 Acid

1. 트랙 4 → Plugin → Acid Engine → SQUELCH를 고릅니다.
2. 패턴 1과 원하는 길이를 지정합니다.
3. SEQ → B1 PATTERNS → SHIFT + B3 GEN → **ACID GEN**으로 갑니다.
4. Density 70 / Accent 40 / Slide 25로 시작하고 두 번째 설정 페이지의 AUTO MUTATE는 OFF로 둡니다.
5. GENERATE ACID → 클릭 / APPLY, PLAY로 비교합니다.

**여기서 트랙 1–4에 GENERATE SONG을 실행하지 마세요.** SOUND + MIDI는 지금 만든 드럼·베이스·코드 악기까지 교체할 수 있습니다. ACID GEN 또는 GENERATE T4는 해당 트랙만 대상으로 합니다. Back은 GEN 메인, 다시 Back은 PATTERNS입니다.

## 선택 과제: 트랙 5 Break

1. 사용할 권한이 있고 **실제 2마디**임을 아는 루프를 Samples에 넣습니다.
2. 트랙 5 → Plugin → Break Engine을 선택합니다.
3. 브라우저 **LOAD A / K1 LOAD BARS = 2**를 확인한 후 파일을 클릭합니다.
4. 준비가 끝나면 BREAK GEN이 유지됩니다. 비어 있던 패턴에 Straight가 준비됩니다.
5. PLAY로 듣고 BRK PERF를 엽니다. 1 CHOPS는 슬라이스, 2 ROLLS는 누른 동안 반복 명령입니다.
6. 재진입은 트랙 5 → SEQ → B1 PATTERNS → SHIFT + B3 GEN → BREAK GEN입니다.

Break의 2마디 패턴은 다른 트랙의 4마디 패턴 동안 반복될 수 있습니다. 반·두 배 속도라면 소스 마디 수를 먼저 확인합니다. Grain은 2페이지 pad 3 STRETCH를 누른 채 5페이지로 이동해야 효과를 확인할 수 있습니다. LOOP VARIATIONS는 LOOP 모드·재생·PATTERN HOLD OFF가 필요합니다.

## 멈췄을 때 돌아갈 경로

| 상황 | 조작 |
| --- | --- |
| 소리 화면을 못 찾음 | SAMPLE |
| 패드가 패턴 번호만 바꿈 | SEQ를 놓고 SAMPLE |
| 다른 트랙을 편집 중 | PAD BANK + 대상 패드, 헤더 확인 |
| 신스 노브 대신 Save Slot 표시 | SHIFT + 인코더 클릭으로 악기 EDIT 복귀 |
| Break 설정을 잃어버림 | PATTERNS → SHIFT + B3 GEN → BREAK GEN |
| 잔향·음이 끊기지 않음 | 400ms 이내 STOP 두 번 |

[전체 매뉴얼](USER_MANUAL_KO_DRAFT.md) · [필수 조작과 구조](GETTING_STARTED_KO.md) · [English First Groove](FIRST_GROOVE_020_EN.md)
