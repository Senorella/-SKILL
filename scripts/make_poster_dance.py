# -*- coding: utf-8 -*-
"""
make_poster_dance.py — 民族舞蹈展演「大地之舞」三版海报
套用 skill v4.24 配色决策卡：民族服饰浓烈多彩 → 黑底为主 + 高饱和民族色 + 2-3 色。

文案：大地之舞（主）/ 跟着风的方向起舞（副）/ 从草原到雪山，一步一故乡
     预约观演 / 2027.6.12—6.28 / 周六至周日15:00-17:00 / 城市文化中心一层沉浸展厅

方案一「暗夜独舞」：独舞长袖，黑底反白，藏红 + 经幡金
方案二「草原群舞」：群舞雪山，白底正片墨点（云留白），草原绿 + 藏红
方案三「风之舞袖」：舞袖丝带，黑底反白，经幡蓝 + 藏红
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import qrcode
import os
from typographic_halftone import render_size_halftone, render_size_halftone_light, GI
from utils import save_no_overwrite

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "dance_poster")
os.makedirs(OUT, exist_ok=True)

W, H = 1024, 1536

# ---- 民族色（高饱和，黑底用亮版）----
DADI     = (198, 130, 76)     # 大地赭（方案一主色：大地之舞）
CAO_L    = (79, 180, 104)     # 草原绿亮版（方案一辅色：从草原）
CAOYUAN  = (46, 122, 72)      # 草原绿深版（方案二主色，白底）
JINGFAN  = (90, 138, 212)     # 经幡蓝（方案三主色）
ZANGHONG = (200, 56, 74)      # 藏红（方案二/三辅色点缀）
MILK     = (245, 241, 232)    # 奶白（信息）
GREY_D   = (150, 150, 150)
GREY_B   = (110, 115, 118)

F_ZIYU  = os.path.join(ROOT, "fonts", "ZiYuQuWeiXiangSu.ttf")
F_AA    = os.path.join(ROOT, "fonts", "AaXiaoGouGuaiGuaiXiangSuTi.ttf")
F_YHBD  = "C:/Windows/Fonts/msyhbd.ttc"
F_YH    = "C:/Windows/Fonts/msyh.ttc"
F_DENGB = "C:/Windows/Fonts/Dengb.ttf"

TITLE_L1 = "大地之舞——"
TITLE_L2 = "跟着风的方向起舞"
SLOGAN = "从草原到雪山，一步一故乡"
EN    = "DANCE OF THE EARTH · FOLLOW THE WIND"
CTA    = "预约观演"
CTA_SUB = "扫码微信小程序预约"
CTA_URL = "https://weixin.qq.com"
PERIOD = "2027.6.12 — 6.28"
HOURS  = "周六至周日 15:00–17:00"
VENUE  = "城市文化中心一层沉浸展厅"
HOST   = "城市文化中心"

SRC_SOLO  = "Black_and_white_grayscale__a_f_2026-10-10T12-53-53.png"
SRC_GROUP = "Black_and_white_grayscale__gro_2026-10-10T12-54-10.png"
SRC_DANCER = "Black_and_white_grayscale__a_f_2026-10-10T13-07-39.png"   # 全身舞者（原丝带特写风格化后识别度低，已弃用）

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

def global_pad_light(img, alpha=140):
    overlay = Image.new("RGBA", img.size, (255, 255, 255, alpha))
    img.paste(overlay, (0, 0), overlay)

def _mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def brighten_bands(src, top_h=200, bot_y=1220, strength=0.92):
    """渲染前把源图顶部/底部做灰度渐变提亮（非羽化）：正片渲染在信息区自然留白"""
    px = src.load()
    W_, H_ = src.size
    for y in range(0, top_h):
        t = ((top_h - y) / top_h) ** 0.5
        for x in range(W_):
            v = px[x, y]
            px[x, y] = int(v + (255 - v) * strength * t)
    for y in range(bot_y, H_):
        t = ((y - bot_y) / max(1, H_ - bot_y)) ** 0.5
        for x in range(W_):
            v = px[x, y]
            px[x, y] = int(v + (255 - v) * strength * t)
    return src

TITLE_SIZE = 200
TITLE_DY = int(0.55 * TITLE_SIZE)   # 像素体墨迹顶偏移 = 110
LINE1_H = 122   # 行1「大地之舞——」墨迹高
LINE2_H = 152   # 行2「跟着风的方向起舞」墨迹高
LINE_GAP = 30   # 行间距

def draw_title_two(img, ink_top, color, glow=False):
    """完整标题两行：同一字体（像素体）/ 同一字号（200px）/ 同一颜色，左对齐 x40。
    行1「大地之舞——」行2「跟着风的方向起舞」。返回行2墨迹底 y。"""
    y1 = ink_top - TITLE_DY
    gradient_text(img, (40, y1), TITLE_L1, f(F_ZIYU, TITLE_SIZE),
                  _mix(color, (255, 255, 255), 0.15) if glow else color, color,
                  glow=color if glow else None, glow_alpha=18, glow_blur=10)
    y2 = ink_top + LINE1_H + LINE_GAP - TITLE_DY
    gradient_text(img, (40, y2), TITLE_L2, f(F_ZIYU, TITLE_SIZE),
                  _mix(color, (255, 255, 255), 0.15) if glow else color, color,
                  glow=color if glow else None, glow_alpha=18, glow_blur=10)
    return ink_top + LINE1_H + LINE_GAP + LINE2_H

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

def bottom_light(d, label_fill, venue_fill, cta_fill):
    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=label_fill)
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=venue_fill)
    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=label_fill)
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=label_fill)
    qr = make_qr(CTA_URL); paste_qr(img_holder[0], qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=cta_fill, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=label_fill, anchor="ra")


# ============ 方案一「大地独舞」：独舞长袖，黑底反白，大地赭+草原绿 ============
def build_1():
    src = load_clean(SRC_SOLO).resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = img.convert("RGB")
    global_pad_dark(img, alpha=185)
    img_holder[0] = img
    d = ImageDraw.Draw(img)
    time_module(d, DADI, MILK, GREY_D)
    bot = draw_title_two(img, 230, DADI, glow=True)
    d.text((44, bot + 26), SLOGAN, font=f(F_YHBD, 42), fill=CAO_L)
    tracked(d, (44, bot + 96), EN, f(F_DENGB, 17), GREY_D, 0.08)
    bottom_dark(d, MILK, CAO_L)
    return img


# ============ 方案二「草原群舞」：群舞雪山，白底正片（云留白），草原绿+藏红 ============
def build_2():
    src = load_clean(SRC_GROUP).resize((W, H), Image.LANCZOS)
    src = brighten_bands(src)   # 顶部/底部留白带，文字排留白处
    img = render_size_halftone_light(src, cell=7, contrast=1.35, ink_gamma=0.85,
                                     rim=True, white_point=0.30)
    # colorize：墨点→草原绿，底→纯白
    img = ImageOps.colorize(img.convert("L"), black=(46, 122, 72), white=(255, 255, 255)).convert("RGB")
    global_pad_light(img, alpha=90)
    img_holder[0] = img
    d = ImageDraw.Draw(img)
    time_module(d, CAOYUAN, (110, 118, 112), GREY_B)
    bot = draw_title_two(img, 230, CAOYUAN, glow=False)
    d.text((44, bot + 26), SLOGAN, font=f(F_YHBD, 42), fill=ZANGHONG)
    tracked(d, (44, bot + 96), EN, f(F_DENGB, 17), GREY_B, 0.08)
    bottom_light(d, GREY_B, CAOYUAN, ZANGHONG)
    return img


# ============ 方案三「风之舞袖」：全身舞者，黑底反白，经幡蓝+藏红 ============
def build_3():
    src = load_clean(SRC_DANCER).resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = img.convert("RGB")
    global_pad_dark(img, alpha=185)
    img_holder[0] = img
    d = ImageDraw.Draw(img)
    time_module(d, JINGFAN, MILK, GREY_D)
    bot = draw_title_two(img, 230, JINGFAN, glow=True)
    d.text((44, bot + 26), SLOGAN, font=f(F_YHBD, 42), fill=ZANGHONG)
    tracked(d, (44, bot + 96), EN, f(F_DENGB, 17), GREY_D, 0.08)
    bottom_dark(d, MILK, ZANGHONG)
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
        ("1_大地独舞赭", build_1()),
        ("2_草原群舞绿", build_2()),
        ("3_风之舞袖经幡蓝", build_3()),
    ]
    for name, img in variants:
        save_no_overwrite(img, os.path.join(OUT, f"dance_{name}.png"))

    _d = ImageDraw.Draw(Image.new("L", (1, 1)))
    tlw = int(_d.textlength(TITLE_L2, font=f(F_ZIYU, TITLE_SIZE)))   # 行2最宽
    tlh = LINE1_H + LINE_GAP + LINE2_H
    print("---- 防重叠检查（标题左对齐 x40 两行）----")
    assert_no_overlap("方案一", (40, 230, 40 + tlw, 230 + tlh))
    assert_no_overlap("方案二", (40, 230, 40 + tlw, 230 + tlh))
    assert_no_overlap("方案三", (40, 230, 40 + tlw, 230 + tlh))

    files = sorted(n for n in os.listdir(OUT) if n.startswith("dance_") and n.endswith(".png"))
    thumbs = [Image.open(os.path.join(OUT, n)).resize((256, 384)) for n in files]
    sheet = Image.new("RGB", (256 * len(thumbs) + 8 * (len(thumbs) - 1), 384), (40, 40, 44))
    x = 0
    for t in thumbs:
        sheet.paste(t, (x, 0)); x += 264
    sheet.save(os.path.join(OUT, "_dance_compare.png"), "PNG")
    print("sheet ok")

if __name__ == "__main__":
    main()
