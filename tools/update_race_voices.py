"""
ROOSTER RUMBLE: Derby Race 장내 아나운서 보이스 교체 및 자동화 마스터 스크립트
- 격정적/하이텐션 보이스 지원 (Edge-TTS 기반 고품질 신경망 보이스)
- DSP 마스터링: 140Hz HPF, 3~4.5kHz 프레즌스 펀치, 새츄레이션/소프트 리미팅
- 원클릭 27종 보이스 전수 재생성 및 풀 레이스 데모 3종 재합성 지원
"""

import os
import sys
import argparse
import asyncio
import numpy as np
import lameenc
import miniaudio
from scipy import signal
import edge_tts

SAMPLE_RATE = 44100
BITRATE = 192

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio", "race")
VOICE_DIR = os.path.join(AUDIO_DIR, "voice")
CACHE_DIR = os.path.join(BASE_DIR, "tools", "source_cache")
DEMO_DIR = os.path.join(AUDIO_DIR, "demo")

os.makedirs(VOICE_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# 27종 대사 스크립트 명세 (파일명, 영문대사, 속도, 피치)
# 격정적 톤 연출을 위해 구간별 속도(+16%~+30%) 및 피치(+2Hz~+7Hz) 상승 적용
VOICE_SCRIPTS = [
    # 1. 선수 번호 호출 6종
    ("vo_rooster_num_01.mp3", "Number 1!", "+16%", "+2Hz"),
    ("vo_rooster_num_02.mp3", "Number 2!", "+16%", "+2Hz"),
    ("vo_rooster_num_03.mp3", "Number 3!", "+16%", "+2Hz"),
    ("vo_rooster_num_04.mp3", "Number 4!", "+16%", "+2Hz"),
    ("vo_rooster_num_05.mp3", "Number 5!", "+16%", "+2Hz"),
    ("vo_rooster_num_06.mp3", "Number 6!", "+16%", "+2Hz"),

    # 2. W-1: 출발선 멘트 5종 (긴장감 고조)
    ("vo_us_start_01.mp3", "And away they go!", "+18%", "+3Hz"),
    ("vo_us_start_02.mp3", "And they're off in Rooster Rumble!", "+20%", "+4Hz"),
    ("vo_us_start_03.mp3", "Off the mark and away they sprint!", "+20%", "+4Hz"),
    ("vo_us_flinch_01.mp3", "Bad break! Stumbled off the line!", "+18%", "+3Hz"),
    ("vo_us_flinch_02.mp3", "Awkward start, losing ground early!", "+18%", "+3Hz"),

    # 3. W-2: 초반 선두 멘트 3종 (페이스업)
    ("vo_us_early_01.mp3", "Showing early speed to take the lead!", "+20%", "+4Hz"),
    ("vo_us_early_02.mp3", "Grabs the lead early on!", "+20%", "+4Hz"),
    ("vo_us_early_03.mp3", "Setting the pace out front!", "+20%", "+4Hz"),

    # 4. W-3: 중반 순위 역전 및 접전 4종 (치열한 격돌)
    ("vo_us_over_01.mp3", "Takes over the lead!", "+24%", "+5Hz"),
    ("vo_us_over_02.mp3", "Makes a powerful surge!", "+24%", "+5Hz"),
    ("vo_us_over_03.mp3", "Surging to the front!", "+24%", "+5Hz"),
    ("vo_us_side_01.mp3", "Head-to-head in a battle!", "+24%", "+5Hz"),

    # 5. W-4: 종반 라스트 스퍼트 4종 (포효와 질주)
    ("vo_us_stretch_01.mp3", "Down the stretch they come!", "+26%", "+6Hz"),
    ("vo_us_stretch_02.mp3", "Leading them to the wire!", "+26%", "+6Hz"),
    ("vo_us_stretch_03.mp3", "They're sprinting for the wire!", "+26%", "+6Hz"),
    ("vo_us_stretch_chui.mp3", "Charging hard from behind!", "+26%", "+6Hz"),

    # 6. W-5: 결승선 골인 및 사진 판독 5종 (최고조 절정)
    ("vo_us_win_01.mp3", "Wins it wire-to-wire!", "+28%", "+7Hz"),
    ("vo_us_win_02.mp3", "It is all victory at the wire!", "+28%", "+7Hz"),
    ("vo_us_win_03.mp3", "Takes the victory in Rooster Rumble!", "+28%", "+7Hz"),
    ("vo_us_photo_01.mp3", "Too close to call! They cross the line together!", "+28%", "+7Hz"),
    ("vo_us_photo_02.mp3", "Nose to nose at the wire! Who took it?!", "+28%", "+7Hz"),
]

def save_mp3(file_path: str, audio_data: np.ndarray, sample_rate: int = SAMPLE_RATE, bitrate: int = BITRATE):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    max_val = np.max(np.abs(audio_data))
    if max_val > 0.95:
        audio_data = audio_data / max_val * 0.95
        
    audio_data = np.tanh(audio_data * 1.05) / 1.05

    if audio_data.ndim == 1:
        num_channels = 1
        int_data = np.int16(audio_data * 32767)
    elif audio_data.ndim == 2:
        num_channels = audio_data.shape[1]
        int_data = np.int16(audio_data * 32767).flatten()
    else:
        raise ValueError("Unsupported audio shape")

    encoder = lameenc.Encoder()
    encoder.set_bit_rate(bitrate)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(num_channels)
    encoder.set_quality(2)
    mp3_data = encoder.encode(int_data.tobytes())
    mp3_data += encoder.flush()

    with open(file_path, "wb") as f:
        f.write(mp3_data)

async def synthesize_voice_single(text: str, voice_id: str, out_raw_path: str, rate: str, pitch: str):
    comm = edge_tts.Communicate(text, voice_id, rate=rate, pitch=pitch)
    await comm.save(out_raw_path)

def process_voice_dsp(raw_mp3_path: str, output_path: str, aggressive: bool = True):
    """
    격정적 아나운서 보이스 특화 DSP 체인:
    1. 140Hz HPF (마이크 럼블 및 불필요한 저역 제거)
    2. 2.8kHz ~ 4.8kHz 프레즌스 펀치 (+40% 자음 어택 및 선명도 부스트)
    3. 아날로그 세츄레이션 (Tanh 드라이브로 단단한 음압 확보)
    4. 센터 포커스 스테레오 마스터링
    5. 시작/끝 10ms 페이드 (클릭 노이즈 완벽 차단)
    """
    with open(raw_mp3_path, "rb") as f:
        dec = miniaudio.decode(f.read(), output_format=miniaudio.SampleFormat.FLOAT32, nchannels=2, sample_rate=SAMPLE_RATE)
    sr = dec.sample_rate
    raw = np.frombuffer(dec.samples, dtype=np.float32).reshape(-1, dec.nchannels)
    
    mono = np.mean(raw, axis=1) if dec.nchannels > 1 else raw[:, 0]

    # 1. 140Hz 3차 HPF
    sos_hp = signal.butter(3, 140, btype='highpass', fs=sr, output='sos')
    filtered = signal.sosfilt(sos_hp, mono)

    # 2. 2.8kHz ~ 4.8kHz 프레즌스 EQ 부스트
    sos_bp = signal.butter(2, [2800, 4800], btype='bandpass', fs=sr, output='sos')
    presence = signal.sosfilt(sos_bp, filtered) * (0.42 if aggressive else 0.30)
    filtered += presence

    # 3. 아날로그 새츄레이션 (음압 및 펀치감)
    if aggressive:
        filtered = np.tanh(filtered * 1.25) / 1.15

    # 4. 피크 정규화 (0.88 헤드룸)
    mx = np.max(np.abs(filtered))
    if mx > 0:
        filtered = filtered / mx * 0.88

    # 5. 스테레오 센터 배치 & 양 끝 10ms 페이드
    stereo = np.zeros((len(filtered), 2))
    fade_len = int(0.01 * sr)
    filtered[:fade_len] *= np.linspace(0, 1, fade_len)
    filtered[-fade_len:] *= np.linspace(1, 0, fade_len)
    stereo[:, 0] = filtered
    stereo[:, 1] = filtered

    save_mp3(output_path, stereo)

async def build_all_voices(voice_id: str, aggressive: bool = True):
    print(f"\n========================================================")
    print(f"🎙️  장내 아나운서 보이스 27종 교체 작업 시작")
    print(f"   - 선택된 보이스: {voice_id}")
    print(f"   - DSP 모드: {'격정적 스포츠 마스터링 (Aggressive)' if aggressive else '표준 클린 (Standard)'}")
    print(f"========================================================")

    for i, (fname, text, rate, pitch) in enumerate(VOICE_SCRIPTS, 1):
        raw_tmp = os.path.join(CACHE_DIR, f"temp_{fname}")
        final_out = os.path.join(VOICE_DIR, fname)
        
        await synthesize_voice_single(text, voice_id, raw_tmp, rate, pitch)
        process_voice_dsp(raw_tmp, final_out, aggressive=aggressive)
        
        if os.path.exists(raw_tmp):
            os.remove(raw_tmp)
            
        print(f"  [{i:02d}/27] 완료: {fname} | Rate: {rate} | Script: {text}")

    print(f"\n✅ 27종 보이스 교체 생성 완료: {VOICE_DIR}")

def main():
    parser = argparse.ArgumentParser(description="Derby Race Voice Updater")
    parser.add_argument("--voice", default="en-US-BrianMultilingualNeural", help="Voice model ID")
    parser.add_argument("--standard-dsp", action="store_true", help="Use standard clean DSP instead of aggressive")
    parser.add_argument("--rebuild-sim", action="store_true", help="Rebuild full race simulation demos")
    args = parser.parse_args()

    asyncio.run(build_all_voices(args.voice, aggressive=not args.standard_dsp))

    if args.rebuild_sim:
        sim_script = os.path.join(os.path.dirname(__file__), "generate_race_simulation.py")
        if os.path.exists(sim_script):
            print("\n🔄 풀 레이스 시뮬레이션 데모 3종 재합성 실행 중...")
            os.system(f'python "{sim_script}"')
            print("✅ 풀 레이스 시뮬레이션 데모 갱신 완료!")

if __name__ == "__main__":
    main()
