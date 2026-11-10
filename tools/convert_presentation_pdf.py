import subprocess
import os
import pathlib
import sys

sys.stdout.reconfigure(encoding='utf-8')

base_dir = pathlib.Path(__file__).parent.resolve()
html_file = base_dir / "ROOSTER RUMBLE 모드 요약 소개 (프레젠테이션).html"
pdf_file = base_dir / "ROOSTER RUMBLE 모드 요약 소개.pdf"
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# If PDF already exists, remove it first
if pdf_file.exists():
    try:
        pdf_file.unlink()
        print("Removed existing PDF file.")
    except Exception as e:
        print(f"Warning: could not remove existing PDF: {e}")

file_url = html_file.as_uri()

cmd = [
    edge_path,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_file}",
    file_url
]

print(f"Converting {file_url} -> {pdf_file}")
res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
print("Exit code:", res.returncode)

if pdf_file.exists():
    print(f"SUCCESS: PDF created, size = {pdf_file.stat().st_size} bytes")
else:
    print("FAILED: PDF not created")
