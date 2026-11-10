# ROOSTER RUMBLE — 산출물 웹보드 & 디렉터리 아카이브

이 디렉터리는 **ROOSTER RUMBLE** 프로젝트의 확정된 최종 산출물(기획서, 사운드보드, 그래픽 스크린샷, 3D 데모, 마스터 데이터)을 웹에서 열람할 수 있도록 구성된 GitHub Pages 배포용 정적 웹사이트입니다.

모든 파일은 웹보드의 좌측 메뉴 및 하부 분류와 동일한 물리적 폴더 구조로 정리되어 있습니다.

---

## 📁 디렉터리 구조 안내

```
docs/
├── index.html                  # 웹보드 메인 포털 SPA (사이드바 대시보드)
├── board_data.js / .json       # 자동 생성된 카탈로그 메타데이터
├── assets/                     # 공용 오디오(BGM/SFX/Voice) 및 이미지 에셋
│
├── common/                     # 🌟 공통 / 통합 (Integrated)
│   ├── core/                   # 📑 핵심 기획 & 플로우 (통합 MVP 구성안, 플로우차트 등)
│   ├── data/                   # 📊 마스터 데이터 & 밸런스 (데이터 테이블, 볼륨 산정서 등)
│   └── qa/                     # 📋 QA 검수 & 발표 자료 (체크리스트, 모드 소개, PT 멘트 등)
│
├── race/                       # 🏇 Derby Race (경주 모드)
│   ├── docs/                   # 📑 기획 & 순위/배당 규칙 (MVP 기획서, 순위 산출 공식 등)
│   ├── audio/                  # 🔊 사운드보드 & 성우 보이스 (사운드보드, 청음보드, BGM)
│   ├── visuals/                # 🖼️ 인게임 스크린샷 갤러리 (중계, 로비, 카운트다운, 결과)
│   ├── demo/                   # 🎮 3D 레이스 시뮬레이터 데모 (derby-race-demos)
│   └── data/                   # 📊 연출 큐 & 카메라 데이터 (cue_table, camera_frames 등)
│
├── pit/                        # 🥊 Rumble Pit (격투 모드)
│   ├── docs/                   # 📑 기획 & 전투 공식/동작 (MVP 기획서, 전투 판정 규칙 등)
│   ├── audio/                  # 🔊 SFX 사운드보드 & BGM (효과음 보드, 전투 BGM)
│   ├── visuals/                # 🖼️ 매치업 & 전투 UI 스샷 (대진표, 베팅 슬립, 액션 등)
│   └── demo/                   # 🎮 웹 로비 UI 인터랙티브 데모
│
└── farm/                       # 🌾 Rumble Farm (농장 모드)
    └── docs/                   # 📑 육성 & 교배 기획서 (Rumble Farm MVP 기획서)
```

---

## 🚀 GitHub Pages 배포 안내
1. GitHub 저장소 **Settings > Pages** 메뉴로 이동합니다.
2. **Build and deployment > Branch**를 `main` 브랜치, 폴더를 `/docs`로 설정 후 **Save**합니다.
3. 배포 URL(`https://<계정명>.github.io/<저장소명>/`)로 전 세계 어디서든 브라우저로 접속 가능합니다.

---

## 🔄 동기화 방법 (원본 수정 및 신규 문서 추가 시)
프로젝트 상위 디렉터리에서 `sync_webboard.bat`를 더블클릭하거나 아래 명령을 실행합니다:
```bash
python sync_webboard.py
```
- 수정된 파일만 자동으로 복사(스마트 증분 동기화)됩니다.
- 신규 파일도 자동으로 분석되어 해당 하부 폴더로 자동 분류 복사됩니다.
- HTML 파일이 하위 폴더로 복사될 때 에셋 상대경로(`assets/` → `../../assets/`)가 자동 보정됩니다.
