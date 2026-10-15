# -*- coding: utf-8 -*-
"""声音艺术展底图分析：水印修补 + 行亮度分布"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image

GI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated-images")
W, H = 1024, 1536
SRC = {
    "listen": "Black_and_white_grayscale__clo_2026-10-10T13-14-02.png",  # 戴耳机聆听
    "market": "Black_and_white_grayscale__a_b_2026-10-10T13-14-21.png",  # 菜市场吆喝
    "mic":    "Black_and_white_grayscale__a_v_2026-10-10T13-14-42.png",  # 麦克风夜景
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
    print(f"\n=== {name} 行灰度（每96px段：均值/亮像素>110占比%）===")
    for y0 in range(0, H, 96):
        s = 0; bright = 0; n = 0
        for y in range(y0, min(y0 + 96, H)):
            for x in range(0, W, 3):
                v = px[x, y]
                s += v
                if v > 110: bright += 1
                n += 1
        print(f"y {y0:4d}-{min(y0+95,H):4d}: 均值{s/n:5.0f}  亮{bright/n*100:5.1f}% {'#' * int(bright/n*100/2)}")
