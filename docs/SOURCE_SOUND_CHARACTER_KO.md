# 원본 사운드 특성 대조

C4 / velocity 110, 0.5초 게이트와 0.5초 릴리스 조건으로 2,659개 선택을 측정했다. 작은 출력·DC·클리핑 후보는 원본 모듈을 직접 불러온 출력과 별도로 대조했다. 이 문서는 원본 프리셋을 자동 보정하는 지시가 아니다.

총 후보 69개. 짧은 게이트의 낮은 피크 29개, 평균 DC 절댓값 0.05 초과 3개, 전체 샘플 중 절댓값 1 이상 비율 0.5% 초과 37개다. 기준은 진단용이며 음악적 결함이나 사용 불가 판정이 아니다.

원본 모듈 직접 출력과 랙 출력의 최대 피크 차이는 0.00036621, 최대 RMS 차이는 0.00003685였다. Braids Pad의 확률적 출력에는 편차가 있다. 이는 물리 기기 청취나 완전한 파형 동일성 검증을 대신하지 않는다.

Plaits의 세 모델에서 DC가 크게 측정되며, 일부 모델·내장 6-Op 프로그램은 원본 모듈에서도 클리핑된다. 고정 원본 플러그인은 엔진별 게인 보정과 의도적인 하드 클리핑을 사용한다. 이번 포트 수정에서 원본 DSP·게인·엔벌로프를 임의로 바꾸지 않았다. 이는 별도 청취·믹싱 검토 항목이다.

짧은 게이트에서 약했던 프리셋은 4초 홀드, Aphex Hold 계열은 32초 홀드로 다시 측정했다. 긴 어택과 원래 작은 레벨을 구분했다.

| 엔진 | 원본 프리셋 | 홀드 길이 | 홀드 피크 |
|---|---|---:|---:|
| S1Vave | PTN 4-13 | 4s | 0.13882 |
| Aphex | Endless Hold | 32s | 0.36273 |
| Aphex | Slow Evolution | 32s | 0.37329 |
| Aphex | Tape Hiss Drone | 32s | 0.39926 |
| Aphex | Modular Hum | 32s | 0.34268 |
| Braids | Pad | 4s | 0.05862 |
| Dexed | Dexed_01 / MIRIDOR 1 | 4s | 0.04279 |
| Dexed | Dexed_01 / RUMBLE   1 | 4s | 0.06250 |
| Dexed | Dexed_01 / FILTER-SWP | 4s | 0.06525 |
| Dexed | Dexed_01 / LFO SWEEP | 4s | 0.05765 |
| Dexed | SynprezFM_01 / TAKE OFF | 4s | 0.00742 |
| Dexed | SynprezFM_05 / CIANIA | 4s | 0.14334 |
| Dexed | SynprezFM_06 / JUPITER | 4s | 0.16296 |
| Dexed | SynprezFM_06 / Heavy Mach | 4s | 0.04294 |
| Dexed | SynprezFM_07 / Cymbalrev3 | 4s | 0.03903 |
| Dexed | SynprezFM_09 / On the Run | 4s | 0.05768 |
| Dexed | SynprezFM_13 / MIRIDOR 1 | 4s | 0.04279 |
| Dexed | SynprezFM_15 / STRM1 LNGA | 4s | 0.09659 |
| Dexed | SynprezFM_18 / *reverse | 4s | 0.04053 |
| Dexed | SynprezFM_19 / BlueDeluge | 4s | 0.07700 |
| Dexed | SynprezFM_21 / CIGALES | 4s | 0.00455 |
| Dexed | SynprezFM_22 / StarGalaxy | 4s | 0.02789 |
| Dexed | SynprezFM_23 / ^Water^ | 4s | 0.04944 |
| Dexed | SynprezFM_26 / LFO SWEEP | 4s | 0.05765 |
| Dexed | SynprezFM_26 / WORRY | 4s | 0.00443 |
| Dexed | SynprezFM_30 / EXPAN. A06 | 4s | 0.11450 |
| Dexed | SynprezFM_32 / BackSuir 1 | 4s | 0.10513 |
| Hera | Reed 1 | 4s | 0.00146 |
| Hera | Space Sound 2 | 4s | 0.02808 |

특히 Dexed CIGALES, Dexed WORRY, Hera Reed 1은 긴 홀드에서도 피크가 0.005 미만이다. 원본 모듈 직접 출력도 같은 수준이므로 포트에서 만든 음량 감소로 판정하지 않았다. 브라우저 이름은 보존하며, 자동 노멀라이즈나 원본 패치 재작성을 하지 않는다.
