# Break Manipulator와 Acid Generator

## Break Engine

플러그인 목록에서 **Break Engine**을 선택하고 루프를 불러온다. 루프 브라우저의 K1 LOAD BARS에서 실제 길이를 1–4마디로 지정한 뒤 파일을 선택하고 Push한다. 재로드는 SEQ / PATTERNS → SHIFT+B3 GEN → BREAK GEN → BROWSE SAMPLE로 진입한다. 기존처럼 16개 슬라이스와 템포에 맞는 패턴을 준비한다. 원본 녹음 파일은 제공하지 않는다. Break DSP는 원본처럼 모노이며 스테레오 루프는 합쳐서 처리한다.

이제 EDIT 또는 BREAK 메뉴의 **BRK PERF**에서 전용 연주 화면을 사용한다. 인코더를 돌리거나 누르면 다음 페이지로 이동하며, 위에 현재 페이지와 전체 페이지 수가 표시된다.

| 페이지 | 패드와 노브 |
|---|---|
| 1 CHOPS | 패드 1–16으로 슬라이스 연주. Orbit, DJ Filter, Pattern Hold(배포본 표기 LOOP HOLD) |
| 2 ROLLS | 패드를 누르는 동안 Repeat·Up·Down·Shrink·Build·Stretch·Echo 연주 |
| 3 SOURCE A / B | 패드 1은 A, 패드 2는 B, 패드 3은 Return. Play Mode, Pattern Hold(배포본 표기 LOOP HOLD), DJ Filter |
| 4 LOOP VARIATIONS | Variation, Drift, Tail Fill. Variation·Drift는 LOOP 모드 + Pattern Hold OFF에서 내부 마디 경계부터 적용 |
| 5 GRAIN / STRETCH | 그레인 길이, 이음새 크로스페이드, 2–4배 Stretch |
| 6 TRACK MIX | 트랙 음량, 팬, Send A |

ROLLS의 패드 배치는 아래쪽부터 다음과 같다.

| 패드 | 기능 |
|---|---|
| 1–4 | 1/4 Repeat, Build, Stretch, Echo |
| 5–8 | 1/8 Repeat, Down, Up, Shrink |
| 9–12 | 1/16 Repeat, Down, Up, Shrink |
| 13–16 | 1/32 Repeat, Down, Up, Shrink |

SOURCE 페이지의 **LOAD B**로 두 번째 루프를 선택한다. A와 B는 같은 마디 수로 해석하며, 파일의 실제 프레임 길이가 달라도 각각 같은 구절에 맞춰 재생한다. 원본 FM-1의 고정 길이 A/B 뱅크를 사용자가 직접 불러오는 루프로 대체한 구조다.

**CHOP**은 시퀀스에 지정한 슬라이스를 재생한다. **LOOP**는 시퀀스의 게이트가 열려 있는 동안 원본의 내부 브레이크 패턴·Variation·Drift를 사용한다. 기존 GEN 슬라이스 패턴은 CHOP으로 시작한다.

**Record + Play** 상태에서 ROLLS와 SOURCE 패드를 누르면 연주 명령과 누른 길이를 현재 시퀀스에 기록한다. A/B와 Return도 기록하며, 재생할 때 같은 명령을 실행한다. 연주한 명령을 SEQ의 선택 레인으로 표시하며, STEP EDIT와 ROLL에도 음 이름 대신 명령 이름이 나온다. 스텝을 누른 채 인코더를 돌리면 해당 스텝의 Chop·Roll·A/B·Return 명령을 바꾼다. Return은 Variation·Drift를 원래 상태로 돌린다. 기존 시퀀스를 새 패턴으로 덮어쓰지 않는다.

아래 **GEN**은 BREAK 생성 메뉴로 돌아간다. 그 메뉴의 BACK은 GEN 메인 메뉴로 이동한다. 정지 버튼을 두 번 누르는 전체 오디오 중단 동작도 유지한다.

## Break 조작 안내 · hotfix.2

### 현재 배포본에서 다시 진입

Break 트랙 선택 → **SEQ / PATTERNS → SHIFT + B3 GEN → BREAK GEN → BRK PERF**. BRK PERF의 **B1 GEN**은 BREAK GEN으로 돌아간다. BREAK GEN의 B1 BACK 또는 SHIFT + 엔코더는 GEN 메인으로, 한 번 더 실행하면 창을 닫는다. 별도의 “Breaker Setup” 메뉴는 없다. hotfix.1까지는 A 루프 로드 시 STRAIGHT 생성 후 Stage로 이동해 메뉴가 잠시 나타났다가 사라질 수 있었다. hotfix.2에서는 BREAK GEN을 유지한다.

### 작동 조건을 듣고 확인

