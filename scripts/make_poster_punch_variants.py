# -*- coding: utf-8 -*-
"""
make_poster_punch_variants.py — 高冲击力配色方案（参考 TRY NEW THINGS / 金鱼 / 电光蓝海报）
特点：高饱和高覆盖——点阵浓密染色不透白，文字用同一极高饱和色压白纸；
     含单色强冲与双色撞色两种打法。
输出：output/dunhuang_typographic_halftone/punch_variants/*.png
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps
import qrcode
import os
from typographic_halftone import render_size_halftone, GI

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "dunhuang_typographic_halftone", "punch_variants")
os.makedirs(OUT, exist_ok=True)

W, H = 1024, 1536

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

def global_pad_light(img, alpha=100):
    overlay = Image.new("RGBA", img.size, (255, 255, 255, alpha))
    img.paste(overlay, (0, 0), overlay)

def _whiten(img, thresh=225):
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = px[x, y]
            if r > thresh and g > thresh and b > thresh:
                px[x, y] = (255, 255, 255)
    return img

def _mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ---- 高冲击方案 ----
# hue: 底图染色最深点颜色（高饱和）；text: 文字主色；accent: 撞色点缀（无则同 hue）
SCHEMES = {
    # P1 电光蓝（TRY NEW THINGS 式群青）
    "P1_电光蓝": dict(hue=(43, 43, 224), text=(35, 35, 200), paper=(255, 255, 255)),
    # P2 荧光橙（金鱼式橙红）
    "P2_荧光橙": dict(hue=(255, 72, 0), text=(232, 58, 0), paper=(255, 255, 255)),
    # P3 高饱和绿（亚洲象绿加冲）
    "P3_冲击绿": dict(hue=(0, 168, 66), text=(0, 148, 56), paper=(255, 255, 255)),
    # P4 电光紫红
    "P4_紫红电光": dict(hue=(196, 16, 224), text=(172, 8, 200), paper=(255, 255, 255)),
    # P5 橙蓝撞色：底图金鱼橙，文字电光蓝
    "P5_橙蓝撞色": dict(hue=(255, 92, 10), text=(29, 51, 198), paper=(255, 255, 255)),
}

def render_base(hue, paper):
    src = Image.open(os.path.join(GI, "Full_bleed_poster_background___2026-10-09T15-49-47.png"))
    src = src.convert("L").resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    inv = ImageOps.invert(img).convert("L")
    px = inv.load()
    for y in range(H):
        for x in range(W):
            v = px[x, y] / 255.0
            px[x, y] = int((v ** 1.35) * 255)   # 弱提亮：保留浓密覆盖
    colored = ImageOps.colorize(inv, black=hue, white=paper)
    _whiten(colored)
    global_pad_light(colored, alpha=100)
    return colored

def draw_poster(img, S, out_path):
    text, hue, paper = S["text"], S["hue"], S["paper"]
    c_soft = _mix(text, paper, 0.38)     # 英文/标签
    c_grey = _mix(text, (130, 130, 130), 0.45)

    d = ImageDraw.Draw(img)

    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=c_soft, anchor="ra")
    d.text((984, 74), DATE, font=f(F_AA, 54), fill=text, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=c_grey, anchor="ra")

    d.text((40, 220), "壁上万象：", font=f(F_ZIYU, 236), fill=text)
    d.text((40, 470), TITLE_S, font=f(F_ZIYU, 182), fill=text)

    d.text((44, 690), SLOGAN, font=f(F_YHBD, 42), fill=text)
    tracked(d, (44, 748), EN, f(F_DENGB, 17), c_soft, 0.08)

    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=c_soft)
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=text)

    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=c_soft)
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=c_grey)

    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (900, 1414), 90)
    d.text((892, 1424), CTA, font=f(F_YHBD, 24), fill=text, anchor="ra")
    d.text((892, 1462), CTA_SUB, font=f(F_YH, 17), fill=c_grey, anchor="ra")

    img.save(out_path, "PNG")
    print("saved:", out_path)

def main():
    bases = {name: render_base(S["hue"], S["paper"]) for name, S in SCHEMES.items()}
    for name, S in SCHEMES.items():
        draw_poster(bases[name].copy(), S, os.path.join(OUT, f"dunhuang_typo_{name}.png"))

    files = sorted(n for n in os.listdir(OUT) if n.endswith(".png") and not n.startswith("_"))
    thumbs = [Image.open(os.path.join(OUT, n)).resize((256, 384)) for n in files]
    sheet = Image.new("RGB", (256 * len(thumbs) + 8 * (len(thumbs) - 1), 384), (60, 60, 60))
    x = 0
    for t in thumbs:
        sheet.paste(t, (x, 0)); x += 264
    sheet.save(os.path.join(OUT, "_compare_sheet.png"))
    print("sheet ok")

if __name__ == "__main__":
    main()
