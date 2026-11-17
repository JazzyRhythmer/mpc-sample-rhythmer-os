# Rhythmer OS 0.2.0 — 실기기 검증용 베타

**첫 설치에는 전체 SD.zip을 사용하세요.** 앱·플러그인·킷·프리셋 카탈로그가 함께 포함됩니다. 전원을 끄고 카드 전체를 백업한 뒤 아래 설치 안내를 따르세요. `UPDATE.zip`은 앱 전용 파일이며 첫 설치용이 아닙니다.

개발자: **jazzy rhythmer**. Instagram: https://www.instagram.com/jazzyrhythmer/ · YouTube: https://www.youtube.com/@jazzyrhythmer

빌드·오프라인 검증 후 사용자가 실기기에서 테스트하는 베타다.  이 안내는 소유자 베타 설치용이며, 기기 설치는 소유자가 직접 진행한다. 설치 전 프로젝트·샘플·카드 내용을 백업한다.

## 파일 구조

- `autorun/`: 기존 Melodee SD 부팅·체크섬·RAM 실행·stock 복구 구조. 내부 실행 폴더와 app 선택자는 `rhythmer`를 사용한다.
- `Samples/Rhythmer/Hortator CC0 Percussion/`: CC0 퍼커션 샘플 5개.
- `RHYTHMER_OS.json`: 구현 범위와 검증 한계.
- `SOURCE_LOCK.json`, `RELEASES_LOCK.json`, `THIRD_PARTY_NOTICES.md`, 각 폴더의 라이선스·SOURCE 기록.
- `SHA256SUMS`: 개발판 파일별 체크섬.

이 개발판은 자동으로 SD카드나 기기에 복사하지 않았다. 실제 사용을 시작할 때 기존 카드 자료를 백업하고, MPC Sample AC50의 firmware 1.3.0.12 조건을 확인해야 한다. 기존 SD launcher는 다른 firmware에서 실행을 거부한다. ZIP의 최상위 `autorun`과 `Rhythmer`가 카드의 최상위 폴더가 되는 기존 SD 실행 구조를 사용한다. stock MPC 앱 패치나 VST enhancement 패치를 실행하지 않는다.

## 버전과 파일 선택

앱 버전은 **RHYTHMER OS 0.2.0**이며 기반은 Melodee Sample 0.3.0입니다. 전체 설치에는 `RHYTHMER-OS-0.2.0-SD.zip`과 같은 이름의 `.sha256` 파일을 사용합니다. 

## 첫 조작 안내

처음 사용하는 분은 [GETTING_STARTED_KO.md](GETTING_STARTED_KO.md)의 트랙 선택·진입·타입 변경·녹음·프리셋 저장 순서를 먼저 확인하세요. SAMPLE은 선택 트랙의 악기 메인 화면이며, PAD FX + KNOB FX는 TRACKS입니다.

## 악기와 Rhythmer Kit

빈 트랙에서는 인코더로 Drum / Keygroup / Plugin 카드를 선택하고 Push합니다. Settings의 FEATURES를 FULL로 설정하면 MIDI / Audio도 표시됩니다. Drum은 카드 샘플·빈 킷·입력 녹음을, MIDI는 출력 포트를 이어서 고릅니다. B1 BACK 또는 SHIFT + Push는 소스 선택에서 타입 선택으로, 타입 선택에서 이전 트랙 화면으로 돌아갑니다. 모든 트랙이 비어 있어도 TRACKS로 나올 수 있습니다.

새 프로젝트는 첫 트랙에 기기의 팩토리 킷을 불러옵니다. NEW 확인창의 B2 EMPTY를 선택하면 빈 킷으로 시작합니다. 악기를 추가하려면 PAD BANK + 패드로 다른 빈 트랙을 선택하세요.

