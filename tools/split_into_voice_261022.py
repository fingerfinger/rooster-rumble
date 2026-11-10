"""
ROOSTER RUMBLE: voice_261022 전용 정밀 다중 타입 분할 및 마스터링 스크립트
- 기존 assets/audio/race/voice 폴더는 100% 보존 (삭제/수정 없음)
- 신규 assets/audio/race/voice_261022 폴더에 타입별(type_1, type_2, type_3) 및 통합 파일 생성
- 10개 배치 파일 전수 정밀 커팅, 140Hz HPF + 프레즌스 EQ + 아날로그 마스터링 적용
"""

import os
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
import numpy as np
import lameenc
import miniaudio
from scipy import signal

SAMPLE_RATE = 44100
BITRATE = 192

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio", "race")
IMPORT_DIR = os.path.join(AUDIO_DIR, "voice_import")
OUT_ROOT = os.path.join(AUDIO_DIR, "voice_261022")
OUT_T1 = os.path.join(OUT_ROOT, "type_1")
OUT_T2 = os.path.join(OUT_ROOT, "type_2")
OUT_T3 = os.path.join(OUT_ROOT, "type_3")

for d in [OUT_ROOT, OUT_T1, OUT_T2, OUT_T3]:
    os.makedirs(d, exist_ok=True)

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

def master_clip(clip: np.ndarray, sr: int = SAMPLE_RATE) -> np.ndarray:
    mono = np.mean(clip, axis=1) if clip.ndim > 1 else clip

    # 140Hz 3차 HPF
    sos_hp = signal.butter(3, 140, btype='highpass', fs=sr, output='sos')
    filtered = signal.sosfilt(sos_hp, mono)

    # 2.8k ~ 4.8k 프레즌스 EQ (+35%)
    sos_bp = signal.butter(2, [2800, 4800], btype='bandpass', fs=sr, output='sos')
    filtered += signal.sosfilt(sos_bp, filtered) * 0.35

    # 0.88 헤드룸 피크 정규화
    mx = np.max(np.abs(filtered))
    if mx > 0:
        filtered = filtered / mx * 0.88

    # 스테레오 센터 배치 & 10ms 페이드
    stereo = np.zeros((len(filtered), 2))
    fade_len = int(0.01 * sr)
    filtered[:fade_len] *= np.linspace(0, 1, fade_len)
    filtered[-fade_len:] *= np.linspace(1, 0, fade_len)
    stereo[:, 0] = filtered
    stereo[:, 1] = filtered
    return stereo

def load_file(filename: str):
    p = os.path.join(IMPORT_DIR, filename)
    with open(p, "rb") as f:
        dec = miniaudio.decode(f.read(), output_format=miniaudio.SampleFormat.FLOAT32, nchannels=2, sample_rate=SAMPLE_RATE)
    raw = np.frombuffer(dec.samples, dtype=np.float32)
    return raw.reshape(-1, dec.nchannels), dec.sample_rate

