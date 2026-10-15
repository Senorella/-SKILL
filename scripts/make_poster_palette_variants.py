# -*- coding: utf-8 -*-
"""
make_poster_palette_variants.py — 敦煌矿物色多方案产出
底图渲染一次（变尺寸半调 cell7），复制画布后按不同调色板排字，一次产出多张方案。
配色参考：敦煌包装色卡 / 丝路岩彩 / 青绿山水 / 鼓乐朱砂 等矿物色系，允许超过三色。
输出：output/dunhuang_typographic_halftone/palette_variants/*.png
"""
from PIL import Image, ImageDraw, ImageFont
import qrcode
import os
from typographic_halftone import render_size_halftone, GI

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "dunhuang_typographic_halftone", "palette_variants")
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

# ---- 文案 ----
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

def global_pad(img, alpha=185):
    overlay = Image.new("RGBA", img.size, (10, 10, 10, alpha))
    img.paste(overlay, (0, 0), overlay)

# ---- 调色板方案（敦煌矿物色发散，允许 >3 色）----
PALETTES = {
    # A 窟壁经典：鎏金主 + 石绿/朱砂双色点缀（莫高窟壁最经典组合）
    "A_窟壁经典": dict(
        title=(233, 184, 87), accent=(214, 96, 59), secondary=(95, 184, 154),
        white=(242, 239, 230), grey=(140, 138, 130)),
    # B 青绿山水：石青石绿双主色（丝路岩彩画青绿飘带）
    "B_青绿山水": dict(
        title=(82, 199, 176), accent=(61, 126, 166), secondary=(217, 164, 65),
        white=(239, 234, 224), grey=(128, 132, 128)),
    # C 朱砂盛世：朱砂红主 + 杏橙/鎏金辅助（鼓乐海报暖色系）
    "C_朱砂盛世": dict(
        title=(224, 80, 56), accent=(240, 160, 80), secondary=(239, 196, 106),
        white=(245, 240, 232), grey=(150, 130, 118)),
    # D 土黄岩彩：赭石/沙金大地色 + 灰绿点缀（第X窟土黄底岩彩）
    "D_土黄岩彩": dict(
        title=(201, 138, 75), accent=(229, 192, 138), secondary=(127, 160, 140),
        white=(240, 234, 222), grey=(138, 128, 112)),
    # E 鎏金+石青双色：克制雅致（藏蓝深底配鎏金提亮）
    "E_鎏金石青": dict(
        title=(233, 184, 87), accent=(77, 138, 166), secondary=(95, 184, 154),
        white=(238, 234, 226), grey=(135, 138, 132)),
}

def render_base():
    src = Image.open(os.path.join(GI, "Full_bleed_poster_background___2026-10-09T15-49-47.png"))
    src = src.convert("L").resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    global_pad(img, alpha=185)
    return img

def draw_poster(img, P, out_path):
    d = ImageDraw.Draw(img)

    # 展期模块（右上）
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=P["grey"], anchor="ra")
    d.text((984, 74), DATE, font=f(F_AA, 54), fill=P["title"], anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=P["white"], anchor="ra")

    # 展览名称（第一焦点）：双行双色分层——主行 title，副行 secondary 点缀色
    d.text((40, 220), "壁上万象：", font=f(F_ZIYU, 236), fill=P["title"])
    d.text((40, 470), TITLE_S, font=f(F_ZIYU, 182), fill=P["title"])

    # 传播语（点缀矿物色）+ 英文
    d.text((44, 690), SLOGAN, font=f(F_YHBD, 42), fill=P["secondary"])
    tracked(d, (44, 748), EN, f(F_DENGB, 17), P["grey"], 0.08)

    # 地点模块
    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=P["grey"])
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=P["white"])

    # 主办方模块
    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=P["grey"])
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=P["grey"])

    # 二维码 + CTA
    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (900, 1414), 90)
    d.text((892, 1424), CTA, font=f(F_YHBD, 24), fill=P["accent"], anchor="ra")
    d.text((892, 1462), CTA_SUB, font=f(F_YH, 17), fill=P["white"], anchor="ra")

    img.save(out_path, "PNG")
    print("saved:", out_path)

def main():
    base = render_base()
    for name, P in PALETTES.items():
        draw_poster(base.copy(), P, os.path.join(OUT, f"dunhuang_typo_{name}.png"))

if __name__ == "__main__":
    main()
