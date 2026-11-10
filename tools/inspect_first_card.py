import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('ROOSTER RUMBLE QA 체크리스트.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('class="qa-card"')
print(text[idx:idx+800])