# ==============================================================================
# 정밀 타임스탬프 커팅 정의 테이블
# ==============================================================================
# 각 항목: (소스파일명, 시작초, 끝초, 타깃파일명, 타입번호 1/2/3)
CUT_SPECS = [
    # --------------------------------------------------------------------------
    # 1. batch_early.mp3 (타입 1: 1~3번 번호 + W-2 선두 3종)
    # --------------------------------------------------------------------------
    ("batch_early.mp3", 0.00, 0.85, "vo_rooster_num_01.mp3", 1),
    ("batch_early.mp3", 1.10, 3.75, "vo_us_early_01.mp3", 1),
    ("batch_early.mp3", 4.20, 5.15, "vo_rooster_num_02.mp3", 1),
    ("batch_early.mp3", 5.35, 7.10, "vo_us_early_02.mp3", 1),
    ("batch_early.mp3", 7.65, 8.60, "vo_rooster_num_03.mp3", 1),
    ("batch_early.mp3", 8.80, 10.68, "vo_us_early_03.mp3", 1),

    # --------------------------------------------------------------------------
    # 2. batch_overtake_1.mp3 (타입 1: 4~6번 번호 + W-3 역전 4종)
    # --------------------------------------------------------------------------
    ("batch_overtake_1.mp3", 0.08, 1.05, "vo_rooster_num_04.mp3", 1),
    ("batch_overtake_1.mp3", 1.15, 2.60, "vo_us_over_01.mp3", 1),
    ("batch_overtake_1.mp3", 2.95, 3.85, "vo_rooster_num_05.mp3", 1),
    ("batch_overtake_1.mp3", 4.00, 5.95, "vo_us_over_02.mp3", 1),
    ("batch_overtake_1.mp3", 6.25, 7.20, "vo_rooster_num_06.mp3", 1),
    ("batch_overtake_1.mp3", 7.30, 8.75, "vo_us_over_03.mp3", 1),
    ("batch_overtake_1.mp3", 10.74, 12.65, "vo_us_side_01.mp3", 1),

    # --------------------------------------------------------------------------
    # 3. batch_overtake_2.mp3 (타입 2: 4~6번 번호 + W-3 역전 4종)
    # --------------------------------------------------------------------------
    ("batch_overtake_2.mp3", 0.10, 1.12, "vo_rooster_num_04.mp3", 2),
    ("batch_overtake_2.mp3", 1.20, 2.80, "vo_us_over_01.mp3", 2),
    ("batch_overtake_2.mp3", 3.40, 4.45, "vo_rooster_num_05.mp3", 2),
    ("batch_overtake_2.mp3", 4.60, 6.60, "vo_us_over_02.mp3", 2),
    ("batch_overtake_2.mp3", 7.20, 8.25, "vo_rooster_num_06.mp3", 2),
    ("batch_overtake_2.mp3", 8.35, 9.95, "vo_us_over_03.mp3", 2),
    ("batch_overtake_2.mp3", 12.75, 15.00, "vo_us_side_01.mp3", 2),

    # --------------------------------------------------------------------------
    # 4. batch_stretch_1.mp3 (타입 1: W-4 스퍼트 2종)
    # --------------------------------------------------------------------------
    ("batch_stretch_1.mp3", 1.18, 3.40, "vo_us_stretch_02.mp3", 1),
    ("batch_stretch_1.mp3", 4.70, 6.45, "vo_us_stretch_chui.mp3", 1),

    # --------------------------------------------------------------------------
    # 5. batch_stretch_2.mp3 (타입 2: W-4 스퍼트 2종)
    # --------------------------------------------------------------------------
    ("batch_stretch_2.mp3", 1.25, 3.75, "vo_us_stretch_02.mp3", 2),
    ("batch_stretch_2.mp3", 5.40, 7.35, "vo_us_stretch_chui.mp3", 2),

    # --------------------------------------------------------------------------
    # 6. batch_win_1.mp3 (타입 1: W-5 우승 2종)
    # --------------------------------------------------------------------------
    ("batch_win_1.mp3", 1.13, 4.30, "vo_us_win_01.mp3", 1),
    ("batch_win_1.mp3", 5.75, 8.15, "vo_us_win_03.mp3", 1),

    # --------------------------------------------------------------------------
    # 7. batch_win_2.mp3 (타입 2: W-5 우승 2종)
    # --------------------------------------------------------------------------
    ("batch_win_2.mp3", 1.18, 4.70, "vo_us_win_01.mp3", 2),
    ("batch_win_2.mp3", 6.10, 8.45, "vo_us_win_03.mp3", 2),

    # --------------------------------------------------------------------------
    # 8. batch_solo_1.mp3 (타입 1: 단독 10종)
    # --------------------------------------------------------------------------
    ("batch_solo_1.mp3", 0.00, 1.50, "vo_us_start_01.mp3", 1),
    ("batch_solo_1.mp3", 1.80, 4.00, "vo_us_start_02.mp3", 1),
    ("batch_solo_1.mp3", 4.35, 6.70, "vo_us_start_03.mp3", 1),
    ("batch_solo_1.mp3", 7.10, 9.68, "vo_us_flinch_01.mp3", 1),
    ("batch_solo_1.mp3", 10.05, 13.00, "vo_us_flinch_02.mp3", 1),
    ("batch_solo_1.mp3", 13.40, 15.10, "vo_us_stretch_01.mp3", 1),
    ("batch_solo_1.mp3", 15.35, 17.10, "vo_us_stretch_03.mp3", 1),
    ("batch_solo_1.mp3", 17.35, 20.95, "vo_us_photo_01.mp3", 1),
    ("batch_solo_1.mp3", 21.20, 24.25, "vo_us_photo_02.mp3", 1),
    ("batch_solo_1.mp3", 24.50, 27.01, "vo_us_win_02.mp3", 1),

    # --------------------------------------------------------------------------
    # 9. batch_solo_2.mp3 (타입 2: 단독 10종)
    # --------------------------------------------------------------------------
    ("batch_solo_2.mp3", 0.00, 1.60, "vo_us_start_01.mp3", 2),
    ("batch_solo_2.mp3", 1.84, 3.70, "vo_us_start_02.mp3", 2),
    ("batch_solo_2.mp3", 4.04, 6.20, "vo_us_start_03.mp3", 2),
    ("batch_solo_2.mp3", 6.55, 8.95, "vo_us_flinch_01.mp3", 2),
    ("batch_solo_2.mp3", 9.30, 11.70, "vo_us_flinch_02.mp3", 2),
    ("batch_solo_2.mp3", 12.10, 13.70, "vo_us_stretch_01.mp3", 2),
    ("batch_solo_2.mp3", 14.00, 15.60, "vo_us_stretch_03.mp3", 2),
    ("batch_solo_2.mp3", 15.85, 18.75, "vo_us_photo_01.mp3", 2),
    ("batch_solo_2.mp3", 19.05, 21.35, "vo_us_photo_02.mp3", 2),
    ("batch_solo_2.mp3", 21.65, 24.11, "vo_us_win_02.mp3", 2),

    # --------------------------------------------------------------------------
    # 10. batch_solo_3.mp3 (타입 3: 단독 10종)
    # --------------------------------------------------------------------------
    ("batch_solo_3.mp3", 0.00, 1.60, "vo_us_start_01.mp3", 3),
    ("batch_solo_3.mp3", 2.05, 4.10, "vo_us_start_02.mp3", 3),
    ("batch_solo_3.mp3", 4.70, 6.95, "vo_us_start_03.mp3", 3),
    ("batch_solo_3.mp3", 7.65, 10.15, "vo_us_flinch_01.mp3", 3),
    ("batch_solo_3.mp3", 10.75, 13.60, "vo_us_flinch_02.mp3", 3),
    ("batch_solo_3.mp3", 14.20, 16.10, "vo_us_stretch_01.mp3", 3),
    ("batch_solo_3.mp3", 16.60, 18.40, "vo_us_stretch_03.mp3", 3),
    ("batch_solo_3.mp3", 19.00, 22.60, "vo_us_photo_01.mp3", 3),
    ("batch_solo_3.mp3", 23.20, 26.10, "vo_us_photo_02.mp3", 3),
    ("batch_solo_3.mp3", 26.70, 29.31, "vo_us_win_02.mp3", 3),
]

