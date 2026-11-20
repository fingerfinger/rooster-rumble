# 🥊 ROOSTER RUMBLE: Rumble Pit - 인게임 사운드 구성안 (In-Game Sound Specification)

* **문서 상태**: 인게임 사운드 기술 및 기획 명세서 (v3.0 AI 실사 Foley 전면 쇄신 · 승자 PA 보이스 분리 마스터판)
* **문서 버전**: `v3.0.0`
* **마지막 개정일**: 2026-11-19
* **대상 범위**: Rumble Pit 로비/대기실, 1v1 원형 벽면 아레나 전투(3R 2선승제, 45초 격투 + 15초 휴식), 스페셜 공방(`F33` 머리 잡아 바닥 찍기 / `F34` 머리 풀고 반격), 즉시 KO/판정 승자 PA 세리머니 사운드 전반 (BGM 1종, SFX 26종 28개 MP3 파일, 권투/UFC PA 보이스 5트랙, 1R 실전 시뮬레이션 데모 트랙, 8대 콤보·스페셜 레이어링, `cue_table_v6.csv` 1:1 매핑)
* **기반 문서**: [Rumble Pit MVP 구성안.md](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/Rumble%20Pit%20MVP%20%EA%B5%AC%EC%84%B1%EC%95%88.md), [Rumble_Pit_전투_시뮬레이션_규칙_정의서.md](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/Rumble_Pit_%EC%A0%84%ED%88%AC_%EC%8B%9C%EB%AE%AC%EB%A0%88%EC%9D%B4%EC%85%98_%EA%B7%9C%EC%B9%99_%EC%A0%95%EC%9D%98%EC%84%9C.md), [Rumble Pit 선수 공격 방어 동작 구성안.md](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/Rumble%20Pit%20%EC%84%A0%EC%88%98%20%EA%B3%B5%EA%B2%A9%20%EB%B0%A9%EC%96%B4%20%EB%8F%99%EC%9E%91%20%EA%B5%AC%EC%84%B1%EC%95%88.md), [Rumble Pit 전투 장면 인게임 구성안.md](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/Rumble%20Pit%20%EC%A0%84%ED%88%AC%20%EC%9E%A5%EB%A9%B4%20%EC%9D%B8%EA%B2%8C%EC%9E%84%20%EA%B5%AC%EC%84%B1%EC%95%88.md), [통합 MVP 구성안.md](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/%ED%86%B5%ED%95%A9%20MVP%20%EA%B5%AC%EC%84%B1%EC%95%88.md)

---

### ■ 문서 개정 이력 (Revision History)

