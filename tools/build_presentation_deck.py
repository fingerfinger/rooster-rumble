import re
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# Read source HTML
src_html_path = "ROOSTER RUMBLE 모드 요약 소개.html"
with open(src_html_path, "r", encoding="utf-8") as f:
    content = f.read()

# Read the base CSS from style_block_1.css
with open("style_block_1.css", "r", encoding="utf-8") as f:
    base_css = f.read()

# Import the extracted accurate slides
from extract_slides_accurate import slides

non_qa = [s for s in slides if not s['is_qa']]
total_slides = len(non_qa)
print(f"Total non-QA slides to assemble: {total_slides}")

# Print-specific Landscape CSS
print_css = f"""
    @page {{
      size: 297mm 210mm;
      margin: 0;
    }}
    
    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    
    html, body {{
      width: 297mm;
      margin: 0;
      padding: 0;
      background: #0b0f17;
      color: #f1f3f5;
      font-family: -apple-system, BlinkMacSystemFont, 'Malgun Gothic', '맑은 고딕', 'Pretendard', 'Segoe UI', Roboto, sans-serif;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
      font-size: 13.5px;
      line-height: 1.5;
    }}
    
    /* Each slide is an exact A4 Landscape page */
    .slide-page {{
      width: 297mm;
      height: 210mm;
      max-width: 297mm;
      max-height: 210mm;
      padding: 8mm 12mm;
      box-sizing: border-box;
      background: #0b0f17;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      page-break-after: always;
      break-after: page;
      page-break-inside: avoid;
      overflow: hidden;
      position: relative;
    }}
    
    .slide-page:last-child {{
      page-break-after: auto;
      break-after: auto;
    }}
    
    .pt-slide-frame {{
      width: 100%;
      height: 100%;
      box-sizing: border-box;
      background: #14171e;
      border: 1px solid #262c38;
      border-radius: 14px;
      padding: 22px 32px 16px 32px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 0 16px 50px rgba(0, 0, 0, 0.7);
      overflow: hidden;
      position: relative;
    }}
    
    /* Header layout */
    .slide-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      border-bottom: 1px solid #232a36;
      padding-bottom: 10px;
    }}
    .slide-category {{
      font-size: 0.76rem;
      font-weight: 800;
      color: #f59e0b;
      letter-spacing: 0.8px;
      margin-bottom: 3px;
      text-transform: uppercase;
    }}
    .slide-title {{
      font-size: 1.58rem;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: -0.5px;
      line-height: 1.25;
    }}
    .slide-subtitle {{
      font-size: 0.90rem;
      color: #94a3b8;
      font-weight: 500;
    }}
    .slide-page-badge {{
      font-size: 0.82rem;
      font-weight: 800;
      color: #f59e0b;
      background: #1c1917;
      border: 1px solid rgba(245, 158, 11, 0.35);
      padding: 3px 10px;
      border-radius: 6px;
      letter-spacing: 0.5px;
      white-space: nowrap;
    }}
    
    /* Body flex */
    .slide-body {{
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      overflow: hidden;
      min-height: 0;
    }}
    
    /* Footer layout */
    .slide-footer-meta {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: #475569;
      font-size: 0.76rem;
      font-weight: 600;
      letter-spacing: 0.6px;
      margin-top: 10px;
      padding-top: 8px;
      border-top: 1px solid #1c222e;
    }}
    
    /* Hide zoom hints in print/deck */
    .zoom-hint {{
      display: none !important;
    }}
    
    /* Optimized thumbnail heights for full slide balance */
    .pt-shots-grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      height: 100%;
    }}
    .pt-shot-card-large {{
      background: #171b22;
      border: 1px solid #2a313e;
      border-radius: 10px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      height: 100%;
    }}
    .pt-shot-thumb-large {{
      width: 100%;
      height: 295px !important;
      background: #000;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }}
    .pt-shot-thumb-large img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}
    .pt-shot-info-large {{
      padding: 12px 16px !important;
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      background: #171b22;
    }}
    
    .pt-shots-grid-3 {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 14px;
      height: 100%;
    }}
    .pt-shot-card-medium {{
      background: #171b22;
      border: 1px solid #2a313e;
      border-radius: 10px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      height: 100%;
    }}
    .pt-shot-thumb-medium {{
      width: 100%;
      height: 275px !important;
      background: #000;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }}
    .pt-shot-thumb-medium img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: top center;
    }}
    .pt-shot-info-medium {{
      padding: 10px 14px !important;
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      background: #171b22;
    }}
    
    /* Cover slide styling */
    .cover-slide-content {{
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      align-items: center;
      text-align: center;
      padding: 24px 0 10px 0;
    }}
    .cover-badge {{
      background: rgba(245, 158, 11, 0.15);
      color: #f59e0b;
      border: 1px solid rgba(245, 158, 11, 0.35);
      font-size: 0.85rem;
      font-weight: 800;
      padding: 5px 16px;
      border-radius: 20px;
      display: inline-block;
      letter-spacing: 1px;
    }}
    .cover-title {{
      font-size: 3.4rem;
      font-weight: 900;
      letter-spacing: -1px;
      color: #ffffff;
      margin: 14px 0 6px 0;
      background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .cover-sub {{
      font-size: 1.25rem;
      color: #94a3b8;
      font-weight: 600;
      margin-bottom: 26px;
    }}
    .cover-specs {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      width: 100%;
      max-width: 900px;
      margin-bottom: 20px;
    }}
    .cover-spec-card {{
      background: #171c26;
      border: 1px solid #283344;
      border-radius: 12px;
      padding: 20px 16px;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
    }}
    .cover-spec-card h5 {{
      font-size: 1.15rem;
      font-weight: 800;
      color: #f59e0b;
      margin-bottom: 10px;
    }}
    .cover-spec-card p {{
      font-size: 0.88rem;
      color: #94a3b8;
      line-height: 1.6;
    }}
    
    /* Table styling for Slide 14 */
    .data-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 14px;
      font-size: 0.86rem;
    }}
    .data-table th, .data-table td {{
      padding: 9px 12px;
      border: 1px solid #262f3f;
      text-align: left;
    }}
    .data-table th {{
      background: #19202c;
      color: #f59e0b;
      font-weight: 700;
    }}
    .data-table tr:nth-child(even) td {{
      background: #131720;
    }}
"""