def main():
    print("==================================================================")
    print("🎙️  ROOSTER RUMBLE: voice_261022 분할 및 마스터링 시작")
    print(f"   - 기존 assets/audio/race/voice 폴더: 100% 보존 유지")
    print(f"   - 신규 저장 경로: {OUT_ROOT}")
    print("==================================================================")

    # 캐시 파일 로드
    cache = {}
    for src_file, _, _, _, _ in CUT_SPECS:
        if src_file not in cache:
            cache[src_file] = load_file(src_file)

    created_counts = {1: 0, 2: 0, 3: 0}

    for src_file, t_start, t_end, target_name, t_type in CUT_SPECS:
        raw_data, sr = cache[src_file]
        s_idx = int(t_start * sr)
        e_idx = min(len(raw_data), int(t_end * sr))
        clip = raw_data[s_idx:e_idx]

        mastered = master_clip(clip, sr=sr)
        dur = len(mastered) / sr

        # 1) 타입별 전용 서브폴더 저장 (type_1, type_2, type_3)
        type_dir = OUT_T1 if t_type == 1 else (OUT_T2 if t_type == 2 else OUT_T3)
        save_mp3(os.path.join(type_dir, target_name), mastered)

        # 2) 루트 폴더 저장:
        #    - 타입 1은 표준 인게임 파일명(vo_us_start_01.mp3)으로 저장하여 즉시 사용 가능
        #    - 모든 타입은 넘버 고려 접미사(vo_us_start_01_1.mp3, _2.mp3, _3.mp3)로도 보존
        base, ext = os.path.splitext(target_name)
        numbered_name = f"{base}_{t_type}{ext}"
        save_mp3(os.path.join(OUT_ROOT, numbered_name), mastered)

        if t_type == 1:
            save_mp3(os.path.join(OUT_ROOT, target_name), mastered)

        created_counts[t_type] += 1
        print(f"  [{t_type}번 타입] {numbered_name} ({dur:.2f}s) <- {src_file} [{t_start:.2f}s~{t_end:.2f}s]")

    print("\n==================================================================")
    print(f"🎉 voice_261022 폴더 분할 및 마스터링 100% 완결!")
    print(f"   - 타입 1 에셋 생성: {created_counts[1]}개 (27종 풀 세트 완성)")
    print(f"   - 타입 2 에셋 생성: {created_counts[2]}개")
    print(f"   - 타입 3 에셋 생성: {created_counts[3]}개")
    print(f"   - 총 생성 파일: {sum(created_counts.values())}개 에셋")
    print(f"   - 저장 위치: {OUT_ROOT}")
    print("==================================================================")

if __name__ == "__main__":
    main()
