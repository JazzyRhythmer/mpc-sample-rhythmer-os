# Melodee 0.2.0 트랙·플러그인 변경 경로

고정 원본 `v0.2.0`, commit `8880d16116ccb3c69f75fb46bf2166b16c51ef0c`의 소스와 문서 기준이다. Rhythmer OS에 추가한 TRACK SETUP 및 프리셋 목록의 PLUG-INS 버튼과 구분한다. 원본을 실기기에 설치하여 검증했다는 뜻은 아니다.

## 기존 플러그인 교체

1. PAD BANK를 누른 채 대상 트랙의 패드를 누르고 놓는다.
2. SAMPLE SELECT를 누른다. 플러그인 트랙이면 플러그인 브라우저가 열린다.
3. 엔코더로 다른 플러그인을 골라 클릭한다. 기존 패턴을 지우지 않고 악기를 교체한다.
4. 폴더 안의 B1은 상위 폴더로 이동한다. 카드 최상위의 B1은 CANCEL이다.

원본 `open_plugin_picker()`는 악기 선택 후 돌아갈 화면을 독립 Edit로 설정한다. 새 트랙 생성에서는 생성 경로가 복귀 위치를 조정한다. 이를 Rhythmer OS의 성공 후 Stage 복귀와 혼동하지 않는다.

## 같은 플러그인의 프리셋 변경

SAMPLE로 Stage에 진입한다. 플러그인 트랙 B1의 PRESETS 첫 화면에서 엔코더 회전은 프리셋 이동, 클릭은 전체 프리셋 목록이다. 목록에서 회전 후 클릭하면 해당 프리셋을 로드한다. 원본 목록의 B1은 BACK이며 B2/B3에는 교체 버튼이 없다. 프리셋이 없는 악기는 첫 화면이 PLUG-IN으로 표시된다.

## 빈 트랙 생성

빈 트랙을 선택하면 엔코더로 넘기는 일곱 카드가 표시된다. 원하는 카드를 가운데 놓고 클릭한다.

| 카드 | 생성 결과 |
| --- | --- |
| SYNTH / Plugin | 플러그인 목록. 악기를 선택한 뒤 PLUGIN 트랙이 됨 |
| KIT / Empty | 빈 샘플 킷 |
| KIT / Card | 샘플 브라우저에서 로드 |
| KIT / Input | 샘플 녹음 화면 |
| MIDI / Out jack | 외부 단자 MIDI |
| MIDI / USB-C | USB-C MIDI |
| MIDI / All USB | 전체 USB MIDI |

TRACKS에서는 패드로 빈 트랙을 고르면 선택 화면이 열린다. 엔코더로 빈 트랙을 선택한 경우 Push로 Stage에 들어갈 수 있다. B1 CANCEL은 가까운 사용 중 트랙을 선택한다. 모든 트랙이 비어 있으면 돌아갈 사용 중 트랙이 없다. 원본은 빈 트랙 생성 중 상당수 다른 버튼을 막는다.

## 기존 트랙에 샘플 킷 가져오기

SHIFT + PAD 16 → Project → B2 OPEN → 다른 프로젝트 선택 → 작업 카드의 LOAD KIT.

- 해당 프로젝트의 첫 샘플 킷을 선택 트랙으로 가져온다.
- 플러그인/MIDI 트랙도 샘플러 트랙으로 바뀔 수 있다.
- 대상 트랙의 패턴은 유지하며 가져온 프로젝트의 패턴은 가져오지 않는다.
- 하나의 Undo로 되돌릴 수 있다.
- B2 드라이브 선택의 INTERNAL에도 기본 킷 및 MPC Sample 프로젝트가 있다.
- LOAD는 프로젝트 전체 교체이므로 LOAD KIT와 다르다.

