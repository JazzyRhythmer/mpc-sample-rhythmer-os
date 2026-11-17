# 추가 출력 필터 원본 대조 및 구현

2026-11-15. 구현 및 자동 검증 중. 배포 보류.

| 엔진 | 원본과 포트 대조 | 대응 |
|---|---|---|
| Dexed | Move 원본 dx7_plugin.cpp의 공개 합성 파라미터에 일반적인 cutoff/resonance 쌍 없음. Algorithm/Feedback/Output 제어는 유지됨. | 출력 전체 SVF 추가 |
| DRUM-X | original/drumx_voice.c: COLOR는 oscillator FM/drive와 noise cutoff를 함께 제어하며 LP/BP/HP는 noise 경로에 적용됨. 전체 출력 필터와 다름. 이 원본 제어는 포트에 남아 있음. | 원본 음색 구조 유지, 출력 전체 SVF 추가 |
| Plaits | Move 원본 src/dsp의 모델별 Harmonics/Timbre/Morph 및 decay/lpg_colour를 유지. 일부 모델은 Cutoff/Resonance라는 동적 이름이 있으나 전 모델 공통 출력 필터가 아님. | 모델 내부 제어 유지, 출력 전체 SVF 추가 |
| CS-1 | original/cs1_voice.h의 HP/LP 및 brilliance/resonance offset 존재. 포트 p58 Brightness/p59 Resonance와 채널별 필터 제어가 보존되어 있음. 필터 누락으로 분류하면 안 됨. | 원본 필터를 대체하지 않고 출력 전체 SVF 추가 |
| MONO2K | original/m2k_core.c의 HP/LP와 포트 p17 FILTER BASE/p18 FILTER WIDTH/p20 LP RESONANCE 보존. 단일 cutoff 노브와 다른 원본 구조. | Base/Width 필터 유지, 출력 전체 SVF 추가 |

원본 파일은 SSD plugins/ports/<port>/original, Move 프로젝트는 source-depot/<project>에서 대조했다. 기존 SOURCE.json/VENDORED.md의 고정 출처와 크레딧은 유지한다. 추가 필터는 Melodee 기반 OS의 기존 EffectKind::Filter를 재사용하며 원본 엔진 기능이라고 표시하지 않는다.

추가 필터는 Rack가 소유하며 트랙 인서트를 자동 삽입하지 않는다. PRESETS와 EDIT는 같은 파라미터를 조정한다. 중립값은 비트 단위 dry 통과. 저장·복원·팩토리 프리셋 재선택·panic offset 17 및 원본 child state 불변을 자동 검사한다. 
