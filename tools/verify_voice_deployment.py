import os

LOCAL_RACE = os.path.abspath(r"assets/audio/race")
SHARE_RACE = os.path.abspath(r"D:\OneDrive\업무_진행\C\ROOSTER RUMBLE_share\ROOSTER RUMBLE_Derby Race\01_Documents\assets\audio\race")
SHARE_DOCS = os.path.abspath(r"D:\OneDrive\업무_진행\C\ROOSTER RUMBLE_share\ROOSTER RUMBLE_Derby Race\01_Documents")

print("=== [배포 검증 시작] ===")

# 1. voice/ 검증
l_v = os.listdir(os.path.join(LOCAL_RACE, "voice"))
s_v = os.listdir(os.path.join(SHARE_RACE, "voice"))
print(f"1. voice/ (신규 공식 보이스 27종): Local={len(l_v)}, Share={len(s_v)} -> {'MATCH' if len(l_v) == len(s_v) and len(s_v) == 27 else 'MISMATCH'}")

# 2. voice_backup_old/ 검증
l_b = os.listdir(os.path.join(LOCAL_RACE, "voice_backup_old"))
s_b = os.listdir(os.path.join(SHARE_RACE, "voice_backup_old"))
print(f"2. voice_backup_old/ (구버전 보이스 27종 백업): Local={len(l_b)}, Share={len(s_b)} -> {'MATCH' if len(l_b) == len(s_b) and len(s_b) == 27 else 'MISMATCH'}")

# 3. voice_261022/ 검증
l_26 = sum(len(f) for _, _, f in os.walk(os.path.join(LOCAL_RACE, "voice_261022")))
s_26 = sum(len(f) for _, _, f in os.walk(os.path.join(SHARE_RACE, "voice_261022")))
print(f"3. voice_261022/ (전체 분할 보이스): Local={l_26}, Share={s_26} -> {'MATCH' if l_26 == s_26 and s_26 >= 58 else 'MISMATCH'}")

# 4. demo/ 검증
l_d = os.listdir(os.path.join(LOCAL_RACE, "demo"))
s_d = os.listdir(os.path.join(SHARE_RACE, "demo"))
print(f"4. demo/ (신규 보이스 재합성 트랙 3종): Local={len(l_d)}, Share={len(s_d)} -> {'MATCH' if len(l_d) == len(s_d) and len(s_d) == 3 else 'MISMATCH'}")

# 5. HTML 청음보드 및 사운드보드 검증
files_to_check = [
    os.path.join(SHARE_DOCS, "Derby_Race_보이스_261022_청음보드.html"),
    os.path.join(SHARE_DOCS, "ROOSTER_RUMBLE_Derby_Race_사운드보드.html"),
    os.path.join(SHARE_RACE, "Derby_Race_보이스_261022_청음보드.html"),
    os.path.join(SHARE_RACE, "derby_race_soundboard.html"),
]
all_html_ok = True
for f in files_to_check:
    exists = os.path.exists(f)
    size = os.path.getsize(f) if exists else 0
    print(f" - {os.path.basename(f)} ({os.path.dirname(f)[-20:]}): exists={exists}, size={size:,} bytes")
    if not exists or size == 0:
        all_html_ok = False

print(f"\nHTML 사운드보드/청음보드 배포 상태: {'ALL OK' if all_html_ok else 'FAILED'}")
print("=== [배포 검증 완료] ===")
