import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('ROOSTER RUMBLE QA 체크리스트.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect the exact inner structure of qa-card
# Print first 2 cards completely
cards = re.findall(r'<div class="qa-card">(.*?)</div>\s*</div>\s*(?:<!--|</div>|<section)', text, re.DOTALL)
print(f"Cards found by regex: {len(cards)}")

# Or search lines inside qa-card
for m in re.finditer(r'<div class="qa-card">(.*?)(?=<div class="qa-card">|</section>)', text, re.DOTALL):
    chunk = m.group(1)
    badge = re.search(r'class="qa-badge">([^<]*)<', chunk)
    q = re.search(r'class="qa-q">([^<]*)<', chunk)
    desc = re.search(r'class="qa-desc">([^<]*)<', chunk)
    
    b_txt = badge.group(1).strip() if badge else ""
    q_txt = q.group(1).strip() if q else ""
    d_txt = desc.group(1).strip() if desc else ""
    
    # Clean up whitespace
    q_txt = " ".join(q_txt.split())
    d_txt = " ".join(d_txt.split())
    
    print(f"\n--- {b_txt} ---")
    print(f"Q: {q_txt}")
    print(f"Desc: {d_txt}")
