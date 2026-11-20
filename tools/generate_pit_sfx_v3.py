#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROOSTER RUMBLE - Rumble Pit v3.0 AI 실사 폴리 + 승자 PA 보이스 사운드 제작 파이프라인
- 기존 추상 CC0/금속/비프/사인파 기반 DSP 짜깁기 전면 폐기
- 무료 AI Text-to-SFX (declare-lab/TangoFlux 44.1kHz Stereo 주력 + fffiloni/AudioGen 백업)로
  게임 장면 맞춤형 실사 격투·아레나 폴리 생성 후 최적 임팩트 구간 정밀 추출 & 아레나 마스터링
- 승자 사운드 2종 분리: 우승 닭 울음(sfx_pit_rooster_crow) 폐기 -> 1~3R 동일 PA 성우의 KO승/판정승 보이스
- 라이선스 고지: TangoFlux / AudioGen 생성 음원은 프로토타입·MVP 검증용(Non-Commercial)
- 출력 규격: Stereo, 44.1 kHz, 192 kbps MP3, DC 오프셋 제거, 피크 헤드룸 -1.0 dBFS
"""

import argparse
import asyncio
import io
import json
import os
import time
import urllib.error
import urllib.request
import wave

import edge_tts
import lameenc
import miniaudio
import numpy as np
from scipy import signal

SAMPLE_RATE = 44100
BITRATE = 192
TARGET_PEAK = 0.891  # -1.0 dBFS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "tools", "source_cache")
AI_RAW_DIR = os.path.join(CACHE_DIR, "pit_ai_v3")
VOICE_RAW_DIR = os.path.join(CACHE_DIR, "pit_cc0", "voice_raw")
PIT_DIR = os.path.join(BASE_DIR, "assets", "audio", "pit")
SFX_DIR = os.path.join(PIT_DIR, "sfx")
BGM_DIR = os.path.join(PIT_DIR, "bgm")
DEMO_DIR = os.path.join(PIT_DIR, "demo")
DOCS_SFX_DIR = os.path.join(BASE_DIR, "docs", "assets", "audio", "pit", "sfx")

for d in (AI_RAW_DIR, VOICE_RAW_DIR, SFX_DIR, BGM_DIR, DEMO_DIR):
    os.makedirs(d, exist_ok=True)


# ---------------------------------------------------------------------------
# 오디오 입출력 & 마스터링 유틸리티 (비파괴 원칙: 30Hz HPF 외 대역 왜곡 금지)
# ---------------------------------------------------------------------------
def load_audio(path: str, nchannels: int = 2) -> np.ndarray:
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


def load_wav_bytes(raw_bytes: bytes) -> np.ndarray:
    dec = miniaudio.decode(
        raw_bytes,
        output_format=miniaudio.SampleFormat.FLOAT32,
        nchannels=2,
        sample_rate=SAMPLE_RATE,
    )
    return np.frombuffer(dec.samples, dtype=np.float32).reshape(-1, 2).copy()


def save_wav_stereo(path: str, audio: np.ndarray):
    x = audio.astype(np.float32)
    if x.ndim == 1:
        x = np.column_stack([x, x])
    int_data = np.int16(np.clip(x, -1.0, 1.0) * 32767)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int_data.tobytes())


def save_mp3(path: str, audio: np.ndarray, target_peak: float = TARGET_PEAK):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    x = audio.astype(np.float32).copy()
    if x.ndim == 1:
        x = np.column_stack([x, x])
    x -= np.mean(x, axis=0, keepdims=True)
    pk = np.max(np.abs(x))
    if pk > 1e-6:
        x = x / pk
        x = np.tanh(x * 1.08) / np.tanh(1.08)
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


def hpf(x: np.ndarray, freq: float, order: int = 2) -> np.ndarray:
    sos = signal.butter(order, freq, btype="highpass", fs=SAMPLE_RATE, output="sos")
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


def warm_saturate(x: np.ndarray, drive: float = 1.2) -> np.ndarray:
    return (np.tanh(x * drive) / np.tanh(drive)).astype(np.float32)


def norm_peak(x: np.ndarray, level: float = 1.0) -> np.ndarray:
    pk = np.max(np.abs(x)) if len(x) else 0.0
    if pk < 1e-8:
        return x
    return (x / pk * level).astype(np.float32)


def fade_io(x: np.ndarray, fade_in_ms: float = 2.0, fade_out_ms: float = 40.0) -> np.ndarray:
    out = x.copy()
    fi = min(int(fade_in_ms * SAMPLE_RATE / 1000.0), max(1, len(out) // 3))
    fo = min(int(fade_out_ms * SAMPLE_RATE / 1000.0), max(1, len(out) // 2))
    if fi > 1:
        env = np.linspace(0.0, 1.0, fi)
        out[:fi] *= env[:, None] if out.ndim == 2 else env
    if fo > 1:
        env = np.linspace(1.0, 0.0, fo)
        out[-fo:] *= env[:, None] if out.ndim == 2 else env
    return out


def trim_onset(x: np.ndarray, thresh_ratio: float = 0.05, pre_ms: float = 5.0) -> np.ndarray:
    if len(x) == 0:
        return x
    pk = np.max(np.abs(x))
    if pk < 1e-6:
        return x
    idx = np.where(np.abs(x) >= pk * thresh_ratio)[0]
    if len(idx) == 0:
        return x
    start = max(0, int(idx[0] - pre_ms * SAMPLE_RATE / 1000.0))
    return fade_io(x[start:].copy(), 2.0, 0.0)


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


def make_stereo_wide(mono: np.ndarray, pan: float = 0.0, width_ms: float = 0.0) -> np.ndarray:
    angle = (pan + 1.0) * (np.pi / 4.0)
    l = mono * np.cos(angle)
    r = mono * np.sin(angle)
    if width_ms > 0.1:
        d = int(width_ms * SAMPLE_RATE / 1000.0)
        r_del = np.concatenate([np.zeros(d, dtype=np.float32), r[:-d]]) if len(r) > d else r
        r = 0.55 * r + 0.45 * r_del
    return np.column_stack([l, r]).astype(np.float32)


def arena_reverb(stereo: np.ndarray, wet: float = 0.06, tail_s: float = 0.25, pre_delay_ms: float = 12.0) -> np.ndarray:
    if wet <= 1e-4:
        return stereo
    pad_n = int((tail_s + 0.06) * SAMPLE_RATE)
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
    rev = peaking_eq(hpf(rev, 160.0), 4200.0, 0.7, -4.0)
    out = src + rev * wet
    return trim_tail(out, thresh_ratio=0.008, pad_ms=35.0)


# ---------------------------------------------------------------------------
# 무료 AI Text-to-SFX API 클라이언트 (TangoFlux 주력 + AudioGen 백업)
# ---------------------------------------------------------------------------
def _download_gradio_file(url: str, fallback_bases: list[str] = None) -> bytes:
    candidates = [url]
    if "/c/file=" in url:
        candidates.append(url.replace("/c/file=", "/file="))
    if "/file=" in url and "/gradio_api/file=" not in url:
        candidates.append(url.replace("/file=", "/gradio_api/file="))
    for base in (fallback_bases or []):
        if "/tmp/" in url:
            suffix = url[url.find("/tmp/") :]
            candidates.append(base + suffix)

    last_err = None
    for u in candidates:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read()
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Gradio 파일 다운로드 실패 ({candidates[0]}): {last_err}")


def call_tangoflux(prompt: str, duration: float = 3.0, steps: int = 30, guidance: float = 4.5, max_retries: int = 3) -> np.ndarray:
    post_url = "https://declare-lab-tangoflux.hf.space/call/predict"
    payload = {"data": [prompt, int(steps), float(guidance), float(duration)]}
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                post_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(req, timeout=20) as r:
                ev = json.loads(r.read().decode()).get("event_id")
            if not ev:
                raise RuntimeError("event_id 미반환")
            sse_url = f"{post_url}/{ev}"
            req2 = urllib.request.Request(sse_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req2, timeout=90) as r2:
                while True:
                    raw = r2.readline()
                    if not raw:
                        raise RuntimeError("SSE 조기 종료")
                    line = raw.decode("utf-8", errors="replace").strip()
                    if line.startswith("event: complete"):
                        data_line = r2.readline().decode("utf-8", errors="replace").strip()
                        arr = json.loads(data_line[len("data:") :].strip())
                        file_url = arr[0]["url"]
                        wav_bytes = _download_gradio_file(
                            file_url,
                            fallback_bases=["https://declare-lab-tangoflux.hf.space/file="],
                        )
                        return load_wav_bytes(wav_bytes)
                    if line.startswith("event: error"):
                        err_data = r2.readline().decode("utf-8", errors="replace").strip()
                        raise RuntimeError(f"TangoFlux ZeroGPU 오류: {err_data}")
        except Exception as e:
            print(f"    [TangoFlux 재시도 {attempt}/{max_retries}] {e}")
            if attempt < max_retries:
                time.sleep(2.5 * attempt)
            else:
                raise


def call_audiogen(prompt: str, duration: int = 5, max_retries: int = 2) -> np.ndarray:
    post_url = "https://fffiloni-audiogen.hf.space/gradio_api/call/infer"
    payload = {"data": [prompt, max(5, int(round(duration)))]}
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                post_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(req, timeout=20) as r:
                ev = json.loads(r.read().decode()).get("event_id")
            if not ev:
                raise RuntimeError("AudioGen event_id 미반환")
            sse_url = f"{post_url}/{ev}"
            req2 = urllib.request.Request(sse_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req2, timeout=90) as r2:
                while True:
                    raw = r2.readline()
                    if not raw:
                        raise RuntimeError("AudioGen SSE 조기 종료")
                    line = raw.decode("utf-8", errors="replace").strip()
                    if line.startswith("event: complete"):
                        data_line = r2.readline().decode("utf-8", errors="replace").strip()
                        arr = json.loads(data_line[len("data:") :].strip())
                        file_url = arr[0]["url"]
                        wav_bytes = _download_gradio_file(
                            file_url,
                            fallback_bases=["https://fffiloni-audiogen.hf.space/gradio_api/file="],
                        )
                        return load_wav_bytes(wav_bytes)
                    if line.startswith("event: error"):
                        err_data = r2.readline().decode("utf-8", errors="replace").strip()
                        raise RuntimeError(f"AudioGen 오류: {err_data}")
        except Exception as e:
            print(f"    [AudioGen 재시도 {attempt}/{max_retries}] {e}")
            if attempt < max_retries:
                time.sleep(2.5 * attempt)
            else:
                raise


def fetch_ai_raw(key: str, prompt: str, duration: float = 3.0, engine: str = "tangoflux", regen: bool = False, suffix: str = "_raw") -> np.ndarray:
    cache_path = os.path.join(AI_RAW_DIR, f"{key}{suffix}.wav")
    if os.path.exists(cache_path) and not regen:
        print(f"  [캐시 로드] {key}{suffix}.wav")
        return load_audio(cache_path, 2)

    print(f"  [AI 생성 요청: {engine}] {key} ({duration}s) ...")
    if engine == "audiogen":
        try:
            audio = call_audiogen(prompt, duration=max(5, int(round(duration))))
        except Exception as e:
            print(f"    [AudioGen 실패 ➔ TangoFlux 폴백] {e}")
            audio = call_tangoflux(prompt, duration=duration)
    else:
        try:
            audio = call_tangoflux(prompt, duration=duration)
        except Exception as e:
            print(f"    [TangoFlux 실패 ➔ AudioGen 폴백] {e}")
            audio = call_audiogen(prompt, duration=max(5, int(round(duration))))

    save_wav_stereo(cache_path, audio)
    print(f"    -> 원음 캐시 저장 완료: {os.path.basename(cache_path)} ({len(audio)/SAMPLE_RATE:.2f}s)")
    return audio


# ---------------------------------------------------------------------------
# 스마트 구간 추출기 (임팩트 / 연속 구간)
# ---------------------------------------------------------------------------
def extract_best_segment(
    audio: np.ndarray,
    target_s: float,
    min_s: float,
    mode: str = "impact",
    pre_ms: float = 10.0,
    fade_in_ms: float = 2.0,
    fade_out_ms: float = 65.0,
    label: str = "",
) -> np.ndarray:
    x = audio.astype(np.float32).copy()
    if x.ndim == 1:
        x = np.column_stack([x, x])
    x -= np.mean(x, axis=0, keepdims=True)
    x = hpf(x, 30.0, order=2)

    total_n = len(x)
    if total_n == 0:
        return x

    mono = np.mean(np.abs(x), axis=1)
    hop = int(0.010 * SAMPLE_RATE)  # 10ms frame
    n_frames = max(1, total_n // hop)
    rms = np.array(
        [np.sqrt(np.mean(mono[i * hop : (i + 1) * hop] ** 2)) for i in range(n_frames)],
        dtype=np.float32,
    )
    pk_rms = float(np.max(rms)) if len(rms) else 0.0
    if pk_rms < 1e-6:
        print(f"    [경고] 무음 감지 ({label})")
        return x[: int(target_s * SAMPLE_RATE)]

    if mode == "continuous":
        win_f = max(1, min(n_frames, int(round(target_s / 0.010))))
        if win_f >= n_frames:
            start_f = 0
        else:
            csum = np.concatenate([[0.0], np.cumsum(rms ** 2)])
            win_energy = csum[win_f:] - csum[:-win_f]
            start_f = int(np.argmax(win_energy))
        # 앞부분 무음(>10% 미만) 스킵
        while start_f < n_frames - 1 and rms[start_f] < pk_rms * 0.08:
            start_f += 1
        start_idx = max(0, start_f * hop - int(pre_ms * SAMPLE_RATE / 1000.0))
        end_idx = min(total_n, start_idx + int(target_s * SAMPLE_RATE))
        # min_s 이후 끝단 완전 무음 제거
        min_f = min(n_frames, start_f + int(round(min_s / 0.010)))
        end_f = min(n_frames, int(np.ceil(end_idx / hop)))
        active_f = np.where(rms[min_f:end_f] >= pk_rms * 0.03)[0]
        if len(active_f) > 0:
            last_f = min_f + int(active_f[-1]) + 4
            end_idx = min(end_idx, last_f * hop)
        if end_idx - start_idx < int(min_s * SAMPLE_RATE):
            end_idx = min(total_n, start_idx + int(min_s * SAMPLE_RATE))
    else:
        # 'impact' 모드: 말미(min_s * 0.85) 구간의 끝단 팝 제외 후 최대 피크 버스트 포함
        tail_guard_f = max(1, n_frames - max(10, int(round((min_s * 0.85) / 0.010))))
        pk_f = int(np.argmax(rms[:tail_guard_f])) if np.max(rms[:tail_guard_f]) >= pk_rms * 0.25 else int(np.argmax(rms))
        gap_frames = int(0.14 / 0.010)
        max_lookback_f = int(round((target_s * 0.45) / 0.010))
        earliest_f = max(0, pk_f - max_lookback_f)

        # pk_f에서 뒤로 가면서 연속 무음 gap_frames가 나오면 끊음
        silent_run = 0
        burst_floor_f = earliest_f
        for f_idx in range(pk_f, earliest_f - 1, -1):
            if rms[f_idx] < pk_rms * 0.08:
                silent_run += 1
                if silent_run >= gap_frames:
                    burst_floor_f = f_idx + silent_run
                    break
            else:
                silent_run = 0

        # burst_floor_f 이후 피크 대비 22% 이상 최초 유효 임팩트 프레임 탐지
        rel = rms[burst_floor_f : pk_f + 1]
        hit_candidates = np.where(rel >= pk_rms * 0.22)[0]
        onset_f = burst_floor_f + int(hit_candidates[0]) if len(hit_candidates) else pk_f

        # 샘플 단위 정밀 onset 보정 (트랜지언트 보존)
        search_lo = max(0, (onset_f - 2) * hop)
        search_hi = min(total_n, (onset_f + 2) * hop)
        seg_mono = np.mean(np.abs(x[search_lo:search_hi]), axis=1)
        loc_pk = float(np.max(mono[max(0, onset_f * hop - hop) : min(total_n, (pk_f + 1) * hop)]))
        fine_hits = np.where(seg_mono >= loc_pk * 0.08)[0]
        fine_onset = search_lo + (int(fine_hits[0]) if len(fine_hits) else 0)

        start_idx = max(0, fine_onset - int(pre_ms * SAMPLE_RATE / 1000.0))
        min_end = min(total_n, start_idx + int(min_s * SAMPLE_RATE))
        max_end = min(total_n, start_idx + int(target_s * SAMPLE_RATE))

        # min_s 이후 에너지가 pk_rms 3% 이하로 떨어지는 지점까지 포함
        tail_f_lo = min(n_frames, int(min_end / hop))
        tail_f_hi = min(n_frames, int(np.ceil(max_end / hop)))
        end_idx = max_end
        if tail_f_hi > tail_f_lo:
            quiet_run = 0
            for f_idx in range(tail_f_lo, tail_f_hi):
                if rms[f_idx] <= pk_rms * 0.03:
                    quiet_run += 1
                    if quiet_run >= 3:
                        end_idx = min(max_end, (f_idx + 1) * hop)
                        break
                else:
                    quiet_run = 0

    seg = x[start_idx:end_idx].copy()
    seg = fade_io(seg, fade_in_ms=fade_in_ms, fade_out_ms=fade_out_ms)
    s0, s1 = start_idx / SAMPLE_RATE, end_idx / SAMPLE_RATE
    print(f"    [구간 추출: {label}] [{s0:.2f}s .. {s1:.2f}s] -> {len(seg)/SAMPLE_RATE:.2f}s")
    return seg


# ---------------------------------------------------------------------------
# SFX 레시피 사양 (프롬프트는 상용 교체 시에도 재사용할 수 있도록 명시 관리)
# ---------------------------------------------------------------------------
BATCH1_SPECS = [
    {
        "key": "hit_poke",
        "filename": "sfx_pit_hit_poke.mp3",
        "prompt": "Single sharp heavy blunt punching bag thump hitting dense thick leather solidly, tight crisp organic strike, dry studio foley, no speaking, no voice, no clicks, no music",
        "duration": 2.0,
        "target_s": 0.20,
        "min_s": 0.13,
        "mode": "impact",
        "reverb_wet": 0.05,
        "fade_out_ms": 40.0,
        "engine": "tangoflux",
        "triple_peck": True,
    },
    {
        "key": "hit_spur",
        "filename": "sfx_pit_hit_spur.mp3",
        "prompt": "Single sharp fast air whoosh followed by a tearing leather rip and hard meaty body slap impact, isolated dry studio sound effect, no drum beat, no metal, no music",
        "duration": 2.0,
        "target_s": 0.44,
        "min_s": 0.30,
        "mode": "impact",
        "reverb_wet": 0.06,
        "fade_out_ms": 55.0,
        "engine": "tangoflux",
    },
    {
        "key": "guard_gen",
        "filename": "sfx_pit_guard_gen.mp3",
        "prompt": "Realistic close up foley of hard dense bone and thick keratin colliding and deflecting sharply like a martial arts shin block parry, solid dry bone clack impact with forceful air push, no metal, no sword, no bell, no music",
        "duration": 3.0,
        "target_s": 0.45,
        "min_s": 0.32,
        "mode": "impact",
        "reverb_wet": 0.06,
        "fade_out_ms": 55.0,
        "engine": "tangoflux",
    },
    {
        "key": "grab_pin",
        "filename": "sfx_pit_grab_pin.mp3",
        "prompt": "Realistic close up foley of grabbing and pinning down a struggling large bird by the neck feathers, rough vigorous wing rustling, heavy cloth and feather clinch wrestle grip, no clicking, no beeps, no music",
        "duration": 3.0,
        "target_s": 0.56,
        "min_s": 0.40,
        "mode": "continuous",
        "reverb_wet": 0.05,
        "fade_out_ms": 65.0,
        "engine": "tangoflux",
    },
    {
        "key": "break",
        "filename": "sfx_pit_break.mp3",
        "prompt": "Quick tearing cloth escape burst followed immediately by a single explosive heavy heavyweight kick thumping solid torso ribs hard, isolated dry studio impact sound effect, no drum beat, no metal, no music",
        "duration": 2.0,
        "target_s": 0.58,
        "min_s": 0.42,
        "mode": "impact",
        "reverb_wet": 0.07,
        "fade_out_ms": 75.0,
        "engine": "tangoflux",
    },
    {
        "key": "groggy",
        "filename": "sfx_pit_groggy.mp3",
        "prompt": "Dazed stunned fighter staggering and stumbling clumsily on loose dirt floor with muffled deep slow heartbeat and heavy dizzy breathing, realistic movie combat stun foley, no beeps, no sine wave, no ringing, no music",
        "duration": 3.0,
        "target_s": 1.65,
        "min_s": 1.40,
        "mode": "continuous",
        "reverb_wet": 0.06,
        "fade_in_ms": 20.0,
        "fade_out_ms": 200.0,
        "engine": "tangoflux",
    },
    {
        "key": "crowd_gasp",
        "filename": "sfx_pit_crowd_gasp.mp3",
        "prompt": "Large packed boxing and MMA stadium crowd suddenly gasping loudly in shock shouting ohhh in unison right after a brutal knockout punch, dramatic sports arena shock reaction, no clapping, no applause, no music",
        "duration": 3.0,
        "target_s": 1.60,
        "min_s": 1.30,
        "mode": "continuous",
        "reverb_wet": 0.04,
        "fade_in_ms": 20.0,
        "fade_out_ms": 240.0,
        "engine": "tangoflux",
        "dual_compare": True,  # AudioGen 백업 테이크도 참고용 캐시 저장
    },
]

BATCH2_SPECS = [
    {
        "key": "hit_wing",
        "filename": "sfx_pit_hit_wing.mp3",
        "prompt": "Powerful loud hawk wings flapping three heavy wind gusts followed by a deep solid body slam thud on packed dirt, isolated dry foley sound effect, no crowing, no chirping, no music",
        "duration": 3.0,
        "target_s": 0.72,
        "min_s": 0.52,
        "mode": "continuous",
        "reverb_wet": 0.07,
        "fade_out_ms": 70.0,
        "engine": "tangoflux",
    },
    {
        "key": "hit_gen",
        "filename": "sfx_pit_hit_gen.mp3",
        "prompt": "Single crisp heavy leather boxing glove punch slapping and thumping solidly against flesh and ribs, dry close up studio foley sound effect, no crowd, no music",
        "duration": 2.0,
        "target_s": 0.36,
        "min_s": 0.24,
        "mode": "impact",
        "reverb_wet": 0.05,
        "fade_out_ms": 50.0,
        "engine": "tangoflux",
    },
    {
        "key": "hit_crit",
        "filename": "sfx_pit_hit_crit.mp3",
        "prompt": "Single devastating heavyweight knockout punch crunching bone and flesh with massive deep sub bass body thud, isolated dry studio impact foley, no crowd, no music",
        "duration": 2.0,
        "target_s": 0.56,
        "min_s": 0.42,
        "mode": "impact",
        "reverb_wet": 0.08,
        "fade_out_ms": 80.0,
        "engine": "tangoflux",
    },
    {
        "key": "guard",
        "filename": "sfx_pit_guard.mp3",
        "prompt": "Single dull heavy punch absorbed by thick leather punching pad and dense pillow stuffing, muffled cushioned thump with soft dry rustle, isolated studio foley, no chime, no metal, no music",
        "duration": 2.0,
        "target_s": 0.40,
        "min_s": 0.28,
        "mode": "impact",
        "reverb_wet": 0.05,
        "fade_out_ms": 60.0,
        "engine": "tangoflux",
    },
    {
        "key": "dodge",
        "filename": "sfx_pit_dodge.mp3",
        "prompt": "Single fast agile air whoosh sweeping past close microphone followed by light gravel foot shuffle, isolated dry studio foley, no impact hit, no music",
        "duration": 2.0,
        "target_s": 0.30,
        "min_s": 0.22,
        "mode": "impact",
        "reverb_wet": 0.04,
        "fade_out_ms": 45.0,
        "target_peak": 0.65,
        "engine": "tangoflux",
    },
    {
        "key": "miss",
        "filename": "sfx_pit_miss.mp3",
        "prompt": "Single short sharp empty air whoosh punch swing missing target, fast light wind swish, dry studio foley sound effect, no hit, no music",
        "duration": 2.0,
        "target_s": 0.22,
        "min_s": 0.16,
        "mode": "impact",
        "reverb_wet": 0.03,
        "fade_out_ms": 40.0,
        "engine": "tangoflux",
    },
    {
        "key": "slam",
        "filename": "sfx_pit_slam.mp3",
        "prompt": "Heavy wrestling body slam crashing violently onto hard packed dirt and loose gravel ground, massive deep thud followed by spraying dirt and small rocks, isolated foley, no explosion, no music",
        "duration": 3.0,
        "target_s": 0.78,
        "min_s": 0.58,
        "mode": "impact",
        "reverb_wet": 0.09,
        "fade_out_ms": 110.0,
        "engine": "tangoflux",
    },
    {
        "key": "grab_miss",
        "filename": "sfx_pit_grab_miss.mp3",
        "prompt": "Single short quick cloth rustle hand lunge snatching empty air and missing, subtle wind brush, isolated dry studio foley, no clicking, no music",
        "duration": 2.0,
        "target_s": 0.26,
        "min_s": 0.19,
        "mode": "impact",
        "reverb_wet": 0.04,
        "fade_out_ms": 45.0,
        "engine": "tangoflux",
    },
    {
        "key": "grab_escape",
        "filename": "sfx_pit_grab_escape.mp3",
        "prompt": "Sudden forceful burst of wing flaps and cloth ripping free with rapid spinning air swoosh, isolated dry foley sound effect, no chirping, no music",
        "duration": 2.0,
        "target_s": 0.42,
        "min_s": 0.30,
        "mode": "impact",
        "reverb_wet": 0.05,
        "fade_out_ms": 55.0,
        "engine": "tangoflux",
    },
    {
        "key": "knockdown",
        "filename": "sfx_pit_knockdown.mp3",
        "prompt": "Heavy limp human body falling and slamming dead weight onto sandy dirt ground, dull heavy thud and sand slide tail, isolated dry studio foley, no music",
        "duration": 3.0,
        "target_s": 0.62,
        "min_s": 0.46,
        "mode": "impact",
        "reverb_wet": 0.08,
        "fade_out_ms": 95.0,
        "engine": "tangoflux",
    },
    {
        "key": "wall_impact",
        "filename": "sfx_pit_wall_impact.mp3",
        "prompt": "Heavy body crashing sideways into hollow wooden plank wall and wire mesh fence, solid wood board thump followed immediately by chain link wire rattle, isolated foley, no music",
        "duration": 3.0,
        "target_s": 0.62,
        "min_s": 0.45,
        "mode": "impact",
        "reverb_wet": 0.08,
        "fade_out_ms": 90.0,
        "engine": "tangoflux",
    },
]


def _resample_stereo_pitch(x: np.ndarray, semitones: float) -> np.ndarray:
    if abs(semitones) < 0.05 or len(x) < 32:
        return x
    ratio = 2.0 ** (semitones / 12.0)
    new_len = max(16, int(len(x) / ratio))
    xp = np.linspace(0.0, 1.0, len(x))
    fp = np.linspace(0.0, 1.0, new_len)
    if x.ndim == 1:
        return np.interp(fp, xp, x).astype(np.float32)
    return np.column_stack([np.interp(fp, xp, x[:, 0]), np.interp(fp, xp, x[:, 1])]).astype(np.float32)


def process_ai_spec(spec: dict, regen_set: set, audiogen_set: set):
    key = spec["key"]
    regen = ("all" in regen_set) or (key in regen_set)
    engine = "audiogen" if (key in audiogen_set) else spec.get("engine", "tangoflux")

    raw = fetch_ai_raw(key, spec["prompt"], duration=spec["duration"], engine=engine, regen=regen)
    if spec.get("dual_compare"):
        ag_path = os.path.join(AI_RAW_DIR, f"{key}_audiogen.wav")
        if regen or not os.path.exists(ag_path):
            try:
                ag_raw = fetch_ai_raw(
                    key,
                    spec["prompt"],
                    duration=max(5.0, spec["duration"]),
                    engine="audiogen",
                    regen=regen,
                    suffix="_audiogen",
                )
                # AudioGen 참고 비교용 MP3도 source_cache에 보관
                ag_seg = extract_best_segment(
                    ag_raw,
                    target_s=spec["target_s"],
                    min_s=spec["min_s"],
                    mode=spec["mode"],
                    fade_in_ms=spec.get("fade_in_ms", 2.0),
                    fade_out_ms=spec.get("fade_out_ms", 65.0),
                    label=f"{key}_audiogen",
                )
                save_mp3(os.path.join(AI_RAW_DIR, f"{key}_audiogen_preview.mp3"), arena_reverb(ag_seg, wet=spec["reverb_wet"]))
            except Exception as e:
                print(f"    [AudioGen 비교 생성 스킵] {e}")

    seg = extract_best_segment(
        raw,
        target_s=spec["target_s"],
        min_s=spec["min_s"],
        mode=spec["mode"],
        pre_ms=10.0,
        fade_in_ms=spec.get("fade_in_ms", 2.0),
        fade_out_ms=spec.get("fade_out_ms", 65.0),
        label=key,
    )
    if spec.get("triple_peck"):
        # 1타 AI 실사 타격 원음을 저·중역 바디 보존 상태로 0 / 105 / 210ms 자연 3연타 조합
        offsets_ms = [0, 105, 210]
        pitches = [0.0, 1.6, 3.2]
        gains = [0.92, 0.96, 1.05]
        pans = [-0.14, 0.14, 0.0]
        total_len = int(0.52 * SAMPLE_RATE)
        mix = np.zeros((total_len, 2), dtype=np.float32)
        for off_ms, pt, g, pn in zip(offsets_ms, pitches, gains, pans):
            hit = fade_io(_resample_stereo_pitch(seg, pt), fade_in_ms=2.0, fade_out_ms=35.0)
            mono_h = hit.mean(axis=1) if hit.ndim == 2 else hit
            st_h = make_stereo_wide(mono_h, pan=pn)
            idx = int(off_ms * SAMPLE_RATE / 1000.0)
            take = min(len(st_h), total_len - idx)
            if take > 0:
                mix[idx : idx + take] += st_h[:take] * g
        seg = trim_tail(mix, thresh_ratio=0.01, pad_ms=35.0)
    out = arena_reverb(seg, wet=spec.get("reverb_wet", 0.06), tail_s=0.22, pre_delay_ms=10.0)
    out = fade_io(out, fade_in_ms=spec.get("fade_in_ms", 2.0), fade_out_ms=spec.get("fade_out_ms", 60.0))
    save_mp3(os.path.join(SFX_DIR, spec["filename"]), out, target_peak=spec.get("target_peak", TARGET_PEAK))
    print(f"  [저장 완료] {spec['filename']}")


# ---------------------------------------------------------------------------
# 승자 아나운서 PA 보이스 2종 (KO 승 / 판정 승) — 1R~3R과 동일 성우·PA 체인
# ---------------------------------------------------------------------------
def build_winner_pa_voices(regen_set: set):
    print("=== [승자 PA 아나운서 보이스 2종 생성 (KO 승 / 판정 승)] ===")

    async def _gen():
        jobs = [
            {
                "key": "win_ko",
                "out": "sfx_pit_win_ko.mp3",
                "parts": [
                    ("win_ko_p1.mp3", "KNOCKOUT!!", "en-US-GuyNeural", "+18%", "+4Hz", "hype"),
                    ("win_ko_p2.mp3", "It's all over! We have a champion!", "en-US-ChristopherNeural", "+8%", "+2Hz", "lead"),
                ],
                "gap_ms": 180,
            },
            {
                "key": "win_decision",
                "out": "sfx_pit_win_decision.mp3",
                "parts": [
                    ("win_dec_p1.mp3", "By unanimous decision!", "en-US-ChristopherNeural", "+6%", "+1Hz", "lead"),
                    ("win_dec_p2.mp3", "WE HAVE A WINNER!!", "en-US-GuyNeural", "+18%", "+4Hz", "hype"),
                ],
                "gap_ms": 180,
            },
        ]
        for job in jobs:
            regen = ("all" in regen_set) or (job["key"] in regen_set)
            clips = []
            for raw_fn, text, voice, rate, pitch, style in job["parts"]:
                rp = os.path.join(VOICE_RAW_DIR, raw_fn)
                if regen or not os.path.exists(rp):
                    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(rp)
                v = trim_tail(trim_onset(load_audio(rp, 1), 0.04, 10.0), 0.02, 40.0)
                if style == "hype":
                    vp = norm_peak(
                        warm_saturate(peaking_eq(peaking_eq(hpf(v, 140.0), 3200, 1.0, 5.5), 220, 1.0, 3.0), 1.55),
                        1.02,
                    )
                else:
                    vp = norm_peak(
                        warm_saturate(peaking_eq(hpf(v, 130.0), 2800, 1.1, 4.5), 1.35),
                        0.92,
                    )
                clips.append(vp)
            gap = np.zeros(int(job["gap_ms"] * SAMPLE_RATE / 1000.0), dtype=np.float32)
            combined = np.concatenate([clips[0], gap, clips[1]])
            pa_out = arena_reverb(make_stereo_wide(combined, 0.0, width_ms=4.0), wet=0.22, tail_s=0.45, pre_delay_ms=22.0)
            save_mp3(os.path.join(SFX_DIR, job["out"]), fade_io(pa_out, 3.0, 140.0), target_peak=TARGET_PEAK)
            print(f"  [승자 보이스 저장] {job['out']} ({len(pa_out)/SAMPLE_RATE:.2f}s)")

    asyncio.run(_gen())


# ---------------------------------------------------------------------------
# 구버전 우승 닭 울음 제거 & 1R 실전 데모 재합성
# ---------------------------------------------------------------------------
def remove_deprecated_assets():
    for target_dir in (SFX_DIR, DOCS_SFX_DIR):
        p = os.path.join(target_dir, "sfx_pit_rooster_crow.mp3")
        if os.path.exists(p):
            os.remove(p)
            print(f"  [구버전 삭제] {p}")


def build_round1_demo():
    print("=== [1R 실전 시뮬레이션 데모 (38.0초, v3.0 AI 폴리 + KO승 콜) 재합성] ===")
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
    add_sfx(4.50, "sfx_pit_hit_poke.mp3", gain=1.02, pan=-0.28, duck_db=-3.5, duck_hold=0.28)
    add_sfx(5.20, "sfx_pit_guard.mp3", gain=1.02, pan=0.28, duck_db=-3.5, duck_hold=0.22)
    add_sfx(6.55, "sfx_pit_hit_wing.mp3", gain=1.02, pan=0.25, duck_db=-4.2, duck_hold=0.40)
    add_sfx(7.55, "sfx_pit_guard_gen.mp3", gain=1.02, pan=-0.25, duck_db=-4.5, duck_hold=0.28)
    add_sfx(8.15, "sfx_pit_dodge.mp3", gain=0.98, pan=-0.35, duck_db=-2.5, duck_hold=0.20)
    add_sfx(8.65, "sfx_pit_hit_spur.mp3", gain=1.05, pan=-0.20, duck_db=-4.5, duck_hold=0.30)
    add_sfx(9.75, "sfx_pit_miss.mp3", gain=0.95, pan=0.30)
    add_sfx(10.30, "sfx_pit_hit_gen.mp3", gain=1.00, pan=-0.20, duck_db=-3.8, duck_hold=0.25)

    # 스페셜 공방 1: [특방 F34] 잡기 체결 -> 회전 탈출 -> 쌍발 카운터 -> 외벽 철망
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

    # 스페셜 공방 2: [특공 F33] 머리 잡아 바닥 찍기 -> 슬로우 -> 다운 -> KO 3연타 벨 + 환호 + KO 승 PA 콜
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
    save_mp3(out_path, master_mix, target_peak=TARGET_PEAK)
    print(f"  [완료] v3.0 1R 시뮬레이션 데모 저장 -> {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Rumble Pit v3.0 AI 실사 폴리 + 승자 PA 보이스 생성기")
    parser.add_argument("--batch", choices=["1", "2", "all"], default="all", help="실행할 배치 (1: 핵심 7종+승자2종, 2: 나머지 11종+정리+데모, all: 전체)")
    parser.add_argument("--regen", default="", help="쉼표 구분 강제 재생성 키 목록 (예: hit_poke,crowd_gasp 또는 all)")
    parser.add_argument("--audiogen", default="", help="AudioGen 엔진 우선 사용 키 목록 (예: crowd_gasp)")
    parser.add_argument("--only", default="", help="지정한 키만 생성 및 마스터링 (예: hit_poke,guard_gen)")
    parser.add_argument("--demo-only", action="store_true", help="1R 데모만 재합성")
    args = parser.parse_args()

    regen_set = {x.strip() for x in args.regen.split(",") if x.strip()}
    audiogen_set = {x.strip() for x in args.audiogen.split(",") if x.strip()}
    only_set = {x.strip() for x in args.only.split(",") if x.strip()}

    if args.demo_only:
        remove_deprecated_assets()
        build_round1_demo()
        return

    if only_set:
        all_specs = BATCH1_SPECS + BATCH2_SPECS
        for sp in all_specs:
            if sp["key"] in only_set:
                process_ai_spec(sp, regen_set, audiogen_set)
        if only_set & {"win_ko", "win_decision"}:
            build_winner_pa_voices(regen_set)
        return

    if args.batch in ("1", "all"):
        print("=== [Batch 1] 유저 지적 최우선 7종 AI 폴리 생성 시작 ===")
        for sp in BATCH1_SPECS:
            process_ai_spec(sp, regen_set, audiogen_set)
        build_winner_pa_voices(regen_set)

    if args.batch in ("2", "all"):
        print("=== [Batch 2] 나머지 전투/스페셜/상태 11종 AI 폴리 생성 시작 ===")
        for sp in BATCH2_SPECS:
            process_ai_spec(sp, regen_set, audiogen_set)
        remove_deprecated_assets()
        kept = [
            "sfx_pit_round1_start.mp3",
            "sfx_pit_round2_start.mp3",
            "sfx_pit_round3_start.mp3",
            "sfx_pit_bell_single.mp3",
            "sfx_pit_ko_bell.mp3",
            "sfx_pit_crowd_roar.mp3",
            "sfx_pit_last_stand.mp3",
            "sfx_pit_ko_slow.mp3",
        ]
        missing_kept = [f for f in kept if not os.path.exists(os.path.join(SFX_DIR, f))]
        print(f"  [기존 우수 실녹음 유지 확인] {len(kept)-len(missing_kept)}/{len(kept)}종 정상 (누락: {missing_kept})")
        build_round1_demo()


if __name__ == "__main__":
    main()
