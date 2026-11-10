"""
ROOSTER RUMBLE: 연결 호흡(Connected Flow) 음원 정밀 분할 및 마스터링 도구
- 번호+상황 연결 문장에서 호흡 경계점을 감지하여 단절 없는 라이브 억양 에셋으로 분할
- 피치 불변 1.25배속 타임스트레치 및 DSP 마스터링 일괄 적용
"""

import os
import sys
import argparse
import numpy as np
import lameenc
import miniaudio
from scipy import signal

SAMPLE_RATE = 44100
BITRATE = 192

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio", "race")
VOICE_DIR = os.path.join(AUDIO_DIR, "voice")
IMPORT_DIR = os.path.join(AUDIO_DIR, "voice_import")

os.makedirs(IMPORT_DIR, exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)

def phase_vocoder_time_stretch(mono: np.ndarray, rate: float = 1.0, sr: int = SAMPLE_RATE) -> np.ndarray:
    if abs(rate - 1.0) < 0.01:
        return mono

    n_fft = 2048
    hop = 512
    win = np.hanning(n_fft)

    num_frames = (len(mono) - n_fft) // hop + 1
    if num_frames < 2:
        return mono

    frames = np.lib.stride_tricks.sliding_window_view(mono[:(num_frames - 1) * hop + n_fft], n_fft)[::hop]
    stft = np.fft.rfft(frames * win, axis=-1).T

    time_steps = np.arange(0, stft.shape[1], rate)
    time_steps = time_steps[time_steps < stft.shape[1] - 1]
    output_stft = np.zeros((stft.shape[0], len(time_steps)), dtype=complex)

    phi_advance = np.linspace(0, np.pi * hop, stft.shape[0])
    phase_accum = np.angle(stft[:, 0])

    for i, t in enumerate(time_steps):
        t0 = int(t)
        t1 = t0 + 1
        alpha = t - t0

        mag = (1 - alpha) * np.abs(stft[:, t0]) + alpha * np.abs(stft[:, t1])
        dphi = np.angle(stft[:, t1]) - np.angle(stft[:, t0]) - phi_advance
        dphi = dphi - 2 * np.pi * np.round(dphi / (2 * np.pi))
        phase_accum += phi_advance + dphi
        output_stft[:, i] = mag * np.exp(1j * phase_accum)

    out_len = int((output_stft.shape[1] - 1) * hop + n_fft)
    out = np.zeros(out_len, dtype=np.float32)
    norm = np.zeros(out_len, dtype=np.float32)

    for i in range(output_stft.shape[1]):
        frame = np.fft.irfft(output_stft[:, i]) * win
        start = i * hop
        out[start:start + n_fft] += frame
        norm[start:start + n_fft] += win ** 2

    nonzero = norm > 1e-6
    out[nonzero] /= norm[nonzero]
    return out

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

def master_mono_clip(mono: np.ndarray, speed: float = 1.0) -> np.ndarray:
    if abs(speed - 1.0) >= 0.02:
        mono = phase_vocoder_time_stretch(mono, rate=speed, sr=SAMPLE_RATE)

    # 140Hz HPF + 2.8k~4.8k EQ boost
    sos_hp = signal.butter(3, 140, btype='highpass', fs=SAMPLE_RATE, output='sos')
    filtered = signal.sosfilt(sos_hp, mono)
    sos_bp = signal.butter(2, [2800, 4800], btype='bandpass', fs=SAMPLE_RATE, output='sos')
    filtered += signal.sosfilt(sos_bp, filtered) * 0.35

    mx = np.max(np.abs(filtered))
    if mx > 0:
        filtered = filtered / mx * 0.88

    stereo = np.zeros((len(filtered), 2))
    fade_len = int(0.01 * SAMPLE_RATE)
    filtered[:fade_len] *= np.linspace(0, 1, fade_len)
    filtered[-fade_len:] *= np.linspace(1, 0, fade_len)
    stereo[:, 0] = filtered
    stereo[:, 1] = filtered
    return stereo

def detect_voice_segments(audio: np.ndarray, sr: int = SAMPLE_RATE, threshold: float = 0.025, min_silence_sec: float = 0.25):
    win_size = int(sr * 0.02)
    hop = win_size // 2
    
    num_wins = len(audio) // hop - 1
    rms = np.zeros(num_wins)
    for i in range(num_wins):
        seg = audio[i * hop : i * hop + win_size]
        rms[i] = np.sqrt(np.mean(seg ** 2))
        
    peak_rms = np.max(rms)
    actual_thresh = max(threshold, peak_rms * 0.07)
    
    is_speech = rms > actual_thresh
    min_silence_wins = int(min_silence_sec * sr / hop)
    
    segments = []
    in_speech = False
    start_win = 0
    silence_count = 0
    
    for i, active in enumerate(is_speech):
        if active:
            if not in_speech:
                in_speech = True
                start_win = max(0, i - 2)
            silence_count = 0
        else:
            if in_speech:
                silence_count += 1
                if silence_count >= min_silence_wins or i == len(is_speech) - 1:
                    end_win = min(len(audio), (i - silence_count + 3) * hop + win_size)
                    start_sample = start_win * hop
                    if (end_win - start_sample) > int(0.12 * sr):
                        segments.append((start_sample, min(len(audio), end_win)))
                    in_speech = False
                    silence_count = 0

    return segments

