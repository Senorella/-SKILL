# -*- coding: utf-8 -*-
"""分析 A/B 版底图的亮度行分布，找主体（内容）垂直范围"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from make_poster_song_variants import (load_filled, SRC_DIANCHA, SRC_RUYAO,
                                       render_size_halftone, global_pad_dark,
                                       global_pad_light, _whiten, W, H, ImageOps)

def row_profile(img, name, bright_on_dark, thresh):
    g = img.convert("L")
    px = g.load()
    print(f"\n=== {name} 行亮度分布（每64px一段，内容像素占比%）===")
    for y0 in range(0, H, 64):
        cnt = 0
        total = W * 64
        for y in range(y0, min(y0 + 64, H)):
            for x in range(0, W, 2):  # 隔列采样提速
                v = px[x, y]
                if bright_on_dark:
                    if v > thresh: cnt += 1
                else:
                    if v < thresh: cnt += 1  # 白底上的灰点
        pct = cnt / (total / 2) * 100
        bar = "#" * int(pct / 2)
        print(f"y {y0:4d}-{min(y0+63,H):4d}: {pct:5.1f}% {bar}")

# A 版底图（黑底点茶）——在柔光层之前分析原始半调
src = load_filled(SRC_DIANCHA, crop_ratio=0.90)
img_a = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
row_profile(img_a, "A版底图 黑底点茶 半调原图（亮像素>60=内容）", True, 60)

# B 版底图（白底汝窑）——反相 gamma 后、柔光前分析
src = load_filled(SRC_RUYAO, crop_ratio=0.90)
img_b = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
img_b = ImageOps.invert(img_b).convert("L")
px = img_b.load()
for y in range(H):
    for x in range(W):
        v = px[x, y] / 255.0
        px[x, y] = int((v ** 1.7) * 255)
img_b = img_b.convert("RGB")
_whiten(img_b)
row_profile(img_b, "B版底图 白底汝窑 半调原图（暗像素<245=内容）", False, 245)