샘플 킷 트랙의 SAMPLE SELECT 브라우저에서도 `.xpm`/`.xty` 같은 킷 프로그램과 킷 뱅크를 선택할 수 있다. 전체 킷 로드는 `load_kit_file`, 뱅크 파일은 `load_bank_file`, 일반 오디오 파일은 선택 패드 로드로 분기한다. 뱅크 로드는 현재 샘플 킷의 선택 뱅크를 대상으로 한다.

## 일반적인 트랙 타입 변경

원본에는 기존 트랙을 PLUGIN/SAMPLER/MIDI/EMPTY로 바꾸는 공통 TRACK TYPE 메뉴가 없다.

| 현재 → 목표 | 원본의 일반 경로 |
| --- | --- |
| 플러그인 → 다른 플러그인 | SAMPLE SELECT에서 직접 교체 |
| 플러그인 또는 MIDI → 샘플 킷 | Project의 LOAD KIT, 또는 Clear 후 KIT 생성 |
| 샘플 킷 → 다른 샘플 킷 | Project의 LOAD KIT 또는 샘플 브라우저 |
| 샘플 킷/MIDI → 플러그인 | Clear 후 SYNTH / Plugin 생성 |
| 플러그인/샘플 킷 → MIDI | Clear 후 MIDI 카드 선택 |
| 사용 중 트랙 → EMPTY | Clear track |
| MIDI → 다른 MIDI 출력 | DEVICE의 PORT/CHANNEL 변경; 타입 교체 불필요 |

Clear 경로는 TRACKS에서 대상 선택 후 ERASE, 또는 PAD BANK + ERASE + 대상 패드다. 확인 후 악기와 모든 패턴이 지워진다. 믹서 스트립은 남으며 Undo로 복구할 수 있다. 악기만 제거하고 패턴을 유지하는 Rhythmer OS의 EMPTY 전환과 다르다.

## 실제 진입 경로로 혼동하면 안 되는 코드

- 독립 `Edit` 화면에는 B1 PLUG-INS 코드가 있지만, Stage B1의 EDIT는 별도의 Stage 하위 화면이다. 동일한 버튼 배열이라고 안내하지 않는다. Keys 페이지의 Push→Edit 코드도 있지만 SAMPLE 홀드의 Keys 오버레이가 Push를 Keys 페이지에 전달한다고 단정할 수 없다.
- 예전 `StageKind::Preset`의 ENGINE 바인딩도 남아 있다. 현재 제공되는 PLUGIN/SAMPLER/MIDI의 Stage 구성에서 이 메뉴가 노출되는 일반 경로는 확인되지 않았다. K3로 언제든 타입을 바꿀 수 있다고 안내하지 않는다.
- 트랙 복사·이동·프로젝트 전체 LOAD는 타입도 바꿀 수 있지만 패턴까지 복사·교체하므로 악기만 변경하는 경로가 아니다.
- FX의 플러그인 선택은 인서트/버스/마스터 효과를 고르는 경로이며 트랙 악기 교체와 다르다.
- FREEZE/DEEP FREEZE는 트랙을 샘플러 타입으로 바꾸는 메뉴가 아니다.

## Rhythmer OS와의 차이

Rhythmer OS는 원본 SAMPLE SELECT 경로를 유지하고, 악기 프리셋 목록 B2 PLUG-INS 및 TRACKS B1 TRACK SETUP을 추가한다. TRACK TYPE은 모든 패턴을 보존한다. DELETE TRACK은 별도 확인 후 패턴까지 삭제한다. 의도적으로 EMPTY로 바꾼 트랙도 네이티브 타입 선택 화면을 사용한다. 실제 배포·기기 설치 여부는 개발 소스의 존재와 별도로 확인해야 한다.

근거: 원본 `shell/shell.cpp`, `shell/new_track.cpp`, `shell/plugin_jobs.cpp`, `shell/track_copy.cpp`, `shell/project_jobs.cpp`, `pages/plugin_presets_page.cpp`, `pages/project_page.cpp`, `pages/samples_page.cpp`, `engine/engine_info.cpp`, `docs/MELODEE.md`.
