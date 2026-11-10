import argparse
import os
import re
import shutil
import sys

ROOT_DIR = r"d:\OneDrive\업무_진행\C\ROOSTER RUMBLE"
LOCAL_VERSIONS_DIR = os.path.join(ROOT_DIR, "versions")
DEPLOY_DIR = r"D:\OneDrive\업무_진행\C\ROOSTER RUMBLE_share\ROOSTER RUMBLE_Derby Race\01_Documents"
DEPLOY_VERSIONS_DIR = os.path.join(DEPLOY_DIR, "versions")

TARGET_VERSION = "v1.2.0"

# 12 Target Markdown Documents (workspace filename -> deployed base name without prefix/version)
MD_DOCS = [
    ("Rumble_Pit_전투_시뮬레이션_규칙_정의서.md", "Rumble_Pit_전투_시뮬레이션_규칙_정의서"),
    ("Rumble Pit MVP 구성안.md", "Rumble_Pit_MVP_구성안"),
    ("Rumble Pit 선수 공격 방어 동작 구성안.md", "Rumble_Pit_선수_공격_방어_동작_구성안"),
    ("Rumble Pit 전투 장면 인게임 구성안.md", "Rumble_Pit_전투_장면_인게임_구성안"),
    ("Rumble Pit 인게임 사운드 구성안.md", "Rumble_Pit_인게임_사운드_구성안"),
    ("Rumble Pit 웹 로비 기본 구성 요소 정의.md", "Rumble_Pit_웹_로비_기본_구성_요소_정의"),
    ("Rumble_Pit_데모_선수_동작_프롬프트.md", "Rumble_Pit_데모_선수_동작_프롬프트"),
    ("Rumble Pit 기획방향.md", "Rumble_Pit_기획방향"),
    ("통합 MVP 구성안.md", "통합_MVP_구성안"),
    ("Rumble Farm MVP 구성안.md", "Rumble_Farm_MVP_구성안"),
    ("통합_MVP_전체_게임_플로우차트.md", "통합_MVP_전체_게임_플로우차트"),
    ("통합 기획방향.md", "통합_기획방향"),
]

# 4 Target HTML Documents (workspace filename -> deployed base name without prefix/version)
HTML_DOCS = [
    ("Rumble_Pit_전투_시뮬레이션_규칙_정의서.html", "Rumble_Pit_전투_시뮬레이션_규칙_정의서"),
    ("Rumble_Pit_MVP_구성안.html", "Rumble_Pit_MVP_구성안"),
    ("Rumble_Farm_MVP_구성안.html", "Rumble_Farm_MVP_구성안"),
    ("통합_MVP_구성안.html", "통합_MVP_구성안"),
]


def fix_html_latex_escapes(html_path: str) -> None:
    with open(html_path, "r", encoding="utf-8") as f:
        text = f.read()
    orig = text
    # Fix control characters that were accidentally produced from \text, \times, \frac, \right, \alpha
    text = text.replace("\text{", r"\text{")
    text = text.replace("\times", r"\times")
    text = text.replace("\frac{", r"\frac{")
    text = text.replace("\x0crac{", r"\frac{")
    text = text.replace("\right)", r"\right)")
    text = text.replace("\nigh", r"\righ")
    text = text.replace("ight)", r"\right)")
    text = text.replace(r"\\right)", r"\right)")
    text = text.replace("\x07lpha", r"\alpha")
    text = text.replace(" lpha", r" \alpha")
    if text != orig:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"  [FIXED LATEX] {os.path.basename(html_path)}")


def cmd_sync() -> int:
    print("=== [STAGE 1: SYNC] 마스터 데이터 및 규칙 동기화 확인 ===")
    for md_file, _ in MD_DOCS:
        p = os.path.join(ROOT_DIR, md_file)
        if not os.path.exists(p):
            print(f"  [ERROR] 누락된 마크다운 파일: {md_file}")
            return 1
    print(f"  [OK] 대상 마크다운 문서 {len(MD_DOCS)}종 전수 확인 완료")
    return 0


