import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

pt_path = 'ROOSTER RUMBLE PT 멘트 요약.html'
with open(pt_path, 'r', encoding='utf-8') as f:
    text = f.read()

print(f"=== Validating {pt_path} ===")
print(f"File character length: {len(text)}")

# Check 23 slides
cards = re.findall(r'id="s(\d{2})"', text)
print(f"Total script cards found: {len(cards)}")
assert len(cards) == 23, f"Expected 23 cards, got {len(cards)}"
assert cards == [f"{i:02d}" for i in range(1, 24)], f"Card IDs mismatch: {cards}"
print("All 23 cards matched s01 ~ s23 perfectly!")

# Check quick nav buttons
nav_btns = re.findall(r'href="#s(\d{2})"', text)
print(f"Total nav quick jump buttons: {len(nav_btns)}")
assert len(nav_btns) == 23, f"Expected 23 nav buttons, got {len(nav_btns)}"

# Check banned word
banned = '네오' + '위즈'
assert banned not in text, "Banned word found in text!"
print("Banned word check passed: 0 occurrences.")

# Check required user phrases in slide 02
assert "게임 판정 알고리즘과 배팅 시스템의 안정성을 최우선으로" in text
assert "게임 그래픽은 피드백 반영을 위해 시연 버전으로 준비" in text
assert "경기 세부 룰 및 그래픽/연출 컨셉 의견에 따라 변동성이 큰 부분은 피드백 반영하며 적용 예정" in text
print("Slide 02 required phrases verified successfully!")

# Check required user phrase in slide 22
assert "중간 베팅" in text and "수수료 수익" in text
print("Slide 22 intermediate bet phrase verified successfully!")

# Check div tag balancing
open_divs = len(re.findall(r'<div\b', text))
close_divs = len(re.findall(r'</div>', text))
print(f"Tag balance: open divs = {open_divs}, close divs = {close_divs}, diff = {open_divs - close_divs}")
assert open_divs == close_divs, f"Div tag mismatch: {open_divs} != {close_divs}"

print("\n========================================================")
print("=== ALL PT SCRIPT VALIDATION CHECKS PASSED 100%! ===")
print("========================================================")
