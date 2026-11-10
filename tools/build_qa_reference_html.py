import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("tools/qa_references.json", "r", encoding="utf-8") as f:
    items = json.load(f)

# HTML Generator
html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ROOSTER RUMBLE - QA 레퍼런스 가이드 (영상 및 웹 링크)</title>
  <style>
    :root {{
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --border: #e2e8f0;
      --border-dark: #cbd5e1;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --text-sub: #334155;
      --primary: #0284c7;
      --primary-light: #e0f2fe;
      --derby: #0284c7;
      --rumble: #e11d48;
      --yt-red: #ff0000;
      --gg-blue: #1a73e8;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Malgun Gothic', '맑은 고딕', 'Pretendard', 'Segoe UI', Roboto, sans-serif;
      background-color: var(--bg);
      color: var(--text-main);
      line-height: 1.6;
      font-size: 14.5px;
      padding-bottom: 80px;
    }}

    /* Container */
    .container {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 30px 24px;
    }}

    /* Header */
    .page-header {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 32px 36px;
      margin-bottom: 24px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
      position: relative;
    }}
    .header-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--primary-light);
      color: var(--primary);
      border: 1px solid #bae6fd;
      font-size: 0.8rem;
      font-weight: 800;
      padding: 3px 10px;
      border-radius: 6px;
      margin-bottom: 12px;
      letter-spacing: 0.5px;
    }}
    .page-title {{
      font-size: 1.95rem;
      font-weight: 900;
      color: var(--text-main);
      letter-spacing: -0.8px;
      margin-bottom: 8px;
    }}
    .page-sub {{
      font-size: 0.98rem;
      color: var(--text-muted);
      line-height: 1.6;
    }}
    .header-notice {{
      margin-top: 18px;
      padding: 12px 18px;
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-left: 4px solid #16a34a;
      border-radius: 8px;
      font-size: 0.88rem;
      color: #166534;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    /* Filter Bar */
    .filter-bar {{
      display: flex;
      gap: 10px;
      margin-bottom: 24px;
      position: sticky;
      top: 16px;
      z-index: 100;
      background: rgba(248, 250, 252, 0.92);
      backdrop-filter: blur(8px);
      padding: 8px 0;
    }}
    .filter-btn {{
      background: #ffffff;
      border: 1px solid var(--border-dark);
      padding: 9px 18px;
      border-radius: 8px;
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--text-sub);
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }}
    .filter-btn:hover {{
      border-color: var(--primary);
      color: var(--primary);
      transform: translateY(-1px);
    }}
    .filter-btn.active {{
      background: var(--text-main);
      color: #ffffff;
      border-color: var(--text-main);
      box-shadow: 0 4px 10px rgba(15, 23, 42, 0.25);
    }}
    .filter-count {{
      font-size: 0.76rem;
      background: rgba(0, 0, 0, 0.08);
      padding: 1px 7px;
      border-radius: 12px;
      font-weight: 800;
    }}
    .filter-btn.active .filter-count {{
      background: rgba(255, 255, 255, 0.25);
      color: #ffffff;
    }}

    /* QA Cards List */
    .qa-list {{
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}

    /* QA Item Card */
    .qa-ref-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px 28px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
      transition: border-color 0.2s, box-shadow 0.2s;
    }}
    .qa-ref-card:hover {{
      border-color: #94a3b8;
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.07);
    }}

    /* Card Top Bar */
    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}
    .card-tags {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .mode-badge {{
      font-size: 0.76rem;
      font-weight: 800;
      padding: 3px 9px;
      border-radius: 6px;
      letter-spacing: 0.4px;
    }}
    .mode-badge.derby {{
      background: #e0f2fe;
      color: #0369a1;
      border: 1px solid #bae6fd;
    }}
    .mode-badge.rumble {{
      background: #ffe4e6;
      color: #be123c;
      border: 1px solid #fecdd3;
    }}
    .cat-tag {{
      font-size: 0.78rem;
      color: #475569;
      font-weight: 700;
      background: #f1f5f9;
      padding: 3px 9px;
      border-radius: 6px;
      border: 1px solid #e2e8f0;
    }}
    .qa-item-num {{
      font-size: 0.82rem;
      font-weight: 800;
      color: var(--text-muted);
      letter-spacing: 0.5px;
    }}

    /* Question & Desc */
    .qa-question-text {{
      font-size: 1.15rem;
      font-weight: 800;
      color: var(--text-main);
      line-height: 1.45;
      margin-bottom: 10px;
    }}
    .qa-desc-box {{
      background: #f0f9ff;
      border: 1px solid #bae6fd;
      border-left: 4px solid var(--primary);
      padding: 10px 16px;
      border-radius: 6px;
      font-size: 0.88rem;
      color: #0369a1;
      line-height: 1.55;
      margin-bottom: 16px;
    }}

    /* Insight Box */
    .insight-box {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 12px 18px;
      margin-bottom: 18px;
    }}
    .insight-benchmark {{
      font-size: 0.84rem;
      color: #0f172a;
      font-weight: 700;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .insight-benchmark span {{
      color: #0284c7;
      font-weight: 800;
    }}
    .insight-text {{
      font-size: 0.86rem;
      color: #475569;
      line-height: 1.55;
    }}

    /* Reference Links Grid (2 Columns) */
    .ref-links-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }}
    .ref-link-card {{
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 10px;
      background: #ffffff;
      transition: border-color 0.2s, background-color 0.2s;
    }}
    .ref-link-card.yt {{
      background: #fffafa;
      border-color: #fee2e2;
    }}
    .ref-link-card.yt:hover {{
      border-color: #f87171;
    }}
    .ref-link-card.web {{
      background: #f0f7ff;
      border-color: #dbeafe;
    }}
    .ref-link-card.web:hover {{
      border-color: #60a5fa;
    }}

    .ref-head {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .ref-icon-badge {{
      font-size: 0.74rem;
      font-weight: 800;
      padding: 3px 8px;
      border-radius: 4px;
      white-space: nowrap;
    }}
    .ref-icon-badge.yt {{
      background: #fee2e2;
      color: #dc2626;
      border: 1px solid #fca5a5;
    }}
    .ref-icon-badge.web {{
      background: #dbeafe;
      color: #2563eb;
      border: 1px solid #93c5fd;
    }}
    .ref-title {{
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--text-main);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}

    .ref-buttons {{
      display: flex;
      gap: 8px;
      margin-top: 4px;
    }}
    .ref-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 14px;
      border-radius: 6px;
      font-size: 0.82rem;
      font-weight: 700;
      text-decoration: none;
      transition: all 0.15s ease;
      cursor: pointer;
    }}
    .ref-btn.yt-primary {{
      background: #dc2626;
      color: #ffffff;
      box-shadow: 0 2px 6px rgba(220, 38, 38, 0.25);
    }}
    .ref-btn.yt-primary:hover {{
      background: #b91c1c;
      transform: translateY(-1px);
    }}
    .ref-btn.yt-secondary {{
      background: #ffffff;
      color: #dc2626;
      border: 1px solid #fca5a5;
    }}
    .ref-btn.yt-secondary:hover {{
      background: #fee2e2;
    }}
    .ref-btn.web-primary {{
      background: #2563eb;
      color: #ffffff;
      box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
    }}
    .ref-btn.web-primary:hover {{
      background: #1d4ed8;
      transform: translateY(-1px);
    }}
    .ref-btn.web-secondary {{
      background: #ffffff;
      color: #2563eb;
      border: 1px solid #bfdbfe;
    }}
    .ref-btn.web-secondary:hover {{
      background: #eff6ff;
    }}

    /* Footer */
    .page-footer {{
      margin-top: 40px;
      text-align: center;
      font-size: 0.84rem;
      color: var(--text-muted);
      border-top: 1px solid var(--border);
      padding-top: 24px;
    }}

    @media (max-width: 860px) {{
      .ref-links-grid {{
        grid-template-columns: 1fr;
      }}
      .card-top {{
        flex-direction: column;
        align-items: flex-start;
        gap: 6px;
      }}
    }}
  </style>
