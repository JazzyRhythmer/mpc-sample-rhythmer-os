# Rhythmer OS 0.2.0 — 실기기 검증용 베타

beta.2 → beta.3은 플러그인과 카탈로그도 바뀌므로 전체 SD.zip을 사용한다. UPDATE.zip은 앱만 바꾸며 이 수정 전체를 설치하지 않는다. SD_CARD_GUIDE.md의 전원 종료·백업·전체 파일 복사 절차를 따른다.


개발자: **jazzy rhythmer**. Instagram: https://www.instagram.com/jazzyrhythmer/ · YouTube: https://www.youtube.com/@jazzyrhythmer

빌드·오프라인 검증 후 사용자가 실기기에서 테스트하는 베타다. 기기 설치·물리 조작·청취·latency는 현재 미검증으로 표시한다. 이 안내는 공개 베타 설치용이며, 기기 설치는 소유자가 직접 진행한다. 설치 전 프로젝트·샘플·카드 내용을 백업한다.

## 파일 구조

- `autorun/`: 기존 Melodee SD 부팅·체크섬·RAM 실행·stock 복구 구조. 내부 실행 폴더와 app 선택자는 `rhythmer`를 사용한다.
- `Samples/Rhythmer/Hortator CC0 Percussion/`: CC0 퍼커션 샘플 5개.
- `RHYTHMER_OS.json`: 구현 범위와 검증 한계.
- `SOURCE_LOCK.json`, `RELEASES_LOCK.json`, `THIRD_PARTY_NOTICES.md`, 각 폴더의 라이선스·SOURCE 기록.
- `SHA256SUMS`: 개발판 파일별 체크섬.

이 개발판은 자동으로 SD카드나 기기에 복사하지 않았다. 실제 사용을 시작할 때 기존 카드 자료를 백업하고, MPC Sample AC50의 firmware 1.3.0.12 조건을 확인해야 한다. 기존 SD launcher는 다른 firmware에서 실행을 거부한다. ZIP의 최상위 `autorun`과 `Rhythmer`가 카드의 최상위 폴더가 되는 기존 SD 실행 구조를 사용한다. stock MPC 앱 패치나 VST enhancement 패치를 실행하지 않는다.

## 악기와 Rhythmer Kit

빈 트랙에서는 인코더를 돌려 PLUG-IN / KIT / MIDI 계열의 카드를 선택한 뒤 Push로 연다. 기본 7개 카드 중 원하는 유형을 선택할 수 있다. B2는 Sample Kit, B3는 MIDI 바로가기다. 플러그인 브라우저에서 취소하면 같은 빈 트랙으로 돌아온다.

플러그인 목록 맨 위의 Rhythmer Kit을 선택하면 PRESETS에서 36개 킷을 바꿀 수 있다. 모든 킷의 1–16번 패드가 채워져 있다. EDIT에서 B3 PAD SOURCE를 열면 K1 Pad / K2 Engine / K3 Sound로 선택한 패드만 바꾼다. B3 SAVE는 저장 화면, 그다음 B3 EDIT는 사운드 편집 화면으로 이동한다. 실제 패드를 눌러 편집 대상을 선택할 수도 있다. 킷에 따라 B–D bank에 추가 음색이 있다. Hortator MD 추가 6종의 원본 사운드 구성은 HORTATOR_KITS_KO.md를 참고한다.

개별 엔진은 한 트랙에서 한 음색을 연주한다. Keys의 Chromatic 또는 Scale을 선택한다. 멜로디 엔진의 원래 MIDI/폴리포니를 유지하며, 드럼 단일 음색은 C4 기준 Tape 피치로 연주한다. 드럼의 길이와 기존 꼬리도 함께 피치 변환된다.

Stage PRESETS에서 엔진·프리셋 이름과 애니메이션을 보고, EDIT에서 소리를 편집한다. B2 PRESETS에서 인코더로 선택하고 Push/LOAD로 로드한다. 현재 프리셋 이름은 EDIT 상단에도 표시된다. 인코더/−/+로 3개씩 이동하며, 6줄 목록 중 K1–K3 표시가 있는 줄을 해당 노브로 조절한다. EDIT 현재/전체 표시로 위치를 확인한다. 일반 악기는 B3 SAVE에서 Save slot과 Save Sound로, 킷은 PAD SOURCE 다음 SAVE에서 Save slot과 Save Kit으로 저장한다. 저장된 항목은 PRESETS의 User Sound / User Kit에 추가된다. 동일 슬롯에 저장하면 해당 슬롯을 교체한다.

프로젝트 저장은 전체 킷의 패드별 엔진·음색·편집 파라미터를 보존한다. 사용자 프리셋은 Rhythmer/Presets에 저장한다. 베타 업데이트 시 autorun과 Rhythmer/Plugins/RHYTHMER - Rhythmer Kit을 포함해 패키지 전체를 복사한다. 자세한 단계는 SOUND_KIT_GUIDE.md를 참고한다.

## Generator와 사용자 Break