| 버전 (Version) | 개정일 (Date) | 주요 개정 내역 및 상세 변경 사항 | 관련 절 바로가기 |
| :---: | :---: | :--- | :--- |
| **v1.0.0** | 2026-09-29 | **[격투 사운드 구성안 단독 문서 독립 신설]** 기존 베이스 문서 내용 100% 보존 상태에서 격투 BGM·SFX 14종·라운드 순수 보이스·오디오 아키텍처·믹싱/덕킹 규격 전면 집대성 | [[#1. 개요 및 사운드 아키텍처\|1장 사운드 아키텍처]] |
| **v1.1.0** | 2026-09-29 | **[미제작 BGM 정리, 사운드보드 연동 항목 제거 및 1R 시뮬레이션 데모 신설]** 제작 음원 부재 미제작 인트로 BGM 삭제, 사운드보드 연동 항목 정리, 1라운드 실전 사운드 시뮬레이션 데모(`demo_pit_round1_simulation.mp3`) 신규 구축 및 세부 타임라인 명세 수립 | [[#8. 1라운드 실전 사운드 시뮬레이션 샘플 사양 및 시나리오\|8장 1R 사운드 시뮬레이션]] |
| **v1.2.0** | 2026-10-08 | **[비의인화 닭 골격 기반 공/방/이동 기술 명칭 및 즉시 KO 사운드 매핑 동기화]** `Rumble Pit MVP 구성안(v1.2.0)` 및 `Rumble_Pit_전투_시뮬레이션_규칙_정의서(v1.2.0)` 기준 공격 4종(`전진 부리 속사`, `낮은 발톱 할퀴기`, `비상 발톱 급습`, `광폭 발버둥 난타`), 방어 3종(`깃털 부풀려 버티기`, `납작 엎드리기`, `맞발톱 쳐내기`), 이동 6종 및 바닥 다운 즉시 KO 사운드 트리거 명세 일괄 동기화 | [[#3. SFX (효과음) 26종 상세 명세\|3장 SFX 상세 명세]] |
| **v2.0.0** | 2026-11-19 | **[리얼·강조 3-Layer 전면 리디자인 및 스페셜 공방(`F33/F34`) 시퀀스 신설]**<br>1. 무료 인디 팩(Kenney) 의존 전면 폐기 ➔ **OpenGameArt CC0 실사 전투·폴리 + 서브 펀치 + 실제 수탉 기합·포효** 기반 3-Layer(어택·바디·테일) 사운드 전면 재제작 (`25종 27개 MP3`)<br>2. **공격 vs 방어·패링 대역 분리 강화**: 타격(2.5~6kHz 크랙+펀치), 깃털 가드(2kHz↓ 댐핑 흡수), 맞발톱 패링(황금 메탈 링)의 즉각적 청각 변별력 확보<br>3. **스페셜 공방 6종 신설**: `[특공 F33]` 머리 잡아 바닥 찍기(`GRAB_PIN`, `SLAM`, `GRAB_MISS`) 및 `[특방 F34]` 머리 풀고 반격(`GRAB_ESCAPE`, `BREAK`, `GROGGY`) 단계별 음원 제작<br>4. **특수상태·시스템 보강**: `MISS`, `WALL_IMPACT`, `KO_SLOW`, `CROWD_GASP`, `ROOSTER_CROW` 신설 및 권투/UFC PA 아나운서 라운드 보이스(`1R~3R`) 전면 쇄신<br>5. **BGM EQ 카빙(`1.5~4.2kHz -3.2dB`) · 고속 사이드체인(`8ms`) · `cue_table_v6.csv` 1:1 매핑표** 및 `38.03초` 실전 데모 트랙 재합성 완료 | • [[#1.3 3-Layer 리얼·강조 사운드 디자인 규격\|1.3절 3-Layer 디자인 규격]]<br>• [[#3.3 스페셜 공격·방어 (F33/F34) 시퀀스 효과음 (6종)\|3.3절 스페셜 공방 6종]]<br>• [[#6. 8대 콤보·스페셜 공방 사운드 레이어링 명세\|6장 8대 레이어링 명세]]<br>• [[#7. 연출 큐 테이블 (cue_table_v6.csv) ↔ 실음원 1:1 매핑표\|7장 큐 시트 1:1 매핑]] |
| **v2.1.0** | 2026-11-19 | **[효과음 평가 반영 — 관중 탄성 리얼 교체 및 공/방 변별력 전면 차별화]**<br>1. **관중 탄성(`SFX_PIT_CROWD_GASP`) 전면 교체**: 공포 영화풍(`oooooooooo.ogg` 변조) 소스 완전 폐기 ➔ 실사 경기장 2채널 급등 서지 + 다중 관객 짧은 `"Whoa/Oh/Hey"` 리액션(`1.38초`)으로 자연스러운 스포츠 환호 질감 구현<br>2. **'1기술 · 1재질 · 1리듬 · 소스 배타 할당' 원칙 수립**: `HIT_POKE`(저역 0% 3연타 딱-딱-딱), `HIT_SPUR`(230ms 발톱 긁힘), `HIT_WING`(3연속 날갯짓 돌풍➔급강하), `HIT_GEN`(2.8~3.2kHz 단단한 스냅 정타), `GUARD`(9ms 부드러운 480Hz↓ 쿠션+깃털 부스럭), `GUARD_GEN`(900Hz↑ 순수 황금 메탈 패링), `BREAK`(차임➔쌍발 가슴 킥 2연타), `WALL_IMPACT`(빈 목재 판자+철망 떨림) 재제작으로 전투 쌍 평균 스펙트럼 유사도 `0.450` (`HIT_GEN ↔ GUARD` 유사도 `0.572`) 달성<br>3. **`SFX_PIT_SLAM` · `SFX_PIT_KNOCKDOWN` 저역 밸런스 교정**: 과도한 초저역 마스킹 제거로 자갈·모래 산란(`SLAM` Sub `31.5%`) 및 전신 낙하 흙 쓸림 명료도 개선<br>4. **사운드보드 v2.1 UI 개편**: 상단 `공/방 변별력 즉시 비교 바` 신설 및 25종 재측정 메타데이터·`1R` 데모 트랙 동기화 | • [[#1.3 3-Layer 리얼·강조 사운드 디자인 규격\|1.3절 3-Layer 디자인 규격]]<br>• [[#3. SFX (효과음) 26종 상세 명세\|3장 SFX 상세 명세]]<br>• [[#8. 1라운드 실전 사운드 시뮬레이션 샘플 사양 및 시나리오\|8장 1R 사운드 시뮬레이션]] |
| **v3.0.0** | 2026-11-19 | **[AI 실사 Foley 전면 쇄신(7대 피드백 해소) 및 승자 아나운서 보이스 2종 분리]**<br>1. **추상 CC0·합성음 전면 폐기 ➔ 무료 AI Text-to-SFX (`declare-lab/TangoFlux` 44.1kHz Stereo) 전환**: 장난감 클릭(`공1`), 플라스틱 긁힘(`공2`), 중세 칼/금속 차임(`방3`, `F34`), 순수 사인파 비프(`그로기`), 닭 울음(`rooster_crow`) 100% 제거<br>2. **7대 지적 항목 실사 격투 폴리 교체**: `HIT_POKE`(묵직한 3연속 쪼기 타격), `HIT_SPUR`(거친 찢김+바디 슬랩), `GUARD_GEN`(단단한 뼈·각질 패리 충돌), `GRAB_PIN`(격렬한 깃털 클린치 제압), `BREAK`(깃털 탈출➔폭발적 가슴 킥), `GROGGY`(먹먹한 심장 고동+거친 호흡 비틀거림), `CROWD_GASP`(UFC/복싱 KO 순간 단발 경악 함성) 포함 전투 18종 AI 실사 재생성 (`Mean Sim 0.575`, `HIT_GEN↔GUARD 0.550`)<br>3. **승자 PA 보이스 2종 분리 (`SFX_PIT_WIN_KO` · `SFX_PIT_WIN_DECISION`)**: `sfx_pit_rooster_crow.mp3` 삭제 ➔ 1R~3R과 동일 PA 성우의 **KO 승 / 판정 승** 콜 분리 신설 (총 **26종 28개 MP3**)<br>4. **라이선스 투명 고지 및 보드·데모 동기화**: `TangoFlux/AudioGen` 프로토타입·MVP(Non-Commercial) 사용 명시 및 상용 프롬프트 보존, 1R 데모(`38.03초`, `WIN_KO` 마감) 및 사운드보드 `v3.0` 갱신 | • [[#1.3 3-Layer 리얼·강조 사운드 디자인 규격\|1.3절 AI 실사 Foley 규격]]<br>• [[#3. SFX (효과음) 26종 상세 명세\|3장 SFX 26종 명세]]<br>• [[#4.3 승리 확정 아나운서 PA 보이스 2종 (KO 승 / 판정 승)\|4.3절 승자 PA 2종]]<br>• [[#8. 1라운드 실전 사운드 시뮬레이션 샘플 사양 및 시나리오\|8장 1R 사운드 시뮬레이션]] |

---

## 목차
1. [[#1. 개요 및 사운드 아키텍처]]
   - [[#1.1 문서 목적 및 정체성]]
   - [[#1.2 5대 오디오 채널 레이어 구조]]
   - [[#1.3 3-Layer 리얼·강조 사운드 디자인 규격]]
2. [[#2. BGM (배경음악) 사양 및 EQ 카빙 명세]]
   - [[#2.1 전투 BGM: BGM_PIT_FIGHT (혈투의 링)]]
3. [[#3. SFX (효과음) 26종 상세 명세]]
   - [[#3.1 공격 기술 효과음 (5종)]]
   - [[#3.2 방어 · 회피 · 패링 · 빗나감 효과음 (4종)]]
   - [[#3.3 스페셜 공격·방어 (F33/F34) 시퀀스 효과음 (6종)]]
   - [[#3.4 특수 상태 · 다운 · 벽 충돌 · 슬로우 효과음 (4종)]]
   - [[#3.5 시스템 · 벨 · 관중 · 승리 PA 보이스 효과음 (6종 + 라운드 보이스 1종 3트랙)]]
4. [[#4. 권투·UFC 스타일 라운드 시작 보이스 및 타종 연출 명세]]
   - [[#4.1 아레나 PA 하이텐션 아나운서 보이스 (1R~3R)]]
   - [[#4.2 단독 1회 공식 벨소리 독립 타종 연동]]
   - [[#4.3 승리 확정 아나운서 PA 보이스 2종 (KO 승 / 판정 승)]]
5. [[#5. 인게임 오디오 믹싱, 고속 덕킹 및 반복 피로도 제어]]
   - [[#5.1 오디오 우선순위 체계 (Priority Queue)]]
   - [[#5.2 고속 사이드체인 덕킹 파라미터 규격 (Attack 8ms)]]
   - [[#5.3 다빈도 SFX 엔진 랜덤 변조 규격]]
6. [[#6. 8대 콤보·스페셜 공방 사운드 레이어링 명세]]
7. [[#7. 연출 큐 테이블 (cue_table_v6.csv) ↔ 실음원 1:1 매핑표]]
8. [[#8. 1라운드 실전 사운드 시뮬레이션 샘플 사양 및 시나리오]]
   - [[#8.1 가상 1라운드 세부 타임라인 (38.03초)]]
9. [[#9. 리소스 관리 및 디렉터리 구조]]

---

## 1. 개요 및 사운드 아키텍처

### 1.1 문서 목적 및 정체성
* `ROOSTER RUMBLE` 원형 투계 격투 모드(Rumble Pit)의 BGM, SFX 26종(28개 MP3), 아나운서 보이스(라운드 3종 + 승자 콜 2종), 스페셜 공방(`F33`/`F34`) 시퀀스 및 엔진 연동 매핑 표준 정의.
* 기존 저품질 CC0/DSP 필터 짜깁기 탈피 및 7대 실전 청음 피드백을 반영하여 **AI 실사 격투 폴리 + 무금속/무비프 아레나 리얼 톤 + KO/판정 승자 PA 보이스 분리**를 구현한 `v3.0.0` 마스터 명세서.
* 실제 제작·청음 검증 완료된 음원 에셋(`assets/audio/pit/`), `cue_table_v6.csv` 및 `v3.0` 사운드보드(변별력 즉시 비교 바 · A/B 비교 지원)와의 100% 일치성 확보.

### 1.2 5대 오디오 채널 레이어 구조

```mermaid
flowchart TD
    L4["Layer 4: 시스템 & 공식 벨 (KO 벨, 1회 벨)"] --> Mixer["Master Pit Audio Mixer"]
    L3["Layer 3: 권투·UFC PA 아나운서 보이스 (1R~3R · KO승 · 판정승)"] --> Mixer
    L2["Layer 2: AI 실사 전투 Foley SFX (공격 5, 방어·패리·회피 4, 스페셜 F33·F34 6, 상태·벽 4)"] --> Mixer
    L1["Layer 1: EQ 카빙 전투 BGM (bgm_pit_fight.mp3, 1.5~4.2kHz -3.2dB)"] --> Mixer
    L0["Layer 0: 투계장 관중 앰비언스 (ROAR / GASP 분리)"] --> Mixer
    Mixer --> Out["Final Stereo Combat Audio Output (-0.6 ~ -1.9 dBFS)"]
```

| 레이어 | 대상 사운드 | 기준 출력 볼륨 | 덕킹 및 동적 제어 정책 |
| :--- | :--- | :---: | :--- |
| **Layer 4 (System/Bell)** | KO 확정 3연타 벨, 단독 1회 공식 벨 | `0 dB` (최상위) | 덕킹 미적용 (상시 최우선 클린 출력) |
| **Layer 3 (Voice)** | 아레나 PA 아나운서 보이스 (1R~3R / KO 승 / 판정 승) | `-0.5 ~ 0 dB` | 하위 Layer 1(BGM) `-7.5 ~ -18.0 dB` 감쇄 트리거 |
| **Layer 2 (Combat SFX)** | 일반 공/방 9종 + 스페셜(`F33/F34`) 6종 + 상태/벽 4종 | `-1.0 ~ -2.5 dB` | 타격/스페셜 적중 시 BGM `8ms` 고속 사이드체인 덕킹 유발 |
| **Layer 1 (BGM)** | EQ 카빙 배틀 오케스트라 (`bgm_pit_fight.mp3`) | `-5.2 dB` | `1.5~4.2kHz` 대역 선제 컷 + 타격 순간 자동 감쇄, KO 시 페이드아웃 |
| **Layer 0 (Crowd)** | 투계장 환호(`ROAR`) 및 경악 충격(`GASP`) | `-4.0 ~ -8.0 dB` | 평시 저역 필터링 앰비언스 ➔ 치명타/슬램 시 `GASP`, KO 시 `ROAR` 폭발 |

### 1.3 3-Layer 리얼·강조 사운드 디자인 규격
* **v3.0 제작 파이프라인 전환 (추상 CC0·DSP 합성 전면 폐기 ➔ 무료 AI 실사 Foley)**:
  * **주력 생성 엔진**: 공개 Text-to-SFX AI 모델 **`declare-lab/TangoFlux` (`44.1 kHz Stereo`, ZeroGPU)** 기반 장면 맞춤형 원음 18종 직접 생성 (백업 폴백: `fffiloni/AudioGen`).
  * **스마트 임팩트/연속 구간 추출 + 비파괴 마스터링**: 생성 원음 WAV(`tools/source_cache/pit_ai_v3/`)에서 10ms RMS 엔벨로프 기반 최적 버스트만 정밀 커팅 후 **`30 Hz HPF`** 외 인위적 대역 왜곡 금지, 미세 아레나 스테레오 잔향(`3~9% wet`) 및 `-1.0 dBFS` 피크 정규화 적용 (`SFX_PIT_DODGE`는 고역 오버슈트 방지를 위해 `-1.1 dBFS` 보정).
* **v3.0 4대 금지 규격 및 음향 차별화 원칙**:
  1. **절대 금지 5대 요소**: 장난감 클릭(`wooden/switch`), 플라스틱 긁힘(`scrape`), 중세 칼/금속 종소리(`sword_clash/bell/ding` — 공식 링 벨·외벽 철망 제외), 순수 사인파 비프, 농장 닭 울음(`rooster_crow`).
  2. **공격 4대 실사 계통**: `[공1]` 3연속 가죽·살점 타격 쪼기(`0/105/210ms`) · `[공2]` 고속 공기 절단 + 거친 가죽 찢김·바디 슬랩 · `[공3/공4]` 매 날갯짓 3연풍➔체중 급강하 강타 · `[범용/치명타]` 복싱 미트 정타 vs 뼈 파쇄 KO 헤비 블로우.
  3. **방어·패리·스페셜 비(非)금속 차별화**: `[방1 깃털 가드]` 두꺼운 패드·깃털 먹먹한 쿠션 흡수 · `[방3 맞발톱 패리]` 금속 100% 배제 단단한 뼈·각질 정강이 충돌음(`HIT_GEN ↔ GUARD` 유사도 `0.550`) · `[F33 머리잡기]` 거친 깃털·천 클린치 제압 · `[F34 반격]` 깃 파열➔폭발적 가슴 킥 · `[그로기]` 먹먹한 심장 고동+거친 호흡 비틀거림.
  4. **관중 경악(`CROWD_GASP`) 및 승자 콜 분리**: 복싱/MMA KO 순간의 단발 집단 경악 함성(`"OOOOOHHH!!"`) 전면 적용 + `rooster_crow` 폐기 후 KO 승·판정 승 PA 콜 2종 분리.
* **라이선스 고지 및 상용 런칭 전환 경로**:
  * **현재 상태**: `TangoFlux`/`AudioGen` 기반 음원은 **무료 프로토타입·MVP·사내 QA 검증용(Non-Commercial)** 에셋. (`1R~3R`, `벨 2종`, `환호`, `심장박동`, `슬로우 KO`, `BGM`은 기존 CC0/PA 유지)
  * **상용 전환 시**: `tools/generate_pit_sfx_v3.py` 내 18종 프롬프트 사양을 그대로 상용 AI SFX API(ElevenLabs SFX 등) 또는 Sonniss 상용 번들로 1:1 교체 가능.

---

## 2. BGM (배경음악) 사양 및 EQ 카빙 명세

모든 음원 포맷: `Stereo, 44.1 kHz, 192 kbps MP3`, DC 오프셋 제거 및 소프트 리미터 적용.

### 2.1 전투 BGM: BGM_PIT_FIGHT (혈투의 링)
* **에셋 ID**: `BGM_PIT_FIGHT`
* **파일 경로**: [assets/audio/pit/bgm/bgm_pit_fight.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/bgm/bgm_pit_fight.mp3) *(v1 원본 백업: `assets/audio/pit/sfx_v1_backup/bgm_pit_fight_v1.mp3`)*
* **재생시간 / 용량 / 템포**: **172.64초** / **4,046.3 KB** / **150 BPM** (심리스 루프)
* **v2.0~v3.0 EQ 카빙 마스터링**:
  * `35 Hz` 이하 불필요 초저역 HPF 정리 (서브 펀치·슬램과 부밍 충돌 방지).
  * **`2,600 Hz` 중심(`1.5 ~ 4.2 kHz` 대역) `-3.2 dB` 피킹 컷 + `110 Hz` `-1.0 dB` 정리** ➔ 전투 타격 어택과 아나운서 보이스가 BGM을 뚫고 선명하게 돌출되는 믹싱 공간 확보.
  * 피크 `-1.9 dBFS`, RMS `-15.9 dBFS` 마스터링으로 SFX 중첩 시에도 클리핑 0건 유지.

---

## 3. SFX (효과음) 26종 상세 명세

* **음원 저장 디렉터리**: [assets/audio/pit/sfx/](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/) *(구버전 백업: `assets/audio/pit/sfx_v1_backup/`)*
* **원천 음원 구성**: 전투·스페셜·상태·경악 18종은 `declare-lab/TangoFlux` (`44.1kHz Stereo`) 생성 실사 폴리, 라운드(`1R~3R`) 및 승자(`WIN_KO`·`WIN_DECISION`) PA 보이스 5트랙은 `edge_tts` 듀얼 성우, 벨 2종·관중 대환호·투지 심장박동·KO 슬로우는 기존 실녹음/합성 에셋 유지.

### 3.1 공격 기술 효과음 (5종)

| 연번 | SFX 리소스 ID | 오디오 파일명 (Clickable) | 재생시간 | 파일용량 | v3.0 음향 구성 및 특성 | 연동 동작 및 매핑 사양 |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| 1 | `SFX_PIT_HIT_POKE` | [sfx_pit_hit_poke.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_hit_poke.mp3) | 0.50초 | 11.6 KB | 두꺼운 가죽 타격 AI 원음 1타(`0.20s`) 기반 저·중역 보존 **3연속 빠른 쪼기(`0/105/210ms`)** | `[공1: 전진 부리 속사]` 초고속 3연타 쪼기 |
| 2 | `SFX_PIT_HIT_SPUR` | [sfx_pit_hit_spur.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_hit_spur.mp3) | 0.52초 | 12.2 KB | 빠른 공기 스우시 진입 ➔ 거친 가죽 찢김 + 육중한 바디 슬랩 타격(플라스틱 긁힘 완전 제거) | `[공2: 낮은 발톱 할퀴기]` |
| 3 | `SFX_PIT_HIT_WING` | [sfx_pit_hit_wing.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_hit_wing.mp3) | 0.84초 | 19.6 KB | 거대한 맹금류 3연속 날갯짓 돌풍 ➔ 흙바닥 체중 급강하 바디 슬램 | `[공3: 비상 발톱 급습]`, `[공4: 광폭 발버둥 난타]` |
| 4 | `SFX_PIT_HIT_CRIT` | [sfx_pit_hit_crit.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_hit_crit.mp3) | 0.65초 | 15.3 KB | 뼈·살점 파쇄 헤비급 KO 강타 + 묵직한 서브 바디 충격 | 치명타 강타(`F05`), 가드 브레이크 파열 |
| 5 | `SFX_PIT_HIT_GEN` | [sfx_pit_hit_gen.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_hit_gen.mp3) | 0.42초 | 9.8 KB | 찰지고 단단한 가죽 미트 정타 스냅(Mid `56.2%`, 방어음과 `0.550` 변별) | 다목적 범용 정타(`F03`), 동시 격돌(`Clash`) |

### 3.2 방어 · 회피 · 패링 · 빗나감 효과음 (4종)

| 연번 | SFX 리소스 ID | 오디오 파일명 (Clickable) | 재생시간 | 파일용량 | v3.0 음향 구성 및 특성 | 연동 동작 및 매핑 사양 |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| 6 | `SFX_PIT_GUARD` | [sfx_pit_guard.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_guard.mp3) | 0.47초 | 11.0 KB | 두꺼운 패드·깃털 뭉침에 먹먹하게 흡수되는 쿠션 블록 + 건조한 깃 부스럭 | `[방1: 깃털 부풀려 버티기]` 60% 피해 흡수 |
| 7 | `SFX_PIT_GUARD_GEN` | [sfx_pit_guard_gen.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_guard_gen.mp3) | 0.55초 | 12.9 KB | **금속성 종·칼소리 100% 배제**, 단단한 뼈·각질이 맞부딪혀 튕겨내는 정강이 패리 충돌("딱-퍽!") | `[방3: 맞발톱 쳐내기]` 패링 & 솔리드 블록 |
| 8 | `SFX_PIT_DODGE` | [sfx_pit_dodge.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_dodge.mp3) | 0.39초 | 9.2 KB | 근접 마이크를 스치는 민첩한 저공 공기 스윕 + 빠른 모래 발디딤(Peak `-1.1 dBFS`) | `[방2: 납작 엎드리기]`, `[이5: 측면 사이드 홉]` |
| 9 | `SFX_PIT_MISS` | [sfx_pit_miss.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_miss.mp3) | 0.31초 | 7.3 KB | 타격 바디 없이 허공을 짧고 가볍게 가르는 헛스윙 바람(`0.31초`) | 공격 빗나감 (`F12`, 아트바이블 무진동 큐) |

### 3.3 스페셜 공격·방어 (F33/F34) 시퀀스 효과음 (6종)

| 연번 | SFX 리소스 ID | 오디오 파일명 (Clickable) | 재생시간 | 파일용량 | v3.0 음향 구성 및 특성 | 연동 동작 및 매핑 사양 |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| 10 | `SFX_PIT_GRAB_PIN` | [sfx_pit_grab_pin.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_grab_pin.mp3) | 0.63초 | 14.7 KB | **장난감 클릭 완전 삭제**, 목덜미 천·깃털을 확 움켜쥐고 제압하는 거친 그래플링 클린치 | `[특공 F33-①]` 머리 잡아 고정 (0.2초 유예 시작) |
| 11 | `SFX_PIT_SLAM` | [sfx_pit_slam.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_slam.mp3) | 0.89초 | 20.8 KB | 묵직한 레슬링 바디 슬램이 흙·자갈 바닥에 꽂히는 대충돌 + 자갈·모래 비산 | `[특공 F33-②]` 머리 잡아 바닥 찍기 (`F_SLAM_CLOSE`) |
| 12 | `SFX_PIT_GRAB_MISS` | [sfx_pit_grab_miss.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_grab_miss.mp3) | 0.34초 | 8.0 KB | 허공으로 손을 뻗다 헛잡는 짧은 천 스침 + 바람 스우시(클릭음 제거) | `[특공 F33-③]` 잡기 실패 및 시동 캔슬 시 |
| 13 | `SFX_PIT_GRAB_ESCAPE` | [sfx_pit_grab_escape.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_grab_escape.mp3) | 0.50초 | 11.6 KB | 클린치에서 몸을 틀어 날개·천을 찢으며 빠져나오는 폭발적 회전 스우시 | `[특방 F34-①]` 잡힌 머리 풀기 / 단독 회피 탈출 |
| 14 | `SFX_PIT_BREAK` | [sfx_pit_break.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_break.mp3) | 0.50초 | 11.6 KB | **금속 차임 완전 삭제**, 천·깃 파열 직후 가슴을 정면으로 걷어차는 육중한 역습 바디 킥 | `[특방 F34-②]` 머리 풀고 역습 반격 (`POW × 1.8`) |
| 15 | `SFX_PIT_GROGGY` | [sfx_pit_groggy.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_groggy.mp3) | 1.72초 | 40.4 KB | **비프/사인파 완전 삭제**, 귀가 먹먹하게 잠기는 저역 심장 고동 + 흙바닥 비틀거림·거친 호흡 | `F30` 스탠딩 그로기 / `F33` 플로우 B(`HP < 20%`) |

### 3.4 특수 상태 · 다운 · 벽 충돌 · 슬로우 효과음 (4종)

| 연번 | SFX 리소스 ID | 오디오 파일명 (Clickable) | 재생시간 | 파일용량 | v3.0 음향 구성 및 특성 | 연동 동작 및 매핑 사양 |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| 16 | `SFX_PIT_KNOCKDOWN` | [sfx_pit_knockdown.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_knockdown.mp3) | 0.71초 | 16.5 KB | 힘 풀린 전신이 모래 흙바닥에 무겁게 떨어져 미끄러지는 실사 다운 충격 | 일반 넉다운(`15번`, 2초 후 기상) / 즉시 KO 다운(`13번`) |
| 17 | `SFX_PIT_LAST_STAND` | [sfx_pit_last_stand.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_last_stand.mp3) | 2.59초 | 60.6 KB | 가속 생체 심장박동(`쿵-쿵`) + `55Hz->90Hz` 저역 투지 각성 스웰 라이저 | `Last Stand` 1 HP 투지 생존 발동 시 |
| 18 | `SFX_PIT_WALL_IMPACT` | [sfx_pit_wall_impact.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_wall_impact.mp3) | 0.71초 | 16.5 KB | 목재 판자 외벽 충돌 덤프("덩-!") 직후 아레나 철망 펜스 흔들림 | 원형 아레나 외벽 격돌 (`F31`, `Wall Impact`) |
| 19 | `SFX_PIT_KO_SLOW` | [sfx_pit_ko_slow.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_ko_slow.mp3) | 1.25초 | 29.4 KB | `145Hz -> 34Hz` 타임-슬로우 서브 드롭 + 저역 공기 스윕 | `[특공 F33]` 플로우 A (`HP = 0` 0.4배속 슬로우 KO) |

### 3.5 시스템 · 벨 · 관중 · 승리 PA 보이스 효과음 (6종 + 라운드 보이스 1종 3트랙)

| 연번 | SFX 리소스 ID | 오디오 파일명 (Clickable) | 재생시간 | 파일용량 | v3.0 음향 구성 및 특성 | 연동 동작 및 매핑 사양 |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| 20 | `SFX_PIT_ROUND_START` | [sfx_pit_round1_start.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_round1_start.mp3) | 1.38초 | 32.4 KB | 권투/UFC 링 아나운서 톤 + 아레나 PA 슬랩백 리버브 (1R~3R 완비) | 라운드 시작 순수 보이스 (벨과 완전 분리) |
| 21 | `SFX_PIT_BELL_SINGLE` | [sfx_pit_bell_single.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_bell_single.mp3) | 0.97초 | 22.7 KB | 황동 링 벨 단독 1회 타종 + `650Hz` 바디 공명 + 아레나 잔향 | 라운드 시작(`FIGHT!` 직후) 및 45초 타임오버 |
| 22 | `SFX_PIT_KO_BELL` | [sfx_pit_ko_bell.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_ko_bell.mp3) | 1.80초 | 42.2 KB | 공식 경기 종료 3연속 벨(`Ding! Ding! Ding!`) + 아레나 공간 잔향 | 체력 0 바닥 다운 즉시 KO 경기 종료 확정 |
| 23 | `SFX_PIT_CROWD_ROAR` | [sfx_pit_crowd_roar.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_crowd_roar.mp3) | 3.84초 | 90.0 KB | 실제 경기장 환호 + 함성 스테레오 믹싱, 자연 어택/테일 마감 | KO·판정승 직후 투계장 폭발적 대환호 (`CROWD_ROAR`) |
| 24 | `SFX_PIT_CROWD_GASP` | [sfx_pit_crowd_gasp.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_crowd_gasp.mp3) | 1.67초 | 39.2 KB | **박수 배제 · KO 순간 복싱/MMA 대형 경기장 집단 경악 함성(`"OOOOOHHH!!"`)** (TangoFlux 실사) | 치명타·슬램(`F33`)·반격(`F34`)·이변 순간 (`CROWD_GASP`/`OH`) |
| 25 | `SFX_PIT_WIN_KO` | [sfx_pit_win_ko.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_win_ko.mp3) | 3.53초 | 82.7 KB | **[신설]** 권투 PA 듀얼 보이스: *"KNOCKOUT!! ... It's all over! We have a champion!"* | KO·전의 상실 승리 확정 시 승자 아나운서 콜 (`rooster_crow` 대체) |
| 26 | `SFX_PIT_WIN_DECISION` | [sfx_pit_win_decision.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_win_decision.mp3) | 2.35초 | 55.1 KB | **[신설]** 권투 PA 듀얼 보이스: *"By unanimous decision! ... WE HAVE A WINNER!!"* | 45초 타임오버 판정 승리 확정 시 승자 아나운서 콜 |

---

## 4. 권투·UFC 스타일 라운드 시작 보이스 및 타종 연출 명세

### 4.1 아레나 PA 하이텐션 아나운서 보이스 (1R~3R)
* **보이스 콘셉트**: 구버전 저음 피치 변조 괴수 톤 전면 폐기 ➔ **미국 권투/UFC 링 아나운서 듀얼 조합**(`en-US-ChristopherNeural` 바리톤 라운드 호명 + `en-US-GuyNeural` 하이텐션 `"FIGHT!"` 폭발 샤우팅)에 경기장 PA 방송 체인(`140Hz HPF`, `2.8~3.2kHz` 프레즌스 부스트, 펀치 새츄레이션, 아레나 슬랩백 리버브) 적용.
* **라운드별 순수 음원 목록**:
  * **1라운드**: [sfx_pit_round1_start.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_round1_start.mp3) (`1.38초`, `32.4 KB`) - *"First Round! ... FIGHT!"*
  * **2라운드**: [sfx_pit_round2_start.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_round2_start.mp3) (`1.52초`, `35.5 KB`) - *"Second Round! ... FIGHT!"*
  * **3라운드**: [sfx_pit_round3_start.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_round3_start.mp3) (`1.91초`, `44.7 KB`) - *"Third and Final Round! ... FIGHT!"*

### 4.2 단독 1회 공식 벨소리 독립 타종 연동
* **음원 파일**: [sfx_pit_bell_single.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_bell_single.mp3) (`0.97초`, `22.7 KB`)
* **트리거 규칙**: 라운드 시작 벨 타종 직후 아나운서 보이스 연결 또는 보이스 `"FIGHT!"` 외침 직후 단독 1회 타종, 라운드 45초 타임오버 시 단독 1회 타종.

### 4.3 승리 확정 아나운서 PA 보이스 2종 (KO 승 / 판정 승)
* **교체 배경**: 기존 `sfx_pit_rooster_crow.mp3`가 경기 종료 직후 관중 열기에 찬물을 끼얹는 이질감을 유발함에 따라 파일 완전 폐기 ➔ `1R~3R`과 동일 성우 듀얼 조합(`en-US-GuyNeural` + `en-US-ChristopherNeural`) 및 동일 아레나 PA 방송 체인(`130~140Hz HPF`, `2.8~3.2kHz` 프레즌스, `22ms` 프리딜레이 슬랩백 리버브)으로 **경기 승패 방식별 2종 분리** 제작.
* **승자 보이스 2종 목록**:
  * **KO 승 (`SFX_PIT_WIN_KO`)**: [sfx_pit_win_ko.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_win_ko.mp3) (`3.53초`, `82.7 KB`) — *"KNOCKOUT!! ... It's all over! We have a champion!"* (`F13`, `F14`, `F15` 발동 시 `KO_BELL` + `CROWD_ROAR` 직후 출력)
  * **판정 승 (`SFX_PIT_WIN_DECISION`)**: [sfx_pit_win_decision.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/sfx/sfx_pit_win_decision.mp3) (`2.35초`, `55.1 KB`) — *"By unanimous decision! ... WE HAVE A WINNER!!"* (`F16` 타임오버 판정 종료 시 `BELL_SINGLE` + `CROWD_ROAR` 직후 출력)

---

## 5. 인게임 오디오 믹싱, 고속 덕킹 및 반복 피로도 제어

### 5.1 오디오 우선순위 체계 (Priority Queue)
* `[P0: KO 확정 3연타 벨(KO_BELL) / 스페셜 바닥 찍기(SLAM) / 즉시 KO 다운(KNOCKDOWN)]`
* `[P1: 스페셜 역습 반격(BREAK) / 라운드·승자 PA 보이스(ROUND_START, WIN_KO, WIN_DECISION) / 단독 공식 벨(BELL_SINGLE)]`
* `[P2: 치명타 강타(HIT_CRIT) / 잡기 체결·탈출(GRAB_PIN, GRAB_ESCAPE) / Last Stand 심장박동 / 외벽 격돌]`
* `[P3: 일반 공격(POKE, SPUR, WING, GEN) / 방어·패링·회피·미스(GUARD, GUARD_GEN, DODGE, MISS)]`
* `[P4: EQ 카빙 BGM(BGM_PIT_FIGHT) / 관중 탄성·환호(CROWD_GASP, CROWD_ROAR)]`

### 5.2 고속 사이드체인 덕킹 파라미터 규격 (Attack 8ms)

```mermaid
flowchart LR
    Trg["타격 · 스페셜 · 보이스 트리거"] -->|고속 어택 8ms| Duck["BGM 순간 압착 (-3.5 ~ -10.0 dB)<br>1.5~4.2kHz EQ 카빙으로 공간 선제 확보"]
    Duck --> Play["공/방 시그니처 사운드 클린 돌출"]
    Play -->|릴리즈 220~350ms| Restore["BGM 기본 레벨(-5.2dB) 자연 복귀"]
```

| 트리거 이벤트 | 덕킹 대상 | 감쇄량 (dB) | 어택 타임 | 홀드 타임 | 릴리즈 타임 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **스페셜 바닥 찍기 (`F33`) / 브루탈 KO** | BGM (`bgm_pit_fight`) | **-9.5 ~ -12.0 dB** | 8 ms | 0.85 ~ 1.2 s | 300 ms |
| **스페셜 반격 (`F34`) / 치명타 강타** | BGM (`bgm_pit_fight`) | **-7.0 ~ -7.5 dB** | 8 ms | 0.45 ~ 0.5 s | 240 ms |
| **라운드 보이스 시작** | BGM (`bgm_pit_fight`) | **-7.5 dB** | 15 ms | 1.7 s | 320 ms |
| **일반 타격 / 가드 / 맞발톱 패링** | BGM (`bgm_pit_fight`) | **-3.5 ~ -4.5 dB** | 8 ms | 0.22 ~ 0.35 s | 220 ms |
| **KO 확정 3연타 벨** | BGM 전면 페이드아웃 | **-18.0 dB (종료)** | 50 ms | 2.9 s | 완전 종료 |

### 5.3 다빈도 SFX 엔진 랜덤 변조 규격
* 연속 공격·가드 반복 시 기계적 피로감("머신건 효과") 방지를 위한 Unity 클라이언트 재생 규칙:
  * **피치 랜덤 변조**: 동일 SFX 연속 재생 시 **`±5%` (±0.85 semitone)** 랜덤 피치 시프트 적용.
  * **볼륨 미세 변조**: **`±1.5 dB`** 랜덤 게인 편차 및 좌우 선수 위치 비례 2D 스테레오 패닝(`-0.35 ~ +0.35`) 적용.

---

## 6. 8대 콤보·스페셜 공방 사운드 레이어링 명세

```mermaid
graph TD
    subgraph Combo_Audio_Layering ["8대 콤보 및 스페셜 공방 사운드 레이어링"]
        C1["1. [공4] 광폭 발버둥 난타 + 치명타<br>HIT_WING + HIT_CRIT (0ms 동시)"]
        C2["2. [방3] 맞발톱 쳐내기 패링 & 역습<br>GUARD_GEN ➔ +80ms HIT_SPUR"]
        C3["3. 가드 브레이크 파열 강타<br>GUARD ➔ +50ms HIT_CRIT"]
        C4["4. Last Stand 1 HP ➔ 발톱 역습<br>LAST_STAND ➔ +500ms HIT_SPUR"]
        C5["5. 즉시 KO 피니시 풀 시퀀스<br>KNOCKDOWN ➔ +400ms KO_BELL ➔ +800ms CROWD_ROAR ➔ +1200ms WIN_KO"]
        C6["6. [공1]+[공2] 전진 부리 속사 ➔ 발톱 피니시<br>HIT_POKE ➔ +280ms HIT_SPUR"]
        C7["7. [특공 F33] 머리 잡아 바닥 찍기 (브루탈 KO)<br>GRAB_PIN ➔ +480ms SLAM(+GASP) ➔ +800ms KO_SLOW ➔ KNOCKDOWN ➔ KO_BELL ➔ WIN_KO"]
        C8["8. [특방 F34] 잡힌 머리 풀고 역습 반격 (1.8x)<br>GRAB_PIN ➔ +220ms GRAB_ESCAPE ➔ +380ms BREAK ➔ +400ms WALL_IMPACT(+GASP)"]
    end
```

| 시퀀스 명칭 | 연동 사운드 조합 | 시차(Delay) 규격 | 연출 의도 및 청음 특징 |
| :--- | :--- | :---: | :--- |
| **1. [공4] 광폭 난타 + 치명타** | `HIT_WING` + `HIT_CRIT` | 0ms 동시 출력 | 거대한 맹금류 날갯짓 급강하와 뼈 파쇄 KO 헤비 블로우가 동시 폭발 |
| **2. [방3] 맞발톱 패링 & 역습** | `GUARD_GEN` $\rightarrow$ `HIT_SPUR` | 0ms ➔ +80ms | 단단한 뼈·각질 맞충돌 패리 직후 거친 찢김·바디 슬랩 카운터 |
| **3. 가드 브레이크 파열** | `GUARD` $\rightarrow$ `HIT_CRIT` | 0ms ➔ +50ms | 먹먹한 쿠션 가드 흡수음 직후 헤비 KO 파쇄 타격으로 방어 붕괴 각인 |
| **4. Last Stand 역습** | `LAST_STAND` $\rightarrow$ `HIT_SPUR` | 0ms ➔ +500ms | 생체 심장박동과 각성 라이저 속에서 폭발하는 반격 일격 |
| **5. 즉시 KO 피니시 시퀀스** | `KNOCKDOWN` $\rightarrow$ `KO_BELL` $\rightarrow$ `ROAR` $\rightarrow$ `WIN_KO` | 0 ➔ +400 ➔ +800 ➔ +1200ms | 전신 바닥 충격 ➔ 3연타 벨 ➔ 대환호 ➔ *"KNOCKOUT!!"* 아나운서 콜 |
| **6. [공1]+[공2] 고속 연계** | `HIT_POKE` $\rightarrow$ `HIT_SPUR` | 0ms ➔ +280ms | 3연속 부리 쪼기 가죽 타격 직후 거친 찢김·바디 슬랩 마감 |
| **7. [특공 F33] 머리 잡아 바닥 찍기** | `GRAB_PIN` $\rightarrow$ `SLAM` + `GASP` $\rightarrow$ `KO_SLOW` | 0 ➔ +480ms ➔ +800ms | 거친 깃털 클린치 ➔ 자갈·흙 지면 슬램(+경악 함성) ➔ KO/그로기/넉다운 분기 |
| **8. [특방 F34] 머리 풀고 반격** | `GRAB_PIN` $\rightarrow$ `GRAB_ESCAPE` $\rightarrow$ `BREAK` $\rightarrow$ `WALL` | 0 ➔ +220 ➔ +600 ➔ +1000ms | 클린치 탈출 ➔ 가슴 정면 반격 킥(무금속) ➔ 목재+철망 외벽 격돌 |

---

## 7. 연출 큐 테이블 (cue_table_v6.csv) ↔ 실음원 1:1 매핑표

[cue_table_v6.csv](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/cue_table_v6.csv) 내 격투(`fight`) 및 공통(`any`) 큐 사운드 키와 실제 제작 MP3 파일 간 1:1 연동 매핑 규격:

| 엔진 큐 사운드 키 (`cue_table_v6.csv`) | 매핑 큐 ID | 연결 실음원 파일 (`assets/audio/pit/sfx/`) | 비고 및 엔진 제어 |
| :--- | :--- | :--- | :--- |
| `SFX_Hit_S` | `F03`, `F27` | `sfx_pit_hit_poke.mp3` / `sfx_pit_hit_gen.mp3` | 약공격·속사(`공1`) 및 단발 정타 피치 ±5% 변조 |
| `SFX_Hit_Double` | `F04`, `F27`, `F28`, `F31` | `sfx_pit_hit_spur.mp3` / `sfx_pit_hit_gen.mp3` | 발톱 찢김 타격(`공2`) 및 후속 타격 |
| `SFX_Attack` | `F03`, `F04`, `F05` | `sfx_pit_hit_wing.mp3` / `sfx_pit_hit_gen.mp3` | 도약·광폭 공격(`공3/공4`) |
| `SFX_Crit` | `F05`, `F28` | `sfx_pit_hit_crit.mp3` | 치명타 강타 · 가드 브레이크 파열 |
| `SFX_Miss` | `F12` | `sfx_pit_miss.mp3` | 공격 빗나감 (무진동·저역 배제) |
| `SFX_Whoosh` | `F32`, `H01` | `sfx_pit_dodge.mp3` / `sfx_pit_guard_gen.mp3` | 회피 스우시 및 뼈·각질 맞발톱 패리(`F32`) / 하이라이트 진입 |
| `SFX_Rally` | `F10` | `sfx_pit_last_stand.mp3` | 투혼·위기 극복 심장박동 스웰 |
| `SFX_GrabPin` | `F33` (선행) | `sfx_pit_grab_pin.mp3` | `[특공 F33]` 머리 잡아 깃털 클린치 고정 |
| `SFX_Slam` | `F33` | `sfx_pit_slam.mp3` | `[특공 F33]` 머리 잡아 바닥 쳐박기 본타격 |
| `SFX_GrabEscape` | `F34` (선행) | `sfx_pit_grab_escape.mp3` | `[특방 F34]` 잡힌 머리 회전 탈출 (단독 회피 공용) |
| `SFX_Break` | `F34` | `sfx_pit_break.mp3` | `[특방 F34]` 머리 풀고 역습 1.8x 가슴 카운터 킥 |
| `SFX_Wall` | `F31` | `sfx_pit_wall_impact.mp3` | 원형 아레나 목재+철망 외벽 격돌 (`Wall Impact`) |
| `SFX_Groggy` | `F30`, `F33` 플로우 B | `sfx_pit_groggy.mp3` | 스탠딩 그로기 1.72초 저역 심장 고동 + 거친 호흡 비틀거림 |
| `SFX_Ko` | `F13`, `F14` | `sfx_pit_knockdown.mp3` + `sfx_pit_ko_bell.mp3` | 바닥 다운 충격 + 즉시 KO 3연타 벨 (`F33` 플로우 A 시 `sfx_pit_ko_slow.mp3` 선행) |
| `SFX_Bell` | `F16`, `F17` | `sfx_pit_bell_single.mp3` | 라운드 개시·종료·판정·무승부 단독 1회 벨 |
| `SFX_Fight` | `G07` | `sfx_pit_round1_start.mp3` ~ `round3_start.mp3` | 라운드별 권투 PA 보이스 + 단독 1회 벨 |
| `SFX_Win` | `F13`, `F14`, `F15`, `F16`, `H02` | `sfx_pit_win_ko.mp3` (KO `F13~F15`) / `sfx_pit_win_decision.mp3` (판정 `F16`) | 기존 `SFX_Win` 키 호환 분기 — KO·전의 상실 시 `win_ko`, 판정 시 `win_decision` 재생 (`H02` 결과 화면 승자 콜) |
| `CROWD_ROAR` | `F05`, `F08`, `F13~F16`, `F34`, `H02` | `sfx_pit_crowd_roar.mp3` | 폭발적 투계장 대환호 |
| `CROWD_GASP` / `CROWD_OH` / `CROWD_SWELL` | `F01`, `F02`, `F06`, `F07`, `F09`, `F11`, `F18`, `F28`, `F29`, `F31`, `F33`, `H03` | `sfx_pit_crowd_gasp.mp3` | KO·슬램 순간 경기장 집단 경악 함성(`"OOOOOHHH!!"`, `F28/F29` 등 게인 조절) |
| *(보이스/카운트/입장)* | `G01`, `G02`, `G04~G06` | 공통 UI/카운트 비프 또는 추후 확장 슬롯 | `sfx_pit_dodge.mp3`(등장 스윕) 등 임시 대체 가능 |

---

## 8. 1라운드 실전 사운드 시뮬레이션 샘플 사양 및 시나리오

1라운드 실전 격투 전체(EQ 카빙 BGM, 관중 앰비언스, 1회 벨, 권투 PA 라운드 보이스, AI 실사 일반 공/방·뼈 각질 패리 대비, `[특방 F34]` 머리 풀고 역습+외벽+경악 함성, 치명타+그로기+투지 버티기, `[특공 F33]` 머리 잡아 바닥 찍기+슬로우+즉시 KO 3연타 벨+`WIN_KO` 아나운서 콜)를 압축 검증하는 마스터 시뮬레이션 트랙.

* **오디오 파일 경로**: [assets/audio/pit/demo/demo_pit_round1_simulation.mp3](file:///d:/OneDrive/%EC%97%85%EB%AC%B4_%EC%A7%84%ED%96%89/C/ROOSTER%20RUMBLE/assets/audio/pit/demo/demo_pit_round1_simulation.mp3)
* **트랙 재생시간 / 파일용량**: **38.03초** / **891.4 KB** (`44.1 kHz, 192 kbps Stereo MP3`)
* **마스터링 측정치**: 피크 `-1.3 dBFS`, 실효치 RMS `-17.6 dBFS`, 고속 사이드체인 덕킹(`Attack 8ms`)으로 전 공방 SFX 명료도 확보.

### 8.1 가상 1라운드 세부 타임라인 (38.03초)

* **00.0s ~ 04.0s [오프닝 & 권투 PA 라운드 개시]**:
  * `0.00s`: 투계장 관중 앰비언스 진입 + EQ 카빙 전투 BGM 페이드인.
  * `0.60s`: 경기 시작 단독 1회 공식 벨(`SFX_PIT_BELL_SINGLE`) 타종.
  * `1.30s`: 권투/UFC PA 아나운서 1R 보이스(`SFX_PIT_ROUND_START`: *"First Round! ... FIGHT!"*, BGM `-7.5dB` 덕킹).
* **04.5s ~ 11.5s [일반 공방 & AI 실사 방어·패리 대비 강조]**:
  * `4.50s`: Red 코너 `[공1]` 전진 부리 속사 3연타 (`SFX_PIT_HIT_POKE`, `0.50초`, 좌측 패닝 `-0.28`).
  * `5.20s`: Blue 코너 `[방1]` 깃털 부풀려 버티기 (`SFX_PIT_GUARD`, `0.47초`, 먹먹한 패드+깃털 흡수).
  * `6.55s`: Blue 코너 `[공3/공4]` 비상 발톱 급습 3연속 돌풍 강타 (`SFX_PIT_HIT_WING`, `0.84초`, 우측 패닝 `+0.25`).
  * `7.55s`: Red 코너 `[방3]` 맞발톱 쳐내기 패리 (`SFX_PIT_GUARD_GEN`, `0.55초`, 무금속 뼈·각질 충돌).
  * `8.15s`: Red 코너 `[방2]` 납작 엎드리기 회피 (`SFX_PIT_DODGE`) ➔ `8.65s` `[공2]` 낮은 발톱 할퀴기 반격 (`SFX_PIT_HIT_SPUR`).
  * `9.75s`: 공격 빗나감 (`SFX_PIT_MISS`) ➔ `10.30s` 범용 정타 적중 (`SFX_PIT_HIT_GEN`).
* **12.3s ~ 16.0s [스페셜 공방 1: `[특방 F34]` 머리 풀고 역습 반격]**:
  * `12.35s`: Blue 코너 특수 잡기 시동 ➔ 거친 깃털 클린치 제압 (`SFX_PIT_GRAB_PIN`).
  * `12.82s`: Red 코너 깃털 파열 회전 탈출 (`SFX_PIT_GRAB_ESCAPE`).
  * `13.22s`: **역전 1.8x 가슴 카운터 킥 폭발 (`SFX_PIT_BREAK`, 무금속, BGM `-7.0dB` 고속 덕킹)**.
  * `13.78s`: 피격자 1.5m 밀려나며 목재+철망 외벽 격돌 (`SFX_PIT_WALL_IMPACT`) + `13.95s` 경기장 집단 경악 함성 (`SFX_PIT_CROWD_GASP`).
* **17.2s ~ 25.5s [치명타 · 스탠딩 그로기 · 투지 버티기]**:
  * `17.20s`: 범용 정타 (`SFX_PIT_HIT_GEN`) ➔ `18.00s` **뼈 파쇄 KO 치명타 강타 (`SFX_PIT_HIT_CRIT`, BGM `-7.5dB` 덕킹)**.
  * `18.60s`: 피격자 먹먹한 심장 고동 + 비틀거리는 호흡 그로기 (`SFX_PIT_GROGGY`, `1.72초`).
  * `20.60s`: 체력 1 생존 투지 버티기 발동 (`SFX_PIT_LAST_STAND`, 생체 심장박동 + 각성 스웰).
  * `23.50s` ~ `24.30s`: 최후의 발톱 할퀴기 (`SFX_PIT_HIT_SPUR`) vs 깃털 가드 버티기 (`SFX_PIT_GUARD`).
* **26.7s ~ 38.0s [스페셜 공방 2: `[특공 F33]` 머리 잡아 바닥 찍기 ➔ 브루탈 KO + `WIN_KO` 콜]**:
  * `26.75s`: Red 코너 머리 잡아 깃털 클린치 고정 (`SFX_PIT_GRAB_PIN`).
  * `27.28s`: **레슬링 흙·자갈 바닥 대충돌 슬램 (`SFX_PIT_SLAM`, BGM `-9.5dB` 덕킹)** + `27.55s` 경기장 경악 함성 (`SFX_PIT_CROWD_GASP`).
  * `28.15s`: 0.4배속 브루탈 KO 타임-슬로우 서브 스윕 (`SFX_PIT_KO_SLOW`).
  * `29.05s`: 전신 모래 바닥 넉다운 (`SFX_PIT_KNOCKDOWN`) ➔ `29.65s` **즉시 KO 3연타 벨 (`SFX_PIT_KO_BELL`)** & BGM 페이드아웃.
  * `30.40s` ~ `38.03s`: 투계장 대환호 (`SFX_PIT_CROWD_ROAR`) + `31.85s` **KO 승리 PA 아나운서 콜 (`SFX_PIT_WIN_KO`: *"KNOCKOUT!! It's all over! We have a champion!"*)** 마감.

---

## 9. 리소스 관리 및 디렉터리 구조

```text
assets/audio/pit/
├── bgm/                                # [격투 전용 EQ 카빙 배경음악]
│   └── bgm_pit_fight.mp3               # 150 BPM 배틀 오케스트라 (1.5~4.2kHz -3.2dB 카빙, 172.64s)
├── demo/                               # [격투 실전 사운드 시뮬레이션 데모]
│   └── demo_pit_round1_simulation.mp3  # v3.0 1R 풀 시뮬레이션 (AI 실사 폴리 + WIN_KO 마감, 38.03s, 891.4 KB)
├── sfx/                                # [v3.0 AI 실사 폴리 + 승자 PA 보이스 26종 (총 28개 MP3 + 보드)]
│   ├── pit_sfx_soundboard.html         # 럼블 핏 v3.0 인터랙티브 사운드보드 (7대 개선 비교 바 · A/B 비교)
│   ├── sfx_pit_hit_poke.mp3            # [공1] AI 실사 가죽 타격 기반 3연속 쪼기 (0.50s, 11.6 KB)
│   ├── sfx_pit_hit_spur.mp3            # [공2] AI 실사 가죽 찢김 + 바디 슬랩 (0.52s, 12.2 KB)
│   ├── sfx_pit_hit_wing.mp3            # [공3/공4] AI 실사 맹금류 3연풍 + 체중 급강하 (0.84s, 19.6 KB)
│   ├── sfx_pit_hit_crit.mp3            # [치명타] AI 실사 뼈 파쇄 KO 헤비 블로우 (0.65s, 15.3 KB)
│   ├── sfx_pit_hit_gen.mp3             # [범용] AI 실사 복싱 미트 정타 (0.42s, 9.8 KB)
│   ├── sfx_pit_guard.mp3               # [방1] AI 실사 패드·깃털 쿠션 가드 흡수 (0.47s, 11.0 KB)
│   ├── sfx_pit_guard_gen.mp3           # [방3] AI 실사 무금속 뼈·각질 맞발톱 패리 (0.55s, 12.9 KB)
│   ├── sfx_pit_dodge.mp3               # [방2/이5] AI 실사 저공 스우시 + 모래 디딤 (0.39s, 9.2 KB)
│   ├── sfx_pit_miss.mp3                # [빗나감] AI 실사 허공 단발 헛스윙 (0.31s, 7.3 KB)
│   ├── sfx_pit_grab_pin.mp3            # [특공 F33-①] AI 실사 깃털·천 클린치 제압 (0.63s, 14.7 KB)
│   ├── sfx_pit_slam.mp3                # [특공 F33-②] AI 실사 흙·자갈 바닥 레슬링 슬램 (0.89s, 20.8 KB)
│   ├── sfx_pit_grab_miss.mp3           # [특공 F33-③] AI 실사 헛잡기 천 스침 (0.34s, 8.0 KB)
│   ├── sfx_pit_grab_escape.mp3         # [특방 F34-①] AI 실사 날개·천 회전 탈출 (0.50s, 11.6 KB)
│   ├── sfx_pit_break.mp3               # [특방 F34-②] AI 실사 무금속 가슴 반격 킥 (0.50s, 11.6 KB)
│   ├── sfx_pit_groggy.mp3              # [그로기 F30] AI 실사 심장 고동 + 호흡 비틀거림 (1.72s, 40.4 KB)
│   ├── sfx_pit_knockdown.mp3           # [다운] AI 실사 전신 모래 바닥 낙하 (0.71s, 16.5 KB)
│   ├── sfx_pit_last_stand.mp3          # 투지 버티기 1 HP 생체 심장박동 (2.59s, 60.6 KB)
│   ├── sfx_pit_wall_impact.mp3         # [외벽 F31] AI 실사 목재 판자 + 철망 격돌 (0.71s, 16.5 KB)
│   ├── sfx_pit_ko_slow.mp3             # [슬로우 F33-A] 0.4배속 브루탈 KO 타임드롭 (1.25s, 29.4 KB)
│   ├── sfx_pit_bell_single.mp3         # 단독 1회 공식 링 벨 (0.97s, 22.7 KB)
│   ├── sfx_pit_ko_bell.mp3             # 즉시 KO 확정 3연타 벨 (1.80s, 42.2 KB)
│   ├── sfx_pit_crowd_roar.mp3          # 투계장 열광 대환호 CROWD_ROAR (3.84s, 90.0 KB)
│   ├── sfx_pit_crowd_gasp.mp3          # [교체] AI 실사 경기장 집단 경악 함성 CROWD_GASP (1.67s, 39.2 KB)
│   ├── sfx_pit_win_ko.mp3              # [신규] KO 승 PA 아나운서 콜 SFX_PIT_WIN_KO (3.53s, 82.7 KB)
│   ├── sfx_pit_win_decision.mp3        # [신규] 판정 승 PA 아나운서 콜 SFX_PIT_WIN_DECISION (2.35s, 55.1 KB)
│   ├── sfx_pit_round1_start.mp3        # 권투 PA 1라운드 시작 보이스 (1.38s, 32.4 KB)
│   ├── sfx_pit_round2_start.mp3        # 권투 PA 2라운드 시작 보이스 (1.52s, 35.5 KB)
│   └── sfx_pit_round3_start.mp3        # 권투 PA 3라운드 시작 보이스 (1.91s, 44.7 KB)
└── sfx_v1_backup/                      # [A/B 비교 검증용 v1.2 구버전 원본 백업]
    ├── bgm_pit_fight_v1.mp3
    ├── demo_pit_round1_simulation.mp3
    └── sfx_pit_*.mp3 (16개 원본)
```
