# -*- coding: utf-8 -*-
"""
make_poster_craft.py — 非遗手作市集「造物有灵·手艺的温度市集」三版海报
套用 skill v4.21（主题判断：温暖质朴中高饱和 → 暖白底为主 + 黑底对比）。

文案：造物有灵（主）/ 手艺的温度市集（副）/ 每一件手作，都有一个人的名字
     免费入场 / 2027.2.10—2.25 / 周二至周日10:00-18:00 / 城市文化中心一层沉浸展厅

方案一「纸底手作」：器物静物，暖白正片墨点，朱砂标题居中上置
方案二「蓝印花布」：竹编纹理，反相靛蓝单色染色，标题左对齐上置
方案三「暗夜手作」：双手做陶，黑底反白点阵，暖鎏金标题居中上置（v4.20 版式一）
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import qrcode
import os
from typographic_halftone import render_size_halftone, render_size_halftone_light, GI
from utils import save_no_overwrite

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "craft_poster")
os.makedirs(OUT, exist_ok=True)

W, H = 1024, 1536

# ---- 温暖自然材质色（中高饱和，v4.16 取中偏暖）----
ZHUSHA   = (172, 84, 58)     # 陶土朱砂（暖白底标题/日期/CTA）
INDIGO   = (52, 92, 134)     # 蓝染靛蓝（方案二单色系统）
INDIGO_D = (40, 72, 106)     # 深靛蓝（方案二标题）
GOLD     = (217, 168, 92)    # 暖鎏金（黑底标题，L≈0.71）
ZHU_L    = (212, 105, 74)    # 朱砂亮（黑底 CTA）
WARM_W   = (245, 241, 232)   # 暖纸白
WARM_D   = (107, 101, 96)    # 暖深灰
GREY_D   = (150, 150, 150)
GREY_B   = (110, 115, 118)

F_ZIYU  = os.path.join(ROOT, "fonts", "ZiYuQuWeiXiangSu.ttf")
F_AA    = os.path.join(ROOT, "fonts", "AaXiaoGouGuaiGuaiXiangSuTi.ttf")
F_YHBD  = "C:/Windows/Fonts/msyhbd.ttc"
F_YH    = "C:/Windows/Fonts/msyh.ttc"
F_DENGB = "C:/Windows/Fonts/Dengb.ttf"

TITLE = "造物有灵"
SUB   = "手艺的温度市集"
SLOGAN = "每一件手作，都有一个人的名字"
EN    = "HANDMADE CRAFT MARKET · THE WARMTH OF HANDS"
CTA    = "免费入场"
CTA_SUB = "扫码查看市集详情"
CTA_URL = "https://weixin.qq.com"
PERIOD = "2027.2.10 — 2.25"
HOURS  = "周二至周日 10:00–18:00"
VENUE  = "城市文化中心一层沉浸展厅"
HOST   = "城市文化中心"

SRC_HANDS  = "Black_and_white_grayscale__doc_2026-10-10T12-04-55.png"
SRC_STILLS = "Black_and_white_grayscale__sti_2026-10-10T12-05-12.png"
SRC_WEAVE  = "Black_and_white_grayscale__mac_2026-10-10T12-05-32.png"
SRC_CALICO = "Black_and_white_grayscale__tra_2026-10-10T12-18-54.png"   # 蓝印花布（白凤凰纹）
SRC_CHEER  = "Black_and_white_grayscale__che_2026-10-10T12-19-11.png"   # 轻松手作（玩偶毛线）

INK_DARK  = (52, 46, 41)      # 深墨（浅底传播语，与灰点底图拉开）
WARM_GD   = (100, 90, 80)     # 加深暖灰（小字标签，替代原 WARM_D 提高对比）
BROWN_T   = (74, 56, 38)      # 深暖棕（方案三标题）
TEAL      = (52, 136, 118)    # 松石绿（方案二：青瓷/铜绿/草木染）
TEAL_D    = (30, 94, 82)      # 深松石
PERSIMMON = (166, 106, 56)    # 柿染橙（方案三：柿染工艺）
PERSIMMON_D = (140, 84, 42)   # 深柿橙
PURPLE    = (124, 82, 138)    # 藕荷紫（方案三辅色：绣花丝线/紫草染）

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

def brighten_bands(src, top_h=200, bot_y=1220, strength=0.92):
    """渲染前把源图顶部/底部做灰度渐变提亮（非羽化）：
    让正片渲染在信息区自然留白，文字直接排在留白处，无需后期减淡。"""
    px = src.load()
    W_, H_ = src.size
    for y in range(0, top_h):
        t = ((top_h - y) / top_h) ** 0.5          # 顶部：先快后慢
        for x in range(W_):
            v = px[x, y]
            px[x, y] = int(v + (255 - v) * strength * t)
    for y in range(bot_y, H_):
        t = ((y - bot_y) / max(1, H_ - bot_y)) ** 0.5   # 底部：先快后慢
        for x in range(W_):
            v = px[x, y]
            px[x, y] = int(v + (255 - v) * strength * t)
    return src

TITLE_SIZE = 280
TITLE_DY = int(0.55 * TITLE_SIZE)     # 像素体墨迹顶 = 绘制y + 0.55×字号

def draw_title_dark_bg(img, ink_top, color, anchor=None, x=40):
    gradient_text(img, (x, ink_top - TITLE_DY), TITLE, f(F_ZIYU, TITLE_SIZE),
                  _mix(color, (255, 255, 255), 0.15), color,
                  anchor=anchor, glow=color, glow_alpha=18, glow_blur=10)
    return ink_top + int(0.40 * TITLE_SIZE)

def draw_title_light_bg(img, ink_top, color, anchor=None, x=40):
    d = ImageDraw.Draw(img)
    d.text((x, ink_top - TITLE_DY), TITLE, font=f(F_ZIYU, TITLE_SIZE),
           fill=color, stroke_width=1, stroke_fill=color, anchor=anchor)
    return ink_top + int(0.40 * TITLE_SIZE)

img_holder = [None]

def bottom_dark(d, venue_fill, cta_fill):
    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=GREY_D)
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=venue_fill)
    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=GREY_D)
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=GREY_D)
    qr = make_qr(CTA_URL); paste_qr(img_holder[0], qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=cta_fill, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=WARM_W, anchor="ra")

def bottom_light(d, label_fill, venue_fill, cta_fill):
    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=label_fill)
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=venue_fill)
    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=label_fill)
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=label_fill)
    qr = make_qr(CTA_URL); paste_qr(img_holder[0], qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=cta_fill, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=label_fill, anchor="ra")

def time_module(d, date_fill, hours_fill, label_fill):
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=label_fill, anchor="ra")
    d.text((984, 74), PERIOD, font=f(F_AA, 54), fill=date_fill, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=hours_fill, anchor="ra")


# ============ 方案一「纸底手作」：器物静物，暖白正片墨点，朱砂居中上置 ============
def build_1():
    src = load_clean(SRC_STILLS).resize((W, H), Image.LANCZOS)
    # 中灰调静物：先提亮（gamma 0.62）压低背景暗度，再用高留白阈值正片渲染
    src = src.point(lambda v: int(255 * (v / 255) ** 0.62))
    src = brighten_bands(src)   # 顶部/底部留白带，文字直接排留白处
    img = render_size_halftone_light(src, cell=7, contrast=1.35, ink_gamma=0.85,
                                     rim=True, white_point=0.30)
    img = img.convert("RGB")
    global_pad_light(img, alpha=140)
    img_holder[0] = img
    d = ImageDraw.Draw(img)
    time_module(d, ZHUSHA, WARM_GD, WARM_GD)
    # 标题居中上置（墨迹顶 y230，防重叠）
    bot = draw_title_light_bg(img, 230, ZHUSHA, anchor="ma", x=W // 2)
    d.text((W // 2, bot + 40), SUB, font=f(F_YHBD, 46), fill=ZHUSHA, anchor="ma")
    d.text((W // 2, bot + 120), SLOGAN, font=f(F_YHBD, 42), fill=TEAL, anchor="ma")
    tracked_center(d, bot + 195, EN, f(F_DENGB, 17), (118, 106, 94), 0.08)
    bottom_light(d, WARM_GD, ZHUSHA, ZHUSHA)
    return img


# ============ 方案二「青绿染布」：凤凰纹布块，松石绿点阵，上方文字下方挂布 ============
def build_2():
    src = load_clean(SRC_CALICO)
    # 裁出布块主体（凤凰纹所在区域，避开桌面边缘；水印也在裁剪区外）
    cloth = src.crop((60, 35, 960, 1420))
    # 正片墨点：凤凰亮部留白、布底成松石绿点阵（点阵风格与整套海报统一）
    cloth_ht = render_size_halftone_light(cloth, cell=7, contrast=1.35, ink_gamma=0.85,
                                          rim=True, white_point=0.10)
    cloth_ht = ImageOps.colorize(cloth_ht.convert("L"),
                                 black=(30, 94, 82), white=(255, 255, 255))
    cloth_final = cloth_ht.resize((500, 760), Image.LANCZOS)
    img = Image.new("RGB", (W, H), (255, 255, 255))
    img.paste(cloth_final, ((W - 500) // 2, 560))
    img_holder[0] = img
    d = ImageDraw.Draw(img)
    time_module(d, TEAL, TEAL_D, GREY_B)
    bot = draw_title_light_bg(img, 230, TEAL_D, anchor="ma", x=W // 2)
    d.text((W // 2, bot + 40), SUB, font=f(F_YHBD, 46), fill=TEAL, anchor="ma")
    d.text((W // 2, bot + 120), SLOGAN, font=f(F_YHBD, 42), fill=PERSIMMON, anchor="ma")
    tracked_center(d, bot + 195, EN, f(F_DENGB, 17), GREY_B, 0.08)
    bottom_light(d, GREY_B, TEAL, PERSIMMON)
    return img


# ============ 方案三「柿染手作」：玩偶毛线场景，柿染橙点阵（轻松年轻） ============
def build_3():
    src = load_clean(SRC_CHEER).resize((W, H), Image.LANCZOS)
    # 中灰调场景：提亮 + 高留白阈值正片渲染（同方案一经验）
    src = src.point(lambda v: int(255 * (v / 255) ** 0.62))
    src = brighten_bands(src)   # 顶部/底部留白带，文字直接排留白处
    img = render_size_halftone_light(src, cell=7, contrast=1.35, ink_gamma=0.85,
                                     rim=True, white_point=0.30)
    # colorize：墨点→柿染橙，底→纯白（底色铁律：纯白/纯黑）
    img = ImageOps.colorize(img.convert("L"), black=PERSIMMON_D, white=(255, 255, 255)).convert("RGB")
    global_pad_light(img, alpha=90)
    img_holder[0] = img
    d = ImageDraw.Draw(img)
    time_module(d, PERSIMMON, (150, 100, 60), (150, 120, 90))
    # 标题居中上置（v4.20 版式一，墨迹顶 y230）
    bot = draw_title_light_bg(img, 230, PERSIMMON, anchor="ma", x=W // 2)
    d.text((W // 2, bot + 40), SUB, font=f(F_YHBD, 46), fill=PERSIMMON, anchor="ma")
    d.text((W // 2, bot + 120), SLOGAN, font=f(F_YHBD, 42), fill=PURPLE, anchor="ma")
    tracked_center(d, bot + 195, EN, f(F_DENGB, 17), (150, 120, 90), 0.08)
    bottom_light(d, (150, 120, 90), PERSIMMON, PURPLE)
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
        ("1_纸底手作朱砂", build_1()),
        ("2_青绿染布松石", build_2()),
        ("3_柿染手作橙", build_3()),
    ]
    for name, img in variants:
        save_no_overwrite(img, os.path.join(OUT, f"craft_{name}.png"))

    # 防重叠断言（标题「造物有灵」280px 实测宽）
    _d = ImageDraw.Draw(Image.new("L", (1, 1)))
    tlw = int(_d.textlength(TITLE, font=f(F_ZIYU, TITLE_SIZE)))
    tlh = int(0.40 * TITLE_SIZE)
    print("---- 防重叠检查 ----")
    assert_no_overlap("方案一", (W // 2 - tlw // 2, 230, W // 2 + tlw // 2, 230 + tlh))
    assert_no_overlap("方案二", (40, 240, 40 + tlw, 240 + tlh))
    assert_no_overlap("方案三", (W // 2 - tlw // 2, 230, W // 2 + tlw // 2, 230 + tlh))

    # 对比图
    files = sorted(n for n in os.listdir(OUT) if n.startswith("craft_") and n.endswith(".png"))
    thumbs = [Image.open(os.path.join(OUT, n)).resize((256, 384)) for n in files]
    sheet = Image.new("RGB", (256 * len(thumbs) + 8 * (len(thumbs) - 1), 384), (96, 90, 84))
    x = 0
    for t in thumbs:
        sheet.paste(t, (x, 0)); x += 264
    sheet.save(os.path.join(OUT, "_craft_compare.png"), "PNG")
    print("sheet ok")

if __name__ == "__main__":
    main()
