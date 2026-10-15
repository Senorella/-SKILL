# -*- coding: utf-8 -*-
"""
make_poster_mono_variants.py — 单色矿物系统（模仿「亚洲象」十字绣海报感觉）
核心：白纸底 + 整张海报只用一个矿物色——底图点阵由该色按明度染色（深色点→浅色点），
标题/传播语/信息全部同色系不同明度，形成高度统一的版面。
输出：output/dunhuang_typographic_halftone/mono_variants/*.png
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps
import qrcode
import os
from typographic_halftone import render_size_halftone, GI

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "dunhuang_typographic_halftone", "mono_variants")
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

def global_pad_light(img, alpha=130):
    overlay = Image.new("RGBA", img.size, (255, 255, 255, alpha))
    img.paste(overlay, (0, 0), overlay)

def _whiten(img, thresh=225):
    """把接近白的像素钳制为纯白，消除 gamma/colorize 残留的色偏与灰点。"""
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = px[x, y]
            if r > thresh and g > thresh and b > thresh:
                px[x, y] = (255, 255, 255)
    return img

def _mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ---- 单色方案：hue = 底图染色基准深色 ----
SCHEMES = {
    # M1 石绿（贴「亚洲象」参考）：整版绿
    "M1_石绿单色": dict(hue=(26, 122, 70), paper=(255, 255, 255)),
    # M2 朱砂单色：整版朱砂红
    "M2_朱砂单色": dict(hue=(186, 50, 28), paper=(255, 255, 255)),
    # M3 石青单色：整版石青蓝
    "M3_石青单色": dict(hue=(24, 94, 148), paper=(255, 255, 255)),
}

def render_mono_base(hue, paper):
    """底图：半调 → 反相 → 按单色染色（暗点=深 hue，亮点=纸色）。"""
    src = Image.open(os.path.join(GI, "Full_bleed_poster_background___2026-10-09T15-49-47.png"))
    src = src.convert("L").resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    inv = ImageOps.invert(img).convert("L")
    # 提亮：背景更白、点更通透
    px = inv.load()
    for y in range(H):
        for x in range(W):
            v = px[x, y] / 255.0
            px[x, y] = int((v ** 1.6) * 255)
    colored = ImageOps.colorize(inv, black=hue, white=paper)
    _whiten(colored)
    global_pad_light(colored, alpha=130)
    return colored

def draw_poster(img, S, out_path):
    hue, paper = S["hue"], S["paper"]
    c_title  = _mix(hue, (0, 0, 0), 0.10)    # 标题：比底图最深色再深一档
    c_slogan = _mix(hue, paper, 0.18)        # 传播语：浅一档
    c_soft   = _mix(hue, paper, 0.42)        # 英文/次要：更浅
    c_grey   = _mix(hue, (120, 120, 120), 0.45)  # 信息灰（带色相倾向）

    d = ImageDraw.Draw(img)

    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=c_soft, anchor="ra")
    d.text((984, 74), DATE, font=f(F_AA, 54), fill=c_title, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=c_slogan, anchor="ra")

    d.text((40, 220), "壁上万象：", font=f(F_ZIYU, 236), fill=c_title)
    d.text((40, 470), TITLE_S, font=f(F_ZIYU, 182), fill=c_title)

    d.text((44, 690), SLOGAN, font=f(F_YHBD, 42), fill=c_slogan)
    tracked(d, (44, 748), EN, f(F_DENGB, 17), c_soft, 0.08)

    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=c_soft)
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=c_title)

    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=c_soft)
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=c_grey)

    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (900, 1414), 90)
    d.text((892, 1424), CTA, font=f(F_YHBD, 24), fill=c_title, anchor="ra")
    d.text((892, 1462), CTA_SUB, font=f(F_YH, 17), fill=c_slogan, anchor="ra")

    img.save(out_path, "PNG")
    print("saved:", out_path)

def main():
    bases = {name: render_mono_base(S["hue"], S["paper"]) for name, S in SCHEMES.items()}
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
