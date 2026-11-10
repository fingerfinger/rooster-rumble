import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('ROOSTER RUMBLE QA 체크리스트.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Split into sections: Derby Race vs Rumble Pit
derby_idx = text.find('Derby Race QA 체크리스트')
rumble_idx = text.find('Rumble Pit QA 체크리스트')

def parse_section(sec_text, mode_name):
    # Find category blocks
    # Category has class="category-title"
    cat_starts = [m.start() for m in re.finditer(r'<div class="category-header">', sec_text)]
    cats = []
    for i in range(len(cat_starts)):
        st = cat_starts[i]
        en = cat_starts[i+1] if i+1 < len(cat_starts) else len(sec_text)
        chunk = sec_text[st:en]
        
        cat_title = re.search(r'<div class="category-title">([^<]*)</div>', chunk)
        cat_t = cat_title.group(1).strip() if cat_title else ""
        
        # Cards inside this category
        card_chunks = re.findall(r'<div class="qa-card">(.*?)</div>\s*</div>', chunk, re.DOTALL)
        items = []
        for c in card_chunks:
            badge = re.search(r'class="qa-badge">([^<]*)</span>', c)
            q = re.search(r'class="qa-question">([^<]*)</div>', c)
            desc = re.search(r'class="qa-desc">([^<]*)</div>', c)
            
            b_txt = badge.group(1).strip() if badge else ""
            q_txt = q.group(1).strip() if q else ""
            d_txt = desc.group(1).strip() if desc else ""
            
            items.append({
                'badge': b_txt,
                'question': q_txt,
                'desc': d_txt
            })
        cats.append({
            'mode': mode_name,
            'category': cat_t,
            'items': items
        })
    return cats

derby_cats = parse_section(text[derby_idx:rumble_idx], "Derby Race (경주)")
rumble_cats = parse_section(text[rumble_idx:], "Rumble Pit (격투)")

all_cats = derby_cats + rumble_cats

total_count = 0
for cat in all_cats:
    print(f"\n[{cat['mode']}] {cat['category']} ({len(cat['items'])}문항)")
    for it in cat['items']:
        total_count += 1
        print(f"  [{it['badge']}] {it['question']}")
        print(f"    - {it['desc']}")

print(f"\n>>> Total items: {total_count}")
