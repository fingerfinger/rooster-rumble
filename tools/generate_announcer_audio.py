import os
import asyncio
import numpy as np
import lameenc
import miniaudio
from scipy import signal
import edge_tts

SAMPLE_RATE = 44100
BITRATE = 192

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "assets", "audio", "source_cache")
VOICE_DIR = os.path.join(BASE_DIR, "assets", "audio", "voice")

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)

# 27종 대사 스크립트 명세: (파일명, 영문대사, 속도, 피치)
VOICE_SCRIPTS = [
    # 1. 선수 번호 호출 6종
    ("vo_rooster_num_01.mp3", "Number 1!", "+14%", "+2Hz"),
    ("vo_rooster_num_02.mp3", "Number 2!", "+14%", "+2Hz"),
    ("vo_rooster_num_03.mp3", "Number 3!", "+14%", "+2Hz"),
    ("vo_rooster_num_04.mp3", "Number 4!", "+14%", "+2Hz"),
    ("vo_rooster_num_05.mp3", "Number 5!", "+14%", "+2Hz"),
    ("vo_rooster_num_06.mp3", "Number 6!", "+14%", "+2Hz"),

    # 2. W-1: 출발선 멘트 5종
    ("vo_us_start_01.mp3", "And away they go!", "+16%", "+2Hz"),
    ("vo_us_start_02.mp3", "And they're off in Rooster Rumble!", "+18%", "+3Hz"),
    ("vo_us_start_03.mp3", "Off the mark and away they sprint!", "+18%", "+3Hz"),
    ("vo_us_flinch_01.mp3", "Bad break! Stumbled off the line!", "+16%", "+2Hz"),
    ("vo_us_flinch_02.mp3", "Awkward start, losing ground early!", "+16%", "+2Hz"),

    # 3. W-2: 초반 선두 멘트 3종
    ("vo_us_early_01.mp3", "Showing early speed to take the lead!", "+18%", "+3Hz"),
    ("vo_us_early_02.mp3", "Grabs the lead early on!", "+18%", "+3Hz"),
    ("vo_us_early_03.mp3", "Setting the pace out front!", "+18%", "+3Hz"),

    # 4. W-3: 중반 순위 역전 및 접전 4종
    ("vo_us_over_01.mp3", "Takes over the lead!", "+20%", "+4Hz"),
    ("vo_us_over_02.mp3", "Makes a powerful surge!", "+20%", "+4Hz"),
    ("vo_us_over_03.mp3", "Surging to the front!", "+20%", "+4Hz"),
    ("vo_us_side_01.mp3", "Head-to-head in a battle!", "+20%", "+4Hz"),

    # 5. W-4: 종반 라스트 스퍼트 4종
    ("vo_us_stretch_01.mp3", "Down the stretch they come!", "+22%", "+5Hz"),
    ("vo_us_stretch_02.mp3", "Leading them to the wire!", "+22%", "+5Hz"),
    ("vo_us_stretch_03.mp3", "They're sprinting for the wire!", "+22%", "+5Hz"),
    ("vo_us_stretch_chui.mp3", "Charging hard from behind!", "+22%", "+5Hz"),

    # 6. W-5: 결승선 골인 및 사진 판독 5종
    ("vo_us_win_01.mp3", "Wins it wire-to-wire!", "+24%", "+6Hz"),
    ("vo_us_win_02.mp3", "It is all victory at the wire!", "+24%", "+6Hz"),
    ("vo_us_win_03.mp3", "Takes the victory in Rooster Rumble!", "+24%", "+6Hz"),
    ("vo_us_photo_01.mp3", "Too close to call! They cross the line together!", "+24%", "+6Hz"),
    ("vo_us_photo_02.mp3", "Nose to nose at the wire! Who took it?!", "+24%", "+6Hz"),
]