플러그인 목록 맨 위의 Rhythmer Kit을 선택하면 PRESETS에서 36개 킷을 바꿀 수 있다. 모든 킷의 1–16번 패드가 채워져 있다. EDIT에서 B3 PAD SOURCE를 열면 K1 Pad / K2 Engine / K3 Sound로 선택한 패드만 바꾼다. B3 SAVE는 저장 화면, 그다음 B3 EDIT는 사운드 편집 화면으로 이동한다. 실제 패드를 눌러 편집 대상을 선택할 수도 있다. 킷에 따라 B–D bank에 추가 음색이 있다. Hortator MD 추가 6종의 원본 사운드 구성은 HORTATOR_KITS_KO.md를 참고한다.

개별 엔진은 한 트랙에서 한 음색을 연주한다. Keys의 Chromatic 또는 Scale을 선택한다. 멜로디 엔진의 원래 MIDI/폴리포니를 유지하며, 드럼 단일 음색은 C4 기준 Tape 피치로 연주한다. 드럼의 길이와 기존 꼬리도 함께 피치 변환된다.

Stage PRESETS에서 엔진·프리셋 이름과 애니메이션을 보고, B1 EDIT에서 소리를 편집한다. EDIT에서 인코더 Push를 누르면 Rhythmer Kit은 PAD SOURCE, 개별 엔진은 SAVE 도구로 들어간다. 화면의 PUSH 안내를 따른다. B2 PRESETS에서 인코더로 선택하고 Push/LOAD로 로드한다. 현재 프리셋 이름은 EDIT 상단에도 표시된다. 인코더/−/+로 3개씩 이동하며, 6줄 목록 중 K1–K3 표시가 있는 줄을 해당 노브로 조절한다. EDIT 현재/전체 표시로 위치를 확인한다. 일반 악기는 B3 SAVE에서 Save slot과 Save Sound로, 킷은 PAD SOURCE 다음 SAVE에서 Save slot과 Save Kit으로 저장한다. 저장된 항목은 PRESETS의 User Sound / User Kit에 추가된다. 동일 슬롯에 저장하면 해당 슬롯을 교체한다.

프로젝트 저장은 전체 킷의 패드별 엔진·음색·편집 파라미터를 보존한다. 사용자 프리셋은 Rhythmer/Presets에 저장한다. 설치 시 autorun과 Rhythmer/Plugins/RHYTHMER - Rhythmer Kit을 포함해 패키지 전체를 복사한다. 자세한 단계는 SOUND_KIT_GUIDE.md를 참고한다.

## Generator와 사용자 Break

SEQ → B1 PATTERNS → Shift+B3 GEN에서 GEN을 엽니다. GEN SETUP에서 K3를 SOUND + MIDI로 두고 K1 SONG GROUP으로 1–4 / 5–8 / 9–12 / 13–16을 선택합니다. FM-1 Rhythmer 원본 GEN을 사용해 선택 묶음의 첫 트랙은 Rhythmer Kit, 나머지 세 트랙은 장르에 맞는 악기·프리셋과 MIDI로 생성합니다. 다른 묶음의 트랙과 패턴은 유지하고 MONK는 자동 선택에서 제외합니다. 프로젝트 공통 키·스케일·템포는 기존처럼 함께 적용됩니다. Explore / Random / 장르, Energy, Seed를 조절할 수 있습니다. MIDI ONLY에서는 별도의 MIDI FROM / TO로 1–16 트랙 범위 또는 한 트랙만 지정합니다. Generate T번호는 현재 선택한 한 트랙의 악기를 유지합니다. Break GEN과 Acid GEN은 해당 엔진에서만 표시하며 Back은 GEN 메인으로 돌아옵니다. 대상 설정의 프로젝트 저장·복원과 Undo/Redo를 유지합니다.

BREAK에서는 K1 LOAD BARS에 원본 4/4 루프 길이 1–4마디를 지정하고 BROWSE SAMPLE에서 오디오를 선택한다. 로드 후 원본 전체를 16개 균등 구간으로 나누어 선택 뱅크에 배치하고, 원본 BPM 계산과 기존 Follow/Beats를 통해 템포 싱크한다. 현재 패턴은 원본 마디 수의 Straight 패턴으로 교체된다. 3마디도 전체를 16등분하며, 트랜지언트 자동 검출은 아니다. Genre Chops / Random / Mutate / Tail Fill과 수동 Chop도 유지한다. 자세한 조작법은 GEN_WORKFLOW.md와 USER_MANUAL_KO_DRAFT.md를 참고한다. 내장 Break 음원은 없다.

