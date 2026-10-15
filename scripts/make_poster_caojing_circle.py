# -*- coding: utf-8 -*-
"""
make_poster_caojing_circle.py — 藻井纹样左置大圆版（参考 Theatronic 半圆构图）
- 左侧：藻井纹样放大后装入大圆，圆心在画面左缘外，仅露出右侧弧面（左侧裁切）
- 右侧：时间模块右上、标题右对齐居中偏上、地点/主办右下环绕留白、二维码右下
- 配色沿用 v4.13 方案一：黑底 + 高饱和石绿标题（微弱高光）+ 鎏金/灰白纯色
输出：output/dunhuang_typographic_halftone/caojing_circle/dunhuang_typo_C_藻井圆构图.png
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode
import os, sys
from typographic_halftone import render_size_halftone, GI

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "dunhuang_typographic_halftone", "caojing_circle")
os.makedirs(OUT, exist_ok=True)

W, H = 1024, 1536
JADE_TOP = (84, 240, 188)
JADE_BOT = (24, 178, 136)
GOLD     = (255, 203, 90)
BLUE     = (255, 92, 66)
GREY_W   = (238, 238, 238)
GREY_D   = (150, 150, 150)

F_ZIYU  = os.path.join(ROOT, "fonts", "ZiYuQuWeiXiangSu.ttf")
F_AA    = os.path.join(ROOT, "fonts", "AaXiaoGouGuaiGuaiXiangSuTi.ttf")
F_YHBD  = "C:/Windows/Fonts/msyhbd.ttc"
F_YH    = "C:/Windows/Fonts/msyh.ttc"
F_DENGB = "C:/Windows/Fonts/Dengb.ttf"

TITLE_S = "敦煌色彩数字沉浸展"
EN      = "MURAL UNIVERSE: DUNHUANG COLOR DIGITAL IMMERSIVE EXHIBITION"
SLOGAN  = "在流动的色彩中，走近千年的想象"
CTA     = "预约观展"
CTA_SUB = "扫码去微信小程序预约"
CTA_URL = "https://weixin.qq.com"
DATE    = "2026.11.08 — 2027.01.18"
HOURS   = "周二至周日 10:00–20:00"
VENUE   = "城市文化中心一层沉浸展厅"
HOST    = "城市文化中心"

SRC = sys.argv[1] if len(sys.argv) > 1 else "敦煌莫高窟藻井顶部的华丽纹样_莲花纹与卷草纹交织_黑白灰单色_2026-10-09T19-16-03.png"

def f(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)

def tracked(d, xy, text, font, fill, tracking=0.10):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        w = d.textlength(ch, font=font)
        x += w + w * tracking

def make_qr(data, box_size=6, border=2):
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=box_size, border=border)
    qr.add_data(data); qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

def paste_qr(img, qr_img, xy, size):
    q = qr_img.resize((size, size), Image.LANCZOS)
    img.paste((255, 255, 255), (x0 - 4, y0 - 4, x0 + size + 4, y0 + size + 4)) if False else None
    img.paste(q, xy)

def gradient_text(img, xy, text, font, c_top, c_bottom,
                  anchor=None, glow=None, glow_alpha=22, glow_blur=10, stroke=1):
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    md.text(xy, text, font=font, fill=255, anchor=anchor,
            stroke_width=stroke, stroke_fill=255)
    bbox = mask.getbbox()
    grad = Image.new("RGB", img.size, c_bottom)
    if bbox:
        y0, y1 = bbox[1], max(bbox[3], bbox[1] + 1)
        gp = grad.load()
        for y in range(y0, y1 + 1):
            t = (y - y0) / max(1, (y1 - y0))
            row = tuple(int(c_top[i] + (c_bottom[i] - c_top[i]) * t) for i in range(3))
            for x in range(img.size[0]):
                gp[x, y] = row
    if glow:
        halo = mask.filter(ImageFilter.GaussianBlur(glow_blur))
        halo_col = Image.new("RGB", img.size, glow)
        img.paste(halo_col, (0, 0), halo.point(lambda v: v * glow_alpha // 255))
    img.paste(grad, (0, 0), mask)

def build_pattern_circle():
    """藻井纹样放大后整体平移到左侧，只有右侧露出画面（不做圆形裁切）。"""
    src = Image.open(os.path.join(GI, SRC)).convert("L")
    w, h = src.size
    # 取莲花中心方形区域（莲花居中略偏上），放大保证纹样足够大
    side = min(w, h)
    cx, cy = w // 2, int(h * 0.38)
    half = side // 2
    sq = src.crop((max(0, cx - half), max(0, cy - half),
                   min(w, cx + half), min(h, cy + half)))
    # 放大到画布同等宽度，让至少 1/2 纹样露出画面
    big_w = int(W * 1.0)
    hal = render_size_halftone(sq, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    hal = hal.convert("RGB").resize((big_w, int(big_w * sq.size[1] / sq.size[0])), Image.LANCZOS)

    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    # 纹样右移量：使纹样主体（莲花中心）落在画面约 1/3 处，左侧约一半纹样露出
    offset_x = int(W * 0.33) - big_w // 2   # 莲花中心对准 x≈W/3
    offset_y = H // 2 - hal.size[1] // 2
    canvas.paste(hal, (offset_x, offset_y))
    return canvas

def main():
    img = build_pattern_circle()
    # 全图一张柔光层（铁律）：压暗纹样，给文字让前景
    overlay = Image.new("RGBA", img.size, (10, 10, 10, 185))
    img.paste(overlay, (0, 0), overlay)
    d = ImageDraw.Draw(img)

    # ---- 时间模块（右上，右对齐）----
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=GREY_D, anchor="ra")
    d.text((984, 74), DATE, font=f(F_AA, 54), fill=GOLD, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=GREY_W, anchor="ra")

    # ---- 标题（右侧，右对齐，第一焦点，字号与正式版一致）----
    gradient_text(img, (984, 400), "壁上万象：", f(F_ZIYU, 236),
                  JADE_TOP, JADE_BOT, anchor="ra", glow=JADE_BOT, glow_alpha=22, glow_blur=10)
    gradient_text(img, (984, 640), TITLE_S, f(F_ZIYU, 182),
                  JADE_TOP, JADE_BOT, anchor="ra", glow=JADE_BOT, glow_alpha=22, glow_blur=10)
    d.text((984, 860), SLOGAN, font=f(F_YHBD, 42), fill=GREY_W, anchor="ra")
    tracked_r(d, (984, 920), EN, f(F_DENGB, 17), GREY_D, 0.08)

    # ---- 地点模块（右下，右对齐，环绕纹样留白）----
    d.text((984, 1310), "地点 Location", font=f(F_YHBD, 22), fill=GREY_D, anchor="ra")
    d.text((984, 1344), VENUE, font=f(F_YHBD, 30), fill=GREY_W, anchor="ra")

    # ---- 主办模块（右下独立分区）----
    d.text((984, 1420), "主办 Organizer", font=f(F_YHBD, 20), fill=GREY_D, anchor="ra")
    d.text((984, 1452), HOST, font=f(F_YH, 22), fill=GREY_D, anchor="ra")

    # ---- 二维码（左下，与右侧文字群平衡）----
    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (60, 1400), 64)
    d.text((140, 1404), CTA, font=f(F_YHBD, 24), fill=BLUE)
    d.text((140, 1442), CTA_SUB, font=f(F_YH, 16), fill=GREY_D)

    out = os.path.join(OUT, "dunhuang_typo_C_藻井圆构图.png")
    img.save(out, "PNG")
    print("saved:", out)

def tracked_r(d, xy, text, font, fill, tracking=0.08):
    """右对齐字距排列：先算总宽再从右往左画。"""
    total = sum(d.textlength(ch, font=font) * (1 + tracking) for ch in text) - d.textlength(text[-1], font=font) * tracking
    x = xy[0] - total
    for ch in text:
        d.text((x, xy[1]), ch, font=font, fill=fill)
        w = d.textlength(ch, font=font)
        x += w + w * tracking

if __name__ == "__main__":
    main()