assembled_slides_html = []

for i, s in enumerate(non_qa):
    page_num = i + 1
    badge_str = f"{page_num:02d} / {total_slides:02d}"
    
    slide_raw = s['html']
    
    # 1. Update slide-page-badge
    slide_raw = re.sub(r'<div class="slide-page-badge">[^<]*</div>', f'<div class="slide-page-badge">{badge_str}</div>', slide_raw)
    
    # 2. Update footer page number
    if page_num == 1:
        # Cover slide:
        slide_raw = re.sub(r'<div class="slide-page-badge">[^<]*</div>', f'<div class="slide-page-badge">{badge_str}</div>', slide_raw)
        footer_sub = f"""
        <div class="slide-footer-meta" style="width: 100%;">
          <span>ROOSTER RUMBLE SPEC DECK</span>
          <span>{badge_str}</span>
        </div>
        """
        slide_raw = re.sub(r'<div class="slide-footer-meta">.*?</div>', footer_sub, slide_raw, flags=re.DOTALL)
    else:
        slide_raw = re.sub(r'(<span>ROOSTER RUMBLE SPEC DECK</span>\s*<span>)\s*\d{2}\s*/\s*\d{2}(\s*</span>)', rf'\g<1>{badge_str}\g<2>', slide_raw)
    
    # 3. For the last slide (formerly Slide 23, now Slide 15):
    if page_num == total_slides:
        slide_raw = slide_raw.replace('9. 게임 페이지 바로가기', '8. 게임 페이지 바로가기')
        slide_raw = slide_raw.replace('data-title="9. 게임 바로가기"', 'data-title="8. 게임 바로가기"')
        if badge_str not in slide_raw:
            slide_raw = re.sub(r'<div class="slide-footer-meta">.*?</div>', f'<div class="slide-footer-meta"><span>ROOSTER RUMBLE SPEC DECK</span><span>{badge_str}</span></div>', slide_raw, flags=re.DOTALL)
            
    # 4. Remove PT-specific classes that hide or display block ('pt-slide active')
    slide_raw = re.sub(r'<div class="pt-slide[^"]*"', '<div class="pt-slide-frame"', slide_raw, count=1)
    
    # Wrap in slide-page
    page_html = f"""
    <!-- Slide Page {page_num:02d} -->
    <section class="slide-page" id="slide-{page_num:02d}">
      {slide_raw}
    </section>
    """
    assembled_slides_html.append(page_html)

full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>ROOSTER RUMBLE 모드 요약 소개 (프레젠테이션)</title>
  <style>
{base_css}

{print_css}
  </style>
</head>
<body>
{''.join(assembled_slides_html)}
</body>
</html>
"""

output_html_file = "ROOSTER RUMBLE 모드 요약 소개 (프레젠테이션).html"
with open(output_html_file, "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"Successfully generated: {output_html_file}")
print(f"File size: {os.path.getsize(output_html_file)} bytes")