- 기본 CHOP은 시퀀스의 슬라이스를 재생한다. LOOP HOLD는 오디오 유지가 아닌 **내부 패턴 재생성 중지**이므로 CHOP에서 효과가 들리지 않는다. 트랙 Freeze와도 다르다.
- PLAY → 3 SOURCE A/B에서 K1 LOOP, K2 Hold OFF → 4 LOOP VARIATIONS에서 Variation/Drift를 올린다. 내부 마디가 바뀌는 소리를 듣고 3페이지 Hold ON으로 패턴을 유지한다. Variation/Drift가 0이면 ON/OFF 차이가 적을 수 있다. Hold가 라이브 롤과 모든 조작을 멈추는 것은 아니다.
- GRAIN/STRETCH는 스트레치된 히트에 적용된다. PLAY 중 2 ROLLS에서 **패드 3 STRETCH를 계속 누른 채** 인코더를 돌려 5페이지로 이동하고 Grain/Splice/Slow를 조절한다. 패드를 놓으면 해제된다. STRETCH를 시퀀스에 녹음한 뒤 조절해도 된다. LOOP HOLD는 필요하지 않다. Slow는 해당 히트의 2–4배 스트레치이며 전체 템포가 아니다.
- B는 3페이지 LOAD B로 별도 파일을 넣어야 한다. 6 TRACK MIX는 트랙 음량·팬·Send A이며 패턴 생성 페이지가 아니다.
- RETURN은 Variation/Drift를 리셋한다. 패턴 삭제나 Hold 해제가 아니다. 누른 연주 패드는 놓아서 해제한다.

### 0.4.0-beta.3 · Break workflow hotfix (hotfix.2)

A 루프 로드 완료 후 BREAK GEN을 유지하고 **BRK PERF** 행을 선택한다. Push 또는 B3 OPEN으로 연주 화면을 연다. 로딩 중에는 B1 CANCEL 또는 SHIFT+Push로 트랙 배정을 취소할 수 있다. 파일 디코딩 캐시는 남아도 취소한 요청은 트랙을 바꾸지 않는다. 로딩 중 다른 생성·탐색 조작은 잠시 막고 K1–K3 카드는 비운다.

사용자가 다른 트랙/페이지로 이동했거나 GEN을 닫은 경우 로드 완료가 화면을 되돌리지 않는다. 소스 B도 같은 화면 소유권 규칙을 따른다. PATTERN HOLD는 이전 배포본의 LOOP HOLD와 같은 저장 값·기능이며 이름만 명확히 했다. DSP·패턴 생성 알고리즘·프로젝트 형식은 바꾸지 않았다. 실기기 조작·장시간 재생·설치 복구는 베타 검증 범위다.

## Acid Generator

Acid Engine 트랙에서 SEQ → PATTERNS → Shift+B3 GEN → **ACID GEN**을 선택한다. B2 SETTINGS로 두 설정 페이지를 번갈아 보며 제목의 1 OF 2 / 2 OF 2에서 현재 위치를 확인한다. 인코더로 GENERATE ACID 또는 MUTATE ACID를 선택하고 Push / B3 APPLY로 실행한다. 재진입은 첫 설정 페이지에서 시작한다.

| 설정 페이지 | 노브 |
|---|---|
| 1 / 2 | Density 0–100%, Accent 0–100%, Slide 0–100% |
| 2 / 2 | Octaves 1–3, Base Octave 0–4, Auto Mutate OFF 또는 1–16마디 |

기본값은 FM-1과 같은 Density 70, Accent 40, Slide 25, Octaves 2, Base Octave 1이다. 조성과 스케일은 프로젝트의 현재 설정을 따른다. 생성과 변형에 같은 원본 TB-3PO 함수를 사용한다.

**GENERATE ACID**는 원본 NEW처럼 새 Seed로 새 라인을 만든다. **MUTATE ACID**는 현재 라인을 변형하며 해당 트랙의 32비트 난수 흐름을 이어간다. 시드는 내부에서만 관리하며 노브·숫자 표시·Replay 메뉴는 제공하지 않는다. 생성·변형 과정의 전체 32비트 상태와 Undo/Redo·프로젝트 저장·복원은 그대로 유지한다. 다른 트랙이나 4트랙 GEN의 Seed는 공유하지 않는다.

Tie는 다음 스텝에서 다시 발음하는 노트로 바꾸지 않고, 기존 노트가 이어지는 길이로 변환한다. 패턴 경계를 넘는 Tie도 보존한다. 현재 SEQ 그리드의 1–64스텝을 사용한다. Accent는 원본의 127/96 벨로시티를 따르고 Slide는 시퀀스의 Slide 명령에 연결한다. Undo/Redo는 패턴과 그 트랙의 Seed를 함께 복구한다.

Auto Mutate는 재생 중 지정한 마디 간격마다 변형한다. 녹음·송 재생 중에는 자동 생성하지 않는다. BACK은 GEN 메인 메뉴로 돌아간다.

이 문서는 베타 기능의 조작 안내다. 실제 MPC Sample의 패드 응답, 장시간 재생, 소리 및 녹음 감각은 실기기에서 검증한다.
