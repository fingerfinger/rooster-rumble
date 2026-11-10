import sys

sys.stdout.reconfigure(encoding='utf-8')

html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ROOSTER RUMBLE - PT 발표 멘트 요약 가이드</title>
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: #131b2e;
      --card-border: #232f48;
      --primary: #38bdf8;
      --accent: #f59e0b;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --highlight: #38bdf8;
      --tag-bg: rgba(56, 189, 248, 0.12);
      --tag-border: rgba(56, 189, 248, 0.3);
    }
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Pretendard', 'Noto Sans KR', sans-serif;
      line-height: 1.75;
      padding: 0;
    }
    /* Sticky Navigation */
    .top-nav {
      position: sticky;
      top: 0;
      background: rgba(11, 15, 25, 0.95);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--card-border);
      padding: 12px 24px;
      z-index: 1000;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    .nav-title {
      font-size: 1.05rem;
      font-weight: 800;
      color: var(--primary);
      letter-spacing: -0.5px;
    }
    .nav-quick-list {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .nav-btn {
      background: #1e293b;
      color: var(--text-muted);
      border: 1px solid var(--card-border);
      padding: 4px 9px;
      border-radius: 4px;
      font-size: 0.78rem;
      text-decoration: none;
      font-weight: 600;
      transition: all 0.15s ease;
    }
    .nav-btn:hover {
      background: var(--primary);
      color: #0b0f19;
      border-color: var(--primary);
    }

    /* Container */
    .container {
      max-width: 960px;
      margin: 0 auto;
      padding: 32px 20px 80px;
    }

    /* Document Header */
    .doc-header {
      background: linear-gradient(135deg, #131b2e 0%, #1e293b 100%);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 28px 32px;
      margin-bottom: 32px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    .doc-badge {
      display: inline-block;
      background: rgba(245, 158, 11, 0.15);
      border: 1px solid rgba(245, 158, 11, 0.35);
      color: var(--accent);
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 700;
      margin-bottom: 12px;
    }
    .doc-header h1 {
      font-size: 1.8rem;
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 8px;
      letter-spacing: -0.5px;
    }
    .doc-header p {
      color: var(--text-muted);
      font-size: 0.95rem;
    }

    /* Slide Card */
    .script-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 24px 28px;
      margin-bottom: 24px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.2);
      scroll-margin-top: 80px;
    }
    .script-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid rgba(255,255,255,0.08);
      padding-bottom: 12px;
      margin-bottom: 16px;
    }
    .slide-num-badge {
      background: rgba(56, 189, 248, 0.15);
      border: 1px solid rgba(56, 189, 248, 0.3);
      color: var(--primary);
      padding: 4px 12px;
      border-radius: 6px;
      font-size: 0.88rem;
      font-weight: 800;
      letter-spacing: 0.5px;
    }
    .slide-num-badge.qa {
      background: rgba(245, 158, 11, 0.15);
      border-color: rgba(245, 158, 11, 0.3);
      color: var(--accent);
    }
    .slide-title-text {
      font-size: 1.15rem;
      font-weight: 700;
      color: #ffffff;
    }

    /* Screen Summary Box */
    .screen-summary {
      background: rgba(15, 23, 42, 0.6);
      border-left: 3px solid var(--primary);
      border-radius: 4px;
      padding: 10px 14px;
      margin-bottom: 16px;
      font-size: 0.88rem;
      color: var(--text-muted);
    }
    .screen-summary strong {
      color: #e2e8f0;
    }

    /* Speech Content */
    .speech-box {
      background: #182235;
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 8px;
      padding: 18px 22px;
      margin-bottom: 14px;
    }
    .speech-label {
      font-size: 0.8rem;
      font-weight: 800;
      color: var(--primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .speech-body {
      font-size: 1.05rem;
      color: #f8fafc;
      line-height: 1.85;
      word-break: keep-all;
    }
    .speech-body b, .speech-body strong {
      color: #38bdf8;
      font-weight: 700;
    }
    .speech-body mark {
      background: rgba(245, 158, 11, 0.25);
      color: #fef3c7;
      padding: 2px 6px;
      border-radius: 3px;
    }

    /* Key Point */
    .key-point {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      font-size: 0.86rem;
      color: var(--accent);
      background: rgba(245, 158, 11, 0.08);
      padding: 8px 14px;
      border-radius: 6px;
    }

    /* Print styles */
    @media print {
      body {
        background: #ffffff;
        color: #111827;
      }
      .top-nav {
        display: none;
      }
      .script-card {
        background: #ffffff;
        border: 1px solid #d1d5db;
        box-shadow: none;
        page-break-inside: avoid;
        margin-bottom: 20px;
      }
      .speech-box {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
      }
      .speech-body {
        color: #1f2937;
      }
      .speech-body b, .speech-body strong {
        color: #0369a1;
      }
      .slide-title-text {
        color: #111827;
      }
      .screen-summary {
        background: #f3f4f6;
        color: #4b5563;
      }
    }
  </style>
</head>
<body>

  <!-- Sticky Top Quick Navigation -->
  <nav class="top-nav">
    <div class="nav-title">🎙️ ROOSTER RUMBLE PT 멘트 요약 (총 23 슬라이드)</div>
    <div class="nav-quick-list">
      <a href="#s01" class="nav-btn">S01 표지</a>
      <a href="#s02" class="nav-btn">S02 개요</a>
      <a href="#s03" class="nav-btn">S03 원화1</a>
      <a href="#s04" class="nav-btn">S04 원화2</a>
      <a href="#s05" class="nav-btn">S05 화풍1</a>
      <a href="#s06" class="nav-btn">S06 화풍2</a>
      <a href="#s07" class="nav-btn">S07 경주사양</a>
      <a href="#s08" class="nav-btn">S08 경주실황1</a>
      <a href="#s09" class="nav-btn">S09 경주실황2</a>
      <a href="#s10" class="nav-btn">S10 경주실황3</a>
      <a href="#s11" class="nav-btn">S11 격투사양</a>
      <a href="#s12" class="nav-btn">S12 격투실황1</a>
      <a href="#s13" class="nav-btn">S13 격투실황2</a>
      <a href="#s14" class="nav-btn">S14 모드비교</a>
      <a href="#s15" class="nav-btn">S15 경주QA1</a>
      <a href="#s16" class="nav-btn">S16 경주QA2</a>
      <a href="#s17" class="nav-btn">S17 경주QA3</a>
      <a href="#s18" class="nav-btn">S18 경주QA4</a>
      <a href="#s19" class="nav-btn">S19 격투QA1</a>
      <a href="#s20" class="nav-btn">S20 격투QA2</a>
      <a href="#s21" class="nav-btn">S21 격투QA3</a>
      <a href="#s22" class="nav-btn">S22 격투QA4</a>
      <a href="#s23" class="nav-btn">S23 바로가기</a>
    </div>
  </nav>

  <div class="container">

    <!-- Header -->
    <div class="doc-header">
      <div class="doc-badge">SPEAKER NOTES GUIDE</div>
      <h1>ROOSTER RUMBLE 발표 멘트 요약 가이드</h1>
      <p>총 23개 프레젠테이션 슬라이드별 핵심 발표 스크립트 및 화면 요약 정리 문서입니다. 발표 현장에서 직관적인 리딩 및 진행 가이드로 활용하시기 바랍니다.</p>
    </div>

    <!-- Slide 01 -->
    <div id="s01" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 01 · 표지</div>
        <span class="slide-num-badge">01 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> 게임 타이틀(ROOSTER RUMBLE) 및 듀얼 모드(Derby Race: 30초 쾌속 경주, Rumble Pit: 1v1 실시간 격투) 핵심 사양 카드
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "안녕하십니까. 수탉(Rooster) 캐릭터 기반의 신작 스포츠 경주 및 격투 시뮬레이션 게임, <b>ROOSTER RUMBLE(루스터 럼블)</b>의 프로젝트 요약 소개를 시작하겠습니다.<br><br>
          본 게임은 6마리가 트랙을 전력 질주하는 30초 쾌속 회전의 <b>Derby Race(경주 모드)</b>와, 1대1 대전의 박진감 및 실시간 인플레이 변동 배당을 즐길 수 있는 <b>Rumble Pit(격투 모드)</b>의 듀얼 모드로 구성되어 있습니다. 오늘 발표에서는 핵심 게임 사양과 비주얼 컨셉, 그리고 실무 검증을 위한 QA 체크리스트를 순서대로 말씀드리겠습니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 경주(30초 쾌속 회전율)와 격투(실시간 인플레이 베팅)의 차별화된 듀얼 모드 구조 강조</span>
      </div>
    </div>

    <!-- Slide 02 -->
    <div id="s02" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 02 · 1. 프로젝트 개요</div>
        <span class="slide-num-badge">02 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> 기본 명세(HTML5/WebGL, 무설치, 24시간 자동 운영), 2대 모드 포지셔닝, <b>시연 버전 개발 기준 및 피드백 반영 방향</b>(안정성 최우선, 시연 그래픽, 피드백 기반 룰·연출 고도화)
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "프로젝트 개요입니다. ROOSTER RUMBLE은 별도 앱 설치 없이 PC와 모바일 브라우저, 웹뷰에서 즉시 구동되는 <b>WebGL 기반 웹 표준 게임</b>입니다. 서버 스케줄러를 통해 24시간 무인으로 경기가 자동 생성되고 베팅과 정산이 진행됩니다.<br><br>
          여기서 가장 중요하게 말씀드릴 점은, <mark>현재 준비된 게임 시연 버전은 게임 판정 알고리즘과 배팅 시스템의 안정성을 최우선으로 검증하기 위해 구현</mark>되었다는 점입니다. 그래픽 역시 피드백 수렴을 위한 시연용 버전이며, 경기 세부 룰이나 그래픽/연출 컨셉 등 변동성이 큰 부분들은 오늘 공유드리는 QA 체크리스트와 여러분의 의견을 적극 반영하여 순차적으로 완성도를 높여갈 예정입니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 시연 버전은 '시스템 안정성 최우선'으로 구현되었으며, 그래픽 및 세부 룰은 피드백을 통해 고도화 예정임을 명확히 주지</span>
      </div>
    </div>

    <!-- Slide 03 -->
    <div id="s03" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 03 · 2. 캐릭터 그래픽 스타일 및 원화 (1/4)</div>
        <span class="slide-num-badge">03 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> 기획 원화 레퍼런스 01 (다크 파이터), 02 (3D 컨셉 시트)
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "다음은 캐릭터 그래픽 스타일 및 원화 레퍼런스입니다.<br><br>
          좌측의 <b>다크 파이터</b>는 검붉은 깃털과 단단하게 발달한 근육질 골격을 지닌 헤비급 투계 원형 레퍼런스입니다. 묵직한 체급과 강력한 한방 파워를 직관적으로 상징합니다.<br><br>
          우측의 <b>3D 컨셉 시트</b>는 실제 3D 모델링 제작을 위한 전신 비례, 볏과 깃털 텍스처, 관절 구조 가이드라인을 규정한 원화로, 카툰풍 실루엣과 볼륨감을 안정적으로 확립하는 기준이 됩니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 캐릭터의 골격 비례와 체급별 특성을 규정하는 탄탄한 기준 원화 확보</span>
      </div>
    </div>

    <!-- Slide 04 -->
    <div id="s04" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 04 · 2. 캐릭터 그래픽 스타일 및 원화 (2/4)</div>
        <span class="slide-num-badge">04 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> 기획 원화 레퍼런스 03 (3D 턴어라운드), 04 (정통 투계 3D), 05 (원형 아레나 FX)
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "원화 레퍼런스 후반 3종입니다.<br><br>
          첫 번째 <b>3D 턴어라운드 모델</b>은 360도 전 방향에서의 조형과 라이팅 셰이딩을 검증하여 클로즈업 연출에서도 시각적 결함이 없도록 점검한 시안입니다.<br><br>
          두 번째 <b>정통 투계 3D 모델</b>은 날렵하고 긴 다리와 슬림한 동체를 갖추어 빠른 공격과 회피 모션에 최적화된 골격을 보여줍니다.<br><br>
          세 번째 <b>원형 아레나 배틀 FX</b>는 링 내부 충돌 시 발생하는 섬광, 모래 먼지 폭발 등 현장감 넘치는 격투 긴장감을 시각화한 연출 레퍼런스입니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 3D 모델의 360도 완성도와 격투 현장 연출 FX의 방향성 제시</span>
      </div>
    </div>

    <!-- Slide 05 -->
    <div id="s05" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 05 · 2. 캐릭터 그래픽 스타일 및 원화 (3/4)</div>
        <span class="slide-num-badge">05 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> 핵심 캐릭터 화풍 스타일 01 (카툰 렌더 - SPIKE), 02 (동글동글 큐트)
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "다음은 본 프로젝트의 핵심 화풍 스타일 5종 중 첫 2종입니다.<br><br>
          좌측의 <b>카툰 렌더 스타일(SPIKE)</b>은 선명한 외곽선과 채도 높은 셀셰이딩을 적용했습니다. 옷을 입히는 식의 과도한 의인화를 배제하고 수탉 본연의 깃털과 부리, 볏 골격을 살려 <b>6마리 다자간 경주 트랙에서도 선수의 시각적 식별성이 가장 뛰어납니다.</b><br><br>
          우측의 <b>동글동글 큐트 스타일</b>은 친근한 숏바디/치비 비율과 부드러운 깃털 결감으로, 전연령층과 여성 라이트 유저에게 부담 없이 다가갈 수 있는 비폭력적 스타일입니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 카툰 렌더의 높은 트랙 식별성 vs 큐트 스타일의 대중적 친근감 비교</span>
      </div>
    </div>

    <!-- Slide 06 -->
    <div id="s06" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 06 · 2. 캐릭터 그래픽 스타일 및 원화 (4/4)</div>
        <span class="slide-num-badge">06 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> 핵심 캐릭터 화풍 스타일 03 (정통 싸움닭), 04 (실사풍 극사실), 05 (디지털 사이버)
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "화풍 스타일 후반 3종입니다.<br><br>
          첫 번째 <b>정통 싸움닭(RAGNAROK)</b>은 매서운 눈빛과 긴 목 깃털, 날카로운 발톱을 극대화하여 격투/투계 매니아층을 겨냥한 압도적인 야성미와 긴장감을 전달합니다.<br><br>
          두 번째 <b>실사풍 극사실 3D</b>는 정밀한 깃털 광택과 피부 주름 질감을 극대화하여 실제 스포츠 중계를 보는 듯한 고급 시뮬레이션 감성을 제공합니다.<br><br>
          세 번째 <b>디지털 사이버</b>는 기하학적 로우폴리곤 면과 네온 발광 아이를 결합한 미래형 비주얼로, VIP 프리미엄 스킨이나 특별 테마 트랙에 최적화된 조형입니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 타깃 유저층과 경기 테마에 따라 확장 가능한 5종의 다채로운 비주얼 스펙트럼</span>
      </div>
    </div>

    <!-- Slide 07 -->
    <div id="s07" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 07 · 3. Derby Race 경기 사양</div>
        <span class="slide-num-badge">07 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> 6마리 트랙 주행, 30초 레이스 루프, 단승/복승 베팅, 5단계 컨디션 보정, 동적 카메라 연출
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "지금부터는 모드별 상세 사양입니다. 먼저 <b>Derby Race(경주 모드)</b>입니다.<br><br>
          경기당 약 30초 내외로 전력 질주하는 초스피드 루프를 가지며, 유저는 <b>단승식(1위 적중)</b>과 <b>복승식(1, 2위 순위 무관 적중)</b> 베팅을 즐길 수 있습니다.<br><br>
          각 선수는 최고속도, 가속도, 근성 스탯과 함께 <b>5단계 컨디션 보정</b>을 실시간으로 받아 매 경기 흥미진진한 순위 역전이 발생하며, 3D 동적 트랙 카메라와 상단 순위 UI로 관전 몰입감을 극대화합니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 30초 쾌속 회전 루프와 컨디션 기반의 역동적 레이스 밸런스</span>
      </div>
    </div>

    <!-- Slide 08 -->
    <div id="s08" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 08 · 4. Derby Race 화면 실황 (1/3)</div>
        <span class="slide-num-badge">08 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> [스샷 1] 오픈 베팅 로비(향후 3경기 편성, 마감 카운트다운), [스샷 2] 경기 임박 관전 대기(00:04 마감, 원터치 입장 CTA)
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "경주 모드의 실제 인게임 화면 실황입니다.<br><br>
          좌측 <b>오픈 베팅 로비</b>에서는 향후 예정된 3개 경기의 출전 선수 명단, 배당률, 직전 경기 요약을 한눈에 파악하고 베팅할 수 있습니다.<br><br>
          우측 화면은 <b>마감 4초 전 카운트다운 화면</b>으로, 긴박한 마감 알림과 함께 경기장으로 원터치 입장할 수 있는 직관적인 CTA 버튼을 제공하여 유저의 관전 전환을 매끄럽게 유도합니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 연속 3경기 사전 편성으로 끊김 없는 베팅 회전율 유도</span>
      </div>
    </div>

    <!-- Slide 09 -->
    <div id="s09" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 09 · 4. Derby Race 화면 실황 (2/3)</div>
        <span class="slide-num-badge">09 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> [스샷 3] 3D 라이브 질주 실황(순위 볼 & 완주 진행도 게이지바), [스샷 4] 공식 순위 및 배당금 정산(랩타임, 배당 정산, 리플레이)
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "실제 레이스 진행과 결과 정산 화면입니다.<br><br>
          좌측 <b>3D 인게임 실황 화면</b>에서는 6마리 선수가 트랙을 질주하며, 상단 헤더에 실시간 1위부터 6위까지의 순위 볼과 결승선까지의 완주 진행도 게이지바가 표시되어 한눈에 전황을 읽을 수 있습니다.<br><br>
          우측 <b>결과 정산 화면</b>에서는 결승선 통과 랩타임 기준 공식 1~6위 순위와 당첨 배당금이 즉시 자동 정산되며, 바로 리플레이를 다시 볼 수 있는 버튼이 제공됩니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 실시간 순위 볼 UI의 시인성과 결승 통과 즉시 이루어지는 투명한 자동 정산</span>
      </div>
    </div>

    <!-- Slide 10 -->
    <div id="s10" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 10 · 4. Derby Race 화면 실황 (3/3)</div>
        <span class="slide-num-badge">10 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> [스샷 5] 내 배팅 현황(Active Bets, 배당률, 추가 베팅), [스샷 6] 경기 히스토리(Completed Races, 회차 정보, 다시보기)
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "경주 모드의 유저 데이터 관리 화면입니다.<br><br>
          좌측 <b>내 배팅 현황</b>에서는 현재 활성화된 베팅 내역과 회차별 예상 배당금을 실시간으로 조회하고 추가 베팅을 진행할 수 있습니다.<br><br>
          우측 <b>경기 히스토리</b>에서는 완료된 이전 회차들의 트랙 정보와 경기 결과, 배당률 이력을 투명하게 검토할 수 있으며, 언제든지 지난 경기의 3D 리플레이를 다시 재생하여 결과를 검증할 수 있습니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 지난 경기 리플레이 및 베팅 히스토리 완전 제공을 통한 신뢰도 확보</span>
      </div>
    </div>

    <!-- Slide 11 -->
    <div id="s11" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 11 · 5. Rumble Pit 경기 사양</div>
        <span class="slide-num-badge">11 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> 1v1 대전 격투, 45~60초 라운드제, 실시간 인플레이(In-Play) 변동 배당(종료 5초 전 락), 7종 공수 기술 및 파이트 머니
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "다음은 1대1 대전 모드인 <b>Rumble Pit(격투 모드)</b>입니다.<br><br>
          원형 피트 안에서 45초에서 60초 동안 양측 파이터가 치열한 공방을 펼칩니다. 본 모드의 가장 핵심적인 차별점은 <b>실시간 인플레이(In-Play) 변동 배당</b>입니다. 경기 중 파이터의 잔여 HP와 다운 상태에 따라 실시간으로 배당률이 변동하며, 경기 종료 5초 전까지 추가 베팅이 가능합니다.<br><br>
          7종의 공격/방어 기술과 3연속 콤보 연산 시스템을 갖추고 있으며, 승리 코너 배당금 외에 출전 파이터에게도 파이트 머니가 지급되는 구조입니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 경기 도중 실시간 잔여 HP에 연동되는 라이브 변동 배당의 압도적 몰입감</span>
      </div>
    </div>

    <!-- Slide 12 -->
    <div id="s12" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 12 · 6. Rumble Pit 화면 실황 (1/2)</div>
        <span class="slide-num-badge">12 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> [스샷 A] 1v1 매치업 로비(파이터 프로필, 스탯, 사전 배당률), [스샷 B] 프리매치 베팅 슬립 패널(코너 선택, 칩 단위 베팅 확정)
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "격투 모드의 실제 화면 실황입니다.<br><br>
          좌측 <b>1v1 매치업 로비</b>에서는 레드 코너와 블루 코너 파이터의 프로필과 체급, 공격력/방어력 스탯, 사전 배당률을 정밀하게 비교 분석할 수 있습니다.<br><br>
          우측 <b>베팅 슬립 모달</b>은 유저가 원하는 승리 코너를 원터치로 선택하고 직관적인 칩 단위로 빠르고 간편하게 베팅을 확정할 수 있도록 설계된 UI입니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 양측 파이터 전력 비교의 직관성과 초보자도 쉬운 원터치 칩 베팅 UX</span>
      </div>
    </div>

    <!-- Slide 13 -->
    <div id="s13" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 13 · 6. Rumble Pit 화면 실황 (2/2)</div>
        <span class="slide-num-badge">13 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> [스샷 C] 1v1 3D 인게임 격투 액션(원형 피트 공방, 실시간 추가 베팅), [스샷 D] 최종 결과 판정 및 정산(KO/판정 승리, 배당금 정산)
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "격투 인게임 실황 및 결과 판정 화면입니다.<br><br>
          좌측 <b>3D 액션 관전 화면</b>에서는 원형 피트 안에서 타격 공방을 주고받는 액션을 실시간으로 감상하며, 화면 하단의 실시간 라이브 배당판을 통해 우세한 코너에 즉시 추가 베팅을 넣을 수 있습니다.<br><br>
          우측 <b>결과 정산 화면</b>에서는 최종 KO 또는 타임아웃 판정에 따라 승리 코너가 확정되고 즉시 당첨금이 정산되는 공식 결과 내역을 명확하게 보여줍니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 3D 타격 관전과 실시간 추가 베팅이 한 화면에서 매끄럽게 연결되는 완성도</span>
      </div>
    </div>

    <!-- Slide 14 -->
    <div id="s14" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 14 · 7. 모드 비교 및 기술 사양</div>
        <span class="slide-num-badge">14 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> Derby Race vs Rumble Pit 상세 비교표(인원, 경기시간, 베팅구조, 판정방식, 운영목적) 및 단일 WebGL 웹 기술 스펙
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "두 모드의 비교 및 기술 사양 요약입니다.<br><br>
          <b>Derby Race</b>는 30초의 빠른 턴과 사전 예측 중심으로 회전율을 극대화하며, <b>Rumble Pit</b>은 1분 내외의 라운드 동안 전황 분석과 실시간 인플레이 중간 베팅으로 박진감을 극대화합니다. 서로 다른 유저 성향을 상호 보완하는 강력한 듀얼 루프 구조입니다.<br><br>
          기술적으로는 <b>HTML5와 WebGL 기반의 단일 클라이언트</b>로 구현되어 PC나 모바일 어떤 기기에서도 다운로드 없이 브라우저에서 즉각 구동되는 최고의 접근성을 자랑합니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 회전율 중심(경주)과 분석 몰입감 중심(격투)의 상호 보완 시너지</span>
      </div>
    </div>

    <!-- Slide 15 -->
    <div id="s15" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 15 · 8. QA 체크 리스트 - Derby Race (1/4)</div>
        <span class="slide-num-badge qa">15 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> ■ I. 타깃 시장 & 비주얼 아트 / ■ II. 캐릭터 모션 (문항 01~04)<br>
        01 북미 타깃 적합성, 02 배경/캐릭터 대비(잔디 트랙 타당성), 03 트랙 환경 다양화(날씨/시간대), 04 캐릭터 모션 세분화
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "지금부터는 실제 게임 완성도 고도화를 위한 실무 QA 체크리스트입니다. 앞서 말씀드린 대로 현재 시연 버전의 안정성을 바탕으로 여러분의 전문적인 의견을 수렴하고자 합니다.<br><br>
          첫 페이지에서는 <b>미국 북미 시장의 문화적 친숙도 및 선호 화풍</b>, <b>현재 모래 트랙 대비 향후 잔디 트랙 추가 도입에 대한 타당성</b>, <b>우천/석양/야간 조명 등 환경 변화 시의 관전 시인성 저해 여부</b>, 그리고 <b>기본 질주 외에 스타트 대기나 골인 후 감속 등 세부 모션의 추가 적용 범위</b>에 대해 의견을 구합니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 북미 시장 감성 적합성, 잔디 트랙 도입 타당성 및 모션 다양화 수준 검토</span>
      </div>
    </div>

    <!-- Slide 16 -->
    <div id="s16" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 16 · 8. QA 체크 리스트 - Derby Race (2/4)</div>
        <span class="slide-num-badge qa">16 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> ■ II. 주행 규칙 / ■ III. 카메라 연출 & 판정 (문항 05~08)<br>
        05 주행 이펙트 범위, 06 주행 레인 침범 규정, 07 카메라 워킹 수위, 08 피니시 판정 연출(슬로우 모션 조작 오인)
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "경주 QA 2번째 영역입니다.<br><br>
          현재 시야 방해를 고려해 최소화된 흙먼지 효과 외에 <b>스피드 라인이나 바람 궤적 등 추가 주행 이펙트의 허용 수위</b>, <b>직선 고정 레인 주행 유지 vs 레인 침범(차선 변경) 허용에 따른 돌발 변수와 분석 예측성 간 밸런스 기준</b>, <b>다이내믹 카메라 전환 시 어지러움(멀미) 방지선</b>, 그리고 <b>결승 통과 시 포토 피니시(슬로우 모션) 연출 도입에 따른 실시간성 저해나 조작 오인 가능성</b>에 대한 의견이 필요합니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 레인 침범 시 베팅 분석 신뢰도 영향 및 슬로우모션 조작 오인 방지 밸런스</span>
      </div>
    </div>

    <!-- Slide 17 -->
    <div id="s17" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 17 · 8. QA 체크 리스트 - Derby Race (3/4)</div>
        <span class="slide-num-badge qa">17 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> ■ III. 피니시 판정 / ■ IV. 인게임 UI & 관전 정보 (문항 09~12)<br>
        09 리플레이 분석 정보 실효성, 10 트랙 미니맵 배치 위치, 11 미니맵 순위 변동 이펙트, 12 경기 중 컨디션 표시 방식
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "경주 QA 3번째 영역입니다.<br><br>
          30초 단기 레이스 특성상 <b>리플레이의 역전 마커나 구간 속도 등 상세 데이터 제공이 실제로 유용한지</b>, <b>화면 하단 미니맵이 주행 관전 시야를 방해하지 않고 상단이나 외곽으로 이동할 필요가 있는지</b>, <b>미니맵 상에서 순위 역전 시 적용할 하이라이트 이펙트의 적정 강도</b>, 그리고 <b>베팅 마감 후에도 경기 중 선수의 실시간 컨디션 오라나 아이콘 정보에 유저가 지속적으로 관심을 가지는지</b>를 점검하고자 합니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 30초 숏폼 경주에 맞는 UI 간결성과 미니맵 최적 위치 검증</span>
      </div>
    </div>

    <!-- Slide 18 -->
    <div id="s18" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 18 · 8. QA 체크 리스트 - Derby Race (4/4)</div>
        <span class="slide-num-badge qa">18 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> ■ IV. 관전 정보 / ■ V. 오디오 & 클라이언트 사양 (문항 13~15)<br>
        13 베팅 UI 전반 시인성, 14 아나운서 중계 톤앤매너, 15 모바일 품질/사양 타협 기준
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "경주 QA 마지막 4번째 영역입니다.<br><br>
          <b>베팅 보드의 배당률 표기 및 카운트다운 타이머의 전반적인 시인성</b>, <b>현재 평이한 전통 경마 중계톤 대신 e스포츠 스타일에 맞춘 고조된 과장 중계 보이스 도입 여부</b>, 그리고 <b>저사양 모바일 브라우저 호환을 위한 그래픽 경량화 유지 vs 최소 기기 사양을 상향하여 그래픽 완성도를 높이는 방안 간의 손익</b>에 대해 현업의 현실적인 의견을 구합니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 사운드 중계 톤(경마 vs 게임) 및 모바일 최저 사양 상향 여부 결정</span>
      </div>
    </div>

    <!-- Slide 19 -->
    <div id="s19" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 19 · 8. QA 체크 리스트 - Rumble Pit (1/4)</div>
        <span class="slide-num-badge qa">19 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> ■ I. 그래픽 화풍 & 비주얼 연출 (문항 01~03)<br>
        01 대전 캐릭터 화풍 방향, 02 전투 액션 메커니즘, 03 타격 시각 이펙트 연출
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "다음은 Rumble Pit(격투 모드) QA 체크리스트 총 10문항입니다.<br><br>
          먼저 1페이지에서는 <b>캐릭터 화풍을 대중적인 캐주얼 카툰풍으로 갈지 매니아층 중심의 정통 실사풍으로 갈지</b>, <b>전투 공방 방식을 게임 요소를 강조한 대전 액션으로 할지 실제 닭싸움처럼 킥/발싸움 위주의 사실적 투계 연출로 갈지</b>, 그리고 <b>타격 적중 시 아케이드 히트 섬광과 물리적 깃털/먼지 비산의 적정 배합 비율</b>에 대해 여러분의 피드백을 수렴합니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 아케이드 대전 액션 vs 사실적 투계 연출 간의 비주얼 정체성 확립</span>
      </div>
    </div>

    <!-- Slide 20 -->
    <div id="s20" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 20 · 8. QA 체크 리스트 - Rumble Pit (2/4)</div>
        <span class="slide-num-badge qa">20 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> ■ II. 부상 표현 & 타격 연출 (문항 04~05)<br>
        04 부상 및 선혈(피) 표현 수위(혐오감 완화 고려), 05 히트스톱 연출 및 조작 오인 방지
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "격투 QA 2번째 영역입니다.<br><br>
          <b>타깃 유저의 문화적 취향 및 혐오감 완화를 고려하여 유혈(Blood) 표현을 완전히 배제하고 깃털 손상이나 멍 자국 수준으로 순화하는 방안</b>, 그리고 <b>타격감 강화를 위한 히트스톱(프레임 정지)이나 카메라 흔들림이 실시간 중계의 자연스러움을 해치거나 시스템 조작 의심을 유발하지 않도록 하는 적정 강도 기준</b>에 대한 의견이 필요합니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 혐오감 방지를 위한 피(Blood) 표현 배제 및 히트스톱의 조작 오인 방지선</span>
      </div>
    </div>

    <!-- Slide 21 -->
    <div id="s21" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 21 · 8. QA 체크 리스트 - Rumble Pit (3/4)</div>
        <span class="slide-num-badge qa">21 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> ■ III. 아레나 환경 & 카메라 워킹 (문항 06~08)<br>
        06 경기장 배경 컨셉 및 분위기, 07 방어/그로기 연출과 경기 집중도, 08 다이내믹 카메라 연출 범위
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "격투 QA 3번째 영역입니다.<br><br>
          <b>경기장 배경을 세련된 조명과 펜스를 갖춘 스포츠 링으로 할지 흙바닥과 거친 철망의 언더그라운드 투계장으로 할지</b>, <b>방어(가드) 및 그로기 모션 도입이 경기 속도감을 저해하거나 인위적 승패 조작으로 오인될 소지가 없는지</b>, 그리고 <b>거리 연동 줌인과 로우앵글 등 다이내믹 카메라 워킹의 박진감과 시각적 멀미 방지의 균형선</b>에 대해 의견을 구합니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 스포츠 링 vs 리얼 투계장 환경 컨셉 및 가드/그로기 모션의 조작 오인 배제</span>
      </div>
    </div>

    <!-- Slide 22 -->
    <div id="s22" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 22 · 8. QA 체크 리스트 - Rumble Pit (4/4)</div>
        <span class="slide-num-badge qa">22 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> ■ IV. 전투 규칙 & 베팅 메커니즘 (문항 09~10)<br>
        09 다운 판정 및 카운트다운 규칙, 10 라운드별 추가 베팅 도입 및 형평성
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "격투 QA 마지막 4번째 영역입니다.<br><br>
          <b>파이터 다운 시 판정 처리 방식에 대해 즉시 경기를 종료할 것인지, 아니면 10초 카운트다운과 기립 모션을 도입하여 역전 서스펜스를 살릴 것인지</b>에 대한 규칙 설정, 그리고 <mark>라운드 간 중간 베팅 허용에 따른 배당률 조정이 경기 전 예측 유저의 불만을 유발할 가능성에 대한 의견이 필요합니다. 만약 중간 베팅이 빠진다면 플랫폼의 수수료 수익이 줄어들게 되므로</mark> 이에 대한 절충안을 함께 논의하고자 합니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 다운 판정 룰(즉시 종료 vs 10초 카운트) 및 중간 베팅 형평성과 수수료 수익 밸런스</span>
      </div>
    </div>

    <!-- Slide 23 -->
    <div id="s23" class="script-card">
      <div class="script-header">
        <div class="slide-title-text">Slide 23 · 9. 게임 바로가기</div>
        <span class="slide-num-badge">23 / 23</span>
      </div>
      <div class="screen-summary">
        <strong>🖥️ 화면 구성:</strong> 웹 클라이언트 즉시 접속 URL 링크 배너 및 플랫폼 환경 안내
      </div>
      <div class="speech-box">
        <div class="speech-label">🎙️ 발표 멘트</div>
        <div class="speech-body">
          "마지막으로 게임 바로가기입니다.<br><br>
          화면에 안내된 URL 링크를 통해 지금 바로 PC나 모바일 브라우저에서 실제 작동 중인 <b>ROOSTER RUMBLE 시연 버전</b>을 직접 플레이해보실 수 있습니다.<br><br>
          오늘 발표드린 내용과 QA 체크리스트 항목들을 바탕으로, 여러분의 소중한 피드백을 적극 반영하여 더욱 완성도 높은 게임으로 고도화해 나가겠습니다. 경청해 주셔서 감사합니다. 질의응답 및 피드백 시간을 갖겠습니다."
        </div>
      </div>
      <div class="key-point">
        <span>💡 <strong>핵심 전달:</strong> 실시간 플레이 URL 안내 및 질의응답(Q&A) / 피드백 수렴 전환</span>
      </div>
    </div>

  </div>

</body>
</html>
"""

target_path = r"d:\OneDrive\업무_진행\C\ROOSTER RUMBLE\ROOSTER RUMBLE PT 멘트 요약.html"
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Successfully generated: {target_path}")
print(f"File size: {len(html_content.encode('utf-8'))} bytes")
