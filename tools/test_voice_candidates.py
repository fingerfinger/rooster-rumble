import asyncio
import os
import edge_tts

CANDIDATES = [
    ("en-US-GuyNeural", "기존 (Guy - 차분한 뉴스/안내형)"),
    ("en-US-ChristopherNeural", "후보 1 (Christopher - 단단하고 파워풀한 남성톤)"),
    ("en-US-BrianMultilingualNeural", "후보 2 (Brian Multi - 중후하면서도 힘있는 톤)"),
    ("en-US-EricNeural", "후보 3 (Eric - 역동적이고 텐션 있는 남성톤)"),
    ("en-US-AndrewMultilingualNeural", "후보 4 (Andrew Multi - 명료하고 에너지감 있는 톤)"),
    ("en-GB-RyanNeural", "후보 5 (Ryan - 영국식 박진감 넘치는 더비 중계톤)"),
    ("en-AU-WilliamMultilingualNeural", "후보 6 (William - 호주식 야외 스포츠 아나운서톤)")
]

TEST_LINE = "Nose to nose at the wire! Who took it?!"
OUT_DIR = "assets/audio/race/voice_samples"
os.makedirs(OUT_DIR, exist_ok=True)

async def generate():
    for voice_id, label in CANDIDATES:
        out_path = os.path.join(OUT_DIR, f"sample_{voice_id}.mp3")
        # 격정적 톤을 위해 속도 +24%, 피치 +6Hz 적용
        comm = edge_tts.Communicate(TEST_LINE, voice_id, rate="+24%", pitch="+6Hz")
        await comm.save(out_path)
        print(f"Generated: {voice_id} ({label}) -> {out_path}")

asyncio.run(generate())
