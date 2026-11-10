"""
통합 녹음된 단일 오디오 파일에서 무음 구간을 감지하여 개별 보이스 에셋으로 자동 정밀 분할하는 도구
- 6개 전체 배치(선수번호 6종, W-1~W-5 21종) 일괄 분할 지원
- 피치 보존 고속화(Time-stretch) 및 DSP 마스터링 자동 연계
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

# 6대 배치별 대상 파일명 매핑
BATCH_SPECS = {
    "batch_01": {
        "name": "배치 1: 선수 번호 (6종)",
        "aliases": ["batch_01", "batch1", "number", "num", "01"],
        "expected_count": 6,
        "targets": [
            "vo_rooster_num_01.mp3",
            "vo_rooster_num_02.mp3",
            "vo_rooster_num_03.mp3",
            "vo_rooster_num_04.mp3",
            "vo_rooster_num_05.mp3",
            "vo_rooster_num_06.mp3",
        ]
    },
    "batch_02": {
        "name": "배치 2: W-1 출발 및 늦출발 (5종)",
        "aliases": ["batch_02", "batch2", "start", "flinch", "w1", "02"],
        "expected_count": 5,
        "targets": [
            "vo_us_start_01.mp3",
            "vo_us_start_02.mp3",
            "vo_us_start_03.mp3",
            "vo_us_flinch_01.mp3",
            "vo_us_flinch_02.mp3",
        ]
    },
    "batch_03": {
        "name": "배치 3: W-2 초반 선두 (3종)",
        "aliases": ["batch_03", "batch3", "early", "lead", "w2", "03"],
        "expected_count": 3,
        "targets": [
            "vo_us_early_01.mp3",
            "vo_us_early_02.mp3",
            "vo_us_early_03.mp3",
        ]
    },
    "batch_04": {
        "name": "배치 4: W-3 중반 역전 및 접전 (4종)",
        "aliases": ["batch_04", "batch4", "over", "surge", "w3", "04"],
        "expected_count": 4,
        "targets": [
            "vo_us_over_01.mp3",
            "vo_us_over_02.mp3",
            "vo_us_over_03.mp3",
            "vo_us_side_01.mp3",
        ]
    },
    "batch_05": {
        "name": "배치 5: W-4 라스트 스퍼트 (4종)",
        "aliases": ["batch_05", "batch5", "stretch", "wire", "w4", "05"],
        "expected_count": 4,
        "targets": [
            "vo_us_stretch_01.mp3",
            "vo_us_stretch_02.mp3",
            "vo_us_stretch_03.mp3",
            "vo_us_stretch_chui.mp3",
        ]
    },
    "batch_06": {
        "name": "배치 6: W-5 골인 및 판독 (5종)",
        "aliases": ["batch_06", "batch6", "win", "finish", "photo", "w5", "06"],
        "expected_count": 5,
        "targets": [
            "vo_us_win_01.mp3",
            "vo_us_win_02.mp3",
            "vo_us_win_03.mp3",
            "vo_us_photo_01.mp3",
            "vo_us_photo_02.mp3",
        ]
    }
}

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

def detect_voice_segments(audio: np.ndarray, sr: int = SAMPLE_RATE, threshold: float = 0.025, min_silence_sec: float = 0.22):
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

def process_batch_file(filepath: str, batch_key: str, speed: float = 1.0):
    spec = BATCH_SPECS[batch_key]
    print(f"\n--- [{spec['name']}] 분할 처리 시작 ---")
    print(f"  소스 파일: {filepath}")

    with open(filepath, "rb") as f:
        dec = miniaudio.decode(f.read(), output_format=miniaudio.SampleFormat.FLOAT32, nchannels=2, sample_rate=SAMPLE_RATE)
    raw = np.frombuffer(dec.samples, dtype=np.float32).reshape(-1, dec.nchannels)
    mono = np.mean(raw, axis=1) if dec.nchannels > 1 else raw[:, 0]

    segments = detect_voice_segments(mono, sr=SAMPLE_RATE)
    expected = spec["expected_count"]
    print(f"  [신호 감지] {len(segments)}개 구간 감지됨 (기대치: {expected}개)")

    if len(segments) != expected:
        print(f"  ⚠️ [주의] 감지된 구간 수({len(segments)})와 목표 수량({expected})이 일치하지 않습니다.")
        if len(segments) < expected:
            print(f"  분할 실패: 멘트 간 간격을 최소 0.5초 이상 띄우고 다시 생성하십시오.")
            return False

    targets = spec["targets"]
    for i in range(min(expected, len(segments))):
        s_start, s_end = segments[i]
        clip = mono[s_start:s_end]
        mastered = master_mono_clip(clip, speed=speed)
        
        target_name = targets[i]
        target_path = os.path.join(VOICE_DIR, target_name)
        save_mp3(target_path, mastered)
        dur = len(mastered) / SAMPLE_RATE
        print(f"  ✅ [{i+1}/{expected}] {target_name} (길이: {dur:.2f}s, 배속: {speed}x) 저장 완료")

    return True

def identify_batch(filename: str):
    lower = filename.lower()
    for b_key, spec in BATCH_SPECS.items():
        for alias in spec["aliases"]:
            if alias in lower:
                return b_key
    return None

def main():
    parser = argparse.ArgumentParser(description="Multi-batch Audio Splitter")
    parser.add_argument("--batch", choices=["batch_01", "batch_02", "batch_03", "batch_04", "batch_05", "batch_06"], help="Force specific batch")
    parser.add_argument("--speed", type=float, default=1.25, help="Playback speed multiplier (default: 1.25)")
    parser.add_argument("--rebuild-sim", action="store_true", help="Rebuild full race simulation demos after split")
    args = parser.parse_args()

    # IMPORT_DIR에 있는 모든 mp3/wav 파일 자동 검사
    files = [f for f in os.listdir(IMPORT_DIR) if f.endswith(('.mp3', '.wav'))]
    if not files:
        print(f"\n[안내] {IMPORT_DIR} 폴더에 분할할 오디오 파일이 없습니다.")
        print(f"일레븐랩스에서 생성한 통합 오디오 파일을 해당 폴더에 넣은 후 실행하십시오.")
        return

    processed = 0
    for fname in sorted(files):
        fpath = os.path.join(IMPORT_DIR, fname)
        b_key = args.batch or identify_batch(fname)
        if b_key:
            ok = process_batch_file(fpath, b_key, speed=args.speed)
            if ok:
                processed += 1
        else:
            print(f"  [건너뜀] {fname}: 배치 번호 식별 불가 (예: batch_01_numbers.mp3 와 같이 명명 권장)")

    print(f"\n🎉 총 {processed}개 배치 분할 처리 완료.")
    
    if args.rebuild_sim or processed > 0:
        sim_script = os.path.join(os.path.dirname(__file__), "generate_race_simulation.py")
        if os.path.exists(sim_script):
            print("\n🔄 풀 레이스 시뮬레이션 데모 자동 갱신 중...")
            os.system(f'python "{sim_script}"')
            print("✅ 풀 레이스 시뮬레이션 데모 갱신 완료!")

if __name__ == "__main__":
    main()
