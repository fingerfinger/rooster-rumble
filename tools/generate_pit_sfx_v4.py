#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROOSTER RUMBLE: Rumble Pit v4.0 스튜디오 무손실 실사 Foley 제작 파이프라인
- Mixkit Commercial-Free Studio WAV + Archive.org USC Hollywood Red Library CC0 1.0 FLAC
- 보호 자산 5개(ko_bell, round1~3_start, bgm_pit_fight) 및 v1_backup 절대 비수정
- AI 생성 SFX(TangoFlux/AudioGen) 0% · 금속성/비프/닭울음 0%
- 승자 PA 보이스 2종(KO 승 / 판정 승): 링 PA + 프로젝트 내 하이텐션 ElevenLabs (순수 보이스 전용)
- v4.0.4: SFX_PIT_BELL_SINGLE v1.2 풀버전 기반 펀치/브라이트니스 리마스터링 (`--only bell_single`)
"""

import argparse
import asyncio
import os
import edge_tts
import lameenc
import miniaudio
import numpy as np
from scipy import signal

SAMPLE_RATE = 44100
BITRATE = 192
DEFAULT_TARGET_PEAK = 0.87

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIT_AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio", "pit")
SFX_DIR = os.path.join(PIT_AUDIO_DIR, "sfx")
BGM_DIR = os.path.join(PIT_AUDIO_DIR, "bgm")
DEMO_DIR = os.path.join(PIT_AUDIO_DIR, "demo")
DOCS_SFX_DIR = os.path.join(BASE_DIR, "docs", "assets", "audio", "pit", "sfx")

STUDIO_DIR = os.path.join(BASE_DIR, "tools", "source_cache", "pit_studio_v4")
VOICE_CACHE_DIR = os.path.join(STUDIO_DIR, "_voice_tests", "v4_win")

os.makedirs(SFX_DIR, exist_ok=True)
os.makedirs(DEMO_DIR, exist_ok=True)
os.makedirs(VOICE_CACHE_DIR, exist_ok=True)

# 절대 덮어쓰기 금지 보호 파일 목록
PROTECTED_FILES = {
    "sfx_pit_ko_bell.mp3",
    "sfx_pit_round1_start.mp3",
    "sfx_pit_round2_start.mp3",
    "sfx_pit_round3_start.mp3",
}


# ---------------------------------------------------------------------------
# 오디오 I/O & 비파괴 DSP 유틸리티 (Windows 한글 경로 안전)
# ---------------------------------------------------------------------------
def load_audio(path: str, nchannels: int = 2) -> np.ndarray:
    """UTF-8 경로/잠금 회피용 바이트 읽기 + miniaudio FLOAT32 44.1kHz 디코딩."""
    with open(path, "rb") as f:
        raw = f.read()
    dec = miniaudio.decode(
        raw,
        output_format=miniaudio.SampleFormat.FLOAT32,
        nchannels=nchannels,
        sample_rate=SAMPLE_RATE,
    )
    arr = np.frombuffer(dec.samples, dtype=np.float32).copy()
    if nchannels > 1:
        arr = arr.reshape(-1, nchannels)
    return arr


def save_mp3(out_path: str, audio: np.ndarray, target_peak: float = DEFAULT_TARGET_PEAK) -> tuple[float, float]:
    """스테레오 44.1kHz 192kbps MP3 인코딩 및 -0.2 dBFS 이하 클린 피크 보장."""
    fname = os.path.basename(out_path)
    if fname in PROTECTED_FILES or fname == "bgm_pit_fight.mp3":
        raise RuntimeError(f"Protected asset write blocked: {fname}")

    x = np.asarray(audio, dtype=np.float32)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)

    # DC / 30Hz 이하 초저역 정리
    sos_dc = signal.butter(2, 30.0, btype="highpass", fs=SAMPLE_RATE, output="sos")
    x = signal.sosfilt(sos_dc, x, axis=0)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)

    mx = float(np.max(np.abs(x)))
    if mx > 1e-8:
        x = x * (target_peak / mx)

    # 과도 파형 오버슈트 방지 소프트 클리퍼
    x = np.tanh(x * 1.03) / np.tanh(1.03)
    mx2 = float(np.max(np.abs(x)))
    if mx2 > target_peak:
        x = x * (target_peak / mx2)

    pcm = (np.clip(x, -1.0, 1.0) * 32767.0).astype(np.int16).tobytes()
    enc = lameenc.Encoder()
    enc.set_bit_rate(BITRATE)
    enc.set_in_sample_rate(SAMPLE_RATE)
    enc.set_channels(2)
    enc.set_quality(2)
    mp3_bytes = enc.encode(pcm) + enc.flush()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(mp3_bytes)

    return len(x) / SAMPLE_RATE, len(mp3_bytes) / 1024.0


def butter_filter(x: np.ndarray, kind: str, cutoff, order: int = 3) -> np.ndarray:
    sos = signal.butter(order, cutoff, btype=kind, fs=SAMPLE_RATE, output="sos")
    return signal.sosfilt(sos, x, axis=0).astype(np.float32)


def peaking_eq(x: np.ndarray, fc: float, q: float, gain_db: float) -> np.ndarray:
    w0 = 2.0 * np.pi * fc / SAMPLE_RATE
    amp = 10.0 ** (gain_db / 40.0)
    alpha = np.sin(w0) / (2.0 * q)
    b0 = 1.0 + alpha * amp
    b1 = -2.0 * np.cos(w0)
    b2 = 1.0 - alpha * amp
    a0 = 1.0 + alpha / amp
    a1 = -2.0 * np.cos(w0)
    a2 = 1.0 - alpha / amp
    sos = np.array([[b0 / a0, b1 / a0, b2 / a0, 1.0, a1 / a0, a2 / a0]], dtype=np.float64)
    return signal.sosfilt(sos, x, axis=0).astype(np.float32)


def norm_peak(x: np.ndarray, peak: float = 0.90) -> np.ndarray:
    mx = float(np.max(np.abs(x)))
    if mx > 1e-8:
        return (x * (peak / mx)).astype(np.float32)
    return x.astype(np.float32)


def fade_io(x: np.ndarray, fade_in_ms: float = 2.0, fade_out_ms: float = 40.0) -> np.ndarray:
    out = x.copy()
    n_in = min(len(out), int(fade_in_ms * SAMPLE_RATE / 1000.0))
    n_out = min(len(out), int(fade_out_ms * SAMPLE_RATE / 1000.0))
    if n_in > 1:
        ramp = np.linspace(0.0, 1.0, n_in, dtype=np.float32)
        out[:n_in] *= ramp[:, None] if out.ndim == 2 else ramp
    if n_out > 1:
        ramp = np.linspace(1.0, 0.0, n_out, dtype=np.float32)
        out[-n_out:] *= ramp[:, None] if out.ndim == 2 else ramp
    return out


def pan_stereo(x: np.ndarray, pan: float = 0.0) -> np.ndarray:
    """모노 또는 스테레오 입력을 [-1, +1] 정위감 스테레오로 배치."""
    pan = float(np.clip(pan, -1.0, 1.0))
    theta = (pan + 1.0) * (np.pi / 4.0)
    gl, gr = np.cos(theta), np.sin(theta)
    if x.ndim == 1:
        return np.stack([x * gl, x * gr], axis=1).astype(np.float32)
    if abs(pan) < 0.02:
        return x.astype(np.float32)
    mono = np.mean(x, axis=1)
    return np.stack([mono * gl, mono * gr], axis=1).astype(np.float32)


def arena_reverb(x: np.ndarray, wet: float = 0.06, tail_s: float = 0.22, pre_delay_ms: float = 12.0) -> np.ndarray:
    """원형 투계장 반사음(Early Reflections + 감쇄 디퓨즈 테일) 부가."""
    if wet <= 0.0:
        return x.astype(np.float32)
    st = pan_stereo(x, 0.0)
    rng = np.random.default_rng(4040)
    n_tail = int(tail_s * SAMPLE_RATE)
    ir = np.zeros((n_tail, 2), dtype=np.float32)

    pre_n = int(pre_delay_ms * SAMPLE_RATE / 1000.0)
    taps_ms = [pre_delay_ms, pre_delay_ms + 9.0, pre_delay_ms + 21.0, pre_delay_ms + 36.0]
    for k, ms in enumerate(taps_ms):
        idx = min(n_tail - 1, int(ms * SAMPLE_RATE / 1000.0))
        amp = 0.26 * (0.72 ** k)
        ir[idx, k % 2] += amp
        ir[min(n_tail - 1, idx + 11), (k + 1) % 2] += amp * 0.7

    t = np.arange(max(0, n_tail - pre_n), dtype=np.float32) / SAMPLE_RATE
    if len(t) > 0:
        decay = np.exp(-t / max(0.06, tail_s * 0.34))
        tail_noise = rng.standard_normal((len(t), 2)).astype(np.float32) * decay[:, None] * 0.045
        tail_noise = butter_filter(tail_noise, "lowpass", 3600.0, order=2)
        ir[pre_n:] += tail_noise

    wet_sig = np.stack(
        [
            signal.fftconvolve(st[:, 0], ir[:, 0], mode="full")[: len(st) + int(0.14 * SAMPLE_RATE)],
            signal.fftconvolve(st[:, 1], ir[:, 1], mode="full")[: len(st) + int(0.14 * SAMPLE_RATE)],
        ],
        axis=1,
    ).astype(np.float32)

    out = np.zeros_like(wet_sig)
    out[: len(st)] += st
    out += wet_sig * wet
    return out


def trim_tail(x: np.ndarray, thresh_ratio: float = 0.012, pad_ms: float = 35.0) -> np.ndarray:
    amp = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    mx = float(np.max(amp))
    if mx <= 1e-8:
        return x
    idx = np.where(amp > mx * thresh_ratio)[0]
    if len(idx) == 0:
        return x
    end_idx = min(len(x), int(idx[-1]) + int(pad_ms * SAMPLE_RATE / 1000.0))
    return x[:end_idx]


def trim_onset(x: np.ndarray, thresh_ratio: float = 0.02, pre_ms: float = 8.0) -> np.ndarray:
    amp = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    mx = float(np.max(amp))
    if mx <= 1e-8:
        return x
    idx = np.where(amp > mx * thresh_ratio)[0]
    if len(idx) == 0:
        return x
    start_idx = max(0, int(idx[0]) - int(pre_ms * SAMPLE_RATE / 1000.0))
    return x[start_idx:]


def load_slice(rel_path: str, t0: float, t1: float, flt=None, gain: float = 1.0, fade_in_ms: float = 2.0, fade_out_ms: float = 20.0) -> np.ndarray:
    """스튜디오 원음 구간 추출 + 옵션 필터 + 슬라이스 정규화 + 가장자리 클릭 방지."""
    full_path = os.path.join(STUDIO_DIR, rel_path)
    y = load_audio(full_path, nchannels=2)
    s0 = max(0, int(round(t0 * SAMPLE_RATE)))
    s1 = min(len(y), int(round(t1 * SAMPLE_RATE)))
    seg = y[s0:s1].copy()
    seg = butter_filter(seg, "highpass", 32.0, order=2)
    if flt is not None:
        kind, cutoff = flt
        seg = butter_filter(seg, kind, cutoff, order=3)
    seg = norm_peak(seg, 0.90)
    seg = fade_io(seg, fade_in_ms=fade_in_ms, fade_out_ms=fade_out_ms)
    return (seg * gain).astype(np.float32)


def mix_events(events: list[dict], reverb_wet: float = 0.06, reverb_tail_s: float = 0.22) -> np.ndarray:
    """시간(ms)·패닝(pan)·볼륨(gain) 기반 멀티-레이어 믹싱."""
    loaded = []
    max_len = 0
    for ev in events:
        seg = load_slice(
            ev["src"],
            ev["t0"],
            ev["t1"],
            flt=ev.get("flt"),
            gain=ev.get("gain", 1.0),
            fade_in_ms=ev.get("fi", 2.0),
            fade_out_ms=ev.get("fo", 22.0),
        )
        if ev.get("eq"):
            for fc, q, db in ev["eq"]:
                seg = peaking_eq(seg, fc, q, db)
        st = pan_stereo(seg, ev.get("pan", 0.0))
        off = int(round(ev.get("at_ms", 0.0) * SAMPLE_RATE / 1000.0))
        max_len = max(max_len, off + len(st))
        loaded.append((off, st))

    buf = np.zeros((max_len, 2), dtype=np.float32)
    for off, st in loaded:
        buf[off : off + len(st)] += st

    buf = trim_tail(buf, thresh_ratio=0.012, pad_ms=35.0)
    if reverb_wet > 0.0:
        buf = arena_reverb(buf, wet=reverb_wet, tail_s=reverb_tail_s, pre_delay_ms=11.0)
    return trim_tail(buf, thresh_ratio=0.01, pad_ms=25.0)


# ---------------------------------------------------------------------------
# 21종 스튜디오 실사 Foley 사양 정의 (Mixkit WAV + Red Library CC0 FLAC)
# ---------------------------------------------------------------------------
STUDIO_SFX_SPECS = [
    # [공격 5종]
    {
        "filename": "sfx_pit_hit_poke.mp3",
        "reverb_wet": 0.05,
        "target_peak": 0.86,
        "fade_in_ms": 1.5,
        "fade_out_ms": 30.0,
        "layers": [
            {"src": "mixkit/2151_soft_quick_punch.wav", "t0": 0.08, "t1": 0.28, "at_ms": 0, "pan": -0.16, "gain": 0.88, "flt": ("highpass", 190.0)},
            {"src": "mixkit/2149_hard_quick_punch.wav", "t0": 0.07, "t1": 0.28, "at_ms": 105, "pan": 0.16, "gain": 0.95, "flt": ("highpass", 190.0)},
            {"src": "mixkit/2165_short_punch_face.wav", "t0": 0.00, "t1": 0.18, "at_ms": 210, "pan": 0.0, "gain": 1.00, "flt": ("highpass", 190.0)},
        ],
    },
    {
        "filename": "sfx_pit_hit_spur.mp3",
        "reverb_wet": 0.06,
        "target_peak": 0.86,
        "fade_in_ms": 1.5,
        "fade_out_ms": 35.0,
        "layers": [
            {"src": "mixkit/2152_quick_knife_slice_cut.mp3", "t0": 0.00, "t1": 0.30, "at_ms": 0, "gain": 0.88, "flt": ("lowpass", 6200.0)},
            {"src": "mixkit/2050_martial_arts_kick.wav", "t0": 0.00, "t1": 0.32, "at_ms": 45, "gain": 0.95},
        ],
    },
    {
        "filename": "sfx_pit_hit_wing.mp3",
        "reverb_wet": 0.08,
        "target_peak": 0.87,
        "fade_in_ms": 4.0,
        "fade_out_ms": 45.0,
        "layers": [
            {"src": "red_library/Red_Library_Animals_Birds__R21-40b-Bird Wings Flapping.flac", "t0": 8.71, "t1": 9.15, "at_ms": 0, "gain": 0.90},
            {"src": "mixkit/2155_impact_strong_punch.mp3", "t0": 0.04, "t1": 0.58, "at_ms": 320, "gain": 1.00},
        ],
    },
    {
        "filename": "sfx_pit_hit_crit.mp3",
        "reverb_wet": 0.10,
        "target_peak": 0.88,
        "fade_in_ms": 1.5,
        "fade_out_ms": 50.0,
        "layers": [
            {"src": "mixkit/2155_impact_strong_punch.mp3", "t0": 0.04, "t1": 0.60, "at_ms": 0, "gain": 1.00},
            {"src": "red_library/Red_Library_Fights__R19-27-Big Fight Punches.flac", "t0": 3.08, "t1": 3.46, "at_ms": 0, "gain": 0.80},
            {"src": "mixkit/1551_bone_breaking_echo.wav", "t0": 0.00, "t1": 0.38, "at_ms": 8, "gain": 0.42},
        ],
    },
    {
        "filename": "sfx_pit_hit_gen.mp3",
        "reverb_wet": 0.06,
        "target_peak": 0.87,
        "fade_in_ms": 1.5,
        "fade_out_ms": 35.0,
        "layers": [
            {"src": "mixkit/2051_boxing_punch.wav", "t0": 0.08, "t1": 0.46, "at_ms": 0, "gain": 1.00},
            {"src": "mixkit/2053_punch_boxing_gloves.wav", "t0": 0.05, "t1": 0.32, "at_ms": 0, "gain": 0.32},
        ],
    },
    # [방어 · 패리 · 회피 · 빗나감 4종]
    {
        "filename": "sfx_pit_guard.mp3",
        "reverb_wet": 0.05,
        "target_peak": 0.86,
        "fade_in_ms": 2.0,
        "fade_out_ms": 35.0,
        "layers": [
            {"src": "red_library/Red_Library_Fights__R15-20-Padded Hits.flac", "t0": 3.12, "t1": 3.38, "at_ms": 0, "gain": 1.00, "flt": ("lowpass", 1600.0)},
            {"src": "red_library/Red_Library_Animals_Birds__R21-40b-Bird Wings Flapping.flac", "t0": 4.02, "t1": 4.42, "at_ms": 20, "gain": 0.45, "flt": ("bandpass", [500.0, 3500.0])},
        ],
    },
    {
        "filename": "sfx_pit_guard_gen.mp3",
        "reverb_wet": 0.06,
        "target_peak": 0.84,
        "fade_in_ms": 1.5,
        "fade_out_ms": 35.0,
        "layers": [
            {"src": "mixkit/2047_martial_arts_fast_punch.wav", "t0": 0.10, "t1": 0.42, "at_ms": 0, "gain": 0.55, "flt": ("highpass", 360.0)},
            {"src": "mixkit/2937_twig_breaking.wav", "t0": 0.14, "t1": 0.40, "at_ms": 4, "gain": 1.00, "flt": ("highpass", 280.0)},
            {"src": "mixkit/1491_arrow_whoosh.wav", "t0": 0.18, "t1": 0.38, "at_ms": 20, "gain": 0.48},
        ],
    },
    {
        "filename": "sfx_pit_dodge.mp3",
        "reverb_wet": 0.04,
        "target_peak": 0.78,
        "fade_in_ms": 4.0,
        "fade_out_ms": 35.0,
        "layers": [
            {"src": "mixkit/1489_air_woosh.wav", "t0": 0.42, "t1": 0.78, "at_ms": 0, "gain": 1.00},
            {"src": "red_library/Red_Library_Fights__R19-06-Fist fight on Dirt.flac", "t0": 15.40, "t1": 15.68, "at_ms": 80, "gain": 0.55},
        ],
    },
    {
        "filename": "sfx_pit_miss.mp3",
        "reverb_wet": 0.03,
        "target_peak": 0.80,
        "fade_in_ms": 4.0,
        "fade_out_ms": 30.0,
        "layers": [
            {"src": "mixkit/2141_punch_through_air.mp3", "t0": 0.24, "t1": 0.49, "at_ms": 0, "gain": 1.00},
        ],
    },
    # [스페셜 공방 F33 / F34 6종]
    {
        "filename": "sfx_pit_grab_pin.mp3",
        "reverb_wet": 0.06,
        "target_peak": 0.86,
        "fade_in_ms": 3.0,
        "fade_out_ms": 40.0,
        "layers": [
            {"src": "red_library/Red_Library_Fights__R09-56-Rustling Fight.flac", "t0": 0.45, "t1": 1.00, "at_ms": 0, "gain": 1.00},
            {"src": "red_library/Red_Library_Animals_Birds__R21-40b-Bird Wings Flapping.flac", "t0": 4.02, "t1": 4.45, "at_ms": 40, "gain": 0.45},
        ],
    },
    {
        "filename": "sfx_pit_slam.mp3",
        "reverb_wet": 0.14,
        "target_peak": 0.88,
        "fade_in_ms": 6.0,
        "fade_out_ms": 140.0,
        "layers": [
            {"src": "mixkit/1492_cinematic_whoosh_fast.wav", "t0": 0.72, "t1": 1.18, "at_ms": 0, "gain": 0.78, "fi": 35.0, "fo": 45.0},
            {"src": "slam_epic/mixkit_2908_movie_trailer_epic_impact.wav", "t0": 0.86, "t1": 1.85, "at_ms": 260, "gain": 1.00, "fi": 8.0, "fo": 140.0},
            {"src": "slam_epic/mixkit_788_big_cinematic_impact.mp3", "t0": 2.10, "t1": 2.95, "at_ms": 260, "gain": 0.36, "flt": ("lowpass", 220.0), "fi": 8.0, "fo": 160.0},
            {"src": "mixkit/753_heavy_fall_mud.wav", "t0": 0.01, "t1": 0.48, "at_ms": 275, "gain": 0.82, "fi": 2.0, "fo": 55.0},
            {"src": "slam_epic/mixkit_403_stone_debris_falling.wav", "t0": 4.14, "t1": 4.92, "at_ms": 330, "pan": -0.15, "gain": 0.65, "flt": ("highpass", 260.0), "fi": 8.0, "fo": 120.0},
        ],
    },
    {
        "filename": "sfx_pit_grab_miss.mp3",
        "reverb_wet": 0.04,
        "target_peak": 0.82,
        "fade_in_ms": 3.0,
        "fade_out_ms": 30.0,
        "layers": [
            {"src": "red_library/Red_Library_Fights__R09-56-Rustling Fight.flac", "t0": 2.66, "t1": 2.94, "at_ms": 0, "gain": 0.65},
            {"src": "mixkit/2148_quick_hit_through_air.wav", "t0": 0.08, "t1": 0.36, "at_ms": 10, "gain": 0.90},
        ],
    },
    {
        "filename": "sfx_pit_grab_escape.mp3",
        "reverb_wet": 0.05,
        "target_peak": 0.84,
        "fade_in_ms": 3.0,
        "fade_out_ms": 35.0,
        "layers": [
            {"src": "red_library/Red_Library_Animals_Birds__R21-40b-Bird Wings Flapping.flac", "t0": 4.02, "t1": 4.45, "at_ms": 0, "gain": 0.90},
            {"src": "mixkit/1491_arrow_whoosh.wav", "t0": 0.18, "t1": 0.38, "at_ms": 70, "gain": 0.95},
        ],
    },
    {
        "filename": "sfx_pit_break.mp3",
        "reverb_wet": 0.09,
        "target_peak": 0.87,
        "fade_in_ms": 1.5,
        "fade_out_ms": 45.0,
        "layers": [
            {"src": "mixkit/2050_martial_arts_kick.wav", "t0": 0.00, "t1": 0.30, "at_ms": 0, "gain": 0.92},
            {"src": "mixkit/2198_strong_punches_body.wav", "t0": 2.45, "t1": 2.88, "at_ms": 105, "gain": 1.00},
            {"src": "red_library/Red_Library_Fights__R15-18-Shot or Hit with Debris.flac", "t0": 2.22, "t1": 2.52, "at_ms": 115, "gain": 0.45},
        ],
    },
    {
        "filename": "sfx_pit_groggy.mp3",
        "reverb_wet": 0.08,
        "target_peak": 0.85,
        "fade_in_ms": 20.0,
        "fade_out_ms": 110.0,
        "layers": [
            {"src": "mixkit/559_slow_heartbeat.wav", "t0": 0.00, "t1": 1.55, "at_ms": 0, "gain": 1.00, "flt": ("lowpass", 320.0)},
            {"src": "mixkit/1489_air_woosh.wav", "t0": 0.42, "t1": 1.05, "at_ms": 80, "pan": -0.35, "gain": 0.36, "flt": ("lowpass", 650.0)},
            {"src": "mixkit/1489_air_woosh.wav", "t0": 0.42, "t1": 1.05, "at_ms": 720, "pan": 0.35, "gain": 0.32, "flt": ("lowpass", 650.0)},
            {"src": "red_library/Red_Library_Fights__R19-06-Fist fight on Dirt.flac", "t0": 15.40, "t1": 15.68, "at_ms": 180, "pan": -0.22, "gain": 0.44},
            {"src": "red_library/Red_Library_Fights__R09-79-Fall on Gravel.flac", "t0": 2.02, "t1": 2.52, "at_ms": 800, "pan": 0.22, "gain": 0.40},
        ],
    },
    # [특수 상태 · 다운 · 벽 충돌 · 슬로우 4종]
    {
        "filename": "sfx_pit_knockdown.mp3",
        "reverb_wet": 0.09,
        "target_peak": 0.87,
        "fade_in_ms": 2.0,
        "fade_out_ms": 55.0,
        "layers": [
            {"src": "red_library/Red_Library_Fights__R15-19-Muffled Body Fall.flac", "t0": 6.17, "t1": 6.45, "at_ms": 0, "gain": 0.85},
            {"src": "red_library/Red_Library_Impacts__R28-56-Sand Bags Dropped onto Wood Floor.flac", "t0": 7.72, "t1": 8.32, "at_ms": 0, "gain": 0.90, "flt": ("lowpass", 2200.0)},
            {"src": "red_library/Red_Library_Fights__R09-79-Fall on Gravel.flac", "t0": 1.70, "t1": 2.40, "at_ms": 80, "gain": 0.78},
        ],
    },
    {
        "filename": "sfx_pit_last_stand.mp3",
        "reverb_wet": 0.06,
        "target_peak": 0.86,
        "fade_in_ms": 25.0,
        "fade_out_ms": 160.0,
        "layers": [
            {"src": "mixkit/495_fast_heartbeat.wav", "t0": 0.15, "t1": 2.65, "at_ms": 0, "gain": 1.00, "flt": ("lowpass", 500.0)},
        ],
    },
    {
        "filename": "sfx_pit_wall_impact.mp3",
        "reverb_wet": 0.14,
        "target_peak": 0.86,
        "fade_in_ms": 2.0,
        "fade_out_ms": 50.0,
        "layers": [
            {"src": "red_library/Red_Library_Impacts__R28-55-Thumps on Large Hollow Wooden Surface.flac", "t0": 2.65, "t1": 3.05, "at_ms": 0, "gain": 1.00},
            {"src": "red_library/Red_Library_Fights__R15-19-Muffled Body Fall.flac", "t0": 6.17, "t1": 6.40, "at_ms": 0, "gain": 0.65},
            {"src": "mixkit/389_metal_grill_quick_hit.wav", "t0": 0.06, "t1": 0.44, "at_ms": 30, "gain": 0.72},
        ],
    },
    {
        "filename": "sfx_pit_ko_slow.mp3",
        "reverb_wet": 0.08,
        "target_peak": 0.86,
        "fade_in_ms": 6.0,
        "fade_out_ms": 120.0,
        "layers": [
            {"src": "mixkit/1143_cinematic_whoosh_deep_impact.mp3", "t0": 0.28, "t1": 1.65, "at_ms": 0, "gain": 1.00},
        ],
    },
    # [관중 2종]
    {
        "filename": "sfx_pit_crowd_roar.mp3",
        "reverb_wet": 0.0,
        "target_peak": 0.87,
        "fade_in_ms": 180.0,
        "fade_out_ms": 600.0,
        "layers": [
            {"src": "mixkit/462_huge_crowd_cheering_victory.wav", "t0": 0.50, "t1": 4.30, "at_ms": 0, "gain": 1.00, "flt": ("highpass", 110.0), "fi": 80.0, "fo": 250.0},
        ],
    },
    {
        "filename": "sfx_pit_crowd_gasp.mp3",
        "reverb_wet": 0.06,
        "target_peak": 0.86,
        "fade_in_ms": 35.0,
        "fade_out_ms": 380.0,
        "layers": [
            {"src": "crowd_whistle/fs_764055_gsc24_cheer_whistle_noclap.mp3", "t0": 9.80, "t1": 11.75, "at_ms": 0, "gain": 0.92, "flt": ("highpass", 120.0), "fi": 55.0, "fo": 380.0},
            {"src": "crowd_whistle/fs_729994_crowd_30k_whistles_cheer.mp3", "t0": 28.50, "t1": 30.50, "at_ms": 35, "gain": 0.58, "flt": ("highpass", 130.0), "fi": 80.0, "fo": 420.0},
            {"src": "crowd_whistle/fs_534607_finger_whistle.mp3", "t0": 0.04, "t1": 0.94, "at_ms": 130, "pan": 0.22, "gain": 0.45, "flt": ("highpass", 350.0), "fi": 30.0, "fo": 120.0},
        ],
    },
]


def build_studio_sfx(only_keys: set[str]):
    print("=== [1/3] 스튜디오 무손실 실사 Foley 21종 마스터링 ===")
    for spec in STUDIO_SFX_SPECS:
        key = spec["filename"].replace("sfx_pit_", "").replace(".mp3", "")
        if only_keys and key not in only_keys:
            continue
        mix = mix_events(spec["layers"], reverb_wet=spec.get("reverb_wet", 0.06))
        out = fade_io(mix, fade_in_ms=spec.get("fade_in_ms", 2.0), fade_out_ms=spec.get("fade_out_ms", 40.0))
        dur_s, kb = save_mp3(
            os.path.join(SFX_DIR, spec["filename"]),
            out,
            target_peak=spec.get("target_peak", DEFAULT_TARGET_PEAK),
        )
        print(f"  [OK] {spec['filename']:28s} | {dur_s:5.2f}s | {kb:6.1f} KB")


# ---------------------------------------------------------------------------
# 승자 아나운서 PA 보이스 2종 (KO 승 / 판정 승)
# ---------------------------------------------------------------------------
def _pa_voice_chain(mono: np.ndarray, is_eleven: bool = False) -> np.ndarray:
    x = butter_filter(mono, "highpass", 150.0, order=3)
    if is_eleven:
        x = peaking_eq(x, 2900.0, 1.1, 3.0)
        x = np.tanh(x * 1.25) / np.tanh(1.25)
    else:
        x = peaking_eq(peaking_eq(x, 3000.0, 1.0, 5.5), 220.0, 1.0, 2.5)
        x = np.tanh(x * 1.55) / np.tanh(1.55)
    x = norm_peak(x, 0.92)
    d1 = int(0.032 * SAMPLE_RATE)
    d2 = int(0.037 * SAMPLE_RATE)
    st = np.zeros((len(x) + d2 + int(0.22 * SAMPLE_RATE), 2), dtype=np.float32)
    st[: len(x), 0] += x * 0.90
    st[: len(x), 1] += x * 0.90
    st[d1 : d1 + len(x), 0] += x * 0.16
    st[d2 : d2 + len(x), 1] += x * 0.14
    return st


def build_winner_voices(only_keys: set[str]):
    if only_keys and not (only_keys & {"win_ko", "win_decision"}):
        return
    print("=== [2/3] 흥분 승자 PA 아나운서 보이스 2종 생성 (KO 승 / 판정 승) ===")

    async def _ensure_edge_parts():
        parts = [
            ("v4_lead_knockout.mp3", "KNOCKOUT!!", "en-US-GuyNeural", "+8%", "+5Hz"),
            ("v4_lead_decision.mp3", "BY UNANIMOUS DECISION!!", "en-US-GuyNeural", "+12%", "+4Hz"),
        ]
        for fn, text, voice, rate, pitch in parts:
            p = os.path.join(VOICE_CACHE_DIR, fn)
            await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(p)

    asyncio.run(_ensure_edge_parts())

    # 프로젝트 내 하이텐션 ElevenLabs 원본 로드 및 무음 경계 정밀 슬라이싱
    raw_unbel = load_audio(os.path.join(BASE_DIR, "assets/audio/race/voice_261022/vo_us_win_01_2.mp3"), 1)
    unbel = trim_tail(trim_onset(raw_unbel[int(2.14 * SAMPLE_RATE) : int(3.45 * SAMPLE_RATE)], 0.015, 6.0), 0.012, 30.0)

    raw_takes = load_audio(os.path.join(BASE_DIR, "assets/audio/race/voice/vo_us_win_03.mp3"), 1)
    takes_vic = trim_tail(trim_onset(raw_takes, 0.015, 6.0), 0.012, 35.0)

    def _compose_winner(lead_path: str, eleven_clip: np.ndarray, gap_ms: float, out_name: str):
        lead_mono = trim_tail(trim_onset(load_audio(lead_path, 1), 0.018, 6.0), 0.015, 25.0)
        s1 = _pa_voice_chain(lead_mono, is_eleven=False)
        s2 = _pa_voice_chain(eleven_clip, is_eleven=True)

        # 순수 보이스 전용 조합 (배경 함성/관중 레이어 0%)
        off2 = max(0, len(s1) - int(0.18 * SAMPLE_RATE)) + int(gap_ms * SAMPLE_RATE / 1000.0)
        tot = off2 + len(s2)
        voice_bus = np.zeros((tot, 2), dtype=np.float32)
        voice_bus[: len(s1)] += s1
        voice_bus[off2 : off2 + len(s2)] += s2

        pa_out = arena_reverb(trim_tail(voice_bus, thresh_ratio=0.01, pad_ms=45.0), wet=0.16, tail_s=0.36, pre_delay_ms=20.0)
        final = fade_io(trim_tail(pa_out, thresh_ratio=0.008, pad_ms=60.0), fade_in_ms=4.0, fade_out_ms=110.0)
        dur_s, kb = save_mp3(os.path.join(SFX_DIR, out_name), final, target_peak=0.86)
        print(f"  [OK] {out_name:28s} | {dur_s:5.2f}s | {kb:6.1f} KB")

    if not only_keys or "win_ko" in only_keys:
        _compose_winner(
            os.path.join(VOICE_CACHE_DIR, "v4_lead_knockout.mp3"),
            unbel,
            110.0,
            "sfx_pit_win_ko.mp3",
        )
    if not only_keys or "win_decision" in only_keys:
        _compose_winner(
            os.path.join(VOICE_CACHE_DIR, "v4_lead_decision.mp3"),
            takes_vic,
            100.0,
            "sfx_pit_win_decision.mp3",
        )


def _bell_opt_compress(x: np.ndarray, thresh: float = 0.22, ratio: float = 3.0, atk_ms: float = 4.0, rel_ms: float = 200.0) -> np.ndarray:
    """비왜곡 피드포워드 엔벨로프 컴프레서: 초기 타격 스냅을 살리면서 벨 서스테인 음량을 깔끔하게 강화."""
    mono_abs = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    atk_c = float(np.exp(-1.0 / max(1.0, atk_ms * SAMPLE_RATE / 1000.0)))
    rel_c = float(np.exp(-1.0 / max(1.0, rel_ms * SAMPLE_RATE / 1000.0)))
    env = np.empty(len(mono_abs), dtype=np.float32)
    cur = 0.0
    for i, v in enumerate(mono_abs):
        c = atk_c if v > cur else rel_c
        cur = c * cur + (1.0 - c) * float(v)
        env[i] = cur
    gain = np.ones_like(env)
    above = env > thresh
    if np.any(above):
        compressed = thresh * ((env[above] / thresh) ** (1.0 / ratio))
        gain[above] = compressed / env[above]
    if x.ndim == 2:
        return (x * gain[:, None]).astype(np.float32)
    return (x * gain).astype(np.float32)


def build_bell_single(only_keys: set[str]):
    """v4.0.4: v1.2 풀렝스 링 벨을 경기 시작용 경쾌·강력 브라이트 톤으로 리마스터링 (--only bell_single 전용)."""
    if "bell_single" not in only_keys:
        return
    print("=== [bell_single] SFX_PIT_BELL_SINGLE (v1.2 풀버전 클린 리마스터링) ===")
    v1_path = os.path.join(PIT_AUDIO_DIR, "sfx_v1_backup", "sfx_pit_bell_single.mp3")
    raw = load_audio(v1_path, 2)
    x = trim_onset(raw, thresh_ratio=0.02, pre_ms=1.5)
    # v1.2 실울림(0~1.42s) 추출 후 아레나 잔향 확장 공간(0.68s) 확보
    x = trim_tail(x, thresh_ratio=0.002, pad_ms=20.0)
    x = butter_filter(x, "highpass", 180.0, order=3)

    # 경쾌한 타격 바디(780Hz) + 실제 링 벨 배음(1.28kHz·2.25kHz·4.5kHz) 부스트
    x = peaking_eq(x, 780.0, 1.1, 2.0)
    x = peaking_eq(x, 1280.0, 1.3, 2.0)
    x = peaking_eq(x, 2250.0, 1.1, 3.0)
    x = peaking_eq(x, 4500.0, 1.1, 3.8)

    # 빠른 어택(0.6ms) 비왜곡 컴프레션 + 1.35x 소프트 리미팅으로 타격 펀치·서스테인 음량 동시 강화
    x = norm_peak(x, 0.90)
    x = _bell_opt_compress(x, thresh=0.16, ratio=2.6, atk_ms=0.6, rel_ms=240.0)
    x = norm_peak(x, 0.94)
    x = (np.tanh(x * 1.35) / np.tanh(1.35)).astype(np.float32)

    # M/S 스테레오 감쇄 없는 미세 와이드닝 (모노 합산 100% 무왜곡)
    mid = 0.5 * (x[:, 0] + x[:, 1])
    side = 0.5 * (x[:, 0] - x[:, 1]) * 1.18
    x = np.stack([mid + side, mid - side], axis=1).astype(np.float32)

    # arena_reverb는 입력 길이 + 0.14s에서 자르므로 무음 패딩 후 0.65s 아레나 테일을 끝까지 보존
    x = np.vstack([x, np.zeros((int(0.62 * SAMPLE_RATE), 2), dtype=np.float32)])
    x = arena_reverb(x, wet=0.20, tail_s=0.65, pre_delay_ms=14.0)
    x = trim_tail(x, thresh_ratio=0.0018, pad_ms=65.0)
    x = fade_io(x, fade_in_ms=1.0, fade_out_ms=340.0)
    dur_s, kb = save_mp3(os.path.join(SFX_DIR, "sfx_pit_bell_single.mp3"), x, target_peak=0.91)
    print(f"  [OK] sfx_pit_bell_single.mp3    | {dur_s:5.2f}s | {kb:6.1f} KB")


# ---------------------------------------------------------------------------
# 1R 실전 시뮬레이션 데모 (38.0초, v4.0 스튜디오 실사 Foley + 흥분 WIN_KO 마감)
# ---------------------------------------------------------------------------
def remove_deprecated_assets():
    for d in (SFX_DIR, DOCS_SFX_DIR):
        p = os.path.join(d, "sfx_pit_rooster_crow.mp3")
        if os.path.exists(p):
            os.remove(p)
            print(f"  [구버전 삭제] {p}")


def build_round1_demo():
    print("=== [3/3] 1R 실전 시뮬레이션 데모 (v4.0 스튜디오 Foley + WIN_KO 마감) 재합성 ===")
    TOTAL_S = 38.0
    N = int(TOTAL_S * SAMPLE_RATE)

    bgm_raw = load_audio(os.path.join(BGM_DIR, "bgm_pit_fight.mp3"), 2)
    bgm_layer = bgm_raw[:N].copy()
    fi = int(1.6 * SAMPLE_RATE)
    bgm_layer[:fi] *= np.linspace(0.0, 1.0, fi)[:, None]

    # 스튜디오 무손실 경기장 관중 앰비언스 (저레벨 배경 베드 루프)
    cheer_src = load_audio(os.path.join(STUDIO_DIR, "mixkit/462_huge_crowd_cheering_victory.wav"), 2)
    cheer_loop = norm_peak(butter_filter(cheer_src[int(1.0 * SAMPLE_RATE) : int(8.5 * SAMPLE_RATE)], "highpass", 160.0), 0.13)
    crowd_bed = np.zeros((N, 2), dtype=np.float32)
    pos = 0
    while pos < N:
        take = min(len(cheer_loop), N - pos)
        crowd_bed[pos : pos + take] = cheer_loop[:take]
        pos += take

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
        clip = load_audio(os.path.join(SFX_DIR, fname), 2)
        if abs(pan) > 0.02:
            clip = pan_stereo(clip, pan=pan)
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

    # 일반 공방 & 방어/패리 대비
    add_sfx(4.50, "sfx_pit_hit_poke.mp3", gain=1.02, pan=-0.28, duck_db=-3.5, duck_hold=0.28)
    add_sfx(5.20, "sfx_pit_guard.mp3", gain=1.02, pan=0.28, duck_db=-3.5, duck_hold=0.22)
    add_sfx(6.55, "sfx_pit_hit_wing.mp3", gain=1.02, pan=0.25, duck_db=-4.2, duck_hold=0.40)
    add_sfx(7.55, "sfx_pit_guard_gen.mp3", gain=1.02, pan=-0.25, duck_db=-4.5, duck_hold=0.28)
    add_sfx(8.15, "sfx_pit_dodge.mp3", gain=0.98, pan=-0.35, duck_db=-2.5, duck_hold=0.20)
    add_sfx(8.65, "sfx_pit_hit_spur.mp3", gain=1.05, pan=-0.20, duck_db=-4.5, duck_hold=0.30)
    add_sfx(9.75, "sfx_pit_miss.mp3", gain=0.95, pan=0.30)
    add_sfx(10.30, "sfx_pit_hit_gen.mp3", gain=1.00, pan=-0.20, duck_db=-3.8, duck_hold=0.25)

    # 스페셜 공방 1: [특방 F34]
    add_sfx(12.35, "sfx_pit_grab_pin.mp3", gain=1.02, pan=0.15, duck_db=-4.5, duck_hold=0.28)
    add_sfx(12.82, "sfx_pit_grab_escape.mp3", gain=1.00, pan=-0.15, duck_db=-4.5, duck_hold=0.25)
    add_sfx(13.22, "sfx_pit_break.mp3", gain=1.08, pan=0.0, duck_db=-7.0, duck_hold=0.48)
    add_sfx(13.78, "sfx_pit_wall_impact.mp3", gain=1.02, pan=0.38, duck_db=-5.0, duck_hold=0.32)
    add_sfx(13.95, "sfx_pit_crowd_gasp.mp3", gain=0.88)

    # 치명타 & 그로기 & 투지
    add_sfx(17.20, "sfx_pit_hit_gen.mp3", gain=0.98, pan=0.25, duck_db=-3.5, duck_hold=0.22)
    add_sfx(18.00, "sfx_pit_hit_crit.mp3", gain=1.10, pan=-0.10, duck_db=-7.5, duck_hold=0.50)
    add_sfx(18.60, "sfx_pit_groggy.mp3", gain=0.98, pan=0.20, duck_db=-4.5, duck_hold=0.95)
    add_sfx(20.60, "sfx_pit_last_stand.mp3", gain=0.95, pan=0.0, duck_db=-6.5, duck_hold=1.80)
    add_sfx(23.50, "sfx_pit_hit_spur.mp3", gain=1.00, pan=-0.25, duck_db=-4.2, duck_hold=0.28)
    add_sfx(24.30, "sfx_pit_guard.mp3", gain=1.00, pan=0.25, duck_db=-3.5, duck_hold=0.22)

    # 스페셜 공방 2: [특공 F33] 브루탈 KO -> WIN_KO
    add_sfx(26.75, "sfx_pit_grab_pin.mp3", gain=1.02, pan=-0.15, duck_db=-5.0, duck_hold=0.35)
    add_sfx(27.28, "sfx_pit_slam.mp3", gain=1.12, pan=0.0, duck_db=-9.5, duck_hold=0.85)
    add_sfx(27.55, "sfx_pit_crowd_gasp.mp3", gain=0.92)
    add_sfx(28.15, "sfx_pit_ko_slow.mp3", gain=0.95, duck_db=-10.0, duck_hold=1.10)
    add_sfx(29.05, "sfx_pit_knockdown.mp3", gain=1.02, duck_db=-12.0, duck_hold=1.20)
    add_sfx(29.65, "sfx_pit_ko_bell.mp3", gain=1.00, duck_db=-18.0, duck_hold=6.00)
    add_sfx(30.40, "sfx_pit_crowd_roar.mp3", gain=0.92)
    add_sfx(31.85, "sfx_pit_win_ko.mp3", gain=1.08, duck_db=-18.0, duck_hold=5.00, is_voice=True)

    fade_s = int(29.65 * SAMPLE_RATE)
    fade_e = int(32.50 * SAMPLE_RATE)
    duck_gain[fade_s:fade_e] *= np.linspace(1.0, 0.0, fade_e - fade_s)
    duck_gain[fade_e:] = 0.0

    bgm_ducked = bgm_layer * 0.48 * duck_gain[:, None]
    master_mix = bgm_ducked + crowd_bed + sfx_layer * 1.05 + voice_layer * 1.05
    fo = int(1.4 * SAMPLE_RATE)
    master_mix[-fo:] *= np.linspace(1.0, 0.0, fo)[:, None]

    out_path = os.path.join(DEMO_DIR, "demo_pit_round1_simulation.mp3")
    dur_s, kb = save_mp3(out_path, master_mix, target_peak=0.87)
    print(f"  [OK] demo_pit_round1_simulation.mp3 | {dur_s:.2f}s | {kb:.1f} KB")


def main():
    parser = argparse.ArgumentParser(description="Rumble Pit v4.0 스튜디오 실사 Foley 생성기")
    parser.add_argument("--only", default="", help="쉼표 구분 생성 키 목록 (예: hit_poke,win_ko)")
    parser.add_argument("--demo-only", action="store_true", help="1R 데모만 재합성")
    parser.add_argument("--no-demo", action="store_true", help="1R 데모 재합성 생략")
    args = parser.parse_args()

    only_keys = {k.strip() for k in args.only.split(",") if k.strip()}
    remove_deprecated_assets()
    if not args.demo_only:
        build_studio_sfx(only_keys)
        build_winner_voices(only_keys)
        build_bell_single(only_keys)
    if not args.no_demo:
        build_round1_demo()


if __name__ == "__main__":
    main()
