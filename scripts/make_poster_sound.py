# -*- coding: utf-8 -*-
"""
make_poster_sound.py — 声音艺术展「你听——城市白噪音采集计划」三版海报
套用 skill v4.24 配色决策卡：文艺实验类 → 黑底 + 声波青/乡愁琥珀 + 中低饱和 + 双色。

文案：你听——城市白噪音采集计划（完整标题两行）
     菜市场的吆喝，也是一种乡愁 / 免费入场 / 2027.3.8—3.30
     周二至周日10:00-20:00 / 城市文化中心一层沉浸展厅

方案一「静听」：戴耳机聆听，黑底反白，声波青 + 琥珀
方案二「市井乡愁」：菜市场吆喝，黑底反白，琥珀 + 声波青
方案三「白噪音采集」：麦克风夜景，黑底反白，银灰 + 声波青
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import qrcode
import os
from typographic_halftone import render_size_halftone, GI
from utils import save_no_overwrite

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "sound_poster")
os.makedirs(OUT, exist_ok=True)

W, H = 1024, 1536

# ---- 声音艺术配色（黑底 → 高饱和 + 高亮度，v4.26）----
WAVE_BLUE = (62, 159, 212)    # 声波青高饱和亮版（S≈0.71，声音科技/频谱）
AMBER     = (224, 160, 60)    # 乡愁琥珀高饱和亮版（S≈0.73，市井暖光）
NOISE_W   = (216, 216, 212)   # 白噪音银灰（灰阶，非彩色，白噪音意象）
MILK      = (238, 238, 236)   # 信息白
GREY_D    = (140, 140, 140)
GREY_B    = (110, 115, 118)

F_ZIYU  = os.path.join(ROOT, "fonts", "ZiYuQuWeiXiangSu.ttf")
F_AA    = os.path.join(ROOT, "fonts", "AaXiaoGouGuaiGuaiXiangSuTi.ttf")
F_YHBD  = "C:/Windows/Fonts/msyhbd.ttc"
F_YH    = "C:/Windows/Fonts/msyh.ttc"
F_DENGB = "C:/Windows/Fonts/Dengb.ttf"

TITLE_L1 = "你听——"
TITLE_L2 = "城市白噪音采集计划"
SLOGAN = "菜市场的吆喝，也是一种乡愁"
EN    = "URBAN WHITE NOISE · A SOUND ART EXHIBITION"
CTA    = "免费入场"
CTA_SUB = "扫码查看展讯"
CTA_URL = "https://weixin.qq.com"
PERIOD = "2027.3.8 — 3.30"
HOURS  = "周二至周日 10:00–20:00"
VENUE  = "城市文化中心一层沉浸展厅"
HOST   = "城市文化中心"

SRC_LISTEN = "Black_and_white_grayscale__clo_2026-10-10T13-14-02.png"
SRC_MARKET = "Black_and_white_grayscale__a_b_2026-10-10T13-14-21.png"
SRC_MIC    = "Black_and_white_grayscale__a_v_2026-10-10T13-14-42.png"

WM_BOX = (880, 1450, 1024, 1536)

def f(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)

def remove_watermark(img):
    x0, y0, x1, y1 = WM_BOX
    w = x1 - x0
    patch = img.crop((x0 - w, y0, x0, y1)).transpose(Image.FLIP_LEFT_RIGHT)
    img.paste(patch, (x0, y0))
    return img

def load_clean(src_name):
    img = Image.open(os.path.join(GI, src_name)).convert("L")
    return remove_watermark(img)

def tracked(d, xy, text, font, fill, tracking=0.10):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        w = d.textlength(ch, font=font)
        x += w + w * tracking

def tracked_center(d, cy, text, font, fill, tracking=0.08):
    total = sum(d.textlength(ch, font=font) * (1 + tracking) for ch in text) \
            - d.textlength(text[-1], font=font) * tracking
    tracked(d, (W // 2 - total / 2, cy), text, font, fill, tracking)

def gradient_text(img, xy, text, font, c_top, c_bottom,
                  anchor=None, glow=None, glow_alpha=18, glow_blur=10, stroke=1):
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

def global_pad_dark(img, alpha=185):
    overlay = Image.new("RGBA", img.size, (10, 10, 10, alpha))
    img.paste(overlay, (0, 0), overlay)

def _mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ---- 完整标题两行（统一字体/字号/颜色，v4.25）----
T_SIZE = 180
T_DY = int(0.55 * T_SIZE)
T_H1 = 65    # 「你听——」墨迹高
T_H2 = 137   # 「城市白噪音采集计划」墨迹高
T_GAP = 30

def draw_title_two(img, ink_top, color, glow=False):
    y1 = ink_top - T_DY
    gradient_text(img, (40, y1), TITLE_L1, f(F_ZIYU, T_SIZE),
                  _mix(color, (255, 255, 255), 0.15) if glow else color, color,
                  glow=color if glow else None, glow_alpha=18, glow_blur=10)
    y2 = ink_top + T_H1 + T_GAP - T_DY
    gradient_text(img, (40, y2), TITLE_L2, f(F_ZIYU, T_SIZE),
                  _mix(color, (255, 255, 255), 0.15) if glow else color, color,
                  glow=color if glow else None, glow_alpha=18, glow_blur=10)
    return ink_top + T_H1 + T_GAP + T_H2

img_holder = [None]

def time_module(d, date_fill, hours_fill, label_fill):
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=label_fill, anchor="ra")
    d.text((984, 74), PERIOD, font=f(F_AA, 54), fill=date_fill, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=hours_fill, anchor="ra")

def bottom_dark(d, venue_fill, cta_fill):
    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=GREY_D)
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=venue_fill)
    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=GREY_D)
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=GREY_D)
    qr = make_qr(CTA_URL); paste_qr(img_holder[0], qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=cta_fill, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=MILK, anchor="ra")


# ============ 方案一「静听」：戴耳机聆听，黑底反白，声波青+琥珀 ============
def build_1():
    src = load_clean(SRC_LISTEN).resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = img.convert("RGB")
    global_pad_dark(img, alpha=185)
    img_holder[0] = img
    d = ImageDraw.Draw(img)
    time_module(d, WAVE_BLUE, MILK, GREY_D)
    bot = draw_title_two(img, 230, WAVE_BLUE, glow=True)
    d.text((44, bot + 26), SLOGAN, font=f(F_YHBD, 42), fill=AMBER)
    tracked(d, (44, bot + 96), EN, f(F_DENGB, 17), GREY_D, 0.08)
    bottom_dark(d, MILK, AMBER)
    return img


# ============ 方案二「市井乡愁」：菜市场吆喝，黑底反白，琥珀+声波青 ============
def build_2():
    src = load_clean(SRC_MARKET).resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = img.convert("RGB")
    global_pad_dark(img, alpha=185)
    img_holder[0] = img
    d = ImageDraw.Draw(img)
    time_module(d, AMBER, MILK, GREY_D)
    bot = draw_title_two(img, 230, AMBER, glow=True)
    d.text((44, bot + 26), SLOGAN, font=f(F_YHBD, 42), fill=WAVE_BLUE, anchor=None)
    tracked(d, (44, bot + 96), EN, f(F_DENGB, 17), GREY_D, 0.08)
    bottom_dark(d, MILK, WAVE_BLUE)
    return img


# ============ 方案三「白噪音采集」：麦克风夜景，黑底反白，银灰+声波青 ============
def build_3():
    src = load_clean(SRC_MIC).resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = img.convert("RGB")
    global_pad_dark(img, alpha=185)
    img_holder[0] = img
    d = ImageDraw.Draw(img)
    time_module(d, NOISE_W, MILK, GREY_D)
    bot = draw_title_two(img, 230, NOISE_W, glow=True)
    d.text((44, bot + 26), SLOGAN, font=f(F_YHBD, 42), fill=WAVE_BLUE)
    tracked(d, (44, bot + 96), EN, f(F_DENGB, 17), GREY_D, 0.08)
    bottom_dark(d, MILK, WAVE_BLUE)
    return img


# ---- v4.17 防重叠断言 ----
TIME_RECT = (627, 45, 984, 180)

def rects_overlap(a, b):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 <= bx0 or bx1 <= ax0 or ay1 <= by0 or by1 <= ay0)

def assert_no_overlap(name, title_rect):
    if rects_overlap(title_rect, TIME_RECT):
        print(f"  !! {name}: 标题与右上时间模块重叠 {title_rect}")
    else:
        print(f"  ✓ {name}: 标题与右上时间模块零重叠")

def main():
    variants = [
        ("1_静听声波青", build_1()),
        ("2_市井乡愁琥珀", build_2()),
        ("3_白噪音银灰", build_3()),
    ]
    for name, img in variants:
        save_no_overwrite(img, os.path.join(OUT, f"sound_{name}.png"))

    _d = ImageDraw.Draw(Image.new("L", (1, 1)))
    tlw = int(_d.textlength(TITLE_L2, font=f(F_ZIYU, T_SIZE)))
    tlh = T_H1 + T_GAP + T_H2
    print("---- 防重叠检查（标题左对齐 x40 两行）----")
    assert_no_overlap("方案一", (40, 230, 40 + tlw, 230 + tlh))
    assert_no_overlap("方案二", (40, 230, 40 + tlw, 230 + tlh))
    assert_no_overlap("方案三", (40, 230, 40 + tlw, 230 + tlh))

    files = sorted(n for n in os.listdir(OUT) if n.startswith("sound_") and n.endswith(".png"))
    thumbs = [Image.open(os.path.join(OUT, n)).resize((256, 384)) for n in files]
    sheet = Image.new("RGB", (256 * len(thumbs) + 8 * (len(thumbs) - 1), 384), (30, 30, 34))
    x = 0
    for t in thumbs:
        sheet.paste(t, (x, 0)); x += 264
    sheet.save(os.path.join(OUT, "_sound_compare.png"), "PNG")
    print("sheet ok")

if __name__ == "__main__":
    main()