</head>
<body>

  <div class="container">
    <!-- Header -->
    <header class="page-header">
      <div class="header-badge">ROOSTER RUMBLE SPEC DECK · BENCHMARK REFERENCE</div>
      <h1 class="page-title">ROOSTER RUMBLE QA 레퍼런스 가이드</h1>
      <p class="page-sub">
        실무 질의 25대 항목(경주 15 + 격투 10)별 논점 분석, 글로벌 대표 게임 및 e스포츠 벤치마킹 타깃, 
        실제 YouTube 공식 트레일러/플레이 영상 및 Google 이미지 검색 레퍼런스 아카이브입니다.
      </p>
      <div class="header-notice">
        <span>💡</span>
        <span>각 항목 카드의 <strong>[YouTube 영상 보기]</strong> 및 <strong>[Google 이미지 검색]</strong> 버튼을 클릭하시면 새 창에서 실제 레퍼런스를 즉시 확인하실 수 있습니다.</span>
      </div>
    </header>

    <!-- Filter Buttons -->
    <div class="filter-bar">
      <button class="filter-btn active" onclick="filterItems('all')">
        전체 항목 <span class="filter-count">25</span>
      </button>
      <button class="filter-btn" onclick="filterItems('Derby Race')">
        🏇 Derby Race (경주) <span class="filter-count">15</span>
      </button>
      <button class="filter-btn" onclick="filterItems('Rumble Pit')">
        🥊 Rumble Pit (격투) <span class="filter-count">10</span>
      </button>
    </div>

    <!-- Cards List -->
    <div class="qa-list" id="qaList">
