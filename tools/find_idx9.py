with open('ROOSTER RUMBLE 모드 요약 소개.html', 'r', encoding='utf-8') as f:
    for num, line in enumerate(f, 1):
        if 'data-index="9"' in line:
            print(num, line.strip())
