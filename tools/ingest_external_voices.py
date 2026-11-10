"""
외부 AI 서비스(ElevenLabs, Fish Audio 등)에서 생성된 음원 파일을
ROOSTER RUMBLE 프로젝트 규격에 맞게 자동 인제스트(검증, DSP 마스터링, 피치 보존 타임스트레치, 데모 재합성)하는 스크립트
"""

import os
import sys
import shutil
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
IMPORT_DIR = os.path.join(BASE_DIR, "assets", "audio", "race", "voice_import")

os.makedirs(IMPORT_DIR, exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)

TARGET_FILES = [
    "vo_rooster_num_01.mp3", "vo_rooster_num_02.mp3", "vo_rooster_num_03.mp3",
    "vo_rooster_num_04.mp3", "vo_rooster_num_05.mp3", "vo_rooster_num_06.mp3",
    "vo_us_start_01.mp3", "vo_us_start_02.mp3", "vo_us_start_03.mp3",
    "vo_us_flinch_01.mp3", "vo_us_flinch_02.mp3",
    "vo_us_early_01.mp3", "vo_us_early_02.mp3", "vo_us_early_03.mp3",
    "vo_us_over_01.mp3", "vo_us_over_02.mp3", "vo_us_over_03.mp3", "vo_us_side_01.mp3",
    "vo_us_stretch_01.mp3", "vo_us_stretch_02.mp3", "vo_us_stretch_03.mp3", "vo_us_stretch_chui.mp3",
    "vo_us_win_01.mp3", "vo_us_win_02.mp3", "vo_us_win_03.mp3",
    "vo_us_photo_01.mp3", "vo_us_photo_02.mp3"
]

def phase_vocoder_time_stretch(mono: np.ndarray, rate: float = 1.0, sr: int = SAMPLE_RATE) -> np.ndarray:
    """
    피치(음높이) 변화 없이 발음 속도만 정밀하게 조절하는 Phase Vocoder 엔진
    rate > 1.0: 고속 재생 (예: 1.25 = 25% 가속)
    """
    if abs(rate - 1.0) < 0.01:
        return mono

    n_fft = 2048
    hop = 512
    win = np.hanning(n_fft)

    # STFT
    num_frames = (len(mono) - n_fft) // hop + 1
    if num_frames < 2:
        return mono

    frames = np.lib.stride_tricks.sliding_window_view(mono[:(num_frames - 1) * hop + n_fft], n_fft)[::hop]
    stft = np.fft.rfft(frames * win, axis=-1).T

    # Phase Vocoder
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

    # iSTFT
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

def master_voice_file(src_path: str, dst_path: str, speed: float = 1.0):
    with open(src_path, "rb") as f:
        dec = miniaudio.decode(f.read(), output_format=miniaudio.SampleFormat.FLOAT32, nchannels=2, sample_rate=SAMPLE_RATE)
    sr = dec.sample_rate
    raw = np.frombuffer(dec.samples, dtype=np.float32).reshape(-1, dec.nchannels)
    mono = np.mean(raw, axis=1) if dec.nchannels > 1 else raw[:, 0]

    # 속도 조절 (피치 불변 Time-stretch)
    if abs(speed - 1.0) >= 0.02:
        mono = phase_vocoder_time_stretch(mono, rate=speed, sr=sr)

    # 140Hz HPF + 2.8k~4.8k EQ boost
    sos_hp = signal.butter(3, 140, btype='highpass', fs=sr, output='sos')
    filtered = signal.sosfilt(sos_hp, mono)
    sos_bp = signal.butter(2, [2800, 4800], btype='bandpass', fs=sr, output='sos')
    filtered += signal.sosfilt(sos_bp, filtered) * 0.35

    mx = np.max(np.abs(filtered))
    if mx > 0:
        filtered = filtered / mx * 0.88

    stereo = np.zeros((len(filtered), 2))
    fade_len = int(0.01 * sr)
    filtered[:fade_len] *= np.linspace(0, 1, fade_len)
    filtered[-fade_len:] *= np.linspace(1, 0, fade_len)
    stereo[:, 0] = filtered
    stereo[:, 1] = filtered

    save_mp3(dst_path, stereo)

def main():
    parser = argparse.ArgumentParser(description="External Voice Ingestion Tool")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier (e.g. 1.25 for +25% speed)")
    args = parser.parse_args()

    print(f"========================================================")
    print(f"📥 외부 보이스 파일 인제스트 마스터 도구")
    print(f"   - 소스 폴더: {IMPORT_DIR}")
    print(f"   - 대상 폴더: {VOICE_DIR}")
    print(f"   - 적용 배속: {args.speed:.2f}x {'(기본 속도)' if args.speed == 1.0 else '(피치 보존 고속화)'}")
    print(f"========================================================")

    found_files = [f for f in os.listdir(IMPORT_DIR) if f.endswith(('.mp3', '.wav'))]
    if not found_files:
        print(f"\n[안내] {IMPORT_DIR} 폴더에 인제스트할 오디오 파일이 없습니다.")
        print(f"외부 AI 서비스에서 생성한 파일들을 해당 폴더에 넣은 뒤 다시 실행하십시오.")
        return

    count = 0
    for target in TARGET_FILES:
        base_name = os.path.splitext(target)[0]
        match = None
        for f in found_files:
            if f == target or os.path.splitext(f)[0] == base_name:
                match = f
                break
        
        if match:
            src = os.path.join(IMPORT_DIR, match)
            dst = os.path.join(VOICE_DIR, target)
            master_voice_file(src, dst, speed=args.speed)
            print(f"  [인제스트 완료] {match} -> {target} (배속: {args.speed}x)")
            count += 1

    print(f"\n총 {count}/{len(TARGET_FILES)}개 파일 인제스트 및 마스터링 완료.")
    if count > 0:
        sim_script = os.path.join(os.path.dirname(__file__), "generate_race_simulation.py")
        if os.path.exists(sim_script):
            print("\n🔄 풀 레이스 시뮬레이션 데모 자동 갱신 중...")
            os.system(f'python "{sim_script}"')
            print("✅ 풀 레이스 시뮬레이션 데모 갱신 완료!")

if __name__ == "__main__":
    main()
