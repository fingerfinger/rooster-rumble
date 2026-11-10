#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROOSTER RUMBLE 웹보드 스마트 동기화 및 마크다운 내장 뷰어 지원 시스템 (v2.2)
- 하부 폴더 구조 자동 배치 (docs/common/core/, docs/race/docs/ 등)
- 마크다운(.md) 및 텍스트(.txt, .csv) 본문을 메타데이터에 인라인 임베딩하여
  로컬 file:// 환경의 CORS 보안 차단 문제 원천 해결 및 초고속 렌더링 지원
- HTML 상대경로(assets/ -> ../../assets/) 깊이별 자동 보정
"""

import os
import sys
import json
import shutil
import datetime
import re
from pathlib import Path

# 콘솔 UTF-8 입출력 지원
if sys.platform.startswith('win'):
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except Exception:
        pass

def format_size(bytes_size):
    """파일 크기를 사람이 읽기 좋은 형식(KB, MB)으로 변환"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"

def should_copy(src_path, dst_path):
    """대상 파일이 없거나 크기/수정시간이 1초 이상 차이날 때만 복사"""
    if not dst_path.exists():
        return True
    src_stat = src_path.stat()
    dst_stat = dst_path.stat()
    if src_stat.st_size != dst_stat.st_size:
        return True
    if abs(src_stat.st_mtime - dst_stat.st_mtime) > 1.0:
        return True
    return False

def copy_with_path_fix(src_path, dst_path, docs_dir):
    """HTML 파일은 상대경로 자동 보정 복사, 일반 파일은 메타데이터 보존 복사"""
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    
    rel_parts = dst_path.relative_to(docs_dir).parts
    depth = len(rel_parts) - 1

    if src_path.suffix.lower() in [".html", ".htm"] and depth > 0:
        prefix = "../" * depth
        try:
            with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            content_fixed = re.sub(r'(["\'\(])assets/', rf'\1{prefix}assets/', content)

            with open(dst_path, "w", encoding="utf-8") as f:
                f.write(content_fixed)
            shutil.copystat(src_path, dst_path)
            return
        except Exception:
            pass

    shutil.copy2(src_path, dst_path)