"""

for item in items:
    mode_class = "derby" if item["mode"] == "Derby Race" else "rumble"
    mode_icon = "🏇" if item["mode"] == "Derby Race" else "🥊"
    
    card_html = f"""
      <article class="qa-ref-card" data-mode="{item['mode']}">
        <div class="card-top">
          <div class="card-tags">
            <span class="mode-badge {mode_class}">{mode_icon} {item['mode']}</span>
            <span class="cat-tag">{item['category']}</span>
          </div>
          <div class="qa-item-num">{item['badge']}</div>
        </div>

        <h2 class="qa-question-text">{item['question']}</h2>

        <div class="qa-desc-box">
          <strong>실무 검증 핵심:</strong> {item['desc']}
        </div>

        <div class="insight-box">
          <div class="insight-benchmark">
            <span>📌 벤치마킹 타깃:</span> {item['benchmark']}
          </div>
          <div class="insight-text">
            <strong>기획 분석:</strong> {item['insight']}
          </div>
        </div>

        <div class="ref-links-grid">
          <!-- YouTube Reference -->
          <div class="ref-link-card yt">
            <div class="ref-head">
              <span class="ref-icon-badge yt">YouTube</span>
              <span class="ref-title" title="{item['youtube_title']}">{item['youtube_title']}</span>
            </div>
            <div class="ref-buttons">
              <a href="{item['youtube_url']}" target="_blank" rel="noopener noreferrer" class="ref-btn yt-primary">
                <span>▶</span> 영상 바로가기
              </a>
              <a href="{item['youtube_search']}" target="_blank" rel="noopener noreferrer" class="ref-btn yt-secondary">
                <span>🔍</span> 관련 영상 검색
              </a>
            </div>
          </div>

          <!-- Web / Image Reference -->
          <div class="ref-link-card web">
            <div class="ref-head">
              <span class="ref-icon-badge web">Google Web</span>
              <span class="ref-title" title="{item['benchmark']}">{item['benchmark']}</span>
            </div>
            <div class="ref-buttons">
              <a href="{item['image_search']}" target="_blank" rel="noopener noreferrer" class="ref-btn web-primary">
                <span>🖼️</span> 이미지 검색 레퍼런스
              </a>
            </div>
          </div>
        </div>
      </article>
    """
    html_content += card_html

html_content += """
    </div>

    <!-- Footer -->
    <footer class="page-footer">
      <p>ROOSTER RUMBLE SPEC DECK · QA 레퍼런스 및 벤치마킹 가이드 문서</p>
      <p style="margin-top: 4px; font-size: 0.8rem; color: #94a3b8;">본 문서는 웹 검색 및 공식 플랫폼의 링크를 통해 기획/디자인 실무 의사결정을 지원합니다.</p>
    </footer>
  </div>

  <script>
    function filterItems(mode) {
      const cards = document.querySelectorAll('.qa-ref-card');
      const buttons = document.querySelectorAll('.filter-btn');

      buttons.forEach(btn => {
        btn.classList.remove('active');
        if (mode === 'all' && btn.textContent.includes('전체')) {
          btn.classList.add('active');
        } else if (mode !== 'all' && btn.textContent.includes(mode)) {
          btn.classList.add('active');
        }
      });

      cards.forEach(card => {
        if (mode === 'all') {
          card.style.display = 'block';
        } else {
          const cardMode = card.getAttribute('data-mode');
          if (cardMode === mode) {
            card.style.display = 'block';
          } else {
            card.style.display = 'none';
          }
        }
      });
    }
  </script>
</body>
</html>
"""

output_path = "ROOSTER RUMBLE QA 레퍼런스 가이드.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully generated: {output_path}")
print(f"Size: {os.path.getsize(output_path)} bytes")
