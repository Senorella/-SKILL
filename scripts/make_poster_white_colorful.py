# -*- coding: utf-8 -*-
"""
make_poster_white_colorful.py — 纯白底 + 彩色点阵底图 + 黑/深色文字
参考：韩国毕业展（鲜艳绿 mosaic + 粉彩纸屑 + 黑字）、骏马展（多彩笔触 + 红字）。
方案 A：主体单一鲜艳绿点阵 + 四周稀疏粉彩纸屑块，黑字，日期点缀色。
方案 B：全彩敦煌色 mosaic（朱砂/橙/金/石绿/石青/紫/桃粉按亮度加权），黑字，红日期。
输出：output/dunhuang_typographic_halftone/white_colorful/*.png
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps
import qrcode
import os, random
from typographic_halftone import render_size_halftone, GI

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "dunhuang_typographic_halftone", "white_colorful")
os.makedirs(OUT, exist_ok=True)

W, H = 1024, 1536
CELL = 7

F_ZIYU  = os.path.join(ROOT, "fonts", "ZiYuQuWeiXiangSu.ttf")
F_AA    = os.path.join(ROOT, "fonts", "AaXiaoGouGuaiGuaiXiangSuTi.ttf")
F_YHBD  = "C:/Windows/Fonts/msyhbd.ttc"
F_YH    = "C:/Windows/Fonts/msyh.ttc"
F_DENGB = "C:/Windows/Fonts/Dengb.ttf"

def f(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)

def tracked(d, xy, text, font, fill, tracking=0.10):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        w = d.textlength(ch, font=font)
        x += w + w * tracking

TITLE_S = "敦煌色彩数字沉浸展"
EN      = "MURAL UNIVERSE: DUNHUANG COLOR DIGITAL IMMERSIVE EXHIBITION"
SLOGAN  = "在流动的色彩中，走近千年的想象"
CTA     = "预约观展"
CTA_SUB = "扫码去微信小程序预约"
CTA_URL = "https://weixin.qq.com"
HOURS   = "周二至周日 10:00–20:00"
VENUE   = "城市文化中心一层沉浸展厅"
HOST    = "城市文化中心"
DATE    = "2026.11.08 — 2027.01.18"
BLACK   = (17, 17, 17)

def make_qr(data, box_size=6, border=2):
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

def paste_qr(img, qr_img, xy, size):
    q = qr_img.resize((size, size), Image.LANCZOS)
    x, y = xy
    img.paste((255, 255, 255), (x - 4, y - 4, x + size + 4, y + size + 4))
    img.paste(q, (x, y))

def _mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def get_block_l():
    """半调 → 反相 → 按 CELL 网格求块均值（值越小=点越浓/主体越亮区）。"""
    if "bl" in _cache:
        return _cache["bl"]
    src = Image.open(os.path.join(GI, "Full_bleed_poster_background___2026-10-09T15-49-47.png"))
    src = src.convert("L").resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=CELL, contrast=1.35, ink_gamma=0.85, rim=True)
    inv = ImageOps.invert(img).convert("L")
    gw, gh = W // CELL, H // CELL
    small = inv.resize((gw, gh), Image.BOX)
    _cache["bl"] = small
    return small

_cache = {}

def draw_text_block(img, d, date_color):
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=(120, 118, 114), anchor="ra")
    d.text((984, 74), DATE, font=f(F_AA, 54), fill=date_color, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=(90, 88, 85), anchor="ra")

    d.text((40, 220), "壁上万象：", font=f(F_ZIYU, 236), fill=BLACK)
    d.text((40, 470), TITLE_S, font=f(F_ZIYU, 182), fill=BLACK)

    d.text((44, 690), SLOGAN, font=f(F_YHBD, 42), fill=(70, 68, 66))
    tracked(d, (44, 748), EN, f(F_DENGB, 17), (150, 148, 145), 0.08)

    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=(120, 118, 114))
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=BLACK)

    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=(120, 118, 114))
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=(150, 148, 145))

    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (900, 1414), 90)
    d.text((892, 1424), CTA, font=f(F_YHBD, 24), fill=date_color, anchor="ra")
    d.text((892, 1462), CTA_SUB, font=f(F_YH, 17), fill=(90, 88, 85), anchor="ra")

# ---------- 方案 A：鲜艳绿主色 + 粉彩纸屑 ----------
GREEN   = (0, 200, 90)
CONFETTI = [(255, 122, 178), (255, 196, 64), (110, 180, 255), (255, 140, 90), (150, 220, 120)]

def render_a():
    small = get_block_l().copy()
    gw, gh = small.size
    sp = small.load()
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(7)
    for gy in range(gh):
        for gx in range(gw):
            v = sp[gx, gy]          # 反相后：值越小=点越浓
            cx, cy = gx * CELL + CELL // 2, gy * CELL + CELL // 2
            if v < 235:
                # 主体：鲜艳绿，浓度差带来深浅
                col = _mix(GREEN, (255, 255, 255), min(0.65, (v - 60) / 260))
                r = max(1.2, CELL * 0.42 * (1 - v / 300))
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
            elif rnd.random() < 0.012:
                # 纸屑：稀疏粉彩小点散布白区
                col = _mix(rnd.choice(CONFETTI), (255, 255, 255), rnd.uniform(0.1, 0.45))
                r = rnd.uniform(1.5, 3.2)
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    return img

def poster_a(out_path):
    img = render_a()
    d = ImageDraw.Draw(img)
    draw_text_block(img, d, date_color=GREEN)
    img.save(out_path, "PNG")
    print("saved:", out_path)

# ---------- 方案 B：全彩敦煌 mosaic ----------
PALETTE = [
    ((227, 57, 17), 0.24),   # 朱砂
    ((255, 122, 0), 0.20),   # 橙
    ((255, 179, 0), 0.18),   # 金
    ((0, 181, 120), 0.16),   # 石绿
    ((45, 125, 210), 0.12),  # 石青
    ((142, 91, 217), 0.06),  # 紫
    ((255, 123, 172), 0.04), # 桃粉
]
RED = (208, 32, 16)

def _pick_color(rnd, concentration):
    """按浓度（0~1，越大越浓）加权选色；浅处向白混合。"""
    total = sum(w for _, w in PALETTE)
    t = rnd.uniform(0, total)
    acc = 0
    for c, w in PALETTE:
        acc += w
        if t <= acc:
            return _mix(c, (255, 255, 255), max(0.0, 0.55 - concentration * 0.55))
    return _mix(PALETTE[0][0], (255, 255, 255), 0.5)

def render_b():
    small = get_block_l().copy()
    gw, gh = small.size
    sp = small.load()
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(11)
    for gy in range(gh):
        for gx in range(gw):
            v = sp[gx, gy]
            if v >= 245:
                continue
            # 浓度：点越浓（v 越小）颜色越饱和、块越大
            conc = max(0.0, min(1.0, (248 - v) / 190))
            col = _pick_color(rnd, conc)
            r = max(1.0, CELL * 0.44 * conc + 0.6)
            cx, cy = gx * CELL + CELL // 2, gy * CELL + CELL // 2
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    return img

def poster_b(out_path):
    img = render_b()
    d = ImageDraw.Draw(img)
    draw_text_block(img, d, date_color=RED)
    img.save(out_path, "PNG")
    print("saved:", out_path)

def main():
    poster_a(os.path.join(OUT, "dunhuang_typo_A_鲜艳绿纸屑.png"))
    poster_b(os.path.join(OUT, "dunhuang_typo_B_全彩马赛克.png"))
    files = sorted(n for n in os.listdir(OUT) if n.endswith(".png") and not n.startswith("_"))
    thumbs = [Image.open(os.path.join(OUT, n)).resize((340, 510)) for n in files]
    sheet = Image.new("RGB", (340 * len(thumbs) + 10 * (len(thumbs) - 1), 510), (60, 60, 60))
    x = 0
    for t in thumbs:
        sheet.paste(t, (x, 0)); x += 350
    sheet.save(os.path.join(OUT, "_compare_sheet.png"))
    print("sheet ok")

if __name__ == "__main__":
    main()
