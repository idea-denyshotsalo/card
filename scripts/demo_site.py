# /// script
# requires-python = ">=3.12"
# dependencies = ["segno>=1.6"]
# ///
"""Build the site from fictional data (scripts/demo_people.json) into .demo/, never touching real pages.

    uv run scripts/demo_site.py            # build only
    uv run scripts/demo_site.py --serve    # build, then serve on http://127.0.0.1:8000
"""

import argparse
import functools
import http.server
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / ".demo"
DATA = ROOT / "scripts" / "demo_people.json"


def build_demo() -> Path:
    """Copy the build sources next to the demo data and run the real build.py there."""
    shutil.copytree(ROOT / "_src", DEMO / "_src", dirs_exist_ok=True)
    shutil.copytree(ROOT / "assets", DEMO / "assets", dirs_exist_ok=True)
    shutil.copyfile(DATA, DEMO / "_src" / "people.json")
    subprocess.run([sys.executable, str(DEMO / "_src" / "build.py")], check=True)
    return DEMO


def serve(port: int) -> None:
    first = json.loads(DATA.read_text(encoding="utf-8"))["people"][0]["slug"]
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DEMO))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        print(f"serving .demo on http://127.0.0.1:{port}/{first}/", flush=True)
        server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--serve", action="store_true", help="serve .demo/ after building")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    build_demo()
    if args.serve:
        serve(args.port)


if __name__ == "__main__":
    main()