SEQ → PATTERNS → Shift+B3 GEN에서 GEN을 엽니다. GEN SETUP에서 K3를 SOUND + MIDI로 두고 K1 SONG GROUP으로 1–4 / 5–8 / 9–12 / 13–16을 선택합니다. FM-1 Rhythmer 원본 GEN을 사용해 선택 묶음의 첫 트랙은 Rhythmer Kit, 나머지 세 트랙은 장르에 맞는 악기·프리셋과 MIDI로 생성합니다. 다른 묶음의 트랙과 패턴은 유지하고 MONK는 자동 선택에서 제외합니다. 프로젝트 공통 키·스케일·템포는 기존처럼 함께 적용됩니다. Explore / Random / 장르, Energy, Seed를 조절할 수 있습니다. MIDI ONLY에서는 별도의 MIDI FROM / TO로 1–16 트랙 범위 또는 한 트랙만 지정합니다. Generate T번호는 현재 선택한 한 트랙의 악기를 유지합니다. Break GEN과 Acid GEN은 해당 엔진에서만 표시하며 Back은 GEN 메인으로 돌아옵니다. 대상 설정의 프로젝트 저장·복원과 Undo/Redo를 유지합니다.

BREAK에서는 K1 LOAD BARS에 원본 4/4 루프 길이 1–4마디를 지정하고 BROWSE SAMPLE에서 오디오를 선택한다. 로드 후 원본 전체를 16개 균등 구간으로 나누어 선택 뱅크에 배치하고, 원본 BPM 계산과 기존 Follow/Beats를 통해 템포 싱크한다. 현재 패턴은 원본 마디 수의 Straight 패턴으로 교체된다. 3마디도 전체를 16등분하며, 트랜지언트 자동 검출은 아니다. Genre Chops / Random / Mutate / Tail Fill과 수동 Chop도 유지한다. 자세한 조작법은 GEN_WORKFLOW.md와 USER_MANUAL_KO_DRAFT.md를 참고한다. 내장 Break 음원은 없다.

## 저장과 종료

기존 project save/load가 plugin state와 샘플 참조를 보존한다. 샘플은 SD에 남겨야 한다. 기존 Exit의 MPC APP/stock 복구 흐름을 유지한다. 실제 카드 제거·전원 차단·기기 복구 동작은 기기 검증 단계에서 확인한다.

## 현재 한계

Linux ARM64 빌드와 offline host 검증은 기기 검증과 다르다. 많은 플러그인을 동시에 켜는 성능은 실측 전이다. 외부 플러그인의 내부 보이스를 CPU Guard가 직접 줄여주지는 않는다. Open MPC wrapper의 기존 DSP mutex 등 실시간 동작도 실기기 부하·지연 검토 대상이다.

필수 크레딧: Based on Melodee by Kerem Kiliç (Ellic Studio), AGPL-3.0-only, and sample-base. Original notices and source attribution are retained.

GEN의 트랙 범위·악기 자동 배정·MIDI 전용 모드와 1–4마디 Break 자동 준비는 [GEN_WORKFLOW.md](GEN_WORKFLOW.md)를 참고하세요.

[Sound and preset verification](VERIFICATION.md). Stop twice within 400 ms cuts all audio; the next note or Play resumes.


## 0.4 기반으로 업데이트

0.3 베타에서 넘어올 때는 카드의 프로젝트·샘플·사용자 프리셋과 기존 autorun을 먼저 백업하고 전체 SD ZIP을 카드 최상위에 풉니다. 새 정식 저장 위치는 Rhythmer/Plugins입니다. 기존 최상위 Plugins는 호환용으로 읽으며 자동 삭제하거나 이동하지 않습니다. 동일 엔진이 새 위치에도 있으면 새 위치를 우선 사용합니다.

이후 호환 Rhythmer 0.4 빌드에서는 서명된 UPDATE ZIP을 카드 최상위에 놓거나 USB 기기 페이지로 전송합니다. 저장 후 설치를 선택하면 이전 실행 폴더를 autorun/rhythmer.prev에 보존하고 재시작합니다. 시작 확인 실패 시 이전 버전으로 복구하는 원본 절차를 사용합니다. UPDATE는 플러그인·킷 데이터 교체용이 아닙니다. 이 데이터가 바뀐 릴리스는 전체 SD 패키지 안내를 따릅니다. Melodee 정식 ZIP은 Rhythmer OS 업데이트로 수락하지 않습니다.

복구는 기기 전원을 끈 뒤 카드를 분리하고 autorun 폴더를 카드 밖에 보관하면 기존 stock 앱으로 부팅됩니다. 이전 베타로 돌아갈 때는 백업한 autorun과 해당 베타의 플러그인 폴더를 복원합니다. 128패턴·Freeze가 포함된 새 프로젝트는 복사본으로 보관하고 이전 베타에서 덮어쓰지 마세요.

## 다운로드 선택과 안내

첫 설치와 이번 0.4 전환에는 **SD.zip** 전체 패키지를 사용한다. **UPDATE.zip**은 호환 Rhythmer 설치의 실행 앱만 업데이트하며 플러그인이나 킷을 포함하지 않는다. SOURCE / MOVE-SOURCE / SUPPORT-SOURCE는 재빌드를 위한 소스 배포물로 SD 설치 파일이 아니다. 배포 페이지의 버전과 `.sha256` 값을 다운로드 파일과 대조한다.

이 프로젝트는 AKAI Professional 또는 inMusic이 승인하거나 지원하는 공식 펌웨어가 아니다. MPC Sample 명칭과 로고의 권리는 각 권리자에게 있다. 소프트웨어는 각 라이선스에 따라 무보증으로 제공된다. 테스트 범위·알려진 한계는 VERIFICATION.md를 확인한다. 제조사 펌웨어를 덮어쓰는 설치가 아니라 SD launcher를 사용하는 방식이다.