def save_mp3(file_path: str, audio_data: np.ndarray, sample_rate: int = SAMPLE_RATE, bitrate: int = BITRATE):
    """
    numpy 오디오 배열(Mono 또는 Stereo)을 MP3 파일로 인코딩하여 저장
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    max_val = np.max(np.abs(audio_data))
    if max_val > 0.95:
        audio_data = audio_data / max_val * 0.95
        
    audio_data = np.tanh(audio_data * 1.02) / 1.02

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


async def synthesize_voice(text: str, out_raw_path: str, rate: str, pitch: str):
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural", rate=rate, pitch=pitch)
    await communicate.save(out_raw_path)


def process_voice_audio(raw_mp3_path: str, output_path: str, crowd_samples: np.ndarray):
    """
    방송국 전용 DSP 필터 & 마스터링:
    1. 하이패스 140Hz (마이크 스탠드 럼블 컷)
    2. 2.5kHz~4.5kHz 프레즌스 EQ (자음 선명도 부스트)
    3. 35ms 스타디움 PA 슬랩백 에코
    4. -18dB 관중 환호 서브믹스
    5. 피크 0.82 클린 마스터링
    """
    dec = miniaudio.decode_file(raw_mp3_path)
    sr = dec.sample_rate
    raw = np.array(dec.samples, dtype=np.float32).reshape(-1, dec.nchannels) / 32768.0
    
    # 모노화
    if dec.nchannels > 1:
        mono = np.mean(raw, axis=1)
    else:
        mono = raw[:, 0]

    # 1. 140Hz 하이패스 필터
    sos_hp = signal.butter(3, 140, btype='highpass', fs=sr, output='sos')
    filtered = signal.sosfilt(sos_hp, mono)

    # 2. 2.5kHz ~ 4.5kHz 프레즌스 대역 강화
    sos_bp = signal.butter(2, [2500, 4500], btype='bandpass', fs=sr, output='sos')
    presence = signal.sosfilt(sos_bp, filtered) * 0.35
    filtered += presence

    # 정규화
    mx_f = np.max(np.abs(filtered))
    if mx_f > 0:
        filtered = filtered / mx_f

    # 3. 스테레오 배치 및 스타디움 PA 슬랩백 (35ms 딜레이)
    slap_samples = int(0.035 * sr)
    tot_len = len(filtered) + slap_samples + int(0.12 * sr) # 여운 공간
    stereo = np.zeros((tot_len, 2))
    stereo[:len(filtered), 0] = filtered * 0.85
    stereo[:len(filtered), 1] = filtered * 0.85
    
    # 슬랩백 에코 (좌/우 약간의 시차)
    stereo[slap_samples:slap_samples + len(filtered), 0] += filtered * 0.14
    slap_r = slap_samples + int(0.005 * sr)
    stereo[slap_r:slap_r + len(filtered), 1] += filtered * 0.12

    # 4. 배경 관중 함성 은은한 서브믹스 (-18dB)
    if crowd_samples is not None and len(crowd_samples) > 0:
        c_len = min(tot_len, len(crowd_samples))
        stereo[:c_len, 0] += crowd_samples[:c_len, 0] * 0.12
        stereo[:c_len, 1] += crowd_samples[:c_len, 1] * 0.12

    # 5. 시작/끝 15ms 페이드
    f_len = int(0.015 * sr)
    stereo[:f_len, 0] *= np.linspace(0, 1, f_len)
    stereo[:f_len, 1] *= np.linspace(0, 1, f_len)
    stereo[-f_len:, 0] *= np.linspace(1, 0, f_len)
    stereo[-f_len:, 1] *= np.linspace(1, 0, f_len)

    # 최종 피크 마스터링 (0.82)
    mx = np.max(np.abs(stereo))
    if mx > 0:
        stereo = stereo / mx * 0.82

    save_mp3(output_path, stereo, sample_rate=sr)


async def main():
    print(f"=== [ROOSTER RUMBLE] 장내 아나운서 영문 보이스 27종 생성 시작 ===")
    
    # 관중 배경음 로드
    crowd_path = os.path.join(CACHE_DIR, "real_crowd_cheer.ogg")
    crowd_samples = None
    if os.path.exists(crowd_path):
        c_dec = miniaudio.decode_file(crowd_path)
        raw_c = np.array(c_dec.samples, dtype=np.float32).reshape(-1, 2) / 32768.0
        # 12초~22초 사이의 안정적인 환호 구간 사용
        s_c = int(12.0 * c_dec.sample_rate)
        e_c = int(22.0 * c_dec.sample_rate)
        crowd_samples = raw_c[s_c:e_c]

    success_count = 0
    for idx, (filename, text, rate, pitch) in enumerate(VOICE_SCRIPTS, 1):
        temp_raw = os.path.join(CACHE_DIR, f"temp_raw_{filename}")
        final_out = os.path.join(VOICE_DIR, filename)

        print(f"[{idx:02d}/27] {filename} 생성 중: \"{text}\" (속도: {rate}, 피치: {pitch})...")
        try:
            await synthesize_voice(text, temp_raw, rate, pitch)
            process_voice_audio(temp_raw, final_out, crowd_samples)
            if os.path.exists(temp_raw):
                os.remove(temp_raw)
            success_count += 1
        except Exception as e:
            print(f"  [ERROR] {filename} 생성 실패: {e}")

    print(f"\n=== 장내 아나운서 보이스 생성 완료: 총 {success_count}/{len(VOICE_SCRIPTS)}개 완료 ===")

if __name__ == "__main__":
    asyncio.run(main())
