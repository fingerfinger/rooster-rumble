import os
import sys
import numpy as np
import miniaudio
import lameenc
from scipy import signal

SAMPLE_RATE = 44100
BITRATE = 192

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio", "race")
BGM_DIR = os.path.join(AUDIO_DIR, "bgm")
SFX_DIR = os.path.join(AUDIO_DIR, "sfx")
VOICE_DIR = os.path.join(AUDIO_DIR, "voice")
DEMO_DIR = os.path.join(AUDIO_DIR, "demo")

os.makedirs(DEMO_DIR, exist_ok=True)

def load_audio(file_path: str) -> np.ndarray:
    with open(file_path, "rb") as f:
        dec = miniaudio.decode(f.read(), output_format=miniaudio.SampleFormat.FLOAT32, nchannels=2, sample_rate=SAMPLE_RATE)
    samples = np.frombuffer(dec.samples, dtype=np.float32).reshape(-1, 2)
    return samples

def save_mp3(file_path: str, audio_data: np.ndarray, sample_rate: int = SAMPLE_RATE, bitrate: int = BITRATE):
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

def apply_panning(stereo_clip: np.ndarray, pan: float) -> np.ndarray:
    mono = np.mean(stereo_clip, axis=1)
    angle = (pan + 1.0) * (np.pi / 4.0)
    l = mono * np.cos(angle)
    r = mono * np.sin(angle)
    return np.column_stack([l, r])

