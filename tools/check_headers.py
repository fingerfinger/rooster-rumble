import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('ROOSTER RUMBLE QA 체크리스트.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Find section titles or h2/h3
headers = re.findall(r'<div class="section-title">([^<]*)</div>|<h[1-4][^>]*>([^<]*)</h[1-4]>', text)
print("Headers:", headers)
