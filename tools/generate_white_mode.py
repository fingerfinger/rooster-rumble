import re
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# Read source HTML
src_html_path = "ROOSTER RUMBLE 모드 요약 소개 (프레젠테이션).html"
with open(src_html_path, "r", encoding="utf-8") as f:
    content = f.read()

white_css = """
    :root {
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --card-sub: #f1f5f9;
      --border: #cbd5e1;
      --text: #0f172a;
      --muted: #64748b;
      --point: #0284c7;
      --red: #e11d48;
      --blue: #2563eb;
    }
    
    @page {
      size: 297mm 210mm;
      margin: 0;
    }
    
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    
    html, body {
      width: 297mm;
      margin: 0;
      padding: 0;
      background: #f1f5f9;
      color: #0f172a;
      font-family: -apple-system, BlinkMacSystemFont, 'Malgun Gothic', '맑은 고딕', 'Pretendard', 'Segoe UI', Roboto, sans-serif;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
      font-size: 13.5px;
      line-height: 1.5;
    }
    
    /* Each slide is an exact A4 Landscape page */
    .slide-page {
      width: 297mm;
      height: 210mm;
      max-width: 297mm;
      max-height: 210mm;
      padding: 8mm 12mm;
      box-sizing: border-box;
      background: #f1f5f9;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      page-break-after: always;
      break-after: page;
      page-break-inside: avoid;
      overflow: hidden;
      position: relative;
    }
    
    .slide-page:last-child {
      page-break-after: auto;
      break-after: auto;
    }
    
    .pt-slide-frame {
      width: 100%;
      height: 100%;
      box-sizing: border-box;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 14px;
      padding: 22px 32px 16px 32px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
      overflow: hidden;
      position: relative;
    }
    
    /* Header layout */
    .slide-header {
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      border-bottom: 2px solid #0284c7;
      padding-bottom: 10px;
    }
    .slide-category {
      font-size: 0.76rem;
      font-weight: 800;
      color: #0284c7;
      letter-spacing: 0.8px;
      margin-bottom: 3px;
      text-transform: uppercase;
    }
    .slide-title {
      font-size: 1.58rem;
      font-weight: 800;
      color: #0f172a;
      letter-spacing: -0.5px;
      line-height: 1.25;
    }
    .slide-subtitle {
      font-size: 0.90rem;
      color: #64748b;
      font-weight: 500;
    }
    .slide-page-badge {
      font-size: 0.82rem;
      font-weight: 800;
      color: #0284c7;
      background: #e0f2fe;
      border: 1px solid #bae6fd;
      padding: 3px 10px;
      border-radius: 6px;
      letter-spacing: 0.5px;
      white-space: nowrap;
    }
    
    /* Body flex */
    .slide-body {
      width: 100%;
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      overflow: hidden;
      min-height: 0;
    }
    
    /* Footer layout */
    .slide-footer-meta {
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: #64748b;
      font-size: 0.76rem;
      font-weight: 600;
      letter-spacing: 0.6px;
      margin-top: 10px;
      padding-top: 8px;
      border-top: 1px solid #e2e8f0;
    }
    
    /* Panels and Grids */
    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }
    .panel {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 16px 20px;
    }
    .panel h4 {
      font-size: 1.05rem;
      font-weight: 800;
      color: #0f172a;
      margin-bottom: 10px;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 6px;
    }
    .clean-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    .clean-list li {
      font-size: 0.88rem;
      color: #334155;
      margin-bottom: 8px;
      line-height: 1.5;
    }
    .clean-list li strong {
      color: #0f172a;
    }
    
    /* Hide zoom hints in print/deck */
    .zoom-hint {
      display: none !important;
    }
    
    /* Shots 2-col */
    .pt-shots-grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      height: 100%;
    }
    .pt-shot-card-large {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      height: 100%;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    .pt-shot-thumb-large {
      width: 100%;
      height: 295px !important;
      background: #f1f5f9;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }
    .pt-shot-thumb-large img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .pt-shot-info-large {
      padding: 12px 16px !important;
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      background: #ffffff;
    }
    .pt-shot-info-large .pt-shot-badge {
      font-size: 0.75rem;
      font-weight: 800;
      color: #0284c7;
      margin-bottom: 4px;
    }
    .pt-shot-info-large .pt-shot-title {
      font-size: 1.02rem;
      font-weight: 800;
      color: #0f172a;
      margin-bottom: 6px;
    }
    .pt-shot-info-large .pt-shot-desc {
      font-size: 0.85rem;
      color: #475569;
      line-height: 1.5;
    }
    
    /* Shots 3-col */
    .pt-shots-grid-3 {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 14px;
      height: 100%;
    }
    .pt-shot-card-medium {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      height: 100%;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    .pt-shot-thumb-medium {
      width: 100%;
      height: 275px !important;
      background: #f1f5f9;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }
    .pt-shot-thumb-medium img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: top center;
    }
    .pt-shot-info-medium {
      padding: 10px 14px !important;
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      background: #ffffff;
    }
    .pt-shot-info-medium .pt-shot-badge {
      font-size: 0.72rem;
      font-weight: 800;
      color: #0284c7;
      margin-bottom: 3px;
    }
    .pt-shot-info-medium .pt-shot-title {
      font-size: 0.96rem;
      font-weight: 800;
      color: #0f172a;
      margin-bottom: 4px;
    }
    .pt-shot-info-medium .pt-shot-desc {
      font-size: 0.82rem;
      color: #475569;
      line-height: 1.45;
    }
    
    /* Cover slide styling (Light Mode) */
    .cover-slide-content {
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      align-items: center;
      text-align: center;
      padding: 24px 0 10px 0;
    }
    .cover-badge {
      background: #e0f2fe;
      color: #0284c7;
      border: 1px solid #bae6fd;
      font-size: 0.85rem;
      font-weight: 800;
      padding: 5px 16px;
      border-radius: 20px;
      display: inline-block;
      letter-spacing: 1px;
    }
    .cover-title {
      font-size: 3.4rem;
      font-weight: 900;
      letter-spacing: -1px;
      color: #0f172a;
      margin: 14px 0 6px 0;
    }
    .cover-sub {
      font-size: 1.25rem;
      color: #475569;
      font-weight: 600;
      margin-bottom: 26px;
    }
    .cover-specs {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      width: 100%;
      max-width: 900px;
      margin-bottom: 20px;
    }
    .cover-spec-card {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      padding: 20px 16px;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
    }
    .cover-spec-card h5 {
      font-size: 1.15rem;
      font-weight: 800;
      color: #0284c7;
      margin-bottom: 10px;
    }
    .cover-spec-card p {
      font-size: 0.88rem;
      color: #475569;
      line-height: 1.6;
    }
    
    /* Table styling for Slide 14 */
    .data-table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 14px;
      font-size: 0.86rem;
    }
    .data-table th, .data-table td {
      padding: 9px 12px;
      border: 1px solid #cbd5e1;
      text-align: left;
    }
    .data-table th {
      background: #f1f5f9;
      color: #0f172a;
      font-weight: 800;
    }
    .data-table td {
      background: #ffffff;
      color: #334155;
    }
    .data-table tr:nth-child(even) td {
      background: #f8fafc;
    }
"""

