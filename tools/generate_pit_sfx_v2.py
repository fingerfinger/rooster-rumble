#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROOSTER RUMBLE - Rumble Pit v2.1 전면 차별화·리얼 사운드 제작 파이프라인
- "1기술 · 1재질 · 1리듬 · 소스 배타 할당" 원칙으로 공/방·스페셜(F33/F34)·특수상태 15종 전면 리디자인
- 공포 느낌의 oooooooooo.ogg 전면 폐기 -> 실사 경기장 급등 서지 + 다중 관중 탄성 리액션 교체
- 출력 규격: Stereo, 44.1 kHz, 192 kbps MP3, DC 오프셋 제거, 피크 헤드룸 -0.8 ~ -1.2 dBFS
"""

import os
import asyncio
import numpy as np
import miniaudio
import lameenc
import edge_tts
from scipy import signal

SAMPLE_RATE = 44100
BITRATE = 192
TARGET_PEAK = 0.891  # -1.0 dBFS (MP3 인코딩 후에도 클리핑 0건 유지)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "tools", "source_cache")
CC0_DIR = os.path.join(CACHE_DIR, "pit_cc0")
PIT_DIR = os.path.join(BASE_DIR, "assets", "audio", "pit")
SFX_DIR = os.path.join(PIT_DIR, "sfx")
BGM_DIR = os.path.join(PIT_DIR, "bgm")
DEMO_DIR = os.path.join(PIT_DIR, "demo")
BACKUP_DIR = os.path.join(PIT_DIR, "sfx_v1_backup")
RACE_SFX_DIR = os.path.join(BASE_DIR, "assets", "audio", "race", "sfx")
VOICE_RAW_DIR = os.path.join(CC0_DIR, "voice_raw")

os.makedirs(SFX_DIR, exist_ok=True)
os.makedirs(BGM_DIR, exist_ok=True)
os.makedirs(DEMO_DIR, exist_ok=True)
os.makedirs(VOICE_RAW_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# 오디오 입출력 및 기본 유틸리티
# ---------------------------------------------------------------------------
def load_audio(path: str, nchannels: int = 1) -> np.ndarray:
    with open(path, "rb") as f:
        dec = miniaudio.decode(
            f.read(),
            output_format=miniaudio.SampleFormat.FLOAT32,
            nchannels=nchannels,
            sample_rate=SAMPLE_RATE,
        )
    arr = np.frombuffer(dec.samples, dtype=np.float32).copy()
    if nchannels == 2:
        arr = arr.reshape(-1, 2)
    return arr


def trim_onset(x: np.ndarray, thresh_ratio: float = 0.08, pre_ms: float = 2.5) -> np.ndarray:
    if len(x) == 0:
        return x
    pk = np.max(np.abs(x))
    if pk < 1e-6:
        return x
    idx = np.where(np.abs(x) >= pk * thresh_ratio)[0]
    if len(idx) == 0:
        return x
    start = max(0, int(idx[0] - pre_ms * SAMPLE_RATE / 1000.0))
    out = x[start:].copy()
    fade = min(int(0.002 * SAMPLE_RATE), len(out))
    if fade > 1:
        out[:fade] *= np.linspace(0.0, 1.0, fade)
    return out


def trim_tail(x: np.ndarray, thresh_ratio: float = 0.015, pad_ms: float = 35.0) -> np.ndarray:
    if len(x) == 0:
        return x
    pk = np.max(np.abs(x))
    if pk < 1e-6:
        return x
    idx = np.where(np.abs(x) >= pk * thresh_ratio)[0]
    if len(idx) == 0:
        return x
    end = min(len(x), int(idx[-1] + pad_ms * SAMPLE_RATE / 1000.0))
    return x[:end].copy()


def slice_ms(x: np.ndarray, start_ms: float, dur_ms: float) -> np.ndarray:
    s = max(0, int(start_ms * SAMPLE_RATE / 1000.0))
    e = min(len(x), s + int(dur_ms * SAMPLE_RATE / 1000.0))
    return x[s:e].copy()


def fade_io(x: np.ndarray, fade_in_ms: float = 2.0, fade_out_ms: float = 30.0) -> np.ndarray:
    out = x.copy()
    fi = min(int(fade_in_ms * SAMPLE_RATE / 1000.0), len(out) // 3)
    fo = min(int(fade_out_ms * SAMPLE_RATE / 1000.0), len(out) // 2)
    if fi > 1:
        env = np.linspace(0.0, 1.0, fi)
        out[:fi] *= env[:, None] if out.ndim == 2 else env
    if fo > 1:
        env = np.linspace(1.0, 0.0, fo)
        out[-fo:] *= env[:, None] if out.ndim == 2 else env
    return out


def resample_pitch(x: np.ndarray, semitones: float) -> np.ndarray:
    if abs(semitones) < 0.05 or len(x) < 32:
        return x
    ratio = 2.0 ** (semitones / 12.0)
    new_len = max(16, int(len(x) / ratio))
    xp = np.linspace(0.0, 1.0, len(x))
    fp = np.linspace(0.0, 1.0, new_len)
    return np.interp(fp, xp, x).astype(np.float32)


def norm_peak(x: np.ndarray, level: float = 1.0) -> np.ndarray:
    pk = np.max(np.abs(x)) if len(x) else 0.0
    if pk < 1e-8:
        return x
    return (x / pk * level).astype(np.float32)


def add_aligned(*items) -> np.ndarray:
    max_len = max((len(a) for a, _ in items), default=0)
    out = np.zeros(max_len, dtype=np.float32)
    for a, g in items:
        out[: len(a)] += a * g
    return out


def save_mp3(path: str, audio: np.ndarray, target_peak: float = TARGET_PEAK):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    x = audio.astype(np.float32).copy()
    if x.ndim == 1:
        x = np.column_stack([x, x])
    x -= np.mean(x, axis=0, keepdims=True)
    pk = np.max(np.abs(x))
    if pk > 1e-6:
        x = x / pk
        x = np.tanh(x * 1.12) / np.tanh(1.12)
        x = x / np.max(np.abs(x)) * target_peak
    int_data = np.int16(np.clip(x, -1.0, 1.0) * 32767).flatten()
    enc = lameenc.Encoder()
    enc.set_bit_rate(BITRATE)
    enc.set_in_sample_rate(SAMPLE_RATE)
    enc.set_channels(2)
    enc.set_quality(2)
    mp3_bytes = enc.encode(int_data.tobytes()) + enc.flush()
    with open(path, "wb") as f:
        f.write(mp3_bytes)


# ---------------------------------------------------------------------------
# DSP 프로세싱
# ---------------------------------------------------------------------------
def hpf(x: np.ndarray, freq: float, order: int = 2) -> np.ndarray:
    sos = signal.butter(order, freq, btype="highpass", fs=SAMPLE_RATE, output="sos")
    return signal.sosfilt(sos, x, axis=0).astype(np.float32)


def lpf(x: np.ndarray, freq: float, order: int = 2) -> np.ndarray:
    sos = signal.butter(order, min(freq, SAMPLE_RATE * 0.48), btype="lowpass", fs=SAMPLE_RATE, output="sos")
    return signal.sosfilt(sos, x, axis=0).astype(np.float32)


def bpf(x: np.ndarray, low_f: float, high_f: float, order: int = 2) -> np.ndarray:
    sos = signal.butter(order, [low_f, min(high_f, SAMPLE_RATE * 0.48)], btype="bandpass", fs=SAMPLE_RATE, output="sos")
    return signal.sosfilt(sos, x, axis=0).astype(np.float32)


def peaking_eq(x: np.ndarray, f0: float, q: float, gain_db: float) -> np.ndarray:
    if abs(gain_db) < 0.05:
        return x
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * f0 / SAMPLE_RATE
    alpha = np.sin(w0) / (2.0 * q)
    b0 = 1.0 + alpha * A
    b1 = -2.0 * np.cos(w0)
    b2 = 1.0 - alpha * A
    a0 = 1.0 + alpha / A
    a1 = -2.0 * np.cos(w0)
    a2 = 1.0 - alpha / A
    b = np.array([b0 / a0, b1 / a0, b2 / a0], dtype=np.float64)
    a = np.array([1.0, a1 / a0, a2 / a0], dtype=np.float64)
    return signal.lfilter(b, a, x, axis=0).astype(np.float32)


def transient_shaper(x: np.ndarray, attack_boost: float = 1.6, sustain_gain: float = 0.85, attack_ms: float = 18.0) -> np.ndarray:
    mono = x.mean(axis=1) if x.ndim == 2 else x
    fast_n = max(4, int(0.002 * SAMPLE_RATE))
    slow_n = max(16, int(attack_ms * SAMPLE_RATE / 1000.0))
    abs_m = np.abs(mono)
    fast_env = np.convolve(abs_m, np.ones(fast_n) / fast_n, mode="same")
    slow_env = np.convolve(abs_m, np.ones(slow_n) / slow_n, mode="same")
    diff = np.maximum(0.0, fast_env - slow_env)
    pk = np.max(abs_m) + 1e-6
    gain = sustain_gain + (attack_boost - sustain_gain) * np.clip(diff / (pk * 0.25), 0.0, 1.0)
    return (x * gain[:, None] if x.ndim == 2 else x * gain).astype(np.float32)


def warm_saturate(x: np.ndarray, drive: float = 1.25) -> np.ndarray:
    return (np.tanh(x * drive) / np.tanh(drive)).astype(np.float32)


def synth_sub_punch(dur_s: float = 0.28, f_start: float = 135.0, f_end: float = 44.0, decay_tau: float = 0.09) -> np.ndarray:
    n = int(dur_s * SAMPLE_RATE)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    freq = f_end + (f_start - f_end) * np.exp(-t / 0.022)
    phase = 2.0 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    body = np.sin(phase) + 0.25 * np.sin(phase * 2.0) * np.exp(-t / 0.03)
    env = (1.0 - np.exp(-t / 0.002)) * np.exp(-t / decay_tau)
    return (body * env).astype(np.float32)


def synth_noise_burst(dur_s: float, low_f: float, high_f: float, attack_s: float = 0.005, decay_tau: float = 0.08) -> np.ndarray:
    rng = np.random.default_rng(42)
    n = int(dur_s * SAMPLE_RATE)
    noise = rng.standard_normal(n).astype(np.float32)
    filtered = bpf(noise, low_f, high_f, order=2)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    env = np.minimum(1.0, t / max(1e-4, attack_s)) * np.exp(-t / decay_tau)
    return norm_peak(filtered * env, 1.0)


def make_stereo_wide(mono: np.ndarray, pan: float = 0.0, width_ms: float = 0.0) -> np.ndarray:
    angle = (pan + 1.0) * (np.pi / 4.0)
    l = mono * np.cos(angle)
    r = mono * np.sin(angle)
    if width_ms > 0.1:
        d = int(width_ms * SAMPLE_RATE / 1000.0)
        r_del = np.concatenate([np.zeros(d, dtype=np.float32), r[:-d]]) if len(r) > d else r
        r = 0.55 * r + 0.45 * r_del
    return np.column_stack([l, r]).astype(np.float32)


def arena_reverb(stereo: np.ndarray, wet: float = 0.14, tail_s: float = 0.30, pre_delay_ms: float = 12.0) -> np.ndarray:
    pad_n = int((tail_s + 0.08) * SAMPLE_RATE)
    src = np.vstack([stereo, np.zeros((pad_n, 2), dtype=np.float32)])
    n = len(src)
    rev = np.zeros_like(src)
    l_taps_ms = [12.0, 23.5, 37.2, 54.8, 76.1, 108.4, 151.0, 212.0]
    r_taps_ms = [15.3, 27.1, 41.9, 61.2, 83.7, 119.5, 167.0, 234.0]
    for idx, (lm, rm) in enumerate(zip(l_taps_ms, r_taps_ms)):
        dl = int((lm + pre_delay_ms) * SAMPLE_RATE / 1000.0)
        dr = int((rm + pre_delay_ms) * SAMPLE_RATE / 1000.0)
        g = (0.68 ** idx) * 0.42
        if dl < n:
            rev[dl:, 0] += src[: n - dl, 0] * g + src[: n - dl, 1] * (g * 0.25)
        if dr < n:
            rev[dr:, 1] += src[: n - dr, 1] * g + src[: n - dr, 0] * (g * 0.25)
    rev = lpf(hpf(rev, 160.0), 4200.0)
    out = src + rev * wet
    return trim_tail(out, thresh_ratio=0.008, pad_ms=35.0)


def mix_layers(total_dur_s: float, events: list) -> np.ndarray:
    n = int(total_dur_s * SAMPLE_RATE)
    out = np.zeros((n, 2), dtype=np.float32)
    for offset_ms, arr, gain, pan in events:
        if arr is None or len(arr) == 0:
            continue
        st = make_stereo_wide(arr, pan=pan) if arr.ndim == 1 else arr
        idx = int(offset_ms * SAMPLE_RATE / 1000.0)
        if idx < 0:
            st = st[-idx:]
            idx = 0
        if idx >= n:
            continue
        take = min(len(st), n - idx)
        out[idx : idx + take] += st[:take] * gain
    return out


# ---------------------------------------------------------------------------
# 소스 로딩 헬퍼
# ---------------------------------------------------------------------------
def S(rel_path: str, trim: bool = True, pitch: float = 0.0) -> np.ndarray:
    full = os.path.join(CC0_DIR, rel_path) if not os.path.isabs(rel_path) else rel_path
    x = load_audio(full, nchannels=1)
    if trim:
        x = trim_onset(x, thresh_ratio=0.06, pre_ms=2.0)
    if abs(pitch) >= 0.1:
        x = resample_pitch(x, pitch)
    return norm_peak(x, 1.0)


def C(rel_path: str, trim: bool = True, pitch: float = 0.0) -> np.ndarray:
    return S(os.path.join(CACHE_DIR, rel_path), trim=trim, pitch=pitch)


def R(fname: str, trim: bool = True, pitch: float = 0.0) -> np.ndarray:
    return S(os.path.join(RACE_SFX_DIR, fname), trim=trim, pitch=pitch)


# ---------------------------------------------------------------------------
# v2.1 25종(27개 파일) 제작 ("1기술 · 1재질 · 1리듬 · 소스 배타 할당")
# ---------------------------------------------------------------------------
def build_all_sfx():
    print("=== [1/3] 럼블 핏 v2.1 전면 차별화 SFX 25종 (27개 파일) 생성 시작 ===")
    produced = []

    # 각 재질별 배타 할당 소스 로딩
    # 1) 경질 부리 클릭
    wood_click = S("100_cc0_sfx/wooden_01.ogg")
    crack5 = S("wood_crack_hit/wood_impact/crack05.mp3.flac")
    thwack_snap = S("thwack/PCM/thwack-01.wav")

    # 2) 발톱 긁힘·찢김
    scrape3 = S("scrapes/scrape-3.wav")
    scrape6 = S("scrapes/scrape-6.wav")
    swish2 = S("swishes/swishes/swish-2.wav")

    # 3) 날갯짓·깃털
    flap_raw = load_audio(os.path.join(CC0_DIR, "dragonflap.wav"), 1)
    flap_1 = trim_onset(slice_ms(flap_raw, 120, 460), 0.05)
    flap_2 = trim_onset(slice_ms(flap_raw, 550, 480), 0.05)
    paper1 = S("100_cc0_sfx/paper_01.ogg")
    paper2 = S("100_cc0_sfx/paper_02.ogg")
    paper3 = S("100_cc0_sfx/paper_03.ogg")

    # 4) 육체 정타
    thwack_clean = S("thwack/PCM/thwack-09.wav")
    thwack_mid = S("hits_and_punches/hits/hit17.mp3.flac")

    # 5) 치명타 전용 파열
    gun_snap = hpf(slice_ms(C("9mm_gunshot.wav"), 0, 50), 1100.0)
    crack1 = S("wood_crack_hit/wood_impact/crack01.mp3.flac")
    splatter_crunch = trim_onset(slice_ms(load_audio(os.path.join(CC0_DIR, "extreme_splatter/extreme_splatter/crack11.mp3.flac"), 1), 1600, 380), 0.08)
    hit_heavy = S("hits_and_punches/hits/hit35.mp3.flac")

    # 6) 가드 흡수 전용 (고역 차단, 둔탁 방석)
    door_thud = S("100_cc0_sfx/door_close_03.ogg")
    imp_shield9 = S("impact_starninjas/impact.9.ogg")

    # 7) 패링 경질 충돌·링
    clash1 = S("sword_clash/sword_clash.1.ogg")
    ding4 = S("ding_starninjas/ding.4.ogg")

    # 8) 회피 vs 빗나감 스우시
    swish9 = S("swishes/swishes/swish-9.wav")
    swish7 = S("swishes/swishes/swish-7.wav")
    swish12 = S("swishes/swishes/swish-12.wav")
    swish13 = S("swishes/swishes/swish-13.wav")

    # 9) 스페셜 F33/F34 배타 소스
    switch1 = S("100_cc0_sfx/switch_01.ogg")
    towel3 = S("wet_towel_on_floor/wet_towel_on_floor/wet_towel_on_floor-03.flac")
    towel10 = S("wet_towel_on_floor/wet_towel_on_floor/wet_towel_on_floor-10.flac")
    jump1 = S("Jump_1.wav")
    jump2 = S("Jump_2.wav")
    jump3 = S("Jump_3.wav")
    phonk = lpf(C("phonk_kick.wav"), 180.0)
    dishes_gravel = lpf(S("100_cc0_sfx/dishes_02.ogg"), 2600.0)
    swish4 = S("swishes/swishes/swish-4.wav")
    bell2 = S("100_cc0_sfx/bell_02.ogg")
    ding1 = S("ding_starninjas/ding.1.ogg")
    thwack_heavy = S("thwack/PCM/thwack-04.wav")
    thwack_body = S("thwack/PCM/thwack-05.wav")
    hit12 = S("hits_and_punches/hits/hit12.mp3.flac")

    # 10) 외벽 목재 + 철망
    wall_wood = S("wood_crack_hit/wood_impact/impactwood02.mp3.flac")
    wood3 = S("100_cc0_sfx/wooden_03.ogg")
    metal6 = S("100_cc0_sfx/metal_06.ogg")
    metal11 = S("100_cc0_sfx/metal_11.ogg")

    # 11) 흙·수탉
    sand1 = R("sfx_race_gallop_1.mp3")
    sand2 = R("sfx_race_gallop_2.mp3")
    cluck1 = hpf(R("sfx_race_cluck_1.mp3"), 350.0)
    cluck2 = hpf(R("sfx_race_cluck_2.mp3"), 350.0)
    chicken_scream = hpf(trim_onset(C("chiecken.wav"), 0.1), 400.0)

    # ------------------------------------------------------------------
    # [A] 공격 기술 5종 (완전한 재질·리듬·대역 분리)
    # ------------------------------------------------------------------
    # 1. [공1] 전진 부리 속사: 저역 0% (HPF 520Hz), 초고속 3연타 스타카토 ("딱-딱-딱!")
    beak_hit_base = norm_peak(add_aligned(
        (hpf(slice_ms(wood_click, 0, 75), 520.0), 0.90),
        (hpf(slice_ms(thwack_snap, 0, 70), 650.0), 0.72),
        (hpf(slice_ms(crack5, 0, 45), 1400.0), 0.45),
    ))
    poke_mix = mix_layers(0.35, [
        (0, resample_pitch(beak_hit_base, 0.0), 0.90, -0.18),
        (75, resample_pitch(beak_hit_base, 2.5), 0.95, 0.18),
        (150, resample_pitch(beak_hit_base, 5.0), 1.05, 0.0),
        (165, slice_ms(resample_pitch(cluck1, 3.5), 0, 110), 0.16, 0.25),
    ])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_hit_poke.mp3"), fade_io(arena_reverb(poke_mix, wet=0.08, tail_s=0.14), 1.0, 25.0))
    produced.append("sfx_pit_hit_poke.mp3")

    # 2. [공2] 낮은 발톱 할퀴기: 날 선 발톱 연속 긁힘·찢김 ("츠아악-!") - 펀치·서브 제거
    claw_scrape = norm_peak(peaking_eq(bpf(slice_ms(scrape3, 0, 230), 1400.0, 8200.0), 3400, 1.1, 6.0))
    claw_scrape2 = bpf(slice_ms(scrape6, 0, 180), 2000.0, 7500.0)
    claw_snap = hpf(slice_ms(thwack_snap, 0, 110), 400.0)
    spur_mix = mix_layers(0.42, [
        (0, slice_ms(resample_pitch(swish2, 3.0), 0, 85), 0.65, -0.30),
        (22, claw_scrape, 1.10, 0.0),
        (28, claw_scrape2, 0.65, 0.25),
        (25, claw_snap, 0.60, -0.15),
    ])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_hit_spur.mp3"), fade_io(arena_reverb(spur_mix, wet=0.11, tail_s=0.20), 1.0, 35.0))
    produced.append("sfx_pit_hit_spur.mp3")

    # 3. [공3/공4] 비상 발톱 급습 · 광폭 난타: 뚜렷한 3연속 날갯짓 돌풍(0~270ms) -> 체중 급강하 강타(290ms)
    w1 = norm_peak(peaking_eq(hpf(slice_ms(resample_pitch(flap_1, 6.0), 0, 160), 220.0), 1600, 1.0, 5.0))
    w2 = norm_peak(peaking_eq(hpf(slice_ms(resample_pitch(flap_2, 7.0), 0, 160), 240.0), 1900, 1.0, 5.0))
    w3 = norm_peak(peaking_eq(hpf(slice_ms(resample_pitch(flap_1, 8.0), 0, 150), 260.0), 2100, 1.0, 5.5))
    dive_hit = norm_peak(add_aligned(
        (slice_ms(thwack_body, 0, 260), 0.90),
        (hpf(slice_ms(jump2, 0, 240), 90.0), 0.65),
    ))
    wing_mix = mix_layers(0.68, [
        (0, w1, 0.85, -0.38),
        (95, w2, 0.92, 0.38),
        (190, w3, 1.00, -0.25),
        (295, dive_hit, 1.10, 0.0),
        (305, slice_ms(resample_pitch(cluck2, 2.0), 0, 160), 0.16, 0.25),
    ])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_hit_wing.mp3"), fade_io(arena_reverb(warm_saturate(wing_mix, 1.2), wet=0.15, tail_s=0.26), 2.0, 45.0))
    produced.append("sfx_pit_hit_wing.mp3")

    # 4. [범용] 기본 정타 · 동시 격돌: 2.5~4.5kHz 타격 어택 스냅을 살린 단단한 정타 ("짝-퍽!")
    gen_punch = norm_peak(add_aligned(
        (transient_shaper(peaking_eq(bpf(slice_ms(thwack_clean, 0, 240), 140.0, 5500.0), 3200, 1.0, 5.5), 2.3, 0.78), 0.95),
        (peaking_eq(bpf(slice_ms(thwack_snap, 0, 140), 800.0, 6000.0), 2800, 1.1, 4.5), 0.65),
        (bpf(slice_ms(thwack_mid, 0, 220), 140.0, 1600.0), 0.55),
    ))
    gen_mix = mix_layers(0.28, [(0, gen_punch, 1.0, 0.0)])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_hit_gen.mp3"), fade_io(arena_reverb(warm_saturate(gen_mix, 1.25), wet=0.10, tail_s=0.18), 1.0, 30.0))
    produced.append("sfx_pit_hit_gen.mp3")

    # 5. 치명타 강타 · 가드 브레이크 파열: 22ms 호흡 정지 -> 폭발 파열 ("콰직!!") [배타적 파쇄+서브]
    inhale = fade_io(synth_noise_burst(0.022, 600, 2400, 0.015, 0.02)[::-1], 2.0, 2.0) * 0.25
    crit_crunch = peaking_eq(hpf(norm_peak(add_aligned((slice_ms(crack1, 0, 340), 0.7), (splatter_crunch, 0.85))), 450.0), 3400, 1.1, 5.5)
    crit_mix = mix_layers(0.68, [
        (0, inhale, 1.0, 0.0),
        (22, gun_snap, 0.72, -0.15),
        (22, transient_shaper(slice_ms(hit_heavy, 0, 360), 2.2, 0.85), 1.05, 0.0),
        (22, peaking_eq(slice_ms(thwack_heavy, 0, 300), 2200, 1.0, 4.0), 0.85, 0.15),
        (24, crit_crunch, 0.85, -0.20),
        (22, synth_sub_punch(0.30, 155, 45, 0.095), 0.75, 0.0),
        (45, slice_ms(resample_pitch(chicken_scream, 2.0), 0, 160), 0.14, 0.25),
    ])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_hit_crit.mp3"), fade_io(arena_reverb(warm_saturate(crit_mix, 1.55), wet=0.17, tail_s=0.32), 1.0, 50.0))
    produced.append("sfx_pit_hit_crit.mp3")

    # ------------------------------------------------------------------
    # [B] 방어 · 회피 · 패링 · 빗나감 4종
    # ------------------------------------------------------------------
    # 6. [방1] 깃털 부풀려 버티기: 부드러운 8ms 어택 + 480Hz↓ 둔탁 흡수 + 선명한 깃털 부스럭 ("쿵—푸스슥")
    cushion_thud = fade_io(norm_peak(add_aligned(
        (lpf(hpf(slice_ms(door_thud, 0, 220), 80.0), 480.0), 0.95),
        (lpf(hpf(slice_ms(imp_shield9, 0, 220), 90.0), 520.0), 0.72),
    )), 9.0, 35.0)
    feather_rustle = norm_peak(add_aligned(
        (bpf(slice_ms(paper2, 0, 260), 950.0, 3200.0), 0.85),
        (bpf(slice_ms(resample_pitch(flap_1, 6.0), 0, 200), 750.0, 2400.0), 0.55),
    ))
    guard_mix = mix_layers(0.36, [
        (0, cushion_thud, 0.92, -0.10),
        (12, feather_rustle, 0.78, 0.25),
    ])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_guard.mp3"), fade_io(arena_reverb(guard_mix, wet=0.11, tail_s=0.18), 2.0, 35.0))
    produced.append("sfx_pit_guard.mp3")

    # 7. [방3] 맞발톱 쳐내기 황금 패링: 저역 0% (HPF 900Hz), 100% 경질 충돌 + 메탈 링 ("챙—!!")
    parry_clash = peaking_eq(hpf(slice_ms(clash1, 0, 260), 900.0), 3800, 1.2, 5.0)
    parry_ring = peaking_eq(hpf(slice_ms(ding4, 0, 480), 1100.0), 3400, 1.4, 5.5)
    parry_mix = mix_layers(0.54, [
        (0, parry_clash, 0.95, -0.12),
        (4, parry_ring, 0.85, 0.15),
    ])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_guard_gen.mp3"), fade_io(arena_reverb(parry_mix, wet=0.18, tail_s=0.28), 1.0, 45.0))
    produced.append("sfx_pit_guard_gen.mp3")

    # 8. [방2] 납작 엎드리기 · 사이드 홉: 길고 매끈한 하강 스윕 ("슈우우욱-")
    dodge_sweep1 = bpf(resample_pitch(swish9, -1.5), 350.0, 2200.0)
    dodge_sweep2 = bpf(resample_pitch(swish7, 1.0), 500.0, 2600.0)
    dodge_mix = mix_layers(0.36, [
        (0, dodge_sweep1, 0.95, -0.45),
        (55, dodge_sweep2, 0.80, 0.45),
    ])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_dodge.mp3"), fade_io(arena_reverb(dodge_mix, wet=0.09, tail_s=0.14), 2.0, 30.0))
    produced.append("sfx_pit_dodge.mp3")

    # 9. 공격 빗나감 F12: 아주 짧고 가벼운 고역 허공 헛스윙 ("휙!")
    miss_whiff = hpf(norm_peak(add_aligned((slice_ms(resample_pitch(swish12, 3.0), 0, 130), 0.9), (slice_ms(resample_pitch(swish13, 4.0), 0, 120), 0.7))), 1500.0)
    miss_mix = mix_layers(0.19, [(0, miss_whiff, 1.0, 0.25)])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_miss.mp3"), fade_io(arena_reverb(miss_mix, wet=0.07, tail_s=0.10), 1.0, 20.0))
    produced.append("sfx_pit_miss.mp3")

    # ------------------------------------------------------------------
    # [C] 스페셜 공방 F33 / F34 & 그로기 6종
    # ------------------------------------------------------------------
    # 10. [F33-①] 머리 잡아 고정 체결: 타격음 0%, 부리 클램프 물림("콱!") + 깃털 버둥거림("푸드덕")
    clamp_bite = norm_peak(add_aligned(
        (hpf(slice_ms(switch1, 0, 75), 600.0), 0.95),
        (bpf(slice_ms(crack5, 0, 60), 900.0, 4000.0), 0.70),
    ))
    struggle = norm_peak(add_aligned(
        (bpf(slice_ms(paper1, 0, 220), 600.0, 3600.0), 0.85),
        (bpf(slice_ms(resample_pitch(flap_1, 7.0), 0, 200), 500.0, 3000.0), 0.65),
    ))
    pin_mix = mix_layers(0.38, [
        (0, clamp_bite, 1.05, 0.0),
        (60, struggle, 0.85, -0.25),
        (90, slice_ms(resample_pitch(cluck1, 2.5), 0, 110), 0.14, 0.25),
    ])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_grab_pin.mp3"), fade_io(arena_reverb(pin_mix, wet=0.10, tail_s=0.18), 1.0, 35.0))
    produced.append("sfx_pit_grab_pin.mp3")

    # 11. [F33-②] 머리 잡아 바닥 쳐박기 본타격: 뚜렷한 하강(0~185ms) -> 지면 붕괴(185ms) -> 크랙 + 모래·자갈 산란
    drag_down = bpf(resample_pitch(swish9, -5.0), 220.0, 1900.0)
    slam_earth = norm_peak(add_aligned(
        (peaking_eq(hpf(slice_ms(towel3, 0, 340), 95.0), 260, 1.0, 4.5), 0.95),
        (peaking_eq(hpf(slice_ms(jump1, 0, 360), 95.0), 320, 1.0, 4.0), 0.95),
        (bpf(slice_ms(crack1, 0, 260), 800.0, 5200.0), 0.55),
    ))
    gravel_scatter = norm_peak(add_aligned(
        (slice_ms(dishes_gravel, 0, 440), 0.75),
        (bpf(slice_ms(sand1, 0, 520), 750.0, 6200.0), 0.92),
    ))
    slam_mix = mix_layers(1.05, [
        (0, slice_ms(drag_down, 0, 195), 0.85, -0.25),
        (185, slam_earth, 1.18, 0.0),
        (185, slice_ms(phonk, 0, 280), 0.36, 0.0),
        (185, synth_sub_punch(0.36, 130, 42, 0.11), 0.44, 0.0),
        (210, gravel_scatter, 0.92, 0.28),
        (360, bpf(slice_ms(sand2, 0, 440), 600.0, 4800.0), 0.58, -0.28),
    ])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_slam.mp3"), fade_io(arena_reverb(warm_saturate(slam_mix, 1.45), wet=0.22, tail_s=0.45), 2.0, 90.0))
    produced.append("sfx_pit_slam.mp3")

    # 12. [F33-③] 잡기 실패 / 헛잡기: 딱! 헛물기 + 짧은 바람
    grab_miss_mix = mix_layers(0.24, [
        (0, hpf(slice_ms(switch1, 0, 65), 1100.0), 0.85, 0.0),
        (20, slice_ms(resample_pitch(swish12, 2.0), 0, 130), 0.72, 0.25),
    ])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_grab_miss.mp3"), fade_io(arena_reverb(grab_miss_mix, wet=0.08, tail_s=0.12), 1.0, 25.0))
    produced.append("sfx_pit_grab_miss.mp3")

    # 13. [F34-①] 잡힌 머리 풀기 회전 탈출: 탄성 깃 파열("파닥!") -> 밝고 빠른 상승 회전("휘익!")
    shake_off = norm_peak(add_aligned(
        (hpf(slice_ms(resample_pitch(flap_2, 9.0), 0, 140), 550.0), 0.90),
        (bpf(slice_ms(paper3, 0, 160), 900.0, 5000.0), 0.78),
    ))
    spin_up = bpf(resample_pitch(swish4, 5.0), 900.0, 4800.0)
    esc_mix = mix_layers(0.38, [
        (0, shake_off, 1.00, -0.25),
        (95, spin_up, 0.95, 0.45),
    ])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_grab_escape.mp3"), fade_io(arena_reverb(esc_mix, wet=0.12, tail_s=0.18), 1.0, 35.0))
    produced.append("sfx_pit_grab_escape.mp3")

    # 14. [F34-②] 머리 풀고 역습 반격 1.8x: 맑은 황금 차임(0ms 단독 85ms) -> 양발 쌍발 가슴 킥 2연타(90ms/175ms "탕-탁!")
    counter_chime = norm_peak(add_aligned(
        (hpf(slice_ms(bell2, 0, 320), 1400.0), 0.78),
        (hpf(slice_ms(ding1, 0, 300), 1800.0), 0.72),
    ))
    kick_1 = norm_peak(add_aligned((slice_ms(thwack_heavy, 0, 150), 0.95), (slice_ms(hit12, 0, 160), 0.75)))
    kick_2 = resample_pitch(kick_1, 3.0)
    brk_mix = mix_layers(0.66, [
        (0, counter_chime, 0.90, 0.0),
        (90, kick_1, 1.05, -0.18),
        (175, kick_2, 1.10, 0.18),
        (240, slice_ms(sand1, 0, 240), 0.35, 0.25),
    ])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_break.mp3"), fade_io(arena_reverb(warm_saturate(brk_mix, 1.3), wet=0.16, tail_s=0.28), 1.0, 50.0))
    produced.append("sfx_pit_break.mp3")

    # 15. 스탠딩 그로기 F30: 유지/미세 다듬기
    n_grog = int(1.45 * SAMPLE_RATE)
    t_g = np.arange(n_grog, dtype=np.float32) / SAMPLE_RATE
    ring_tone = np.sin(2.0 * np.pi * 2450.0 * t_g) * 0.07 * np.exp(-t_g / 0.85)
    wobble = (0.55 + 0.45 * np.sin(2.0 * np.pi * 3.8 * t_g)) * np.sin(2.0 * np.pi * 68.0 * t_g) * np.exp(-t_g / 0.75) * 0.40
    stumble_steps = mix_layers(1.45, [
        (40, slice_ms(sand1, 0, 180), 0.45, -0.25),
        (380, slice_ms(sand2, 0, 180), 0.50, 0.25),
        (760, slice_ms(sand1, 0, 180), 0.38, -0.15),
    ])
    grog_mix = stumble_steps + make_stereo_wide((ring_tone + wobble).astype(np.float32), 0.0)
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_groggy.mp3"), fade_io(arena_reverb(grog_mix, wet=0.18, tail_s=0.28), 15.0, 180.0))
    produced.append("sfx_pit_groggy.mp3")

    # ------------------------------------------------------------------
    # [D] 특수 상태 · 다운 · 벽 충돌 · 슬로우 4종
    # ------------------------------------------------------------------
    # 16. 바닥 다운 충격: 묵직한 전신 낙하("털썩") + 느린 흙 쓸림("스윽") - 서브 과다 억제
    kd_mix = mix_layers(0.74, [
        (0, hpf(slice_ms(towel10, 0, 320), 90.0), 0.95, 0.0),
        (8, hpf(slice_ms(jump3, 0, 340), 90.0), 0.90, -0.12),
        (0, synth_sub_punch(0.24, 110, 44, 0.08), 0.38, 0.0),
        (110, resample_pitch(slice_ms(sand2, 0, 380), -3.0), 0.68, 0.25),
    ])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_knockdown.mp3"), fade_io(arena_reverb(warm_saturate(kd_mix, 1.3), wet=0.20, tail_s=0.34), 2.0, 75.0))
    produced.append("sfx_pit_knockdown.mp3")

    # 17. 투지 버티기 1 HP 생존
    hb_raw = load_audio(os.path.join(CACHE_DIR, "heartbeat_speedsup.wav"), 1)
    hb_seg = norm_peak(lpf(slice_ms(hb_raw, 0, 2450), 600.0))
    t_ls = np.arange(len(hb_seg), dtype=np.float32) / SAMPLE_RATE
    riser = np.sin(2.0 * np.pi * (55.0 + 35.0 * (t_ls / 2.45)) * t_ls) * (t_ls / 2.45) ** 1.8 * 0.28
    ls_mix = make_stereo_wide(hb_seg * 0.95 + riser, 0.0, width_ms=4.0)
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_last_stand.mp3"), fade_io(arena_reverb(warm_saturate(ls_mix, 1.3), wet=0.16, tail_s=0.25), 15.0, 200.0))
    produced.append("sfx_pit_last_stand.mp3")

    # 18. 원형 외벽 격돌 F31: 속 빈 목재 판자("덩-!") + 철망 펜스 흔들림("철컹—") - 육체 펀치·서브 제거
    wood_panel = peaking_eq(bpf(slice_ms(wall_wood, 0, 340), 150.0, 1200.0), 280, 1.1, 6.0)
    wood_thump = bpf(slice_ms(wood3, 0, 220), 160.0, 950.0)
    fence_rattle = norm_peak(add_aligned(
        (hpf(slice_ms(metal6, 0, 380), 900.0), 0.90),
        (hpf(slice_ms(metal11, 0, 420), 1200.0), 0.72),
    ))
    wall_mix = mix_layers(0.62, [
        (0, wood_panel, 1.00, -0.10),
        (0, wood_thump, 0.85, 0.10),
        (35, fence_rattle, 0.78, 0.28),
    ])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_wall_impact.mp3"), fade_io(arena_reverb(wall_mix, wet=0.22, tail_s=0.35), 1.0, 70.0))
    produced.append("sfx_pit_wall_impact.mp3")

    # 19. 브루탈 KO 슬로우 전환 F33-A
    n_sl = int(1.15 * SAMPLE_RATE)
    t_sl = np.arange(n_sl, dtype=np.float32) / SAMPLE_RATE
    f_sl = 145.0 * np.exp(-t_sl / 0.45) + 34.0
    ph_sl = 2.0 * np.pi * np.cumsum(f_sl) / SAMPLE_RATE
    sub_sweep = (np.sin(ph_sl) + 0.25 * np.sin(ph_sl * 2.0) * np.exp(-t_sl / 0.2)) * np.exp(-t_sl / 0.55) * (1.0 - np.exp(-t_sl / 0.01))
    air_whoosh = synth_noise_burst(0.85, 220, 1400, attack_s=0.02, decay_tau=0.28) * 0.35
    sl_mix = mix_layers(1.15, [(0, sub_sweep, 0.95, 0.0), (0, air_whoosh, 0.55, 0.0)])
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_ko_slow.mp3"), fade_io(arena_reverb(warm_saturate(sl_mix, 1.35), wet=0.22, tail_s=0.38), 5.0, 180.0))
    produced.append("sfx_pit_ko_slow.mp3")

    # ------------------------------------------------------------------
    # [E] 시스템 · 벨 · 관중 2종(탄성 완전 교체) · 보이스 · 포효
    # ------------------------------------------------------------------
    bell_raw = load_audio(os.path.join(CACHE_DIR, "dingdingding.wav"), 1)
    bell_one = trim_onset(bell_raw[int(0.92 * SAMPLE_RATE) :], thresh_ratio=0.08, pre_ms=2.0)
    bell_rich = peaking_eq(peaking_eq(bell_one, 650, 1.2, 4.5), 2400, 1.2, 2.0)
    bell_out = arena_reverb(make_stereo_wide(bell_rich, 0.0, width_ms=6.0), wet=0.24, tail_s=0.65)
    if len(bell_out) > int(2.35 * SAMPLE_RATE):
        bell_out = bell_out[: int(2.35 * SAMPLE_RATE)]
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_bell_single.mp3"), fade_io(bell_out, 1.0, 250.0))
    produced.append("sfx_pit_bell_single.mp3")

    ko_bell_trim = trim_onset(bell_raw, thresh_ratio=0.06, pre_ms=3.0)
    ko_bell_rich = peaking_eq(peaking_eq(ko_bell_trim, 650, 1.2, 4.5), 2400, 1.2, 2.5)
    ko_bell_out = arena_reverb(make_stereo_wide(ko_bell_rich, 0.0, width_ms=6.0), wet=0.25, tail_s=0.60)
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_ko_bell.mp3"), fade_io(ko_bell_out, 1.0, 200.0))
    produced.append("sfx_pit_ko_bell.mp3")

    cheer = load_audio(os.path.join(CACHE_DIR, "real_crowd_cheer.ogg"), 2)
    shout = load_audio(os.path.join(CC0_DIR, "crowd_shouting.ogg"), 1)
    cheer_seg = cheer[int(4.0 * SAMPLE_RATE) : int(7.8 * SAMPLE_RATE)].copy()
    shout_seg = make_stereo_wide(norm_peak(shout[int(1.0 * SAMPLE_RATE) : int(4.8 * SAMPLE_RATE)]), 0.0, width_ms=9.0)
    roar_mix = norm_peak(cheer_seg) * 0.80 + shout_seg * 0.35
    roar_eq = peaking_eq(hpf(roar_mix, 110.0), 2200, 0.9, 3.0)
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_crowd_roar.mp3"), fade_io(roar_eq, 220.0, 650.0))
    produced.append("sfx_pit_crowd_roar.mp3")

    # 23. [전면 교체] 관중 탄성 · 경악 서지 CROWD_GASP (1.35s): 실사 경기장 급등 서지 + 다중 관객 짧은 "Whoa/Oh"
    # real_crowd_cheer.ogg t=37.45~38.80 (rms 0.064 -> 0.131 급상승) + t=8.70~10.05 (rms 0.155 -> 0.244 급등)
    L_sg = int(1.35 * SAMPLE_RATE)
    s_a = int(37.40 * SAMPLE_RATE)
    s_b = int(8.70 * SAMPLE_RATE)
    surge_a = cheer[s_a : s_a + L_sg].copy()
    surge_b = cheer[s_b : s_b + L_sg].copy()
    t_sg = np.arange(L_sg, dtype=np.float32) / SAMPLE_RATE
    surge_env = np.minimum(1.0, t_sg / 0.11) * np.exp(-np.maximum(0.0, t_sg - 0.55) / 0.42)
    real_surge = (norm_peak(hpf(surge_a, 140.0)) * 0.65 + norm_peak(hpf(surge_b, 160.0)) * 0.55) * surge_env[:, None]

    async def gen_crowd_react_and_voices():
        # 다중 관중 짧은 리액션 (피치/유령 변조 없이 자연스러운 스포츠 관객)
        reactors = [
            ("cr_1.mp3", "Whoa!", "en-US-GuyNeural", "+30%", "+2Hz", 15, -0.45, 0.26),
            ("cr_2.mp3", "Oh!", "en-US-AriaNeural", "+35%", "+4Hz", 35, 0.42, 0.24),
            ("cr_3.mp3", "Whoa!", "en-US-ChristopherNeural", "+28%", "+0Hz", 55, -0.25, 0.25),
            ("cr_4.mp3", "Oh!", "en-US-JennyNeural", "+34%", "+2Hz", 80, 0.28, 0.22),
            ("cr_5.mp3", "Hey!", "en-US-EricNeural", "+32%", "+1Hz", 110, 0.0, 0.20),
        ]
        react_events = []
        for fn, txt, v, rt, pt, off_ms, pan, g in reactors:
            rp = os.path.join(VOICE_RAW_DIR, fn)
            if not os.path.exists(rp):
                await edge_tts.Communicate(txt, v, rate=rt, pitch=pt).save(rp)
            vc = trim_tail(trim_onset(load_audio(rp, 1), 0.05, 8.0), 0.03, 25.0)
            # 대역 제한(380~2600Hz)으로 경기장 관중 군중 속 원거리 질감으로 자연 융합
            vc_room = bpf(norm_peak(vc), 380.0, 2600.0)
            react_events.append((off_ms, vc_room, g, pan))

        react_bed = mix_layers(1.35, react_events)
        react_bed = arena_reverb(react_bed, wet=0.28, tail_s=0.35, pre_delay_ms=18.0)[: len(real_surge)]
        gasp_final = real_surge.copy()
        gasp_final[: len(react_bed)] += react_bed * 0.45
        gasp_final = peaking_eq(hpf(gasp_final, 140.0), 1600, 0.9, 2.5)
        save_mp3(os.path.join(SFX_DIR, "sfx_pit_crowd_gasp.mp3"), fade_io(gasp_final, 25.0, 280.0))

        # 25. 라운드 시작 보이스 3종
        scripts = [
            ("sfx_pit_round1_start.mp3", "First Round!", "FIGHT!"),
            ("sfx_pit_round2_start.mp3", "Second Round!", "FIGHT!"),
            ("sfx_pit_round3_start.mp3", "Third and Final Round!", "FIGHT!"),
        ]
        for idx, (out_name, lead_txt, fight_txt) in enumerate(scripts, 1):
            p_lead = os.path.join(VOICE_RAW_DIR, f"lead_{idx}.mp3")
            p_fight = os.path.join(VOICE_RAW_DIR, f"fight_{idx}.mp3")
            if not os.path.exists(p_lead):
                await edge_tts.Communicate(lead_txt, "en-US-ChristopherNeural", rate="+6%", pitch="+1Hz").save(p_lead)
            if not os.path.exists(p_fight):
                await edge_tts.Communicate(fight_txt, "en-US-GuyNeural", rate="+22%", pitch="+5Hz").save(p_fight)
            v_lead = trim_tail(trim_onset(load_audio(p_lead, 1), 0.04, 15.0), 0.02, 40.0)
            v_fight = trim_tail(trim_onset(load_audio(p_fight, 1), 0.05, 10.0), 0.02, 60.0)
            v_lead_p = norm_peak(warm_saturate(peaking_eq(hpf(v_lead, 130.0), 2800, 1.1, 4.5), 1.35), 0.84)
            v_fight_p = norm_peak(warm_saturate(peaking_eq(peaking_eq(hpf(v_fight, 140.0), 3200, 1.0, 6.0), 220, 1.0, 3.0), 1.65), 1.05)
            gap = np.zeros(int(0.18 * SAMPLE_RATE), dtype=np.float32)
            combined = np.concatenate([v_lead_p, gap, v_fight_p])
            pa_out = arena_reverb(make_stereo_wide(combined, 0.0, width_ms=4.0), wet=0.22, tail_s=0.45, pre_delay_ms=22.0)
            save_mp3(os.path.join(SFX_DIR, out_name), fade_io(pa_out, 3.0, 120.0))

    asyncio.run(gen_crowd_react_and_voices())
    produced.extend(["sfx_pit_crowd_gasp.mp3", "sfx_pit_round1_start.mp3", "sfx_pit_round2_start.mp3", "sfx_pit_round3_start.mp3"])

    # 24. 승리 수탉 챔피언 포효
    rooster_raw = trim_onset(load_audio(os.path.join(CACHE_DIR, "real_rooster_crowing.ogg"), 1), 0.05)
    rooster_one = fade_io(slice_ms(rooster_raw, 0, 1320), 3.0, 120.0)
    rooster_eq = peaking_eq(hpf(rooster_one, 180.0), 2600, 1.1, 4.5)
    rooster_out = arena_reverb(make_stereo_wide(norm_peak(rooster_eq), 0.0, width_ms=5.0), wet=0.24, tail_s=0.45)
    save_mp3(os.path.join(SFX_DIR, "sfx_pit_rooster_crow.mp3"), fade_io(rooster_out, 5.0, 180.0))
    produced.append("sfx_pit_rooster_crow.mp3")

    print(f"  [완료] v2.1 총 {len(produced)}개 파일 생성 완료 -> {SFX_DIR}")
    return produced


def build_bgm_carved():
    print("=== [2/3] 전투 BGM EQ 카빙 마스터링 ===")
    v1_bgm_path = os.path.join(BACKUP_DIR, "bgm_pit_fight_v1.mp3")
    src = load_audio(v1_bgm_path, nchannels=2)
    carved = hpf(src, 35.0, order=2)
    carved = peaking_eq(carved, 2600.0, 0.85, -3.2)
    carved = peaking_eq(carved, 110.0, 1.0, -1.0)
    out_path = os.path.join(BGM_DIR, "bgm_pit_fight.mp3")
    save_mp3(out_path, carved, target_peak=0.891)
    print(f"  [완료] EQ 카빙 BGM 저장 -> {out_path}")


def build_round1_demo():
    print("=== [3/3] 1R 실전 시뮬레이션 데모 (38.0초, v2.1 차별화 음원) 재합성 ===")
    TOTAL_S = 38.0
    N = int(TOTAL_S * SAMPLE_RATE)

    bgm_raw = load_audio(os.path.join(BGM_DIR, "bgm_pit_fight.mp3"), 2)
    bgm_layer = bgm_raw[:N].copy()
    fi = int(1.6 * SAMPLE_RATE)
    bgm_layer[:fi] *= np.linspace(0.0, 1.0, fi)[:, None]

    crowd_raw = load_audio(os.path.join(CACHE_DIR, "real_crowd_cheer.ogg"), 2)
    crowd_bed = norm_peak(hpf(crowd_raw[:N].copy(), 150.0), 0.14)

    sfx_layer = np.zeros((N, 2), dtype=np.float32)
    voice_layer = np.zeros((N, 2), dtype=np.float32)
    duck_gain = np.ones(N, dtype=np.float32)

    def apply_duck(start_s: float, hold_s: float, depth_db: float, atk_ms: float = 8.0, rel_ms: float = 240.0):
        s = int(start_s * SAMPLE_RATE)
        atk_n = max(1, int(atk_ms * SAMPLE_RATE / 1000.0))
        hold_n = max(1, int(hold_s * SAMPLE_RATE))
        rel_n = max(1, int(rel_ms * SAMPLE_RATE / 1000.0))
        target_g = 10.0 ** (depth_db / 20.0)
        env = np.ones(atk_n + hold_n + rel_n, dtype=np.float32)
        env[:atk_n] = np.linspace(1.0, target_g, atk_n)
        env[atk_n : atk_n + hold_n] = target_g
        env[atk_n + hold_n :] = np.linspace(target_g, 1.0, rel_n)
        e = min(N, s + len(env))
        if s < N:
            duck_gain[s:e] = np.minimum(duck_gain[s:e], env[: e - s])

    def add_sfx(t_s: float, fname: str, gain: float = 1.0, pan: float = 0.0, duck_db: float = 0.0, duck_hold: float = 0.25, is_voice: bool = False):
        p = os.path.join(SFX_DIR, fname)
        clip = load_audio(p, 2)
        if abs(pan) > 0.02:
            clip = make_stereo_wide(clip.mean(axis=1), pan=pan)
        idx = int(t_s * SAMPLE_RATE)
        if idx >= N:
            return
        take = min(len(clip), N - idx)
        if is_voice:
            voice_layer[idx : idx + take] += clip[:take] * gain
        else:
            sfx_layer[idx : idx + take] += clip[:take] * gain
        if duck_db < -0.5:
            apply_duck(t_s, duck_hold, duck_db)

    add_sfx(0.60, "sfx_pit_bell_single.mp3", gain=0.88, duck_db=-4.5, duck_hold=0.6)
    add_sfx(1.30, "sfx_pit_round1_start.mp3", gain=1.05, duck_db=-7.5, duck_hold=1.7, is_voice=True)

    # 일반 공방 & 방어/패링 대비
    add_sfx(4.50, "sfx_pit_hit_poke.mp3", gain=0.98, pan=-0.28, duck_db=-3.5, duck_hold=0.24)
    add_sfx(5.15, "sfx_pit_guard.mp3", gain=1.02, pan=0.28, duck_db=-3.5, duck_hold=0.22)
    add_sfx(6.60, "sfx_pit_hit_wing.mp3", gain=1.00, pan=0.25, duck_db=-4.2, duck_hold=0.38)
    add_sfx(7.55, "sfx_pit_guard_gen.mp3", gain=0.98, pan=-0.25, duck_db=-4.5, duck_hold=0.28)
    add_sfx(8.15, "sfx_pit_dodge.mp3", gain=0.95, pan=-0.35, duck_db=-2.5, duck_hold=0.20)
    add_sfx(8.65, "sfx_pit_hit_spur.mp3", gain=1.02, pan=-0.20, duck_db=-4.5, duck_hold=0.30)
    add_sfx(9.75, "sfx_pit_miss.mp3", gain=0.92, pan=0.30)
    add_sfx(10.30, "sfx_pit_hit_gen.mp3", gain=0.98, pan=-0.20, duck_db=-3.8, duck_hold=0.25)

    # 스페셜 공방 1: [특방 F34] 잡기 체결 -> 0.30s 회전 탈출 -> 0.40s 쌍발 카운터 -> 외벽 철망
    add_sfx(12.40, "sfx_pit_grab_pin.mp3", gain=1.00, pan=0.15, duck_db=-4.5, duck_hold=0.25)
    add_sfx(12.75, "sfx_pit_grab_escape.mp3", gain=0.98, pan=-0.15, duck_db=-4.5, duck_hold=0.25)
    add_sfx(13.15, "sfx_pit_break.mp3", gain=1.08, pan=0.0, duck_db=-7.0, duck_hold=0.48)
    add_sfx(13.65, "sfx_pit_wall_impact.mp3", gain=0.98, pan=0.38, duck_db=-5.0, duck_hold=0.32)
    add_sfx(13.75, "sfx_pit_crowd_gasp.mp3", gain=0.78)

    # 치명타 & 그로기 & 투지
    add_sfx(17.20, "sfx_pit_hit_gen.mp3", gain=0.95, pan=0.25, duck_db=-3.5, duck_hold=0.22)
    add_sfx(18.00, "sfx_pit_hit_crit.mp3", gain=1.08, pan=-0.10, duck_db=-7.5, duck_hold=0.50)
    add_sfx(18.60, "sfx_pit_groggy.mp3", gain=0.88, pan=0.20, duck_db=-4.5, duck_hold=0.90)
    add_sfx(20.60, "sfx_pit_last_stand.mp3", gain=0.95, pan=0.0, duck_db=-6.5, duck_hold=1.80)
    add_sfx(23.50, "sfx_pit_hit_spur.mp3", gain=0.98, pan=-0.25, duck_db=-4.2, duck_hold=0.28)
    add_sfx(24.30, "sfx_pit_guard.mp3", gain=0.98, pan=0.25, duck_db=-3.5, duck_hold=0.22)

    # 스페셜 공방 2: [특공 F33] 머리 잡아 바닥 찍기 -> 슬로우 -> KO 3연타 벨 + 포효
    add_sfx(26.80, "sfx_pit_grab_pin.mp3", gain=1.02, pan=-0.15, duck_db=-5.0, duck_hold=0.35)
    add_sfx(27.28, "sfx_pit_slam.mp3", gain=1.12, pan=0.0, duck_db=-9.5, duck_hold=0.85)
    add_sfx(27.55, "sfx_pit_crowd_gasp.mp3", gain=0.85)
    add_sfx(28.15, "sfx_pit_ko_slow.mp3", gain=0.95, duck_db=-10.0, duck_hold=1.10)
    add_sfx(29.05, "sfx_pit_knockdown.mp3", gain=0.98, duck_db=-12.0, duck_hold=1.20)
    add_sfx(29.65, "sfx_pit_ko_bell.mp3", gain=1.00, duck_db=-18.0, duck_hold=6.00)
    add_sfx(30.40, "sfx_pit_crowd_roar.mp3", gain=0.92)
    add_sfx(32.00, "sfx_pit_rooster_crow.mp3", gain=0.96, duck_db=-18.0, duck_hold=5.00)

    fade_s = int(29.65 * SAMPLE_RATE)
    fade_e = int(32.50 * SAMPLE_RATE)
    duck_gain[fade_s:fade_e] *= np.linspace(1.0, 0.0, fade_e - fade_s)
    duck_gain[fade_e:] = 0.0

    bgm_ducked = bgm_layer * 0.48 * duck_gain[:, None]
    master_mix = bgm_ducked + crowd_bed + sfx_layer * 1.05 + voice_layer * 1.05
    fo = int(1.4 * SAMPLE_RATE)
    master_mix[-fo:] *= np.linspace(1.0, 0.0, fo)[:, None]

    out_path = os.path.join(DEMO_DIR, "demo_pit_round1_simulation.mp3")
    save_mp3(out_path, master_mix, target_peak=TARGET_PEAK)
    print(f"  [완료] 1R 시뮬레이션 데모 저장 -> {out_path}")


if __name__ == "__main__":
    build_all_sfx()
    build_bgm_carved()
    build_round1_demo()
    print("=== [v2.1 전체 제작 파이프라인 완료] ===")
