# -*- coding: utf-8 -*-
"""先锋话剧《镜中人》底图预处理分析：
1. 水印修补（右下角镜像贴补）
2. 三张底图半调后（柔光层之前）行亮度分布 → 定标题安全区
3. 主标题像素体渲染测试（含「，」「？」字形检查）
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from typographic_halftone import render_size_halftone

GI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated-images")
W, H = 1024, 1536

SRC = {
    "mirror":   "mirror_b/Black_and_white_grayscale__fil_2026-10-09T20-36-34.png",
    "audience": "mirror_b/Black_and_white_grayscale__fil_2026-10-09T20-36-33.png",
    "gauze":    "Black_and_white_grayscale__hig_2026-10-09T20-37-43.png",
}

WM_BOX = (880, 1450, 1024, 1536)   # 水印区域（含边距）

def remove_watermark(img):
    """右下角水印：取其左侧等宽区域水平镜像贴补"""
    x0, y0, x1, y1 = WM_BOX
    w = x1 - x0
    patch = img.crop((x0 - w, y0, x0, y1)).transpose(Image.FLIP_LEFT_RIGHT)
    img.paste(patch, (x0, y0))
    return img

def load_clean(name):
    img = Image.open(os.path.join(GI, SRC[name])).convert("L")
    return remove_watermark(img)

def row_profile(g, name, bright_on_dark):
    px = g.load()
    tag = "亮=内容" if bright_on_dark else "暗=内容"
    print(f"\n=== {name}（{tag}，每96px一段）===")
    for y0 in range(0, H, 96):
        cnt = 0
        n = 0
        for y in range(y0, min(y0 + 96, H)):
            for x in range(0, W, 3):
                v = px[x, y]
                ok = (v > 100) if bright_on_dark else (v < 210)
                if ok: cnt += 1
                n += 1
        pct = cnt / n * 100
        print(f"y {y0:4d}-{min(y0+95,H):4d}: {pct:5.1f}% {'#' * int(pct / 2)}")

print("---------- 底图行亮度分布（半调后、柔光前） ----------")
for name in SRC:
    src = load_clean(name)
    if name == "gauze":
        # 白底方案：模拟反相+gamma 后的「暗像素=内容」
        img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
        img = ImageOps.invert(img).convert("L")
        px = img.load()
        for y in range(H):
            for x in range(W):
                v = px[x, y] / 255.0
                px[x, y] = int((v ** 1.7) * 255)
        row_profile(img, name + "（白底墨点）", False)
    else:
        img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True).convert("L")
        row_profile(img, name + "（黑底点阵）", True)

print("\n---------- 主标题渲染测试 ----------")
F_ZIYU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "ZiYuQuWeiXiangSu.ttf")
for size in (150, 160, 170):
    img = Image.new("L", (1100, 320), 0)
    d = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(F_ZIYU, size)
    d.text((20, 20), "你，在场吗？", font=f1, fill=255)
    bb = img.getbbox()
    print(f"size={size}: bbox={bb} 墨迹宽={bb[2]-bb[0]} 高={bb[3]-bb[1]}")
# 单独检查「？」「，」字形
img = Image.new("L", (400, 320), 0)
d = ImageDraw.Draw(img)
f1 = ImageFont.truetype(F_ZIYU, 200)
d.text((20, 20), "？", font=f1, fill=255)
print("「？」200px bbox:", img.getbbox())
img = Image.new("L", (400, 320), 0)
d = ImageDraw.Draw(img)
d.text((20, 20), "，", font=f1, fill=255)
print("「，」200px bbox:", img.getbbox())
