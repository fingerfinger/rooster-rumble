#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROOSTER RUMBLE - Rumble Pit v4.0 스튜디오 무손실 실녹음 원음 확보 및 멀티-테이크 스캐너
- Mixkit Free Commercial Lossless WAV (403 시 -preview.mp3 폴백)
- Archive.org USC Hollywood Red Library CC0 1.0 Lossless FLAC
- 전 파일 디코딩 무결성 및 개별 타격/군중 버스트 구간 자동 스캔
"""

import os
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

import miniaudio
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDIO_DIR = os.path.join(BASE_DIR, "tools", "source_cache", "pit_studio_v4")
MIXKIT_DIR = os.path.join(STUDIO_DIR, "mixkit")
RED_DIR = os.path.join(STUDIO_DIR, "red_library")
SAMPLE_RATE = 44100

os.makedirs(MIXKIT_DIR, exist_ok=True)
os.makedirs(RED_DIR, exist_ok=True)

MIXKIT_IDS = [
    # 타격 / 복싱 / 격투
    (2198, "strong_punches_body"),
    (2047, "martial_arts_fast_punch"),
    (2151, "soft_quick_punch"),
    (2149, "hard_quick_punch"),
    (2165, "short_punch_face"),
    (2051, "boxing_punch"),
    (2053, "punch_boxing_gloves"),
    (2055, "boxer_getting_hit"),
    (2050, "martial_arts_kick"),
    (2161, "air_in_hit"),
    (2072, "short_slap"),
    (2155, "impact_strong_punch"),
    (2152, "quick_knife_slice_cut"),
    (2141, "punch_through_air"),
    (2148, "quick_hit_through_air"),
    # 뼈 / 나무 / 철망 / 진흙 / 천 / 스우시 / 슬로우
    (1551, "bone_breaking_echo"),
    (2937, "twig_breaking"),
    (190, "wood_hard_hit"),
    (389, "metal_grill_quick_hit"),
    (753, "heavy_fall_mud"),
    (3167, "cloth_slide_out"),
    (1489, "air_woosh"),
    (1490, "fast_whoosh_transition"),
    (1491, "arrow_whoosh"),
    (1492, "cinematic_whoosh_fast"),
    (1143, "cinematic_whoosh_deep_impact"),
    # 심장박동 / 호흡 / 경기장 환호
    (495, "fast_heartbeat"),
    (559, "slow_heartbeat"),
    (2240, "strong_breathing"),
    (1914, "male_effort_breathing"),
    (462, "huge_crowd_cheering_victory"),
    (460, "stadium_joy_shouting_crowd"),
]

RED_LIBRARY_FILES = [
    ("Red_Library_Fights", "R09-56-Rustling Fight.flac"),
    ("Red_Library_Fights", "R19-01-Fight Scuffle.flac"),
    ("Red_Library_Fights", "R09-79-Fall on Gravel.flac"),
    ("Red_Library_Fights", "R15-19-Muffled Body Fall.flac"),
    ("Red_Library_Fights", "R15-20-Padded Hits.flac"),
    ("Red_Library_Fights", "R17-40-Padded Punches.flac"),
    ("Red_Library_Fights", "R19-27-Big Fight Punches.flac"),
    ("Red_Library_Fights", "R15-18-Shot or Hit with Debris.flac"),
    ("Red_Library_Fights", "R19-06-Fist fight on Dirt.flac"),
    ("Red_Library_Fights", "R15-23-Short, Quick Hits.flac"),
    ("Red_Library_Impacts", "R28-55-Thumps on Large Hollow Wooden Surface.flac"),
    ("Red_Library_Impacts", "R28-56-Sand Bags Dropped onto Wood Floor.flac"),
    ("Red_Library_Animals_Birds", "R21-40b-Bird Wings Flapping.flac"),
    ("Red_Library_Crowds_Indoor_2", "R27-20-Small Crowd Gasps.flac"),
    ("Red_Library_Crowds_Indoor_2", "R25-05-Crowd Murmurs and Gasps in Courtroom.flac"),
    ("Red_Library_Crowds_Indoor_2", "R08-54-Large Crowd Cheering at Event.flac"),
    ("Red_Library_Crowds_Outdoor", "R28-29-Large Crowd Quiet, Then Big Reaction.flac"),
    ("Red_Library_Crowds_Indoor_1", "R25-06-Interior Crowd Reactions.flac"),
    ("Red_Library_Crowds_Indoor_1", "R25-08-Crowd Reaction.flac"),
    ("Red_Library_Crowds_Sports", "R07-38-Witnessing a Fight.flac"),
    ("Red_Library_Crowds_Sports", "R07-06-Boxing Match.flac"),
]


def _download_bytes(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def download_mixkit(sid: int, slug: str) -> tuple[str, str]:
    wav_path = os.path.join(MIXKIT_DIR, f"{sid}_{slug}.wav")
    mp3_path = os.path.join(MIXKIT_DIR, f"{sid}_{slug}.mp3")
    if os.path.exists(wav_path) and os.path.getsize(wav_path) > 1000:
        return f"mixkit/{sid}_{slug}.wav", "cached"
    if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1000:
        return f"mixkit/{sid}_{slug}.mp3", "cached"

    wav_url = f"https://assets.mixkit.co/active_storage/sfx/{sid}/{sid}.wav"
    mp3_url = f"https://assets.mixkit.co/active_storage/sfx/{sid}/{sid}-preview.mp3"
    try:
        data = _download_bytes(wav_url)
        with open(wav_path, "wb") as f:
            f.write(data)
        return f"mixkit/{sid}_{slug}.wav", f"WAV ({len(data)//1024} KB)"
    except urllib.error.HTTPError as e:
        if e.code in (403, 404):
            data = _download_bytes(mp3_url)
            with open(mp3_path, "wb") as f:
                f.write(data)
            return f"mixkit/{sid}_{slug}.mp3", f"MP3 fallback ({len(data)//1024} KB)"
        raise


def download_red(ident: str, fname: str) -> tuple[str, str]:
    safe_name = f"{ident}__{fname}"
    out_path = os.path.join(RED_DIR, safe_name)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        return f"red_library/{safe_name}", "cached"
    url = f"https://archive.org/download/{ident}/{urllib.parse.quote(fname)}"
    data = _download_bytes(url, timeout=45)
    with open(out_path, "wb") as f:
        f.write(data)
    return f"red_library/{safe_name}", f"FLAC ({len(data)//1024} KB)"


def scan_bursts(full_path: str, gap_ms: float = 180.0, thresh_ratio: float = 0.14):
    with open(full_path, "rb") as f:
        dec = miniaudio.decode(
            f.read(),
            output_format=miniaudio.SampleFormat.FLOAT32,
            nchannels=1,
            sample_rate=SAMPLE_RATE,
        )
    y = np.frombuffer(dec.samples, dtype=np.float32)
    dur_s = len(y) / SAMPLE_RATE
    hop = int(0.015 * SAMPLE_RATE)  # 15ms frames
    n_f = max(1, len(y) // hop)
    rms = np.array([np.sqrt(np.mean(y[i * hop : (i + 1) * hop] ** 2)) for i in range(n_f)], dtype=np.float32)
    pk = float(np.max(rms)) if len(rms) else 0.0
    if pk < 1e-6:
        return dur_s, []

    active = rms >= max(pk * thresh_ratio, 0.008)
    gap_f = max(1, int(gap_ms / 15.0))
    # Close small silent gaps < gap_f
    closed = active.copy()
    i = 0
    while i < n_f:
        if not closed[i]:
            j = i
            while j < n_f and not closed[j]:
                j += 1
            if i > 0 and j < n_f and (j - i) <= gap_f:
                closed[i:j] = True
            i = j
        else:
            i += 1

    bursts = []
    i = 0
    while i < n_f:
        if closed[i]:
            j = i
            while j < n_f and closed[j]:
                j += 1
            s_t = max(0.0, i * 0.015 - 0.015)
            e_t = min(dur_s, j * 0.015 + 0.030)
            seg = y[int(s_t * SAMPLE_RATE) : int(e_t * SAMPLE_RATE)]
            if len(seg) > int(0.05 * SAMPLE_RATE):
                seg_pk = 20 * np.log10(float(np.max(np.abs(seg))) + 1e-9)
                seg_rms = 20 * np.log10(float(np.sqrt(np.mean(seg ** 2))) + 1e-9)
                bursts.append((round(s_t, 2), round(e_t, 2), round(e_t - s_t, 2), round(seg_pk, 1), round(seg_rms, 1)))
            i = j
        else:
            i += 1
    return dur_s, bursts


def main():
    print(f"=== [v4.0 스튜디오 원음 확보 시작] Mixkit {len(MIXKIT_IDS)}종 + Red Library {len(RED_LIBRARY_FILES)}종 ===")
    tasks = []
    results = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for sid, slug in MIXKIT_IDS:
            tasks.append(("mixkit", f"{sid}_{slug}", pool.submit(download_mixkit, sid, slug)))
        for ident, fname in RED_LIBRARY_FILES:
            tasks.append(("red", f"{ident}/{fname}", pool.submit(download_red, ident, fname)))

        errors = []
        for kind, label, fut in tasks:
            try:
                rel, status = fut.result()
                results.append(rel)
                print(f"  [OK] {rel:65s} | {status}")
            except Exception as e:
                errors.append((label, str(e)))
                print(f"  [ERR] {label}: {e}")

    print(f"\n다운로드 결과: 성공 {len(results)}/{len(tasks)} | 실패 {len(errors)}")
    if errors:
        for lbl, err in errors:
            print(f"  FAIL: {lbl} -> {err}")

    print("\n=== [디코딩 검증 & 멀티-테이크 버스트 스캔] ===")
    for rel in sorted(results):
        full = os.path.join(STUDIO_DIR, rel)
        try:
            dur, bursts = scan_bursts(full)
            b_str = ", ".join([f"[{i}:{s}..{e}s({d}s,pk{p},rms{r})]" for i, (s, e, d, p, r) in enumerate(bursts[:10])])
            if len(bursts) > 10:
                b_str += f" ... (+{len(bursts)-10} more)"
            print(f"  {rel:65s} | total={dur:.2f}s | bursts={len(bursts)}: {b_str}")
        except Exception as e:
            print(f"  [DECODE FAIL] {rel}: {e}")


if __name__ == "__main__":
    main()
