import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

html_path = "ROOSTER RUMBLE 모드 요약 소개.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the pt-modal container
pt_viewport_idx = content.find('class="pt-viewport"')
print("pt-viewport index:", pt_viewport_idx)

# Find all pt-slide occurrences
# A pt-slide starts with <div class="pt-slide
pattern = re.compile(r'<div class="pt-slide[^"]*"[^>]*>')
slide_starts = [m.start() for m in pattern.finditer(content)]
print("Total pt-slide starts:", len(slide_starts))

slides = []
for i, start_pos in enumerate(slide_starts):
    # To find matching end div, count div nesting
    pos = start_pos
    depth = 0
    while pos < len(content):
        next_open = content.find('<div', pos)
        next_close = content.find('</div>', pos)
        
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        elif next_close != -1:
            depth -= 1
            pos = next_close + 6
            if depth == 0:
                end_pos = pos
                break
        else:
            end_pos = len(content)
            break
            
    slide_html = content[start_pos:end_pos]
    
    # check title
    title_m = re.search(r'class="slide-title">([^<]*)</div>', slide_html)
    t = title_m.group(1) if title_m else ""
    if not t and "cover-title" in slide_html:
        t = "[Cover]"
    
    is_qa = "qa-slide" in slide_html[:100] or "QA 체크" in t
    
    slides.append({
        'index': i + 1,
        'title': t,
        'is_qa': is_qa,
        'start': start_pos,
        'end': end_pos,
        'html': slide_html
    })

print(f"{'Idx':3s} | {'QA':5s} | {'Len':6s} | {'Title'}")
print("-" * 60)
for s in slides:
    print(f"{s['index']:02d}  | {str(s['is_qa']):5s} | {len(s['html']):6d} | {s['title']}")
