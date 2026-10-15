# -*- coding: utf-8 -*-
"""重建上一版「反相处理」的白纱 B 版，用于与正片版对比存档。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageOps
import make_poster_mirror as M
from typographic_halftone import render_size_halftone

src = M.load_clean(M.SRC_GAUZE).resize((M.W, M.H), Image.LANCZOS)
img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
img = ImageOps.invert(img).convert("L")
px = img.load()
for y in range(M.H):
    for x in range(M.W):
        v = px[x, y] / 255.0
        px[x, y] = int((v ** 2.0) * 255)
img = img.convert("RGB")
M._whiten(img, thresh=235)
M.global_pad_light(img, alpha=210)
M.img_holder[0] = img
d = ImageDraw.Draw(img)

# 旧 build_B 的文字排版
d.text((984, 40), "时间 Time", font=M.f(M.F_YHBD, 22), fill=M.GREY_B, anchor="ra")
d.text((984, 74), M.PERIOD, font=M.f(M.F_AA, 54), fill=M.STEEL, anchor="ra")
d.text((984, 148), M.HOURS, font=M.f(M.F_YH, 26), fill=M.GREY_B, anchor="ra")
bot = M.draw_title_light(img, 200, M.STEEL, x=40)
d.text((44, bot + 42), M.SUB, font=M.f(M.F_YHBD, 46), fill=M.STEEL)
d.text((44, bot + 122), M.SLOGAN, font=M.f(M.F_YHBD, 42), fill=M.GREY_B)
M.tracked_center(d, bot + 196, M.EN, M.f(M.F_DENGB, 17), M.GREY_B, 0.08)
M.bottom_block_light(d, M.STEEL, M.GREY_B, M.STEEL)

out = os.path.join(M.OUT, "mirror_B_白底纱幕钢蓝_反相旧版.png")
img.save(out, "PNG")
print("saved:", out)
