# -*- coding: utf-8 -*-
"""
make_poster_typographic.py — 字符半调印刷肖像正式海报（飞天主体）
底图：typographic_halftone.render_halftone（B 高对比参数，cell12）
排版：沿用 v4 层级与布局（标题一体化/超大标题/右下角二维码），配色适配纸色底：
      墨黑 #111111（标题/信息）+ 石青蓝 #2878E8（预约/日期）+ 中灰 #777777（次要）
输出：output/dunhuang_typographic_halftone/dunhuang_typo_A_飞天主体.png
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode
import os
from typographic_halftone import render_size_halftone, GI
import sys

# 底图源：默认飞天，可用命令行参数切换为其他素材文件名
DEFAULT_SRC = "Full_bleed_poster_background___2026-10-09T15-49-47.png"
SRC = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "dunhuang_typographic_halftone")
os.makedirs(OUT, exist_ok=True)

W, H = 1024, 1536
# ---- 黑底高饱和敦煌色（光泽渐变版）----
GOLD_TOP  = (255, 216, 94)    # 鎏金渐变·亮端
GOLD_BOT  = (240, 176, 62)    # 鎏金渐变·深端（色差收窄）
JADE_TOP  = (84, 240, 188)    # 高饱和石绿渐变·亮端
JADE_BOT  = (24, 178, 136)    # 高饱和石绿渐变·深端（色差收窄）
GOLD      = (255, 203, 90)    # 纯色鎏金（小字用）
BLUE      = (255, 92, 66)     # 亮朱砂红：预约观展
GREY_W    = (238, 238, 238)   # 亮灰白：传播语/时间/地点
GREY_D    = (150, 150, 150)   # 中灰：主办方/英文

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

def gradient_text(img, xy, text, font, c_top, c_bottom,
                  anchor=None, glow=None, glow_alpha=70, glow_blur=10, stroke=0):
    """光泽感渐变文字：垂直渐变填充 + 可选同色系外发光（模拟釉面光泽）。
    glow: (r,g,b) 光晕色，None 则不加；stroke: 同色描边宽度(px)用于加粗笔画。"""
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
    # 外发光（同色系柔光，增强光泽层次）
    if glow:
        halo = mask.filter(ImageFilter.GaussianBlur(glow_blur))
        halo_col = Image.new("RGB", img.size, glow)
        img.paste(halo_col, (0, 0), halo.point(lambda v: v * glow_alpha // 255))
    img.paste(grad, (0, 0), mask)

# ---- 文案 ----
TITLE_S = "敦煌色彩数字沉浸展"
EN      = "MURAL UNIVERSE: DUNHUANG COLOR DIGITAL IMMERSIVE EXHIBITION"
SLOGAN  = "在流动的色彩中，走近千年的想象"
CTA     = "预约观展"
CTA_SUB = "扫码去微信小程序预约"
CTA_URL = "https://weixin.qq.com"
PERIOD  = "2026.11.08 — 2027.01.18"
EN_DATE = "NOV 08, 2026 — JAN 18, 2027"
HOURS   = "周二至周日 10:00–20:00"
HOURS_EN = "TUE–SUN 10:00–20:00"
VENUE   = "城市文化中心一层沉浸展厅"
HOST    = "城市文化中心"

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

def global_pad(img, alpha=150):
    """全图一张统一的黑底柔光层：在贴任何文字前铺一次，覆盖整幅画面。
    避免多块局部垫层互相重叠/分隔产生明暗接缝。"""
    overlay = Image.new("RGBA", img.size, (10, 10, 10, alpha))
    img.paste(overlay, (0, 0), overlay)


def main():
    # ---- 底图：字符半调（反白：黑底 + 浅色字符，B 高对比参数）----
    src = Image.open(os.path.join(GI, SRC))
    src = src.convert("L").resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    # 全图统一柔光层：贴文字前只铺一张，覆盖整幅，避免局部垫层重叠/分隔
    global_pad(img, alpha=190)
    d = ImageDraw.Draw(img)

    # ---- 展期模块（右上角分区）：纯色鎏金 ----
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=GREY_D, anchor="ra")
    d.text((984, 74), "2026.11.08 — 2027.01.18", font=f(F_AA, 54), fill=GOLD, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=GREY_W, anchor="ra")

    # ---- 展览名称（第一焦点）：高饱和石绿 + 微弱高光（仅标题保留光泽）----
    gradient_text(img, (40, 220), "壁上万象：", f(F_ZIYU, 236),
                  JADE_TOP, JADE_BOT, glow=JADE_BOT, glow_alpha=22, glow_blur=10, stroke=1)
    gradient_text(img, (40, 470), TITLE_S, f(F_ZIYU, 182),
                  JADE_TOP, JADE_BOT, glow=JADE_BOT, glow_alpha=22, glow_blur=10, stroke=1)

    # 传播语（纯色鎏金）+ 英文标题行
    d.text((44, 690), SLOGAN, font=f(F_YHBD, 42), fill=GOLD)
    tracked(d, (44, 748), EN, f(F_DENGB, 17), GREY_D, 0.08)

    # ---- 地点模块（左下分区）----
    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=GREY_D)
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=GREY_W)

    # ---- 主办方模块（左下独立分区）----
    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=GREY_D)
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=GREY_D)

    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=BLUE, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=GREY_W, anchor="ra")

    out = os.path.join(OUT, "dunhuang_typo_A_飞天主体.png")
    img.save(out, "PNG")
    print("saved:", out)

if __name__ == "__main__":
    main()
