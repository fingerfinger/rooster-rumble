import asyncio
import edge_tts

async def list_us():
    voices = await edge_tts.list_voices()
    for v in voices:
        if v['Locale'].startswith('en-') and v['Gender'] == 'Male':
            print(f"{v['ShortName']:<30} | {v.get('VoicePersonalities', '')}")

asyncio.run(list_us())
