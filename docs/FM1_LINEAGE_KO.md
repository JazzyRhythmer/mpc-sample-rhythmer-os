# FM-1 source lineage

The selected release retains 12 FM-1 variants and DRUM-X. 164 pinned predecessor-credit documents remain under ports/*/UPSTREAM_NOTICES, with original paths, fixed revision URLs and hashes. Full-firmware references are distinguished from synthesis units actually included.

| 포트 | 보존·대조한 제작자와 이전 출처 | 범위 구분 |
|---|---|---|
| FMini-1 | Guilherme Ruppert → Felucca, Leo Kuroshita / Hügelton Instruments. 필터 문서의 CA-72, idlefoundry | CA-72는 회로·보정의 기술적 참고로 명시돼 있으며, 그 코드를 그대로 포트했다고 바꾸어 쓰지 않는다. Felucca의 CREDITS도 보존 |
| S1Vave | Andrew GG → OberVave / Dinghy, zvenson → Felucca, Leo Kuroshita 및 SLOOP, isod89 | Andrew Simper의 필터 토폴로지 등 기술적 출처와 실제 상속 코드 구분. 원본 로고·전용 폰트는 별도 |
| Prophet | Melodee, Kerem Kiliç / Ellic Studio → Felucca, Leo Kuroshita 및 파일별 기여자 | 원본 코드 고지와 Sequential 팩토리 200개 데이터의 별도 출처·이용 조건을 보존 |
| FM-106 | PatttF → Felucca / SLOOP / Dinghy. 원본 README가 명시한 Ultramaster KR-106, Kayrock Screenprinting 및 Melodee, Kerem Kiliç | DSP 출처와 플랫폼·보드 출처를 분리. 원본 팩토리 128개 사용 |
| OberVave | zvenson → Dinghy / Felucca / SLOOP | 원본 LICENSING의 소스 경로별 저작권 표 보존. 플랫폼/UI/시뮬레이터 참고를 DSP로 잘못 표기하지 않음 |
| Hortator | DEADACTIVE → Felucca / Skiff, Leo Kuroshita 및 DEADACTIVE. 원본이 기록한 Mutable Instruments / Émilie Gillet의 Grids·Streams·Plaits 등 | 드럼 DSP, FX, 생성기, 녹음 자산을 구분. VCSL/Versilian Studios·Sam Gossner의 CC0 샘플은 별도 고지 |
| Elixir / LXR 통합 | dmajka의 Elixir → Erica Synths LXR-02 → Julian Schmidt / Sonic Potions LXR. Rings·Plaits·stmlib·Clouds, Émilie Gillet 등 원본 NOTICE의 항목 | 모델·FX 저자 고지와 설계 참고를 구분. 원본 Erica/Hrtl 117킷의 별도 허가 안내를 동봉하며 소프트웨어 GPL로 재허가했다고 주장하지 않음 |
| MONO2K | Inigo Hernandez → Felucca 및 CS-1 / X0X / FoMni 계보 | Gearmulator 측정 참고는 에뮬레이터 코드/ROM을 포함했다는 뜻이 아님. 원본도 코드·데이터 미포함을 명시 |
| CS-1 | twochannels → Dinghy, zvenson → Felucca / SLOOP; FM-106, PatttF에 대한 원본 고지 | 보드·멀티코어 계보는 DSP 자체의 저자와 구분. 원본 톤 테이블과 변환 사운드 표의 고지 보존 |
| K-WASUB | Guizmoh / K-WASUB → KAWA (Omnipotard / Leo Kuroshita), Dinghy, zvenson. CS-1의 CS 엔진 및 Felucca의 FM 관련 계보 | LICENSING이 '새로 작성'으로 구분하는 부분을 코드 복사로 단정하지 않음. 선택한 신스 DSP와 전체 펌웨어의 FM/보드 부분을 구분 |
| K-WASUB Drums | 위와 같은 K-WASUB 원본 커밋 | 별도 드럼 경계만 연결하되 동일 출처 문맥·고지를 함께 보존 |
| Guru-600 | Marc Massé → Felucca, Leo Kuroshita. 원본의 GliGli 프로그램 컬렉션·Surge XT 음색 크레딧도 원문 보존 | P600 DSP 전체를 GliGli 코드라고 단정하지 않음. 원본 255개 프로그램과 확장 값·출처 사용 |
| DRUM-X | Juan Ignacio Antonucci / Juan Jiant 및 Leo Kuroshita / Hügelton Instruments → JIANT / Felucca | Sonic Charge Microtonic은 '아이디어를 참고하여 새로 작성'으로 원본 헤더가 명시. Microtonic 소스코드나 제품 음원을 포트했다는 뜻이 아님 |

Original copyright, SPDX, LICENSE, CREDITS and LICENSING documents are retained. Integration by jazzy rhythmer does not transfer upstream authorship. Original bank data and software licenses are distinguished. See ORIGINAL_PRESET_AUDIT_KO.md for factory data, explicit sample dependencies and separate asset terms; this is not blanket public redistribution clearance.
