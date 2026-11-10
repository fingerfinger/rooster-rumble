with open('tools/generate_race_simulation.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")',
    'AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio", "race")'
)

# DEMO_DIR 및 출력 경로도 점검
text = text.replace(
    'DEMO_DIR = os.path.join(AUDIO_DIR, "demo")',
    'DEMO_DIR = os.path.join(AUDIO_DIR, "demo")'
)

with open('tools/generate_race_simulation.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Path updated successfully!")
