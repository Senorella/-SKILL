# -*- coding: utf-8 -*-
"""
make_poster_film.py — 露天胶片放映「故事讲得很慢」三版海报
套用 skill v4.24 配色决策卡：文艺复古 → 黑底 + 夜蓝/胶片金 + 高饱和（v4.26）。

文案：故事讲得很慢（标题一行 240px）
     没有倍速、没有弹幕，只有风和人 / 预约选座 / 2027.5.1—5.7
     每日19:30-22:00 / 城市文化中心一层沉浸展厅

方案一「夏夜露天」：银幕+观众剪影，黑底反白，夜蓝 + 胶片金
方案二「放映机暖光」：老式放映机，黑底反白，胶片金 + 夜蓝
方案三「星空远幕」：星空下远处的幕布，黑底反白，胶片橙 + 夜蓝
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import qrcode
import os
from typographic_halftone import render_size_halftone, GI
from utils import save_no_overwrite

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "film_poster")
os.makedirs(OUT, exist_ok=True)

W, H = 1024, 1536

# ---- 胶片放映配色（黑底 → 高饱和 + 高亮度，v4.26）----
NIGHT_BLUE = (74, 134, 216)    # 夜蓝（夏夜夜空，S≈0.66）
FILM_GOLD  = (232, 169, 74)    # 胶片金（放映机暖光，S≈0.68）
FILM_AMBER = (224, 126, 60)    # 胶片橙（老胶片，S≈0.73）
MILK       = (245, 241, 232)   # 信息白
GREY_D     = (150, 150, 150)

F_ZIYU  = os.path.join(ROOT, "fonts", "ZiYuQuWeiXiangSu.ttf")
F_AA    = os.path.join(ROOT, "fonts", "AaXiaoGouGuaiGuaiXiangSuTi.ttf")
F_YHBD  = "C:/Windows/Fonts/msyhbd.ttc"
F_YH    = "C:/Windows/Fonts/msyh.ttc"
F_DENGB = "C:/Windows/Fonts/Dengb.ttf"

TITLE = "故事讲得很慢"
SLOGAN = "没有倍速、没有弹幕，只有风和人"
EN    = "SLOW CINEMA NIGHT · OPEN-AIR FILM SCREENING"
CTA    = "预约选座"
CTA_SUB = "扫码微信小程序选座"
CTA_URL = "https://weixin.qq.com"
PERIOD = "2027.5.1 — 5.7"
HOURS  = "每日 19:30–22:00"
VENUE  = "城市文化中心一层沉浸展厅"
HOST   = "城市文化中心"

SRC_SCREEN = "Black_and_white_grayscale__an__2026-10-10T13-27-14.png"  # 露天银幕
SRC_PROJ   = "Black_and_white_grayscale__a_v_2026-10-10T13-27-36.png"  # 放映机
SRC_PAIR   = "Black_and_white_grayscale__bac_2026-10-10T13-27-55.png"  # 两人背影看银幕（替换星空远幕：幕布太小识别度低）

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

# ---- 标题一行（无连接符，v4.25 单标题）----
T_SIZE = 240
T_DY = 70    # 整串墨迹顶偏移【实测】：像素体「慢」字是全幅大外框字形（同宋代「圈」），顶偏移仅 70，非 0.55×字号(132)
T_H = 207     # 整串墨迹高（由「慢」字决定）

def draw_title(img, ink_top, color, glow=False):
    gradient_text(img, (40, ink_top - T_DY), TITLE, f(F_ZIYU, T_SIZE),
                  _mix(color, (255, 255, 255), 0.15) if glow else color, color,
                  glow=color if glow else None, glow_alpha=18, glow_blur=10)
    return ink_top + T_H

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


# ============ 方案一「夏夜露天」：银幕+观众剪影，夜蓝+胶片金 ============
def build_1():
    src = load_clean(SRC_SCREEN).resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = img.convert("RGB")
    global_pad_dark(img, alpha=185)
    img_holder[0] = img
    d = ImageDraw.Draw(img)
    time_module(d, NIGHT_BLUE, MILK, GREY_D)
    bot = draw_title(img, 230, NIGHT_BLUE, glow=True)
    d.text((44, bot + 28), SLOGAN, font=f(F_YHBD, 42), fill=FILM_GOLD)
    tracked(d, (44, bot + 98), EN, f(F_DENGB, 17), GREY_D, 0.08)
    bottom_dark(d, MILK, FILM_GOLD)
    return img


# ============ 方案二「放映机暖光」：老式放映机，胶片金+夜蓝 ============
def build_2():
    src = load_clean(SRC_PROJ).resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = img.convert("RGB")
    global_pad_dark(img, alpha=185)
    img_holder[0] = img
    d = ImageDraw.Draw(img)
    time_module(d, FILM_GOLD, MILK, GREY_D)
    bot = draw_title(img, 230, FILM_GOLD, glow=True)
    d.text((44, bot + 28), SLOGAN, font=f(F_YHBD, 42), fill=NIGHT_BLUE)
    tracked(d, (44, bot + 98), EN, f(F_DENGB, 17), GREY_D, 0.08)
    bottom_dark(d, MILK, NIGHT_BLUE)
    return img


# ============ 方案三「星空远幕」：两人背影看银幕，胶片橙+夜蓝 ============
def build_3():
    src = load_clean(SRC_PAIR).resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = img.convert("RGB")
    global_pad_dark(img, alpha=185)
    img_holder[0] = img
    d = ImageDraw.Draw(img)
    time_module(d, FILM_AMBER, MILK, GREY_D)
    # 标题在星空区（y230-437），传播语下沉到银幕下方剪影暗区（银幕区浅字不可读）
    bot = draw_title(img, 230, FILM_AMBER, glow=True)
    d.text((44, 800), SLOGAN, font=f(F_YHBD, 42), fill=NIGHT_BLUE)
    tracked(d, (44, 870), EN, f(F_DENGB, 17), GREY_D, 0.08)
    bottom_dark(d, MILK, NIGHT_BLUE)
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
        ("1_夏夜露天夜蓝", build_1()),
        ("2_放映机暖光金", build_2()),
        ("3_星空远幕橙", build_3()),
    ]
    for name, img in variants:
        save_no_overwrite(img, os.path.join(OUT, f"film_{name}.png"))

    _d = ImageDraw.Draw(Image.new("L", (1, 1)))
    tlw = int(_d.textlength(TITLE, font=f(F_ZIYU, T_SIZE)))
    print("---- 防重叠检查（标题左对齐 x40 单行）----")
    assert_no_overlap("方案一", (40, 230, 40 + tlw, 230 + T_H))
    assert_no_overlap("方案二", (40, 230, 40 + tlw, 230 + T_H))
    assert_no_overlap("方案三", (40, 230, 40 + tlw, 230 + T_H))

    files = sorted(n for n in os.listdir(OUT) if n.startswith("film_") and n.endswith(".png"))
    thumbs = [Image.open(os.path.join(OUT, n)).resize((256, 384)) for n in files]
    sheet = Image.new("RGB", (256 * len(thumbs) + 8 * (len(thumbs) - 1), 384), (20, 20, 26))
    x = 0
    for t in thumbs:
        sheet.paste(t, (x, 0)); x += 264
    sheet.save(os.path.join(OUT, "_film_compare.png"), "PNG")
    print("sheet ok")

if __name__ == "__main__":
    main()
