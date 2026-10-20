# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright>=1.55", "pillow>=11", "segno>=1.6"]
# ///
"""Re-shoot the README screenshots from the demo site, each frame in light and dark.

Writes docs/img/<frame>-{light,dark}.webp. Uses the installed Google Chrome (no browser download).

    uv run scripts/screenshots.py
"""

import asyncio
import functools
import http.server
import io
import sys
import threading
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from demo_site import ROOT, build_demo  # noqa: E402

OUT = ROOT / "docs" / "img"
# frame name: (path on the demo site, element to capture)
FRAMES = {
    "card": ("olena-kovalenko/?lang=en", ".wrap"),
    "guide": ("guide/?p=olena-kovalenko", ".g-hero"),
}


async def shoot(base: str) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome")
        for name, (path, selector) in FRAMES.items():
            for scheme in ("light", "dark"):
                page = await browser.new_page(
                    viewport={"width": 390, "height": 844}, device_scale_factor=2, color_scheme=scheme, locale="en-US"
                )
                await page.goto(f"{base}/{path}", wait_until="networkidle")
                await page.wait_for_timeout(1200)  # let the entrance animation settle
                png = await page.locator(selector).screenshot()
                Image.open(io.BytesIO(png)).save(OUT / f"{name}-{scheme}.webp", quality=90)
                await page.close()
                print(f"docs/img/{name}-{scheme}.webp")
        await browser.close()


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    demo = build_demo()
    handler = functools.partial(QuietHandler, directory=str(demo))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        asyncio.run(shoot(f"http://127.0.0.1:{server.server_port}"))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
