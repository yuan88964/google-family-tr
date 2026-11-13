"""截图标注脚本。

读取 raw/annotations.yaml，把 raw/ 里的原始截图加上红框、箭头、编号圆点和模糊打码，
输出到 docs/images/。没有原图的条目会生成一张灰色占位图。

用法：
    python scripts/annotate.py            # 处理全部条目
    python scripts/annotate.py 03 07      # 只处理指定条目

annotations.yaml 格式（坐标单位是原图像素，矩形写左上角和右下角）：

    "03":
      title: pay.google.com 设置页 · 关闭付款资料入口   # 占位图上显示的说明
      boxes:  [[x1, y1, x2, y2], ...]                  # 红色圆角框
      arrows: [[x1, y1, x2, y2], ...]                  # 从 (x1,y1) 指向 (x2,y2)
      marks:  [[x, y, 1], ...]                         # 编号圆点，圆心坐标 + 数字
      nums:   [1, 2, ...]                              # 或者：按顺序给每个框配编号，圆点自动放在框左侧
      blur:   [[x1, y1, x2, y2], ...]                  # 高斯模糊打码
      crop:   [x1, y1, x2, y2]                         # 可选，最后裁剪
      src:    fam-03                                   # 可选，借用另一张原图
      width:  1600                                     # 可选，输出最大宽度
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
OUT = ROOT / "docs" / "images"
SPEC = RAW / "annotations.yaml"

RED = (234, 67, 53)
WHITE = (255, 255, 255)
FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


def find_raw(name: str) -> Path | None:
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        p = RAW / f"{name}{ext}"
        if p.exists():
            return p
    return None


def placeholder(name: str, title: str) -> Image.Image:
    img = Image.new("RGB", (1600, 900), (241, 243, 244))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1599, 899], outline=(218, 220, 224), width=6)
    d.text((800, 380), f"截图待补 · {name}", fill=(95, 99, 104), font=font(72), anchor="mm")
    d.text((800, 500), title or "", fill=(128, 134, 139), font=font(40), anchor="mm")
    return img


def draw_arrow(d: ImageDraw.ImageDraw, a, b, w: int) -> None:
    x1, y1, x2, y2 = *a, *b
    ang = math.atan2(y2 - y1, x2 - x1)
    head = w * 4.5
    # 线段止于箭头根部，避免线头戳出箭尖
    bx, by = x2 - head * 0.8 * math.cos(ang), y2 - head * 0.8 * math.sin(ang)
    d.line([x1, y1, bx, by], fill=RED, width=w)
    left = (x2 - head * math.cos(ang - 0.45), y2 - head * math.sin(ang - 0.45))
    right = (x2 - head * math.cos(ang + 0.45), y2 - head * math.sin(ang + 0.45))
    d.polygon([(x2, y2), left, right], fill=RED)


def annotate(name: str, spec: dict) -> Path:
    src = find_raw(spec.get("src", name))
    if src is None:
        img = placeholder(name, spec.get("title", ""))
    else:
        img = Image.open(src).convert("RGB")
        # 先打码，再画标注，保证标注不被模糊
        for x1, y1, x2, y2 in spec.get("blur", []) or []:
            region = img.crop((x1, y1, x2, y2))
            radius = max(8, min(x2 - x1, y2 - y1) // 4)
            img.paste(region.filter(ImageFilter.GaussianBlur(radius)), (x1, y1))

        scale = max(img.width, img.height) / 1600
        w = max(3, round(4 * scale))
        d = ImageDraw.Draw(img)
        for x1, y1, x2, y2 in spec.get("boxes", []) or []:
            d.rounded_rectangle([x1, y1, x2, y2], radius=round(8 * scale), outline=RED, width=w)
        for x1, y1, x2, y2 in spec.get("arrows", []) or []:
            draw_arrow(d, (x1, y1), (x2, y2), w)
        r = round(22 * scale)
        f = font(round(26 * scale))
        marks = list(spec.get("marks", []) or [])
        # nums: 按顺序给每个框配一个编号，圆点自动放在框的左侧
        for (x1, y1, x2, y2), n in zip(spec.get("boxes", []) or [], spec.get("nums", []) or []):
            marks.append([max(r + 2, x1 - r - 6), (y1 + y2) // 2, n])
        for x, y, n in marks:
            d.ellipse([x - r - 2, y - r - 2, x + r + 2, y + r + 2], fill=WHITE)
            d.ellipse([x - r, y - r, x + r, y + r], fill=RED)
            d.text((x, y), str(n), fill=WHITE, font=f, anchor="mm")

        if spec.get("crop"):
            img = img.crop(tuple(spec["crop"]))

    max_w = spec.get("width", 1600)
    if img.width > max_w:
        img = img.resize((max_w, round(img.height * max_w / img.width)), Image.LANCZOS)

    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"{name}.png"
    img.save(dst, optimize=True)
    return dst


def main(argv: list[str]) -> None:
    specs = yaml.safe_load(SPEC.read_text(encoding="utf-8")) or {}
    names = argv or list(specs)
    for name in names:
        spec = specs.get(name) or {}
        dst = annotate(name, spec)
        state = "已标注" if find_raw(spec.get("src", name)) else "占位图"
        print(f"{name}: {state} -> {dst.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
