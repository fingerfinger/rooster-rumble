import os
import shutil

LOCAL_AUDIO_DIR = os.path.abspath(r"assets/audio/race")
LOCAL_ROOT = os.path.abspath(".")

SHARE_DOC_DIR = os.path.abspath(r"D:\OneDrive\업무_진행\C\ROOSTER RUMBLE_share\ROOSTER RUMBLE_Derby Race\01_Documents")
SHARE_AUDIO_DIR = os.path.join(SHARE_DOC_DIR, "assets", "audio", "race")

print(f"=== [보이스 배포 시작] ===")
print(f"Local audio: {LOCAL_AUDIO_DIR}")
print(f"Share audio: {SHARE_AUDIO_DIR}")

# 1. voice/ (신규 27개 에셋 전수 복사)
share_voice = os.path.join(SHARE_AUDIO_DIR, "voice")
os.makedirs(share_voice, exist_ok=True)
local_voice = os.path.join(LOCAL_AUDIO_DIR, "voice")
copied_voice = 0
for f in os.listdir(local_voice):
    if f.endswith(".mp3"):
        shutil.copy2(os.path.join(local_voice, f), os.path.join(share_voice, f))
        copied_voice += 1
print(f"[1] 공식 보이스 복사 완료: {copied_voice}개 -> {share_voice}")

# 2. voice_backup_old/ (구버전 보이스 백업 복사)
share_backup = os.path.join(SHARE_AUDIO_DIR, "voice_backup_old")
os.makedirs(share_backup, exist_ok=True)
local_backup = os.path.join(LOCAL_AUDIO_DIR, "voice_backup_old")
copied_backup = 0
if os.path.exists(local_backup):
    for f in os.listdir(local_backup):
        if f.endswith(".mp3"):
            shutil.copy2(os.path.join(local_backup, f), os.path.join(share_backup, f))
            copied_backup += 1
print(f"[2] 구버전 보이스 백업 복사 완료: {copied_backup}개 -> {share_backup}")

# 3. voice_261022/ (신규 분할 58종 및 타입 서브폴더 복사)
share_261022 = os.path.join(SHARE_AUDIO_DIR, "voice_261022")
local_261022 = os.path.join(LOCAL_AUDIO_DIR, "voice_261022")
if os.path.exists(share_261022):
    shutil.rmtree(share_261022)
shutil.copytree(local_261022, share_261022)
count_261022 = sum(len(files) for _, _, files in os.walk(share_261022))
print(f"[3] voice_261022 전체 복사 완료: {count_261022}개 파일 -> {share_261022}")

# 4. demo/ (재합성 데모 3종 복사)
share_demo = os.path.join(SHARE_AUDIO_DIR, "demo")
os.makedirs(share_demo, exist_ok=True)
local_demo = os.path.join(LOCAL_AUDIO_DIR, "demo")
copied_demo = 0
for f in os.listdir(local_demo):
    if f.endswith(".mp3"):
        shutil.copy2(os.path.join(local_demo, f), os.path.join(share_demo, f))
        copied_demo += 1
print(f"[4] 데모 트랙 복사 완료: {copied_demo}개 -> {share_demo}")

# 5. HTML 청음보드 및 사운드보드 동기화
# 5-1) 01_Documents 직하: Derby_Race_보이스_261022_청음보드.html
shutil.copy2(
    os.path.join(LOCAL_ROOT, "Derby_Race_보이스_261022_청음보드.html"),
    os.path.join(SHARE_DOC_DIR, "Derby_Race_보이스_261022_청음보드.html")
)
print(f"[5-1] 01_Documents 직하 청음보드 복사 완료")

# 5-2) assets/audio/race 직하: 청음보드 (상대경로 voice_261022/ 로 변환된 버전)
with open(os.path.join(LOCAL_ROOT, "Derby_Race_보이스_261022_청음보드.html"), "r", encoding="utf-8") as f:
    board_html = f.read()
board_audio_dir_version = board_html.replace("assets/audio/race/voice_261022/", "voice_261022/")
with open(os.path.join(SHARE_AUDIO_DIR, "Derby_Race_보이스_261022_청음보드.html"), "w", encoding="utf-8") as f:
    f.write(board_audio_dir_version)
with open(os.path.join(LOCAL_AUDIO_DIR, "Derby_Race_보이스_261022_청음보드.html"), "w", encoding="utf-8") as f:
    f.write(board_audio_dir_version)
print(f"[5-2] assets/audio/race 내 청음보드 복사 완료")

# 5-3) 사운드보드 동기화
shutil.copy2(
    os.path.join(LOCAL_ROOT, "Derby_Race_사운드보드.html"),
    os.path.join(SHARE_DOC_DIR, "ROOSTER_RUMBLE_Derby_Race_사운드보드.html")
)
shutil.copy2(
    os.path.join(LOCAL_AUDIO_DIR, "derby_race_soundboard.html"),
    os.path.join(SHARE_AUDIO_DIR, "derby_race_soundboard.html")
)
print(f"[5-3] 사운드보드 동기화 완료")

print("\n=== [배포 완료] 모든 에셋 동기화 성공! ===")