pages = re.findall(r'(<section class="slide-page"[^>]*>.*?</section>)', content, re.DOTALL)
updated_pages = []

for idx, p in enumerate(pages):
    p_num = idx + 1
    
    # Slide 2: Clean light notice box
    if p_num == 2:
        clean_notice_box = """
          <!-- 시연 버전 개발 기준 및 피드백 반영 방향 -->
          <div style="margin-top: 14px; background: #f0f9ff; border: 1px solid #bae6fd; border-left: 4px solid #0284c7; border-radius: 8px; padding: 12px 16px;">
            <div style="font-size: 0.85rem; font-weight: 800; color: #0369a1; margin-bottom: 8px;">■ 시연 버전 개발 기준 및 피드백 반영 방향</div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
              <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-size: 0.82rem; font-weight: 800; color: #e11d48; margin-bottom: 4px;">🎯 시스템 안정성 최우선</div>
                <div style="font-size: 0.78rem; color: #475569; line-height: 1.45;">게임 시연 버전은 게임 판정 알고리즘과 배팅 시스템의 안정성을 최우선으로 적용됨</div>
              </div>
              <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-size: 0.82rem; font-weight: 800; color: #d97706; margin-bottom: 4px;">🎨 피드백용 그래픽 시연</div>
                <div style="font-size: 0.78rem; color: #475569; line-height: 1.45;">게임 그래픽은 피드백 반영을 위해 시연 버전으로 준비됨</div>
              </div>
              <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-size: 0.82rem; font-weight: 800; color: #0284c7; margin-bottom: 4px;">🔄 피드백 기반 룰·연출 고도화</div>
                <div style="font-size: 0.78rem; color: #475569; line-height: 1.45;">경기 세부 룰 및 그래픽/연출 컨셉 의견에 따라 변동성이 큰 부분은 피드백 반영하며 적용 예정임</div>
              </div>
            </div>
          </div>
        """
        p = re.sub(r'<!-- 시연 버전 개발 기준.*?</div>\s*</div>\s*</div>', clean_notice_box.strip(), p, flags=re.DOTALL)
        
    # Slide 15: Game access card
    if p_num == 15:
        p = p.replace('background: linear-gradient(180deg, #161b24 0%, #10131a 100%); border: 1.5px solid #283344; border-radius: 16px; box-shadow: 0 20px 50px rgba(0,0,0,0.6);',
                      'background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.06);')
        p = p.replace('color: #fff;', 'color: #0f172a;')
        p = p.replace('var(--muted)', '#64748b')
        p = p.replace('background: #10b981; color: #000;', 'background: #0284c7; color: #ffffff;')
        p = p.replace('box-shadow: 0 8px 24px rgba(16, 185, 129, 0.45);', 'box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3);')
        p = p.replace('background: #0a0d12; border: 1px solid #232c3a;', 'background: #f8fafc; border: 1px solid #cbd5e1;')
        p = p.replace('color: #38bdf8;', 'color: #0284c7;')
        
    # Slide 7: steps row background
    p = re.sub(r'background:\s*#161a22;', 'background: #f1f5f9; border: 1px solid #e2e8f0; color: #334155;', p)
    
    # Slide 14: comparison table and panels
    p = p.replace('background: #131720;', 'background: #f8fafc;')
    p = p.replace('background: #171b24;', 'background: #f8fafc;')
    p = p.replace('border: 1px solid #252d3d;', 'border: 1px solid #e2e8f0;')
    p = p.replace('border: 1px solid #232a36;', 'border: 1px solid #e2e8f0;')
    p = p.replace('color: #e2e8f0;', 'color: #0f172a;')
    
    updated_pages.append(p)

white_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>ROOSTER RUMBLE 모드 요약 소개 (화이트 모드)</title>
  <style>
{white_css}
  </style>
</head>
<body>
{''.join(updated_pages)}
</body>
</html>
"""

output_html = "ROOSTER RUMBLE 모드 요약 소개 (화이트).html"
with open(output_html, "w", encoding="utf-8") as f:
    f.write(white_html)

print(f"Generated clean white mode HTML: {output_html}")
