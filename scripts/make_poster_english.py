# -*- coding: utf-8 -*-
"""
make_poster_english.py — 英文版海报（保持版式/配色不变，文案换英文）
- 版式A：满版黑底石绿（佛像底图，复用 make_poster_typographic 构图）
- 版式B：藻井左置露白（纹样底图，复用 v4.14 构图）
输出：output/dunhuang_typographic_halftone/english/*.png
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode
import os
from typographic_halftone import render_size_halftone, GI

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "dunhuang_typographic_halftone", "english")
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

# ---- 英文文案 ----
TITLE_A  = "Visions on the Wall:"          # 展览名称 第一行
TITLE_B  = "An Immersive Digital Exhibition"  # 第二行
TITLE_C  = "of Dunhuang Colors"            # 第三行
SLOGAN   = "Step into a thousand years of imagination through moving color"
DATE     = "8 November 2026 – 18 January 2027"
HOURS    = "Tuesday–Sunday, 10:00–20:00"
VENUE    = "Immersive Hall, Level 1, City Cultural Center"
HOST     = "City Cultural Center"
CTA      = "Reserve your visit"
CTA_SUB  = "Scan to reserve via WeChat Mini Program"
CTA_URL  = "https://weixin.qq.com"

# 底图素材
SRC_BUDDHA = "敦煌莫高窟彩塑菩萨像_慈悲安详的面容与宝冠璎珞_黑白灰单色__2026-10-09T19-16-07.png"
SRC_PATTERN = "敦煌莫高窟藻井顶部的华丽纹样_莲花纹与卷草纹交织_黑白灰单色_2026-10-09T19-16-03.png"

def f(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)

def tracked(d, xy, text, font, fill, tracking=0.08):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        w = d.textlength(ch, font=font)
        x += w + w * tracking

def tracked_r(d, xy, text, font, fill, tracking=0.08):
    """右对齐字距排列。"""
    total = sum(d.textlength(ch, font=font) * (1 + tracking) for ch in text) \
            - d.textlength(text[-1], font=font) * tracking
    x = xy[0] - total
    for ch in text:
        d.text((x, xy[1]), ch, font=font, fill=fill)
        w = d.textlength(ch, font=font)
        x += w + w * tracking

def make_qr(data, box_size=6, border=2):
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=box_size, border=border)
    qr.add_data(data); qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

def paste_qr(img, qr_img, xy, size):
    q = qr_img.resize((size, size), Image.LANCZOS)
    x, y = xy
    img.paste((255, 255, 255), (x - 4, y - 4, x + size + 4, y + size + 4))
    img.paste(q, (x, y))

def global_pad(img, alpha=150):
    overlay = Image.new("RGBA", img.size, (10, 10, 10, alpha))
    img.paste(overlay, (0, 0), overlay)

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

def render_full(src_name):
    src = Image.open(os.path.join(GI, src_name))
    src = src.convert("L").resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    global_pad(img, alpha=190)
    return img

# ================= 版式A：满版黑底石绿（佛像） =================
def plan_a():
    img = render_full(SRC_BUDDHA)
    d = ImageDraw.Draw(img)

    # 时间模块（右上）
    d.text((984, 40), "Time", font=f(F_DENGB, 22), fill=GREY_D, anchor="ra")
    d.text((984, 74), DATE, font=f(F_AA, 44), fill=GOLD, anchor="ra")
    d.text((984, 140), HOURS, font=f(F_DENGB, 24), fill=GREY_W, anchor="ra")

    # 标题（第一焦点，主标题两行超大 + 副题中号，参照 Theatronic 层级）
    gradient_text(img, (40, 190), "Visions on the", f(F_ZIYU, 170),
                  JADE_TOP, JADE_BOT, glow=JADE_BOT, glow_alpha=22, glow_blur=10)
    gradient_text(img, (40, 370), "Wall:", f(F_ZIYU, 170),
                  JADE_TOP, JADE_BOT, glow=JADE_BOT, glow_alpha=22, glow_blur=10)
    gradient_text(img, (40, 560), "An Immersive Digital Exhibition", f(F_ZIYU, 96),
                  JADE_TOP, JADE_BOT, glow=JADE_BOT, glow_alpha=22, glow_blur=10)
    gradient_text(img, (40, 680), "of Dunhuang Colors", f(F_ZIYU, 96),
                  JADE_TOP, JADE_BOT, glow=JADE_BOT, glow_alpha=22, glow_blur=10)

    # 传播语（两行）
    d.text((44, 830), "Step into a thousand years of imagination", font=f(F_YHBD, 34), fill=GOLD)
    d.text((44, 882), "through moving color", font=f(F_YHBD, 34), fill=GOLD)

    # 地点 / 主办（左下）
    d.text((44, 1330), "Location", font=f(F_DENGB, 22), fill=GREY_D)
    d.text((44, 1364), VENUE, font=f(F_YHBD, 28), fill=GREY_W)
    d.text((44, 1428), "Organizer", font=f(F_DENGB, 22), fill=GREY_D)
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=GREY_D)

    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 22), fill=BLUE, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 15), fill=GREY_W, anchor="ra")

    out = os.path.join(OUT, "dunhuang_english_A_buddha.png")
    img.save(out, "PNG")
    print("saved:", out)

# ================= 版式B：藻井左置露白 =================
def plan_b():
    src = Image.open(os.path.join(GI, SRC_PATTERN)).convert("L")
    w, h = src.size
    side = min(w, h)
    cx, cy = w // 2, int(h * 0.38)
    half = side // 2
    sq = src.crop((max(0, cx - half), max(0, cy - half),
                   min(w, cx + half), min(h, cy + half)))
    big_w = int(W * 1.0)
    hal = render_size_halftone(sq, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    hal = hal.convert("RGB").resize((big_w, int(big_w * sq.size[1] / sq.size[0])), Image.LANCZOS)

    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    offset_x = int(W * 0.33) - big_w // 2
    offset_y = H // 2 - hal.size[1] // 2
    canvas.paste(hal, (offset_x, offset_y))
    global_pad(canvas, alpha=185)
    d = ImageDraw.Draw(canvas)

    # 时间模块（右上）
    d.text((984, 40), "Time", font=f(F_DENGB, 22), fill=GREY_D, anchor="ra")
    d.text((984, 74), DATE, font=f(F_AA, 44), fill=GOLD, anchor="ra")
    d.text((984, 140), HOURS, font=f(F_DENGB, 24), fill=GREY_W, anchor="ra")

    # 标题（右侧右对齐，主标题两行超大 + 副题）
    gradient_text(canvas, (984, 360), "Visions on the", f(F_ZIYU, 150),
                  JADE_TOP, JADE_BOT, anchor="ra", glow=JADE_BOT, glow_alpha=22, glow_blur=10)
    gradient_text(canvas, (984, 520), "Wall:", f(F_ZIYU, 150),
                  JADE_TOP, JADE_BOT, anchor="ra", glow=JADE_BOT, glow_alpha=22, glow_blur=10)
    gradient_text(canvas, (984, 690), "An Immersive Digital", f(F_ZIYU, 84),
                  JADE_TOP, JADE_BOT, anchor="ra", glow=JADE_BOT, glow_alpha=22, glow_blur=10)
    gradient_text(canvas, (984, 800), "Exhibition of Dunhuang Colors", f(F_ZIYU, 84),
                  JADE_TOP, JADE_BOT, anchor="ra", glow=JADE_BOT, glow_alpha=22, glow_blur=10)

    # 传播语（两行）
    d.text((984, 940), "Step into a thousand years of imagination", font=f(F_YHBD, 30), fill=GOLD, anchor="ra")
    d.text((984, 986), "through moving color", font=f(F_YHBD, 30), fill=GOLD, anchor="ra")

    # 地点 / 主办（右下）
    d.text((984, 1300), "Location", font=f(F_DENGB, 22), fill=GREY_D, anchor="ra")
    d.text((984, 1334), VENUE, font=f(F_YHBD, 28), fill=GREY_W, anchor="ra")
    d.text((984, 1416), "Organizer", font=f(F_DENGB, 22), fill=GREY_D, anchor="ra")
    d.text((984, 1450), HOST, font=f(F_YH, 24), fill=GREY_D, anchor="ra")

    qr = make_qr(CTA_URL)
    paste_qr(canvas, qr, (60, 1400), 64)
    d.text((140, 1404), CTA, font=f(F_YHBD, 22), fill=BLUE)
    d.text((140, 1442), CTA_SUB, font=f(F_YH, 15), fill=GREY_D)

    out = os.path.join(OUT, "dunhuang_english_B_pattern.png")
    canvas.save(out, "PNG")
    print("saved:", out)

if __name__ == "__main__":
    plan_a()
    plan_b()
