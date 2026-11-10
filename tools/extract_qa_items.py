import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('ROOSTER RUMBLE QA 체크리스트.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's find each qa item
# Search for qa-card structure
pattern = re.compile(r'<div class="qa-card">(.*?)</div>\s*</div>', re.DOTALL)

# Let's see how each item is structured in the HTML
card_starts = [m.start() for m in re.finditer(r'<div class="qa-card">', text)]
print(f"Total qa-card count: {len(card_starts)}")

items = []
for i in range(len(card_starts)):
    start = card_starts[i]
    end = card_starts[i+1] if i+1 < len(card_starts) else text.find('</section>', start)
    chunk = text[start:end]
    
    badge_m = re.search(r'class="qa-badge">([^<]*)<', chunk)
    badge = badge_m.group(1).strip() if badge_m else ""
    
    q_m = re.search(r'class="qa-q">([^<]*)<', chunk)
    q = q_m.group(1).strip() if q_m else ""
    
    desc_m = re.search(r'class="qa-desc">([^<]*)<', chunk)
    desc = desc_m.group(1).strip() if desc_m else ""
    
    items.append({'badge': badge, 'question': q, 'desc': desc})
    print(f"[{badge}] {q}")

print(f"\nTotal parsed: {len(items)}")