def read_text_content(file_path, max_len=500000):
    """마크다운/텍스트 파일의 본문을 읽어 반환 (로컬 CORS 방지용)"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
            if len(text) > max_len:
                return text[:max_len] + "\n\n... (내용이 너무 길어 일부만 표시됩니다) ..."
            return text
    except Exception:
        return ""

def sync_folder(src_dir, dst_dir):
    """폴더 내의 변경된 파일만 효율적으로 재귀 동기화"""
    copied_count = 0
    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)

    if not src_dir.exists():
        print(f"  [경고] 원본 폴더 없음: {src_dir}")
        return 0

    for root, dirs, files in os.walk(src_dir):
        rel_path = Path(root).relative_to(src_dir)
        target_root = dst_dir / rel_path
        target_root.mkdir(parents=True, exist_ok=True)

        for file in files:
            src_file = Path(root) / file
            dst_file = target_root / file
            if should_copy(src_file, dst_file):
                shutil.copy2(src_file, dst_file)
                copied_count += 1

    return copied_count

def guess_metadata(file_path):
    """파일명과 확장자를 분석하여 모드, 카테고리, 하부 분류(subcat) 자동 추론"""
    name = file_path.name
    name_lower = name.lower()
    ext = file_path.suffix.lower().lstrip(".")

    game_mode = "common"
    if any(k in name_lower for k in ["derby", "race", "경주", "트랙"]):
        game_mode = "race"
    elif any(k in name_lower for k in ["pit", "rumble_pit", "격투", "투계", "선수", "럼블핏"]):
        game_mode = "pit"
    elif any(k in name_lower for k in ["farm", "농장", "육성"]):
        game_mode = "farm"

    category = "docs"
    subcat = "docs"
    badge = "신규"
    badge_type = "secondary"

    if game_mode == "common":
        if any(k in name_lower for k in ["mvp", "플로우", "방향", "기획"]):
            subcat = "core"
        elif any(k in name_lower for k in ["테이블", "데이터", "볼륨"]):
            subcat = "data"
            category = "data"
        elif any(k in name_lower for k in ["qa", "체크리스트", "pt", "로드맵", "마일스톤", "일정"]):
            subcat = "qa"
    elif game_mode in ["race", "pit", "farm"]:
        if any(k in name_lower for k in ["사운드보드", "청음보드", "soundboard"]) or ext in ["mp3", "wav", "ogg"]:
            category = "audio"
            subcat = "audio"
            badge = "사운드"
            badge_type = "info"
        elif ext in ["png", "jpg", "jpeg", "webp", "gif", "svg"]:
            category = "images"
            subcat = "visuals"
            badge = "이미지"
            badge_type = "primary"
        elif ext in ["csv", "json", "xlsx", "tsv"]:
            category = "data"
            subcat = "data"
            badge = "데이터"
            badge_type = "warning"
        elif ext in ["html", "htm"] and any(k in name_lower for k in ["demo", "ui_샘플", "샘플", "prototype"]):
            category = "demos"
            subcat = "demo"
            badge = "데모"
            badge_type = "success"

    title = file_path.stem.replace("_", " ")

    return {
        "id": f"auto_{file_path.stem}_{ext}".replace(" ", "_").replace("-", "_").lower(),
        "title": title,
        "category": category,
        "subcat": subcat,
        "game_mode": game_mode,
        "badge": badge,
        "badge_type": badge_type,
        "is_final": False,
        "desc": f"자동 분류 등록 파일 ({name})",
        "tags": [game_mode, subcat, ext]
    }

def main():
    root_dir = Path(__file__).resolve().parent
    config_file = root_dir / "sync_config.json"

    print("=" * 64)
    print(" 🐓 ROOSTER RUMBLE 웹보드 스마트 동기화 & 뷰어 지원 (v2.2)")
    print(f" 기준 일시: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 64)

    if not config_file.exists():
        print(f"[오류] 설정 파일({config_file.name})을 찾을 수 없습니다.")
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    docs_dir = root_dir / config.get("docs_dir", "docs")
    docs_dir.mkdir(parents=True, exist_ok=True)
    exclude_files = set(config.get("exclude_files", []))

    # 0. 제외 대상 파일 docs 내 잔존 시 자동 삭제
    for exc in exclude_files:
        for p in docs_dir.rglob(exc):
            try:
                p.unlink()
                print(f"  [제외정리] 배포 제외 파일 삭제: {p.name}")
            except Exception:
                pass

    # 1. 공용 에셋 및 데모 폴더 동기화
    print("\n[1/4] 공용 에셋 및 데모 원본 폴더 동기화...")
    folder_sync_rules = config.get("folder_sync", [])
    total_folder_files_copied = 0
    for rule in folder_sync_rules:
        src = root_dir / rule["src"]
        dest = root_dir / rule["dest"]
        desc = rule.get("desc", rule["src"])
        copied = sync_folder(src, dest)
        total_folder_files_copied += copied
        print(f"  • {desc}: {copied}개 파일 업데이트됨")

    # 2. 명시된 주요 파일 동기화 (하부 폴더 구조 배치 및 마크다운 본문 임베딩)
    print("\n[2/4] 명시된 주요 파일 하부 폴더 복사 및 메타데이터 추출...")
    configured_items = config.get("items", [])
    processed_items = []
    registered_src_paths = set()
    file_copied_count = 0

    for item in configured_items:
        if item.get("src") in exclude_files:
            continue
        src_path = root_dir / item["src"]
        dest_path = root_dir / item["dest"]
        registered_src_paths.add(src_path.resolve())

        item_data = dict(item)

        if not src_path.exists():
            print(f"  [누락] 원본 파일 없음: {item['src']}")
            item_data["exists"] = False
            item_data["file_size"] = "0 B"
            item_data["updated_at"] = "-"
        else:
            item_data["exists"] = True

            if should_copy(src_path, dest_path):
                copy_with_path_fix(src_path, dest_path, docs_dir)
                file_copied_count += 1
                status_mark = "복사/배치"
            else:
                status_mark = "최신유지"

            stat = src_path.stat()
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
            item_data["file_size"] = format_size(stat.st_size)
            item_data["bytes"] = stat.st_size
            item_data["updated_at"] = mtime.strftime("%Y-%m-%d %H:%M")
            ext = src_path.suffix.lower().lstrip(".")
            item_data["ext"] = ext

            rel_to_docs = dest_path.relative_to(docs_dir).as_posix()
            item_data["url"] = rel_to_docs

            # 마크다운/CSV/텍스트 파일은 본문을 content에 임베딩하여 로컬 CORS 오류 차단!
            if ext in ["md", "csv", "txt"]:
                item_data["content"] = read_text_content(src_path)

            print(f"  [{status_mark}] [{rel_to_docs}] {item['title']}")

        processed_items.append(item_data)

    # 3. 신규 파일 자동 감지 (하부 폴더로 자동 분류 복사)
    print("\n[3/4] 신규 파일 자동 감지 및 하부 폴더 자동 배치...")
    auto_discovered_count = 0
    ignored_patterns = ["sync_config.json", "sync_webboard.py", "sync_webboard.bat", "prev_", "새 텍스트"]

    for entry in root_dir.iterdir():
        if entry.is_file() and entry.resolve() not in registered_src_paths:
            if entry.name in exclude_files:
                continue
            if any(ign in entry.name for ign in ignored_patterns):
                continue
            if entry.name.startswith("."):
                continue

            ext = entry.suffix.lower().lstrip(".")
            if ext in ["md", "html", "csv", "json", "pdf", "txt", "png", "jpg"]:
                auto_meta = guess_metadata(entry)
                
                dest_path = docs_dir / auto_meta["game_mode"] / auto_meta["subcat"] / entry.name
                
                if should_copy(entry, dest_path):
                    copy_with_path_fix(entry, dest_path, docs_dir)
                    file_copied_count += 1

                stat = entry.stat()
                mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
                auto_meta["exists"] = True
                auto_meta["src"] = entry.name
                auto_meta["dest"] = dest_path.relative_to(root_dir).as_posix()
                auto_meta["file_size"] = format_size(stat.st_size)
                auto_meta["bytes"] = stat.st_size
                auto_meta["updated_at"] = mtime.strftime("%Y-%m-%d %H:%M")
                auto_meta["ext"] = ext
                
                rel_to_docs = dest_path.relative_to(docs_dir).as_posix()
                auto_meta["url"] = rel_to_docs

                if ext in ["md", "csv", "txt"]:
                    auto_meta["content"] = read_text_content(entry)

                processed_items.append(auto_meta)
                auto_discovered_count += 1
                print(f"  [신규배치] [{rel_to_docs}] {entry.name}")

    if auto_discovered_count == 0:
        print("  • 미등록된 신규 파일 없음 (모두 정식 카탈로그에 등록됨)")

    # 3.5 데모 아이템 및 연관 문서(related_docs) 크로스 레퍼런스 구축
    item_map = {it["id"]: it for it in processed_items}
    for it in processed_items:
        # category가 demos인 경우 자동으로 is_demo 설정
        if it.get("category") == "demos":
            it["is_demo"] = True
        
        # related_doc_ids가 있는 경우 상세 정보 객체 리스트로 매핑
        if "related_doc_ids" in it and isinstance(it["related_doc_ids"], list):
            rel_list = []
            for r_id in it["related_doc_ids"]:
                if r_id in item_map:
                    target = item_map[r_id]
                    rel_list.append({
                        "id": target["id"],
                        "title": target["title"],
                        "url": target.get("url", ""),
                        "ext": target.get("ext", ""),
                        "badge": target.get("badge", ""),
                        "game_mode": target.get("game_mode", "")
                    })
            it["related_docs"] = rel_list

    # 3.8 마스터 공개/감추기 및 필독 상태 적용 (board_visibility.json)
    visibility_path = docs_dir / "board_visibility.json"
    visibility_data = {"public_doc_ids": [], "pinned_doc_ids": []}
    if visibility_path.exists():
        try:
            with open(visibility_path, "r", encoding="utf-8") as vf:
                visibility_data = json.load(vf)
        except Exception:
            pass

    public_set = set(visibility_data.get("public_doc_ids", []))
    pinned_set = set(visibility_data.get("pinned_doc_ids", []))

    hidden_count = 0
    public_count = 0
    for it in processed_items:
        # 기본적으로 모든 문서는 감추기(is_hidden=True), 마스터가 명시한 것만 공개(is_hidden=False)
        is_pub = it["id"] in public_set
        it["is_hidden"] = not is_pub
        it["is_pinned"] = it["id"] in pinned_set
        if it["is_hidden"]:
            hidden_count += 1
        else:
            public_count += 1

    print(f"\n[보안 설정] 문서 상태: 공개 {public_count}개, 감추기(기본) {hidden_count}개, 필독 {len(pinned_set)}개")

    # 4. 메타데이터 JS 및 JSON 출력
    print("\n[4/4] 웹보드 배포 데이터 파일 갱신...")
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    board_meta = {
        "project_title": config.get("project_title", "ROOSTER RUMBLE 웹보드"),
        "project_subtitle": config.get("project_subtitle", ""),
        "last_sync": now_str,
        "total_items": len(processed_items),
        "menu_sections": config.get("menu_sections", []),
        "items": processed_items
    }

    # board_data.json 저장
    json_path = docs_dir / "board_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(board_meta, f, ensure_ascii=False, indent=2)

    # board_data.js 저장 (로컬 브라우저 CORS 문제 완전 해결)
    js_path = docs_dir / "board_data.js"
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("// ROOSTER RUMBLE 웹보드 자동 생성 데이터 (v2.2 마크다운 본문 임베딩)\n")
        f.write(f"// 생성 일시: {now_str}\n")
        f.write("window.BOARD_DATA = ")
        json.dump(board_meta, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    print(f"  • JSON 메타데이터 갱신: {json_path.name}")
    print(f"  • JS 메타데이터 갱신: {js_path.name}")

    print("\n" + "=" * 64)
    print(" 🎉 마크다운 뷰어 지원 및 동기화 완료!")
    print(f"  - 동기화 에셋: {total_folder_files_copied}개 파일")
    print(f"  - 하부 폴더 배치 파일: {file_copied_count}개")
    print(f"  - 총 등록 웹보드 항목: {len(processed_items)}개")
    print(f"  - 웹보드 주소: {docs_dir.resolve()}\\index.html")
    print("=" * 64)

    # --push 옵션 지원
    if "--push" in sys.argv:
        import subprocess
        print("\n" + "=" * 64)
        print(" 🚀 GitHub 원클릭 배포 프로세스 시작")
        print("=" * 64)
        try:
            # 1. 현재 변경/신규 파일 목록 조회
            status_res = subprocess.run(["git", "status", "-s"], capture_output=True, text=True, encoding="utf-8", errors="replace")
            raw_lines = [l.rstrip() for l in status_res.stdout.splitlines() if l.strip()]

            if not raw_lines:
                print("\nℹ️ 새로 변경되거나 추가된 파일이 없습니다. (이미 최신 상태)")
            else:
                print("\n[현재 변경된 파일 목록]")
                file_items = []
                for idx, line in enumerate(raw_lines, 1):
                    # git status -s 형식: ' M filename' 또는 '?? filename'
                    code = line[:2].strip()
                    file_name = line[3:].strip().strip('"')
                    file_items.append((code, file_name))
                    print(f"  [{idx:2d}] ({code:2s}) {file_name}")

                selected_files = []
                # 인자로 직접 파일 지정이 없으면 사용자에게 대화형으로 선택
                if "--all" in sys.argv:
                    selected_files = [f for _, f in file_items]
                else:
                    try:
                        choice = input(f"\n📝 커밋할 파일 번호를 입력하세요 (예: 1, 3 / 전체는 A 또는 Enter): ").strip()
                    except Exception:
                        choice = ""

                    if not choice or choice.upper() == "A":
                        selected_files = [f for _, f in file_items]
                        print("  👉 전체 파일을 커밋 대상으로 선택했습니다.")
                    else:
                        # 번호 파싱 (예: 1, 3 또는 1-3)
                        chosen_indices = set()
                        parts = re.split(r'[, \t]+', choice)
                        for p in parts:
                            if '-' in p:
                                sub = p.split('-')
                                if len(sub) == 2 and sub[0].isdigit() and sub[1].isdigit():
                                    for i in range(int(sub[0]), int(sub[1]) + 1):
                                        if 1 <= i <= len(file_items):
                                            chosen_indices.add(i - 1)
                            elif p.isdigit():
                                val = int(p)
                                if 1 <= val <= len(file_items):
                                    chosen_indices.add(val - 1)

                        if not chosen_indices:
                            print("  ⚠️ 올바른 번호가 선택되지 않아 전체 파일을 대상으로 진행합니다.")
                            selected_files = [f for _, f in file_items]
                        else:
                            selected_files = [file_items[i][1] for i in sorted(chosen_indices)]
                            # 웹보드 데이터 파일이 변경된 경우 웹보드 동작을 위해 함께 포함
                            essential_docs = ["docs/board_data.js", "docs/board_data.json", "docs/board_visibility.json"]
                            for ed in essential_docs:
                                for _, fn in file_items:
                                    if fn == ed and fn not in selected_files:
                                        selected_files.append(fn)

                            print(f"\n  👉 선택된 파일 ({len(selected_files)}개):")
                            for sf in selected_files:
                                print(f"     • {sf}")

                # 2. 선택된 파일 스테이징
                for sf in selected_files:
                    subprocess.run(["git", "add", sf], check=True)

                commit_msg = f"docs: 웹보드 산출물 업데이트 ({now_str})"
                if "--msg" in sys.argv:
                    idx = sys.argv.index("--msg")
                    if idx + 1 < len(sys.argv):
                        commit_msg = sys.argv[idx + 1]
                else:
                    try:
                        user_input = input(f"\n📝 커밋 메모를 입력하세요 (엔터 치면 자동 입력): ").strip()
                        if user_input:
                            commit_msg = user_input
                    except Exception:
                        pass

                print(f"\n[Git] 커밋 생성 중: {commit_msg}")
                subprocess.run(["git", "commit", "-m", commit_msg], check=True)

                print("[Git] GitHub로 푸시 중...")
                subprocess.run(["git", "push", "origin", "main"], check=True)

                print("\n" + "=" * 64)
                print(" 🎉 GitHub 배포가 성공적으로 완료되었습니다!")
                print(" 약 1~2분 후 아래 웹사이트에 자동으로 최신 내용이 반영됩니다:")
                print(" 👉 https://fingerfinger.github.io/rooster-rumble/")
                print("=" * 64)
        except Exception as e:
            print(f"\n❌ Git 푸시 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
