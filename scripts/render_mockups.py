"""把 scripts/mockups/*.html 渲染成 raw/<名字>.png（示意图），之后照常用 annotate.py 标注。

用法：python scripts/render_mockups.py
需要本机装有 Chrome 或 Edge。
"""

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts" / "mockups"
RAW = ROOT / "raw"

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]


def browser() -> str:
    for c in CANDIDATES:
        if c and Path(c).exists():
            return c
    raise SystemExit("找不到 Chrome 或 Edge")


def main() -> None:
    exe = browser()
    RAW.mkdir(exist_ok=True)
    for html in sorted(SRC.glob("*.html")):
        out = RAW / f"{html.stem}.png"
        subprocess.run(
            [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--window-size=1280,800", f"--screenshot={out}", html.as_uri()],
            check=True, capture_output=True,
        )
        print(f"{html.name} -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
