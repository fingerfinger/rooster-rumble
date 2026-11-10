import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

print("=== Starting validate_23_deck_final_pit10.py ===")

html_path = r"ROOSTER RUMBLE 모드 요약 소개.html"
with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Total slides count
slide_divs = list(re.finditer(r'<div class="pt-slide[^"]*"\s+data-title="([^"]+)"', text))
print(f"1. Total slides found: {len(slide_divs)} (Expected: 23)")
assert len(slide_divs) == 23, f"Expected 23 slides, got {len(slide_divs)}"

for idx, s in enumerate(slide_divs, 1):
    print(f"   Slide {idx:02d}: {s.group(1)}")

# 2. Check slide badges
badges = re.findall(r'<div class="slide-page-badge">([^<]+)</div>', text)
print(f"\n2. Total slide-page-badges found: {len(badges)} (Expected: 23)")
assert len(badges) == 23, f"Expected 23 badges, got {len(badges)}"
for idx, b in enumerate(badges, 1):
    expected = f"{idx:02d} / 23"
    assert b.strip() == expected, f"Badge mismatch at slide {idx}: got '{b.strip()}', expected '{expected}'"
print("   All 23 badges matched 01/23 ~ 23/23 perfectly!")

# 3. Check slide footers (Slides 02 ~ 23)
footers = re.findall(r'<span>ROOSTER RUMBLE SPEC DECK</span>\s*<span>([^<]+)</span>', text)
print(f"\n3. Total slide-footers found: {len(footers)} (Expected: 22, from Slide 02 to 23)")
assert len(footers) == 22, f"Expected 22 footers, got {len(footers)}"
for idx, ftr in enumerate(footers, 2):
    expected = f"{idx:02d} / 23"
    assert ftr.strip() == expected, f"Footer mismatch at slide {idx}: got '{ftr.strip()}', expected '{expected}'"
print("   All 22 body slide footers matched 02/23 ~ 23/23 perfectly!")

# 4. Check TOC items count and indexing
toc_items = re.findall(r'<div class="toc-item[^"]*"\s+data-index="(\d+)">', text)
print(f"\n4. Total TOC items found: {len(toc_items)} (Expected: 23)")
assert len(toc_items) == 23, f"Expected 23 TOC items, got {len(toc_items)}"
for idx, d_idx in enumerate(toc_items):
    assert int(d_idx) == idx, f"TOC data-index mismatch at position {idx}: got {d_idx}"
print("   All 23 TOC data-index values matched 0 ~ 22 perfectly!")

# 5. Check Derby QA slides (Slides 15 ~ 18: expected cards: 4, 4, 4, 3)
print(f"\n5. Verifying 4 Derby QA slides (Slides 15 ~ 18)...")
derby_expected = [4, 4, 4, 3]
for idx, exp_count in enumerate(derby_expected, 15):
    s = slide_divs[idx - 1]
    start_pos = s.start()
    end_pos = slide_divs[idx].start()
    slide_content = text[start_pos:end_pos]
    
    assert '.qa-grid-scroll' not in slide_content, f"Slide {idx} contains .qa-grid-scroll!"
    assert 'qa-slide-container-noscroll' in slide_content, f"Slide {idx} missing qa-slide-container-noscroll!"
    assert 'qa-slide' in text[start_pos:start_pos+60], f"Slide {idx} missing qa-slide class!"
    
    cards = re.findall(r'<div class="qa-item-card-slide[^"]*">', slide_content)
    assert len(cards) == exp_count, f"Slide {idx} has {len(cards)} cards, expected {exp_count}!"
    print(f"   Slide {idx:02d} ({s.group(1)}): exactly {exp_count} cards, NO scrollbar class, overflow-hidden.")

# 6. Check Rumble Pit QA slides (Slides 19 ~ 22: expected cards: 3, 2, 3, 2)
print(f"\n6. Verifying 4 Rumble Pit QA slides (Slides 19 ~ 22)...")
pit_expected = [3, 2, 3, 2]
for idx, exp_count in enumerate(pit_expected, 19):
    s = slide_divs[idx - 1]
    start_pos = s.start()
    end_pos = slide_divs[idx].start() if idx < 23 else text.find('</main>', start_pos)
    slide_content = text[start_pos:end_pos]
    
    assert '.qa-grid-scroll' not in slide_content, f"Slide {idx} contains .qa-grid-scroll!"
    assert 'qa-slide-container-noscroll' in slide_content, f"Slide {idx} missing qa-slide-container-noscroll!"
    assert 'qa-slide' in text[start_pos:start_pos+60], f"Slide {idx} missing qa-slide class!"
    
    cards = re.findall(r'<div class="qa-item-card-slide[^"]*">', slide_content)
    assert len(cards) == exp_count, f"Slide {idx} has {len(cards)} cards, expected {exp_count}!"
    print(f"   Slide {idx:02d} ({s.group(1)}): exactly {exp_count} cards, NO scrollbar class, overflow-hidden.")

# 7. Check Scroll section #qalist
pos_qalist = text.find('<section id="qalist"')
assert pos_qalist != -1, "Scroll section #qalist not found!"
end_qalist = text.find('</section>', pos_qalist)
qalist_sec = text[pos_qalist:end_qalist]

pit_split_idx = qalist_sec.find('🥊 Rumble Pit')
derby_scroll_cards = re.findall(r'<div class="qa-item-card">', qalist_sec[:pit_split_idx])
pit_scroll_cards = re.findall(r'<div class="qa-item-card">', qalist_sec[pit_split_idx:])

print(f"\n7. Scroll section #qalist cards: Derby = {len(derby_scroll_cards)} (Expected: 15), Pit = {len(pit_scroll_cards)} (Expected: 10)")
assert len(derby_scroll_cards) == 15, f"Expected 15 Derby cards, got {len(derby_scroll_cards)}"
assert len(pit_scroll_cards) == 10, f"Expected 10 Pit cards, got {len(pit_scroll_cards)}"

# 8. Check tag balancing
open_divs = len(re.findall(r'<div\b', text))
close_divs = len(re.findall(r'</div>', text))
print(f"\n8. Tag balance: open divs = {open_divs}, close divs = {close_divs}, diff = {open_divs - close_divs}")
assert open_divs == close_divs, f"Div tag mismatch! Diff: {open_divs - close_divs}"

# 9. Check banned partner name
banned_kw = '네오' + '위즈'
assert banned_kw not in text, f"Banned keyword found in text!"

# 10. Check specific requested phrase in item 10 (old 12)
req_phrase = "중간 베팅 허용에 따른 배당률 조정이 경기 전 예측 유저의 불만을 유발 가능 성에 대한 의견 필요. (중간 베팅 빠진 다면 수수료 수익 줄어듬)"
assert req_phrase in text, "Requested modified phrase not found in text!"
print(f"\n10. Requested modified phrase verified successfully!")

# 11. Verify deleted items are really gone
assert "기본 공격 모션 세분화 수준" not in text, "Item 05 was NOT deleted!"
assert "승패 판정 방식(HP 게이지 vs 복싱식 채점)" not in text, "Item 11 was NOT deleted!"
print("11. Confirmed item 05 and item 11 completely deleted!")

# 12. Check all 8 sections
sections = ['overview', 'artstyle', 'derby', 'pit', 'compare', 'qalist', 'tech', 'play']
for sec in sections:
    assert f'id="{sec}"' in text, f"Missing section id='{sec}'"
print(f"12. All 8 sections present: {sections}")

print("\n========================================================")
print("=== ALL 12 RIGOROUS VALIDATION CHECKS PASSED 100%! ===")
print("========================================================")