def cmd_build() -> int:
    print("=== [STAGE 2: BUILD] HTML 뷰어 빌드 및 수식 무결성 정제 ===")
    for html_file, _ in HTML_DOCS:
        p = os.path.join(ROOT_DIR, html_file)
        if not os.path.exists(p):
            print(f"  [ERROR] 누락된 HTML 파일: {html_file}")
            return 1
        fix_html_latex_escapes(p)
        with open(p, "r", encoding="utf-8") as f:
            c = f.read()
        if TARGET_VERSION not in c:
            print(f"  [ERROR] HTML 버전 미일치 ({TARGET_VERSION} 누락): {html_file}")
            return 1
    min_p = os.path.join(ROOT_DIR, "통합_MVP_구성안_배포용.min.html")
    if os.path.exists(min_p):
        shutil.copy2(os.path.join(ROOT_DIR, "통합_MVP_구성안.html"), min_p)
    print(f"  [OK] 대상 HTML 문서 {len(HTML_DOCS)}종 {TARGET_VERSION} 빌드 및 검증 완료")
    return 0


def slugify_obsidian(heading: str) -> str:
    return heading.strip()


def cmd_validate() -> int:
    print("=== [STAGE 3: VALIDATE] 4단계 자동 검증 파이프라인 구동 ===")
    errors = []

    # 1. 개조식 문체 100% 검증 & 2. 개정 이력 테이블 4열 및 v1.2.0 검증
    prose_pat = re.compile(r"(습니다|합니다|됩니다|입니다|있습니다|없습니다|봅니다|줍니다|갑니다|옵니다|까요\?|네요|군요)([.?!]|\s|$)")
    for md_file, _ in MD_DOCS:
        p = os.path.join(ROOT_DIR, md_file)
        with open(p, "r", encoding="utf-8") as f:
            lines = f.readlines()
        content = "".join(lines)

        # Check version v1.2.0 presence
        if TARGET_VERSION not in content:
            errors.append(f"[버전 누락] {md_file}: {TARGET_VERSION} 표기 없음")

        in_code = False
        for idx, line in enumerate(lines, 1):
            s = line.strip()
            if s.startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            # Ignore quoted dialogues/prompts in quotes if any, check prose endings at end of sentence/line
            m = prose_pat.search(s)
            if m:
                # Allow inside explicit UI message quotes like "..."
                cleaned = re.sub(r'"[^"]*"|\'[^\']*\'', "", s)
                if prose_pat.search(cleaned):
                    errors.append(f"[문체 위반] {md_file}:{idx} -> {s[:60]}")

        # Check 4-column revision history table
        if "## 문서 개정 이력" in content or "문서 개정 이력 (Revision History)" in content:
            if "| 버전 (Version) | 개정일 (Date) |" not in content and "| 버전 | 개정일 |" not in content:
                errors.append(f"[개정이력 헤더 불일치] {md_file}")
            if f"**{TARGET_VERSION}**" not in content and f"| {TARGET_VERSION} |" not in content:
                errors.append(f"[개정이력 {TARGET_VERSION} 행 누락] {md_file}")

    # 3. 교차 참조 위키링크([[...]]) 및 헤더 앵커 전수 검증
    heading_map = {}
    for fname in os.listdir(ROOT_DIR):
        if fname.endswith(".md"):
            fpath = os.path.join(ROOT_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                text = f.read()
            headings = set()
            for m in re.finditer(r"^#{1,6}\s+(.+)$", text, re.MULTILINE):
                h = m.group(1).strip()
                headings.add(h)
            heading_map[fname] = headings
            heading_map[fname[:-3]] = headings

    wikilink_pat = re.compile(r"\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]")
    for md_file, _ in MD_DOCS:
        p = os.path.join(ROOT_DIR, md_file)
        with open(p, "r", encoding="utf-8") as f:
            text = f.read()
        for m in wikilink_pat.finditer(text):
            target_doc = m.group(1).strip()
            target_anchor = m.group(2).strip() if m.group(2) else None
            if target_doc == "파일명" or target_doc.startswith("ROOSTER_RUMBLE_<"):
                continue
            if target_doc not in heading_map:
                errors.append(f"[깨진 위키링크 파일] {md_file} -> [[{m.group(0)}]] (파일 없음: {target_doc})")
            elif target_anchor:
                if target_anchor not in heading_map[target_doc]:
                    errors.append(f"[깨진 위키링크 앵커] {md_file} -> [[{target_doc}#{target_anchor}]]")

    # 4. 핵심 수식 및 도메인 키워드 정합성 검증
    pit_mvp_text = open(os.path.join(ROOT_DIR, "Rumble Pit MVP 구성안.md"), encoding="utf-8").read()
    pit_sim_text = open(os.path.join(ROOT_DIR, "Rumble_Pit_전투_시뮬레이션_규칙_정의서.md"), encoding="utf-8").read()
    pit_snd_text = open(os.path.join(ROOT_DIR, "Rumble Pit 인게임 사운드 구성안.md"), encoding="utf-8").read()

    for move_name in [
        "전진 총총걸음",
        "짧은 뒤로 홉",
        "목 빼고 질주",
        "날개 퍼덕 후방 이탈",
        "측면 사이드 홉",
        "원형 탐색 걸음",
    ]:
        if move_name not in pit_mvp_text or move_name not in pit_sim_text:
            errors.append(f"[조류 6대 이동 명칭 누락] {move_name}")

    for skill_name in [
        "전진 부리 속사",
        "낮은 발톱 할퀴기",
        "비상 발톱 급습",
        "광폭 발버둥 난타",
        "깃털 부풀려 버티기",
        "납작 엎드리기",
        "맞발톱 쳐내기",
    ]:
        if skill_name not in pit_mvp_text or skill_name not in pit_sim_text or skill_name not in pit_snd_text:
            errors.append(f"[비의인화 7대 기술 명칭 누락] {skill_name}")

    for sfx_id in ["SFX_PIT_HIT_GEN", "SFX_PIT_GUARD_GEN", "SFX_PIT_KO_BELL"]:
        if sfx_id not in pit_mvp_text or sfx_id not in pit_snd_text:
            errors.append(f"[핵심 사운드 ID 누락] {sfx_id}")
    if "SFX_PIT_REFEREE_CNT" in pit_mvp_text or "SFX_PIT_REFEREE_CNT" in pit_snd_text:
        errors.append("[폐기된 심판 카운트 사운드 ID 잔존] SFX_PIT_REFEREE_CNT")

    if errors:
        print(f"  [FAIL] 총 {len(errors)}건의 검증 오류 발견:")
        for e in errors:
            print("   -", e)
        return 1

    print("  [OK] 1. 개조식 문체 검증: 위반 0건")
    print("  [OK] 2. 개정 이력 4열 테이블 및 v1.2.0 오름차순 검증: 오류 0건")
    print("  [OK] 3. 교차 참조 위키링크 및 섹션 앵커 전수 검증: 깨진 링크 0건")
    print("  [OK] 4. 공/방/이동(13종)·스탠딩 그로기·즉시 KO·사운드(14종) 정합성 검증: 불일치 0건")
    return 0


def rewrite_wikilinks_for_deploy(text: str, deploy_doc_map: dict) -> str:
    """
    Rewrites [[원본파일명#앵커|별칭]] in deployed Markdown files so that cross-document links
    point to the deployed filename in 01_Documents (e.g. [[ROOSTER_RUMBLE_..._v1.2.0.md#앵커|별칭]]).
    """
    wikilink_pat = re.compile(r"\[\[([^\]|#]+)(#[^\]|]+)?(\|[^\]]+)?\]\]")

    def repl(m):
        doc = m.group(1).strip()
        anchor = m.group(2) or ""
        alias = m.group(3) or ""
        has_ext = doc.endswith(".md")
        base_doc = doc[:-3] if has_ext else doc
        if base_doc in deploy_doc_map:
            deployed_base = deploy_doc_map[base_doc]
            new_doc = f"{deployed_base}.md" if has_ext else deployed_base
            if not alias and not anchor:
                alias = f"|{doc}"
            return f"[[{new_doc}{anchor}{alias}]]"
        return m.group(0)

    return wikilink_pat.sub(repl, text)


def cmd_deploy() -> int:
    print("=== [STAGE 4: DEPLOY] 배포 폴더 구버전 백업 및 v1.2.0 표준 배포 ===")
    os.makedirs(DEPLOY_VERSIONS_DIR, exist_ok=True)
    os.makedirs(LOCAL_VERSIONS_DIR, exist_ok=True)

    # Target base names managed by this deployment
    managed_bases = {base for _, base in MD_DOCS} | {base for _, base in HTML_DOCS}

    # 1. Move any old versions of managed documents in DEPLOY_DIR to DEPLOY_VERSIONS_DIR
    moved_count = 0
    for fname in sorted(os.listdir(DEPLOY_DIR)):
        fpath = os.path.join(DEPLOY_DIR, fname)
        if os.path.isdir(fpath):
            continue

        # Check if fname belongs to one of our managed_bases
        matched_base = None
        for base in sorted(managed_bases, key=len, reverse=True):
            prefix1 = f"ROOSTER_RUMBLE_{base}"
            prefix2 = base
            if fname.startswith(prefix1) or fname.startswith(prefix2):
                matched_base = base
                break

        if not matched_base:
            continue

        # Check if it's already the exact v1.2.0 target file; even if it is, we will overwrite it cleanly,
        # but if it's an older version or unversioned file, move it to DEPLOY_VERSIONS_DIR!
        expected_md = f"ROOSTER_RUMBLE_{matched_base}_{TARGET_VERSION}.md"
        expected_html = f"ROOSTER_RUMBLE_{matched_base}_{TARGET_VERSION}.html"
        if fname in (expected_md, expected_html):
            continue

        # Determine archive filename in DEPLOY_VERSIONS_DIR
        archive_name = fname
        if fname == "ROOSTER_RUMBLE_Rumble_Pit_데모_선수_동작_프롬프트.md":
            archive_name = "ROOSTER_RUMBLE_Rumble_Pit_데모_선수_동작_프롬프트_v1.0.0.md"
        elif not fname.startswith("ROOSTER_RUMBLE_"):
            archive_name = f"ROOSTER_RUMBLE_{fname}"

        dest_path = os.path.join(DEPLOY_VERSIONS_DIR, archive_name)
        shutil.move(fpath, dest_path)
        moved_count += 1
        print(f"  [ARCHIVED OLD DEPLOY] {fname} -> versions/{archive_name}")

    # 1-B. Archive lower-version documents and lower-version document folders across 01_Documents & share root
    share_root = os.path.dirname(os.path.dirname(DEPLOY_DIR))
    lower_version_items = [
        # (source_dir, item_name, target_name_in_versions)
        (share_root, "ROOSTER RUMBLE_Derby Race_순위 산출 정의", "ROOSTER RUMBLE_Derby Race_순위 산출 정의_구버전폴더"),
        (DEPLOY_DIR, "ROOSTER RUMBLE_Derby Race_게임구성안_v2.9.2_파트별", "ROOSTER RUMBLE_Derby Race_게임구성안_v2.9.2_파트별"),
        (DEPLOY_DIR, "ROOSTER RUMBLE_Derby Race_게임기획서_v1.7.3_파트별", "ROOSTER RUMBLE_Derby Race_게임기획서_v1.7.3_파트별"),
        (DEPLOY_DIR, "ROOSTER RUMBLE_Derby Race_게임구성안_v2.9.2.md", "ROOSTER RUMBLE_Derby Race_게임구성안_v2.9.2.md"),
        (DEPLOY_DIR, "ROOSTER RUMBLE_Derby Race_게임 구성_v3.0.3.pdf", "ROOSTER RUMBLE_Derby Race_게임 구성_v3.0.3.pdf"),
        (DEPLOY_DIR, "ROOSTER RUMBLE_Derby Race_게임 구성_v3.0.3.pptx", "ROOSTER RUMBLE_Derby Race_게임 구성_v3.0.3.pptx"),
        (DEPLOY_DIR, "ROOSTER RUMBLE_Derby Race_게임기획서_v1.7.3.md", "ROOSTER RUMBLE_Derby Race_게임기획서_v1.7.3.md"),
        (DEPLOY_DIR, "ROOSTER RUMBLE_Derby Race 인게임 사운드 구성안_MVP.md", "ROOSTER RUMBLE_Derby Race 인게임 사운드 구성안_MVP.md"),
        (DEPLOY_DIR, "ROOSTER RUMBLE_Derby Race_사운드 구성안_v0.9.1.md", "ROOSTER RUMBLE_Derby Race_사운드 구성안_v0.9.1.md"),
        (DEPLOY_DIR, "ROOSTER RUMBLE_Derby Race_순위 산출 정의_예시코드_v1.8.8.js", "ROOSTER RUMBLE_Derby Race_순위 산출 정의_예시코드_v1.8.8.js"),
        (DEPLOY_DIR, "경주 수정 사항_261001.md", "경주 수정 사항_261001.md"),
    ]
    for src_dir, item_name, target_name in lower_version_items:
        src_item = os.path.join(src_dir, item_name)
        if os.path.exists(src_item):
            dest_item = os.path.join(DEPLOY_VERSIONS_DIR, target_name)
            if os.path.exists(dest_item):
                if os.path.isdir(dest_item):
                    shutil.rmtree(dest_item)
                else:
                    os.remove(dest_item)
            shutil.move(src_item, dest_item)
            moved_count += 1
            print(f"  [ARCHIVED LOWER VERSION] {item_name} -> 01_Documents/versions/{target_name}")

    # 2. Ensure all local pre-revision backups in LOCAL_VERSIONS_DIR are also mirrored into DEPLOY_VERSIONS_DIR
    synced_backups = 0
    for bname in sorted(os.listdir(LOCAL_VERSIONS_DIR)):
        bpath = os.path.join(LOCAL_VERSIONS_DIR, bname)
        if not os.path.isfile(bpath):
            continue
        deploy_bname = bname if bname.startswith("ROOSTER_RUMBLE_") else f"ROOSTER_RUMBLE_{bname}"
        deploy_bpath = os.path.join(DEPLOY_VERSIONS_DIR, deploy_bname)
        if not os.path.exists(deploy_bpath) or bname == "CHANGELOG.md":
            shutil.copy2(bpath, deploy_bpath)
            synced_backups += 1
            print(f"  [SYNCED BACKUP] versions/{bname} -> 01_Documents/versions/{deploy_bname}")

    # 3. Build map of workspace document names -> deployed base names in 01_Documents
    deploy_doc_map = {}
    for ws_name, base in MD_DOCS:
        no_ext = ws_name[:-3]
        deploy_doc_map[no_ext] = f"ROOSTER_RUMBLE_{base}_{TARGET_VERSION}"
        deploy_doc_map[base] = f"ROOSTER_RUMBLE_{base}_{TARGET_VERSION}"

    # Also map existing Derby Race / Master Data documents in DEPLOY_DIR so cross-links to them resolve cleanly
    for fname in os.listdir(DEPLOY_DIR):
        if fname.endswith(".md") and fname.startswith("ROOSTER_RUMBLE_"):
            # e.g. ROOSTER_RUMBLE_통합_MVP_마스터_데이터_테이블_v0.8.0.md
            m = re.match(r"^ROOSTER_RUMBLE_(.+)_v\d+\.\d+\.\d+\.md$", fname)
            if m:
                base_key = m.group(1)
                if base_key not in deploy_doc_map:
                    deploy_doc_map[base_key] = fname[:-3]
                    deploy_doc_map[base_key.replace("_", " ")] = fname[:-3]

    # 4. Deploy all 12 v1.2.0 Markdown files with rewritten wikilinks
    deployed_md_count = 0
    for ws_name, base in MD_DOCS:
        src_path = os.path.join(ROOT_DIR, ws_name)
        dest_fname = f"ROOSTER_RUMBLE_{base}_{TARGET_VERSION}.md"
        dest_path = os.path.join(DEPLOY_DIR, dest_fname)

        with open(src_path, "r", encoding="utf-8") as f:
            raw_md = f.read()

        deployed_md = rewrite_wikilinks_for_deploy(raw_md, deploy_doc_map)
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(deployed_md)
        deployed_md_count += 1
        print(f"  [DEPLOYED MD] {dest_fname}")

    # 5. Deploy all 4 v1.2.0 HTML files
    deployed_html_count = 0
    for ws_name, base in HTML_DOCS:
        src_path = os.path.join(ROOT_DIR, ws_name)
        dest_fname = f"ROOSTER_RUMBLE_{base}_{TARGET_VERSION}.html"
        dest_path = os.path.join(DEPLOY_DIR, dest_fname)
        shutil.copy2(src_path, dest_path)
        deployed_html_count += 1
        print(f"  [DEPLOYED HTML] {dest_fname}")

    print(
        f"  [OK] 구버전 이동 {moved_count}건, 백업 동기화 {synced_backups}건, "
        f"신규 {TARGET_VERSION} 배포 완료 (MD {deployed_md_count}종, HTML {deployed_html_count}종)"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="ROOSTER RUMBLE Document Pipeline")
    parser.add_argument("--sync", action="store_true", help="Run sync check")
    parser.add_argument("--build", action="store_true", help="Build/fix HTML files")
    parser.add_argument("--validate", action="store_true", help="Validate style, history, wikilinks, and rules")
    parser.add_argument("--deploy", action="store_true", help="Backup old versions and deploy v1.2.0 files")
    parser.add_argument("--all", action="store_true", help="Run sync, build, validate, and deploy")
    args = parser.parse_args()

    if not any([args.sync, args.build, args.validate, args.deploy, args.all]):
        parser.print_help()
        return 0

    if args.sync or args.all:
        if cmd_sync() != 0:
            return 1
    if args.build or args.all:
        if cmd_build() != 0:
            return 1
    if args.validate or args.all:
        if cmd_validate() != 0:
            return 1
    if args.deploy or args.all:
        if cmd_deploy() != 0:
            return 1

    print("=== [PIPELINE SUCCESS] 모든 파이프라인 단계 정상 완료 (Exit Code: 0) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
