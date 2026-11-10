import asyncio
import os
import edge_tts

CANDIDATES = [
    ("en-US-GuyNeural", "기존 음성 (Guy - 정적/안내톤)"),
    ("en-US-BrianMultilingualNeural", "후보 1: Brian Multi (중후하고 묵직한 파워톤)"),
    ("en-US-ChristopherNeural", "후보 2: Christopher (단단하고 거친 스포츠톤)"),
    ("en-US-AndrewMultilingualNeural", "후보 3: Andrew Multi (날카롭고 빠른 속도감)"),
    ("en-GB-RyanNeural", "후보 4: Ryan (영국 전통 경마/더비 중계톤)"),
    ("en-AU-WilliamMultilingualNeural", "후보 5: William (호주식 스타디움 장내 아나운서)")
]

TEST_LINES = [
    ("start", "And they're off in Rooster Rumble!", "+18%", "+3Hz"),
    ("stretch", "Down the stretch they come!", "+22%", "+5Hz"),
    ("finish", "Nose to nose at the wire! Who took it?!", "+25%", "+6Hz")
]

OUT_DIR = "assets/audio/race/voice_samples"
os.makedirs(OUT_DIR, exist_ok=True)

async def generate_all():
    for voice_id, vlabel in CANDIDATES:
        for tag, text, rate, pitch in TEST_LINES:
            fname = f"{voice_id}_{tag}.mp3"
            fpath = os.path.join(OUT_DIR, fname)
            comm = edge_tts.Communicate(text, voice_id, rate=rate, pitch=pitch)
            await comm.save(fpath)
            print(f"Generated: {fname}")

asyncio.run(generate_all())
