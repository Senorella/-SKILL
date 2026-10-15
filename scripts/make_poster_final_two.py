# -*- coding: utf-8 -*-
"""
make_poster_final_two.py — 最终两方案
S1 单色浅底：底图点阵为同一敦煌色的浅色版（像 TRY NEW THINGS 的浅蓝点阵），
   文字用该色全饱和版压纯白底，冲击力强。
S2 彩色点阵：底图为高饱和敦煌彩色渐变（深红→橙→金，金鱼式 mosaic），
   文字纯黑 #111，底色纯白。
输出：output/dunhuang_typographic_halftone/final_two/*.png
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps
import qrcode
import os, random
from typographic_halftone import render_size_halftone, GI
import sys

# 底图源：默认飞天，可用命令行参数切换为其他素材文件名
DEFAULT_SRC = "Full_bleed_poster_background___2026-10-09T15-49-47.png"
SRC = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "dunhuang_typographic_halftone", "final_two")
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

def global_pad_light(img, alpha=100):
    overlay = Image.new("RGBA", img.size, (255, 255, 255, alpha))
    img.paste(overlay, (0, 0), overlay)

def _whiten(img, thresh=228, inv=None, l_thresh=None):
    """钳制近白像素；若提供 inv（原始亮度图），亮度高于 l_thresh 的像素强制纯白。"""
    px = img.load()
    if inv is not None and l_thresh is not None:
        lp = inv.load()
        for y in range(img.height):
            for x in range(img.width):
                if lp[x, y] > l_thresh:
                    px[x, y] = (255, 255, 255)
                else:
                    r, g, b = px[x, y]
                    if r > thresh and g > thresh and b > thresh:
                        px[x, y] = (255, 255, 255)
        return img
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = px[x, y]
            if r > thresh and g > thresh and b > thresh:
                px[x, y] = (255, 255, 255)
    return img

def _mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

_inv_cache = {}
def get_inv_l():
    """半调渲染一次 → 反相 L 图缓存复用。"""
    if "l" not in _inv_cache:
        src = Image.open(os.path.join(GI, SRC))
        src = src.convert("L").resize((W, H), Image.LANCZOS)
        img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
        _inv_cache["l"] = ImageOps.invert(img).convert("L")
    return _inv_cache["l"].copy()

# ================= S1 单色浅底 =================
S1_HUES = {
    "S1a_单色电光蓝": dict(hue=(43, 43, 224)),
    "S1b_单色朱砂":   dict(hue=(224, 58, 16)),
    "S1c_单色石绿":   dict(hue=(0, 168, 66)),
}

def render_s1(hue):
    """浅色点阵（hue 与白 55% 混合）+ 全饱和文字。"""
    inv = get_inv_l()
    # 强提亮：点阵整体变浅（背景浅、密度低）
    px = inv.load()
    for y in range(H):
        for x in range(W):
            v = px[x, y] / 255.0
            px[x, y] = int((v ** 2.3) * 255)
    light_hue = _mix(hue, (255, 255, 255), 0.45)   # 染色最深点也是浅色
    img = ImageOps.colorize(inv, black=light_hue, white=(255, 255, 255))
    _whiten(img)
    global_pad_light(img, alpha=140)   # 高透明度柔光层：底图点阵进一步压浅
    return img.convert("RGB")

def draw_s1(img, hue, out_path):
    d = ImageDraw.Draw(img)
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=_mix(hue, (255,255,255), 0.35), anchor="ra")
    d.text((984, 74), DATE, font=f(F_AA, 54), fill=hue, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=_mix(hue, (255,255,255), 0.25), anchor="ra")

    d.text((40, 220), "壁上万象：", font=f(F_ZIYU, 236), fill=hue, stroke_width=1, stroke_fill=hue)
    d.text((40, 470), TITLE_S, font=f(F_ZIYU, 182), fill=hue, stroke_width=1, stroke_fill=hue)

    d.text((44, 690), SLOGAN, font=f(F_YHBD, 42), fill=hue)
    tracked(d, (44, 748), EN, f(F_DENGB, 17), _mix(hue, (255,255,255), 0.4), 0.08)

    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=_mix(hue, (255,255,255), 0.35))
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=hue)

    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=_mix(hue, (255,255,255), 0.35))
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=_mix(hue, (255,255,255), 0.3))

    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=hue, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=_mix(hue, (255,255,255), 0.25), anchor="ra")

    img.save(out_path, "PNG")
    print("saved:", out_path)

# ================= S2 彩色点阵 + 黑字 =================
def render_s2():
    """金鱼式 mosaic：深红→橙→金 渐变染色 + 4px 块随机亮度抖动制造多彩像素感。"""
    inv = get_inv_l()
    rnd = random.Random(42)
    px = inv.load()
    # 4x4 块级亮度抖动（mosaic 多彩感），并整体提亮去灰底
    for by in range(0, H, 4):
        for bx in range(0, W, 4):
            j = rnd.uniform(-0.05, 0.05)
            for y in range(by, min(by + 4, H)):
                for x in range(bx, min(bx + 4, W)):
                    v = px[x, y] / 255.0
                    v = max(0.0, min(1.0, v + j))
                    px[x, y] = int((v ** 1.8) * 255)
    # 敦煌暖色渐变：暗=深朱砂 → 中=橙 → 亮=金/白
    img = ImageOps.colorize(inv, black=(200, 38, 8), white=(255, 255, 255),
                            mid=(255, 116, 0), midpoint=126)
    _whiten(img, thresh=240, inv=inv, l_thresh=175)   # 亮度>175 的区域强制纯白
    return img.convert("RGB")

def draw_s2(img, out_path):
    d = ImageDraw.Draw(img)
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=BLACK, anchor="ra")
    d.text((984, 74), DATE, font=f(F_AA, 54), fill=BLACK, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=BLACK, anchor="ra")

    d.text((40, 220), "壁上万象：", font=f(F_ZIYU, 236), fill=BLACK, stroke_width=1, stroke_fill=BLACK)
    d.text((40, 470), TITLE_S, font=f(F_ZIYU, 182), fill=BLACK, stroke_width=1, stroke_fill=BLACK)

    d.text((44, 690), SLOGAN, font=f(F_YHBD, 42), fill=BLACK)
    tracked(d, (44, 748), EN, f(F_DENGB, 17), _mix(BLACK, (255,255,255), 0.45), 0.08)

    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=BLACK)
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=BLACK)

    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=BLACK)
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=_mix(BLACK, (255,255,255), 0.35))

    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=BLACK, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=BLACK, anchor="ra")

    img.save(out_path, "PNG")
    print("saved:", out_path)

def main():
    for name, S in S1_HUES.items():
        draw_s1(render_s1(S["hue"]), S["hue"], os.path.join(OUT, f"dunhuang_typo_{name}.png"))
    draw_s2(render_s2(), os.path.join(OUT, "dunhuang_typo_S2_彩色点阵黑字.png"))

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
