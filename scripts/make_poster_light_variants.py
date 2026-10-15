# -*- coding: utf-8 -*-
"""
make_poster_light_variants.py — 白底图 + 鲜艳深色字 敦煌矿物色方案
底图：变尺寸半调渲染后反相 → 白纸 + 深灰墨点；贴文字前铺一张全图白色柔光层（铁律）。
文字：鲜艳深色矿物色（朱砂/石青/石绿/靛蓝/赭金），允许 >3 色。
输出：output/dunhuang_typographic_halftone/light_variants/*.png
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps
import qrcode
import os
from typographic_halftone import render_size_halftone, GI
import sys

# 底图源：默认飞天，可用命令行参数切换为其他素材文件名
DEFAULT_SRC = "Full_bleed_poster_background___2026-10-09T15-49-47.png"
SRC = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "dunhuang_typographic_halftone", "light_variants")
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

def global_pad_light(img, alpha=205):
    """白底海报的全图柔光层（铁律：仅一张、全图、贴文字前铺完）：
    白色半透明层压浅墨点，给文字留出干净前景。"""
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

# ---- 白底调色板（鲜艳深色矿物字）----
PALETTES = {
    # W1 朱砂鼓乐：朱砂红主 + 石绿/赭金（对应鼓乐海报暖色）
    "W1_朱砂鼓乐": dict(
        title=(208, 32, 16), secondary=(0, 150, 110), accent=(186, 122, 6),
        grey=(105, 100, 92)),
    # W2 石青青绿：石青蓝主 + 朱砂/石绿（青绿山水冷色）
    "W2_石青青绿": dict(
        title=(0, 110, 190), secondary=(210, 45, 30), accent=(0, 150, 110),
        grey=(98, 106, 110)),
    # W3 岩彩暖调：赭红主 + 石青/鎏金（丝路岩彩大地暖色）
    "W3_岩彩暖调": dict(
        title=(190, 58, 18), secondary=(0, 110, 160), accent=(186, 130, 0),
        grey=(112, 100, 88)),
    # W4 靛蓝金：靛蓝主 + 朱砂/石绿（沉稳雅致对比）
    "W4_靛蓝金": dict(
        title=(40, 58, 150), secondary=(210, 45, 30), accent=(0, 150, 110),
        grey=(102, 102, 106)),
}

def render_base_light():
    src = Image.open(os.path.join(GI, SRC))
    src = src.convert("L").resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = ImageOps.invert(img)          # 反相：黑底墨点 → 白纸深点
    img = img.convert("L")
    # 提亮曲线：gamma>1 把灰点推向白，画面明快（保留中灰主体层次）
    px = img.load()
    for y in range(H):
        for x in range(W):
            v = px[x, y] / 255.0
            px[x, y] = int((v ** 1.7) * 255)
    img = img.convert("RGB")
    _whiten(img)
    global_pad_light(img, alpha=205)
    return img

def draw_poster(img, P, out_path):
    d = ImageDraw.Draw(img)

    # 展期模块（右上）
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=P["grey"], anchor="ra")
    d.text((984, 74), DATE, font=f(F_AA, 54), fill=P["title"], anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=P["grey"], anchor="ra")

    # 展览名称（第一焦点）
    d.text((40, 220), "壁上万象：", font=f(F_ZIYU, 236), fill=P["title"], stroke_width=1, stroke_fill=P["title"])
    d.text((40, 470), TITLE_S, font=f(F_ZIYU, 182), fill=P["title"], stroke_width=1, stroke_fill=P["title"])

    # 传播语（第二矿物色）+ 英文
    d.text((44, 690), SLOGAN, font=f(F_YHBD, 42), fill=P["secondary"])
    tracked(d, (44, 748), EN, f(F_DENGB, 17), P["grey"], 0.08)

    # 地点模块
    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=P["grey"])
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=P["title"])

    # 主办方模块
    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=P["grey"])
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=P["grey"])

    # 二维码 + CTA
    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=P["accent"], anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=P["grey"], anchor="ra")

    img.save(out_path, "PNG")
    print("saved:", out_path)

def main():
    base = render_base_light()
    for name, P in PALETTES.items():
        draw_poster(base.copy(), P, os.path.join(OUT, f"dunhuang_typo_{name}.png"))

    # 对比拼图
    from PIL import Image as I
    files = [n for n in os.listdir(OUT) if n.endswith(".png") and not n.startswith("_")]
    files.sort()
    thumbs = [I.open(os.path.join(OUT, n)).resize((256, 384)) for n in files]
    sheet = I.new("RGB", (256 * len(thumbs) + 8 * (len(thumbs) - 1), 384), (60, 60, 60))
    x = 0
    for t in thumbs:
        sheet.paste(t, (x, 0)); x += 264
    sheet.save(os.path.join(OUT, "_compare_sheet.png"))
    print("sheet ok")

if __name__ == "__main__":
    main()