def generate_race_simulation(output_path: str, variant: int = 1):
    print(f"=== [시뮬레이션] 26초 풀 레이스 인게임 사운드 트랙 생성 (버전 {variant}) ===")
    
    TOTAL_DURATION = 29.5
    TOTAL_SAMPLES = int(TOTAL_DURATION * SAMPLE_RATE)
    
    layer_voice = np.zeros((TOTAL_SAMPLES, 2), dtype=np.float32)
    layer_sfx = np.zeros((TOTAL_SAMPLES, 2), dtype=np.float32)
    layer_bgm = np.zeros((TOTAL_SAMPLES, 2), dtype=np.float32)
    layer_crowd = np.zeros((TOTAL_SAMPLES, 2), dtype=np.float32)

    # 1. 보이스 이벤트 (신규 일레븐랩스 에셋 기반)
    if variant == 1:
        voice_events = [
            (1.50, os.path.join(VOICE_DIR, "vo_us_start_02.mp3"), 1.00),     # "And they're off in Rooster Rumble!"
            (5.50, os.path.join(VOICE_DIR, "vo_rooster_num_03.mp3"), 0.95),  # "Number 3!"
            (6.50, os.path.join(VOICE_DIR, "vo_us_early_03.mp3"), 0.95),     # "Setting the pace out front!"
            (11.50, os.path.join(VOICE_DIR, "vo_rooster_num_05.mp3"), 0.98), # "Number 5!"
            (12.50, os.path.join(VOICE_DIR, "vo_us_over_01.mp3"), 0.98),     # "Takes over the lead!"
            (14.30, os.path.join(VOICE_DIR, "vo_us_side_01.mp3"), 1.00),     # "Head-to-head in a battle!"
            (18.50, os.path.join(VOICE_DIR, "vo_us_stretch_01.mp3"), 1.02),  # "Down the stretch they come!"
            (20.30, os.path.join(VOICE_DIR, "vo_rooster_num_05.mp3"), 1.05), # "Number 5!"
            (21.30, os.path.join(VOICE_DIR, "vo_us_stretch_02.mp3"), 1.05),  # "Leading them to the wire!"
            (23.20, os.path.join(VOICE_DIR, "vo_us_photo_02.mp3"), 1.10),    # "Nose to nose at the wire! Who took it?!"
            (26.00, os.path.join(VOICE_DIR, "vo_rooster_num_05.mp3"), 1.05), # "Number 5!"
            (27.00, os.path.join(VOICE_DIR, "vo_us_win_01.mp3"), 1.05),      # "Wins it wire-to-wire!"
        ]
    elif variant == 2:
        voice_events = [
            (1.50, os.path.join(VOICE_DIR, "vo_us_start_01.mp3"), 1.00),     # "And away they go!"
            (5.50, os.path.join(VOICE_DIR, "vo_rooster_num_01.mp3"), 0.95),
            (6.50, os.path.join(VOICE_DIR, "vo_us_early_01.mp3"), 0.95),
            (11.50, os.path.join(VOICE_DIR, "vo_rooster_num_04.mp3"), 0.98),
            (12.50, os.path.join(VOICE_DIR, "vo_us_over_02.mp3"), 0.98),
            (18.50, os.path.join(VOICE_DIR, "vo_us_stretch_03.mp3"), 1.02),
            (20.30, os.path.join(VOICE_DIR, "vo_rooster_num_03.mp3"), 1.05),
            (21.30, os.path.join(VOICE_DIR, "vo_us_stretch_chui.mp3"), 1.05),
            (23.20, os.path.join(VOICE_DIR, "vo_us_photo_01.mp3"), 1.10),
            (26.00, os.path.join(VOICE_DIR, "vo_rooster_num_03.mp3"), 1.05),
            (27.00, os.path.join(VOICE_DIR, "vo_us_win_03.mp3"), 1.05),
        ]
    else:
        voice_events = [
            (1.50, os.path.join(VOICE_DIR, "vo_us_start_03.mp3"), 1.00),
            (4.00, os.path.join(VOICE_DIR, "vo_us_flinch_01.mp3"), 0.95),
            (7.50, os.path.join(VOICE_DIR, "vo_rooster_num_02.mp3"), 0.95),
            (8.50, os.path.join(VOICE_DIR, "vo_us_early_02.mp3"), 0.95),
            (13.00, os.path.join(VOICE_DIR, "vo_rooster_num_06.mp3"), 0.98),
            (14.00, os.path.join(VOICE_DIR, "vo_us_over_03.mp3"), 0.98),
            (18.50, os.path.join(VOICE_DIR, "vo_us_stretch_01.mp3"), 1.02),
            (21.00, os.path.join(VOICE_DIR, "vo_rooster_num_06.mp3"), 1.05),
            (22.00, os.path.join(VOICE_DIR, "vo_us_stretch_02.mp3"), 1.05),
            (24.00, os.path.join(VOICE_DIR, "vo_us_photo_02.mp3"), 1.10),
            (26.50, os.path.join(VOICE_DIR, "vo_us_win_02.mp3"), 1.05),
        ]

    ducking_mask = np.ones(TOTAL_SAMPLES, dtype=np.float32)

    for start_t, v_path, vol in voice_events:
        if not os.path.exists(v_path):
            continue
        v_clip = load_audio(v_path) * vol
        s_idx = int(start_t * SAMPLE_RATE)
        e_idx = s_idx + len(v_clip)
        if e_idx <= TOTAL_SAMPLES:
            layer_voice[s_idx:e_idx] += v_clip
            d_start = max(0, s_idx - int(0.06 * SAMPLE_RATE))
            d_end = min(TOTAL_SAMPLES, e_idx + int(0.18 * SAMPLE_RATE))
            ducking_mask[d_start:d_end] = np.minimum(ducking_mask[d_start:d_end], 0.32)

    kernel_len = int(0.12 * SAMPLE_RATE)
    kernel = np.ones(kernel_len) / kernel_len
    ducking_smooth = np.convolve(ducking_mask, kernel, mode='same')
    ducking_smooth = np.clip(ducking_smooth, 0.32, 1.0)

    # 2. SFX 레이어
    startgun_clip = load_audio(os.path.join(SFX_DIR, "sfx_race_startgun.mp3"))
    layer_sfx[:len(startgun_clip)] += startgun_clip * 1.05

    gallop_clips = [load_audio(os.path.join(SFX_DIR, f"sfx_race_gallop_{i}.mp3")) for i in [1, 2, 3]]
    roosters = [
        {"pan": -0.35, "phase": 0.00, "vol": 0.55},
        {"pan": -0.18, "phase": 0.04, "vol": 0.50},
        {"pan":  0.00, "phase": 0.02, "vol": 0.65},
        {"pan": +0.12, "phase": 0.05, "vol": 0.50},
        {"pan": +0.28, "phase": 0.01, "vol": 0.65},
        {"pan": +0.40, "phase": 0.06, "vol": 0.48},
    ]

    current_t = 0.75
    step_cnt = 0
    while current_t < 22.50:
        for r_idx, r in enumerate(roosters):
            t_hit = current_t + r["phase"]
            if t_hit >= 22.50:
                continue
            idx_hit = int(t_hit * SAMPLE_RATE)
            g_clip = gallop_clips[(step_cnt + r_idx) % 3]
            g_panned = apply_panning(g_clip, r["pan"]) * r["vol"]
            l_g = min(len(g_panned), TOTAL_SAMPLES - idx_hit)
            layer_sfx[idx_hit:idx_hit + l_g] += g_panned[:l_g]
        current_t += 0.100
        step_cnt += 1

    # 닭 기합소리
    cluck_events = [(4.5, 1, 0.0), (9.0, 2, 0.2), (16.0, 2, -0.2), (20.5, 3, 0.28)]
    for c_t, c_id, c_pan in cluck_events:
        c_path = os.path.join(SFX_DIR, f"sfx_race_cluck_{c_id}.mp3")
        if os.path.exists(c_path):
            c_clip = load_audio(c_path)
            c_panned = apply_panning(c_clip, c_pan) * 0.75
            idx_c = int(c_t * SAMPLE_RATE)
            l_c = min(len(c_panned), TOTAL_SAMPLES - idx_c)
            layer_sfx[idx_c:idx_c + l_c] += c_panned[:l_c]

    # 3. BGM 레이어
    bgm_race = load_audio(os.path.join(BGM_DIR, "bgm_ingame_race.mp3"))
    bgm_start_idx = int(0.75 * SAMPLE_RATE)
    bgm_end_idx = int(22.50 * SAMPLE_RATE)
    bgm_len = bgm_end_idx - bgm_start_idx
    bgm_loop = np.tile(bgm_race, (int(np.ceil(bgm_len / len(bgm_race))), 1))[:bgm_len] * 0.78
    
    # 덕킹
    bgm_duck = ducking_smooth[bgm_start_idx:bgm_end_idx, None]
    bgm_loop *= bgm_duck
    f_bgm = int(0.40 * SAMPLE_RATE)
    bgm_loop[-f_bgm:, 0] *= np.linspace(1, 0, f_bgm)
    bgm_loop[-f_bgm:, 1] *= np.linspace(1, 0, f_bgm)
    layer_bgm[bgm_start_idx:bgm_end_idx] += bgm_loop

    # 정산 팡파레
    bgm_result = load_audio(os.path.join(BGM_DIR, "bgm_result_theme.mp3"))
    fanfare_start_idx = int(26.20 * SAMPLE_RATE)
    l_f = min(len(bgm_result), TOTAL_SAMPLES - fanfare_start_idx)
    layer_bgm[fanfare_start_idx:fanfare_start_idx + l_f] += bgm_result[:l_f] * 0.85

    # 4. 관중 함성 레이어
    crowd_clip = load_audio(os.path.join(SFX_DIR, "sfx_crowd_cheer.mp3"))
    crowd_loop = np.tile(crowd_clip, (int(np.ceil(TOTAL_SAMPLES / len(crowd_clip))), 1))[:TOTAL_SAMPLES]
    crowd_env = np.ones(TOTAL_SAMPLES, dtype=np.float32) * 0.48
    crowd_env[:int(3.0 * SAMPLE_RATE)] = np.linspace(0.68, 0.48, int(3.0 * SAMPLE_RATE))
    idx_slow = int(22.5 * SAMPLE_RATE)
    idx_finish = int(25.5 * SAMPLE_RATE)
    crowd_env[idx_slow:idx_finish] = np.linspace(0.48, 0.80, idx_finish - idx_slow)
    crowd_env[idx_finish:] = 0.82
    layer_crowd = crowd_loop * crowd_env[:, None]

    # 5. 마스터 결합
    sfx_duck = np.where(ducking_smooth < 0.6, 0.65, 1.0)[:, None]
    layer_sfx_ducked = layer_sfx * sfx_duck
    master_mix = layer_voice * 0.95 + layer_sfx_ducked * 0.90 + layer_bgm * 1.00 + layer_crowd * 0.85

    f_final = int(0.50 * SAMPLE_RATE)
    master_mix[-f_final:, 0] *= np.linspace(1, 0, f_final)
    master_mix[-f_final:, 1] *= np.linspace(1, 0, f_final)

    mx = np.max(np.abs(master_mix))
    if mx > 0:
        master_mix = master_mix / mx * 0.88

    save_mp3(output_path, master_mix, sample_rate=SAMPLE_RATE, bitrate=BITRATE)
    dur = len(master_mix) / SAMPLE_RATE
    rms = np.sqrt(np.mean(master_mix**2))
    print(f"  [완료] {output_path} (길이: {dur:.2f}s, 피크: {np.max(np.abs(master_mix)):.2f}, RMS: {rms:.3f})")

def main():
    print("\n[SUCCESS] 풀 레이스 시뮬레이션 데모 3종 갱신 완료!")
    print("==================================================================")
    
    # 1) 데모 1 (메인 26초 시뮬레이션)
    out1 = os.path.join(DEMO_DIR, "demo_race_simulation_26s.mp3")
    generate_race_simulation(out1, variant=1)

    # 2) 데모 2
    out2 = os.path.join(DEMO_DIR, "demo_race_simulation_sample_2.mp3")
    generate_race_simulation(out2, variant=2)

    # 3) 데모 3
    out3 = os.path.join(DEMO_DIR, "demo_race_simulation_sample_3.mp3")
    generate_race_simulation(out3, variant=3)

    print("\n[SUCCESS] 풀 레이스 시뮬레이션 데모 3종 갱신 완료!")

if __name__ == "__main__":
    main()