def split_sentence_at_comma(sentence_mono: np.ndarray, sr: int = SAMPLE_RATE):
    """
    'NUMBER ONE, [호흡] takes over...' 문장 내에서 쉼표 호흡(에너지 최소점)을 찾아 앞(번호)/뒤(상황)로 2분할
    """
    win_size = int(sr * 0.015)
    hop = win_size // 2
    num_wins = len(sentence_mono) // hop - 1
    rms = np.zeros(num_wins)
    for i in range(num_wins):
        seg = sentence_mono[i * hop : i * hop + win_size]
        rms[i] = np.sqrt(np.mean(seg ** 2))

    # 문장 시작 후 0.4초 ~ 1.3초 사이에서 에너지 골짜기(Valleys / Dip) 탐색 (번호 발음 뒤 호흡 지점)
    min_search_win = int(0.35 * sr / hop)
    max_search_win = min(len(rms) - 2, int(1.30 * sr / hop))
    
    if min_search_win >= max_search_win:
        split_sample = int(0.75 * sr)
    else:
        dip_win = min_search_win + np.argmin(rms[min_search_win:max_search_win])
        split_sample = dip_win * hop

    part_a = sentence_mono[:split_sample]
    part_b = sentence_mono[split_sample:]
    return part_a, part_b

def process_all_connected_batches(speed: float = 1.25):
    print(f"\n========================================================")
    print(f"🎙️  연결 호흡(Connected Flow) 음원 정밀 분할 및 배치 시작")
    print(f"   - 적용 배속: {speed:.2f}x (피치 불변 Time-stretch)")
    print(f"========================================================")

    files = os.listdir(IMPORT_DIR)
    
    # 1. 파트 1: 단독 독립 멘트 10종 (batch_solo)
    solo_candidates = [f for f in files if "solo" in f.lower() or "part1" in f.lower()]
    if solo_candidates:
        src = os.path.join(IMPORT_DIR, solo_candidates[0])
        print(f"\n[1/5] 단독 멘트 10종 처리: {src}")
        with open(src, "rb") as f:
            dec = miniaudio.decode(f.read(), output_format=miniaudio.SampleFormat.FLOAT32, nchannels=2, sample_rate=SAMPLE_RATE)
        mono = np.mean(np.frombuffer(dec.samples, dtype=np.float32).reshape(-1, dec.nchannels), axis=1)
        segs = detect_voice_segments(mono)
        solo_targets = [
            "vo_us_start_01.mp3", "vo_us_start_02.mp3", "vo_us_start_03.mp3",
            "vo_us_flinch_01.mp3", "vo_us_flinch_02.mp3",
            "vo_us_stretch_01.mp3", "vo_us_stretch_03.mp3",
            "vo_us_photo_01.mp3", "vo_us_photo_02.mp3",
            "vo_us_win_02.mp3"
        ]
        for i, target in enumerate(solo_targets):
            if i < len(segs):
                clip = mono[segs[i][0]:segs[i][1]]
                mastered = master_mono_clip(clip, speed=speed)
                save_mp3(os.path.join(VOICE_DIR, target), mastered)
                print(f"  ✅ {target} ({len(mastered)/SAMPLE_RATE:.2f}s) 저장 완료")

    # 2. 파트 2: 초반 선두 3종 (batch_early)
    early_candidates = [f for f in files if "early" in f.lower() or "part2" in f.lower()]
    if early_candidates:
        src = os.path.join(IMPORT_DIR, early_candidates[0])
        print(f"\n[2/5] 초반 선두 연결 3종 분할: {src}")
        with open(src, "rb") as f:
            dec = miniaudio.decode(f.read(), output_format=miniaudio.SampleFormat.FLOAT32, nchannels=2, sample_rate=SAMPLE_RATE)
        mono = np.mean(np.frombuffer(dec.samples, dtype=np.float32).reshape(-1, dec.nchannels), axis=1)
        segs = detect_voice_segments(mono)
        for i in range(min(3, len(segs))):
            sent = mono[segs[i][0]:segs[i][1]]
            p_num, p_action = split_sentence_at_comma(sent)
            num_file = f"vo_rooster_num_{i+1:02d}.mp3"
            early_file = f"vo_us_early_{i+1:02d}.mp3"
            save_mp3(os.path.join(VOICE_DIR, num_file), master_mono_clip(p_num, speed=speed))
            save_mp3(os.path.join(VOICE_DIR, early_file), master_mono_clip(p_action, speed=speed))
            print(f"  ✅ [연결 분할] {num_file} & {early_file} 저장 완료")

    # 3. 파트 3: 중반 역전/접전 4종 (batch_overtake)
    over_candidates = [f for f in files if "over" in f.lower() or "part3" in f.lower()]
    if over_candidates:
        src = os.path.join(IMPORT_DIR, over_candidates[0])
        print(f"\n[3/5] 중반 역전 연결 4종 분할: {src}")
        with open(src, "rb") as f:
            dec = miniaudio.decode(f.read(), output_format=miniaudio.SampleFormat.FLOAT32, nchannels=2, sample_rate=SAMPLE_RATE)
        mono = np.mean(np.frombuffer(dec.samples, dtype=np.float32).reshape(-1, dec.nchannels), axis=1)
        segs = detect_voice_segments(mono)
        over_actions = ["vo_us_over_01.mp3", "vo_us_over_02.mp3", "vo_us_over_03.mp3", "vo_us_side_01.mp3"]
        for i in range(min(4, len(segs))):
            sent = mono[segs[i][0]:segs[i][1]]
            p_num, p_action = split_sentence_at_comma(sent)
            if i < 3:
                num_file = f"vo_rooster_num_{i+4:02d}.mp3"
                save_mp3(os.path.join(VOICE_DIR, num_file), master_mono_clip(p_num, speed=speed))
            save_mp3(os.path.join(VOICE_DIR, over_actions[i]), master_mono_clip(p_action, speed=speed))
            print(f"  ✅ [연결 분할] {over_actions[i]} 저장 완료")

    # 4. 파트 4: 직선 스퍼트 2종 (batch_stretch)
    stretch_candidates = [f for f in files if "stretch" in f.lower() or "part4" in f.lower()]
    if stretch_candidates:
        src = os.path.join(IMPORT_DIR, stretch_candidates[0])
        print(f"\n[4/5] 직선 스퍼트 연결 2종 분할: {src}")
        with open(src, "rb") as f:
            dec = miniaudio.decode(f.read(), output_format=miniaudio.SampleFormat.FLOAT32, nchannels=2, sample_rate=SAMPLE_RATE)
        mono = np.mean(np.frombuffer(dec.samples, dtype=np.float32).reshape(-1, dec.nchannels), axis=1)
        segs = detect_voice_segments(mono)
        stretch_actions = ["vo_us_stretch_02.mp3", "vo_us_stretch_chui.mp3"]
        for i in range(min(2, len(segs))):
            sent = mono[segs[i][0]:segs[i][1]]
            _, p_action = split_sentence_at_comma(sent)
            save_mp3(os.path.join(VOICE_DIR, stretch_actions[i]), master_mono_clip(p_action, speed=speed))
            print(f"  ✅ [연결 분할] {stretch_actions[i]} 저장 완료")

    # 5. 파트 5: 골인 및 우승 2종 (batch_win)
    win_candidates = [f for f in files if "win" in f.lower() or "part5" in f.lower()]
    if win_candidates:
        src = os.path.join(IMPORT_DIR, win_candidates[0])
        print(f"\n[5/5] 골인 및 우승 연결 2종 분할: {src}")
        with open(src, "rb") as f:
            dec = miniaudio.decode(f.read(), output_format=miniaudio.SampleFormat.FLOAT32, nchannels=2, sample_rate=SAMPLE_RATE)
        mono = np.mean(np.frombuffer(dec.samples, dtype=np.float32).reshape(-1, dec.nchannels), axis=1)
        segs = detect_voice_segments(mono)
        win_actions = ["vo_us_win_01.mp3", "vo_us_win_03.mp3"]
        for i in range(min(2, len(segs))):
            sent = mono[segs[i][0]:segs[i][1]]
            _, p_action = split_sentence_at_comma(sent)
            save_mp3(os.path.join(VOICE_DIR, win_actions[i]), master_mono_clip(p_action, speed=speed))
            print(f"  ✅ [연결 분할] {win_actions[i]} 저장 완료")

    print("\n🎉 모든 연결 호흡 음원 분할 및 마스터링 완결!")
    sim_script = os.path.join(os.path.dirname(__file__), "generate_race_simulation.py")
    if os.path.exists(sim_script):
        print("\n🔄 풀 레이스 시뮬레이션 데모 갱신 중...")
        os.system(f'python "{sim_script}"')
        print("✅ 풀 레이스 데모 갱신 완료!")

def main():
    parser = argparse.ArgumentParser(description="Split Connected Voice Audio")
    parser.add_argument("--speed", type=float, default=1.25, help="Playback speed multiplier")
    args = parser.parse_args()
    process_all_connected_batches(speed=args.speed)

if __name__ == "__main__":
    main()
