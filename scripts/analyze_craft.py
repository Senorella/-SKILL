# -*- coding: utf-8 -*-
"""非遗手作市集底图分析：水印修补 + 行亮度分布（定标题落位）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image

GI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated-images")
W, H = 1024, 1536

SRC = {
    "hands":  "Black_and_white_grayscale__doc_2026-10-10T12-04-55.png",   # 双手做陶
    "stills": "Black_and_white_grayscale__sti_2026-10-10T12-05-12.png",   # 器物静物
    "weave":  "Black_and_white_grayscale__mac_2026-10-10T12-05-32.png",   # 竹编纹理
}
WM_BOX = (880, 1450, 1024, 1536)

def remove_watermark(img):
    x0, y0, x1, y1 = WM_BOX
    w = x1 - x0
    patch = img.crop((x0 - w, y0, x0, y1)).transpose(Image.FLIP_LEFT_RIGHT)
    img.paste(patch, (x0, y0))
    return img

for name, fn in SRC.items():
    img = remove_watermark(Image.open(os.path.join(GI, fn)).convert("L"))
    px = img.load()
    print(f"\n=== {name} 行灰度（每96px段：均值/暗像素<110占比%）===")
    for y0 in range(0, H, 96):
        s = 0; dark = 0; n = 0
        for y in range(y0, min(y0 + 96, H)):
            for x in range(0, W, 3):
                v = px[x, y]
                s += v
                if v < 110: dark += 1
                n += 1
        mean = s / n
        pct = dark / n * 100
        print(f"y {y0:4d}-{min(y0+95,H):4d}: 均值{mean:5.0f}  暗{pct:5.1f}% {'#' * int(pct / 2)}")