## 저장과 종료

프로젝트는 재생·녹음·프린트가 멈춘 상태에서 마지막 조작 후 약 3초 뒤 자동 저장됩니다. SHIFT + Pad 16의 프로젝트 화면에서 B1 SAVE AS로 새 이름을 지정해 저장할 수 있습니다. 가져온 MPC 프로젝트는 SAVE AS를 먼저 실행합니다. 악기 상태와 샘플 참조를 보존하며, 사용한 원본 샘플은 SD에 남겨야 합니다. 기존 Exit의 MPC APP/stock 복구 흐름을 유지한다. 실제 카드 제거·전원 차단·기기 복구 동작은 기기 검증 단계에서 확인한다.

## 현재 한계

Linux ARM64 빌드와 offline host 검증은 기기 검증과 다르다. 많은 플러그인을 동시에 켜는 성능은 실측 전이다. 외부 플러그인의 내부 보이스를 CPU Guard가 직접 줄여주지는 않는다. Open MPC wrapper의 기존 DSP mutex 등 실시간 동작도 실기기 부하·지연 검토 대상이다.

필수 크레딧: Based on Melodee by Kerem Kiliç (Ellic Studio), AGPL-3.0-only, and sample-base. Original notices and source attribution are retained.

GEN의 트랙 범위·악기 자동 배정·MIDI 전용 모드와 1–4마디 Break 자동 준비는 [GEN_WORKFLOW.md](GEN_WORKFLOW.md)를 참고하세요.

[Sound and preset verification](VERIFICATION.md). Stop twice within 400 ms cuts all audio; the next note or Play resumes.


## 설치와 기본 앱 복구

프로젝트·샘플·카드 전체를 백업하고 MPC Sample의 전원을 끕니다. 전체 SD ZIP을 풀어 `autorun/`, `Rhythmer/`, `Samples/`가 카드 최상위에 오도록 복사합니다. 카드를 안전하게 추출하고 기기에 넣은 뒤 전원을 켜 SD launcher 안내를 따릅니다. 플러그인 저장 위치는 `Rhythmer/Plugins`입니다.

기본 MPC 앱으로 돌아가려면 전원을 끄고 카드를 분리한 뒤 `autorun/` 폴더를 카드 밖으로 옮깁니다. 프로젝트·샘플은 백업을 유지하세요.

## 다운로드 선택과 안내

첫 설치에는 **SD.zip** 전체 패키지를 사용한다. **UPDATE.zip**은 호환 Rhythmer 설치의 실행 앱만 업데이트하며 플러그인이나 킷을 포함하지 않는다. SOURCE / MOVE-SOURCE / SUPPORT-SOURCE는 재빌드를 위한 소스 배포물로 SD 설치 파일이 아니다. 배포 페이지의 버전과 `.sha256` 값을 다운로드 파일과 대조한다.

이 프로젝트는 AKAI Professional 또는 inMusic이 승인하거나 지원하는 공식 펌웨어가 아니다. MPC Sample 명칭과 로고의 권리는 각 권리자에게 있다. 소프트웨어는 각 라이선스에 따라 무보증으로 제공된다. 테스트 범위·알려진 한계는 VERIFICATION.md를 확인한다. 제조사 펌웨어를 덮어쓰는 설치가 아니라 SD launcher를 사용하는 방식이다.


프리셋 저장: K1 Save slot 1–64 → K2 Save Sound / Save Kit → K3 Status Ready. B2 PRESETS / KIT PRESETS에서 User Sound / User Kit을 선택하고 Push / LOAD로 복원한다. 같은 슬롯은 덮어쓴다. SHIFT + Push는 원래 Stage EDIT 위치로 돌아간다. 프로젝트 SAVE는 음색 프리셋과 별개로 패턴·편곡을 저장한다.
