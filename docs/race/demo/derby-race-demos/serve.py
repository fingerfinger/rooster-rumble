"""압축 해제한 제작 도구를 외부 접속 없이 로컬 브라우저에서 실행한다."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import functools
import os
import webbrowser

directory = Path(__file__).resolve().parent
handler = functools.partial(SimpleHTTPRequestHandler, directory=str(directory))
with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
    url = f"http://127.0.0.1:{server.server_port}/demos/index.html"
    print(f"제작 도구: {url}", flush=True)
    print("종료하려면 Ctrl+C를 누르세요.", flush=True)
    if os.environ.get("DEMO_NO_BROWSER") != "1":
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
