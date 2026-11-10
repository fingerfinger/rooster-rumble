import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('ROOSTER RUMBLE QA 체크리스트.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all qa-card blocks
cards = re.findall(r'<div class="qa-card">(.*?)</div>\s*</div>', text, re.DOTALL)
print(f"Total cards regex: {len(cards)}")

# Better: iterate through lines or structure
items = []
current_mode = ""
current_cat = ""

for line in text.splitlines():
    if '<div class="mode-title">' in line:
        current_mode = re.search(r'>([^<]*)<', line).group(1).strip()
    elif '<div class="cat-header">' in line:
        current_cat = re.search(r'>([^<]*)<', line).group(1).strip()
    elif '<span class="qa-badge">' in line:
        badge = re.search(r'>([^<]*)<', line).group(1).strip()
        items.append({
            'mode': current_mode,
            'cat': current_cat,
            'badge': badge,
            'q': '',
            'desc': ''
        })
    elif '<div class="qa-question">' in line and items:
        q = re.search(r'>([^<]*)<', line).group(1).strip()
        items[-1]['q'] = q
    elif '<div class="qa-desc">' in line and items:
        desc = re.search(r'>([^<]*)<', line).group(1).strip()
        items[-1]['desc'] = desc

print(f"Successfully parsed items: {len(items)}")
for i, it in enumerate(items):
    print(f"{i+1:02d}. [{it['mode'][:10]}] [{it['cat']}] [{it['badge']}] {it['q']}")
