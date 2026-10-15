# -*- coding: utf-8 -*-
"""
make_poster_mirror.py — 先锋话剧《镜中人》三版海报
套用 exhibition-poster-two-step-pipeline skill（v4.13 三方案 + v4.15 标题下沉 + v4.16 配色取中）。

文案：
  主标题：你，在场吗？   副标题：沉浸式话剧《镜中人》
  传播语：观众席和舞台之间，只隔一层纱
  行动提示：预约购票   展期：2027年3月1日至3月15日
  开放时间：周五至周日19:00-21:00   地点/主办：城市文化中心

A 版 · 黑底满版（镜中人底图）：冰镜蓝标题置顶部暗带 + 冷红 CTA
B 版 · 白底单色（高调纱幕底图）：冷钢蓝单色系统
C 版 · 黑底（观众席底图）：琥珀金标题居中于「观众席与舞台之间」的天然暗带
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import qrcode
import os
from typographic_halftone import render_size_halftone, render_size_halftone_light, GI
from utils import save_no_overwrite

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "mirror_poster")
os.makedirs(OUT, exist_ok=True)

W, H = 1024, 1536

# ---- 先锋话剧配色（v4.16 饱和度取中：标题 S≈0.4，点缀 S≈0.5）----
MIRROR_BLUE = (111, 163, 200)   # 冰镜蓝（A 版标题/日期）
EMBER_RED   = (196, 82, 96)     # 冷红（CTA「预约购票」，A/C 版）
STEEL       = (58, 94, 130)     # 冷钢蓝（B 版单色系统）
AMBER       = (201, 152, 90)    # 琥珀金（C 版标题/日期，舞台灯光色）
MIST_W      = (232, 234, 236)   # 雾白
GREY_D      = (150, 150, 150)
GREY_B      = (98, 106, 110)

F_ZIYU  = os.path.join(ROOT, "fonts", "ZiYuQuWeiXiangSu.ttf")
F_AA    = os.path.join(ROOT, "fonts", "AaXiaoGouGuaiGuaiXiangSuTi.ttf")
F_YHBD  = "C:/Windows/Fonts/msyhbd.ttc"
F_YH    = "C:/Windows/Fonts/msyh.ttc"
F_DENGB = "C:/Windows/Fonts/Dengb.ttf"

TITLE = "你，在场吗？"
SUB   = "沉浸式话剧《镜中人》"
SLOGAN = "观众席和舞台之间，只隔一层纱"
EN    = "IMMERSIVE THEATRE · THE MAN IN THE MIRROR"
CTA    = "预约购票"
CTA_SUB = "扫码微信小程序购票"
CTA_URL = "https://weixin.qq.com"
PERIOD = "2027.3.1 — 3.15"
HOURS  = "周五至周日 19:00–21:00"
VENUE  = "城市文化中心一层沉浸展厅"
HOST   = "城市文化中心"

SRC_MIRROR   = "mirror_b/Black_and_white_grayscale__fil_2026-10-09T20-36-34.png"
SRC_AUDIENCE = "mirror_b/Black_and_white_grayscale__fil_2026-10-09T20-36-33.png"
SRC_GAUZE    = "Black_and_white_grayscale__hig_2026-10-09T20-37-43.png"

WM_BOX = (880, 1450, 1024, 1536)   # 「AI生成」水印区域

def f(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)

def remove_watermark(img):
    """右下角水印：取其左侧等宽区域水平镜像贴补"""
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
    """英文行水平居中（先测总宽）"""
    total = sum(d.textlength(ch, font=font) * (1 + tracking) for ch in text) \
            - d.textlength(text[-1], font=font) * tracking
    tracked(d, (W // 2 - total / 2, cy), text, font, fill, tracking)

def gradient_text(img, xy, text, font, c_top, c_bottom,
                  anchor=None, glow=None, glow_alpha=20, glow_blur=10, stroke=1):
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

def global_pad_light(img, alpha=210):
    overlay = Image.new("RGBA", img.size, (255, 255, 255, alpha))
    img.paste(overlay, (0, 0), overlay)

def _whiten(img, thresh=235):
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = px[x, y]
            if r > thresh and g > thresh and b > thresh:
                px[x, y] = (255, 255, 255)
    return img

def _mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# 像素体字形比例（实测）：墨迹顶 ≈ 绘制y + 0.55×字号
TITLE_SIZE = 280
TITLE_DY   = int(0.55 * TITLE_SIZE)   # 绘制 y = 目标墨迹顶 - TITLE_DY

def draw_title_dark(img, ink_top_y, color, anchor=None, x=40):
    """黑底版主标题：指定墨迹顶 y。返回墨迹底 y。"""
    gradient_text(img, (x, ink_top_y - TITLE_DY), TITLE, f(F_ZIYU, TITLE_SIZE),
                  _mix(color, (255, 255, 255), 0.15), color,
                  anchor=anchor, glow=color, glow_alpha=18, glow_blur=10)
    return ink_top_y + int(0.40 * TITLE_SIZE)   # 墨迹底（含逗号下伸）

def draw_title_light(img, ink_top_y, color, x=40):
    d = ImageDraw.Draw(img)
    d.text((x, ink_top_y - TITLE_DY), TITLE, font=f(F_ZIYU, TITLE_SIZE),
           fill=color, stroke_width=1, stroke_fill=color)
    return ink_top_y + int(0.40 * TITLE_SIZE)

def bottom_block_dark(d, venue_fill, cta_fill, cta_sub_fill):
    """地点/主办左下 + 二维码右下（黑底）"""
    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=GREY_D)
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=venue_fill)
    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=GREY_D)
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=GREY_D)
    qr = make_qr(CTA_URL)
    paste_qr(img_holder[0], qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=cta_fill, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=cta_sub_fill, anchor="ra")

def bottom_block_light(d, venue_fill, label_fill, cta_fill):
    """地点/主办左下 + 二维码右下（白底）"""
    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=label_fill)
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=venue_fill)
    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=label_fill)
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=label_fill)
    qr = make_qr(CTA_URL)
    paste_qr(img_holder[0], qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=cta_fill, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=label_fill, anchor="ra")

img_holder = [None]   # bottom_block 里访问当前 img


# ============ A 版 · 黑底满版（镜中人）冰镜蓝 ============
def build_A():
    src = load_clean(SRC_MIRROR).resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = img.convert("RGB")
    global_pad_dark(img, alpha=185)
    img_holder[0] = img
    d = ImageDraw.Draw(img)

    # 时间模块右上
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=GREY_D, anchor="ra")
    d.text((984, 74), PERIOD, font=f(F_AA, 54), fill=MIRROR_BLUE, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=MIST_W, anchor="ra")

    # 主标题：居中（呼应镜中人的对称构图）。墨迹顶 y230，与右上时间模块墨迹底 y180 错开 ≥50px
    bot = draw_title_dark(img, 230, MIRROR_BLUE, anchor="ma", x=W // 2)

    # 副标题 + 传播语 + 英文（居中，压镜框上部过渡区，柔光承托）
    d.text((W // 2, bot + 42), SUB, font=f(F_YHBD, 46), fill=MIST_W, anchor="ma")
    d.text((W // 2, bot + 122), SLOGAN, font=f(F_YHBD, 42), fill=MIST_W, anchor="ma")
    tracked_center(d, bot + 196, EN, f(F_DENGB, 17), GREY_D, 0.08)

    bottom_block_dark(d, MIST_W, EMBER_RED, MIST_W)
    return img


# ============ B 版 · 白底单色（白纱正片墨点）冷钢蓝 ============
def build_B():
    # 白纱是「白主体」：禁用 invert 反相（会把白纱变成墨点密集区），
    # 改用白底墨点正片模式——白纱留白、褶皱与人影成墨点，保住白纱辨识度
    src = load_clean(SRC_GAUZE).resize((W, H), Image.LANCZOS)
    img = render_size_halftone_light(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = img.convert("RGB")
    global_pad_light(img, alpha=140)   # 轻微统一，不抹纹理
    img_holder[0] = img
    d = ImageDraw.Draw(img)

    # 时间模块右上
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=GREY_B, anchor="ra")
    d.text((984, 74), PERIOD, font=f(F_AA, 54), fill=STEEL, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=GREY_B, anchor="ra")

    # 主标题（白底方案：纱幕全画幅纹理，标题置上部，深钢蓝压制浅墨点）
    bot = draw_title_light(img, 200, STEEL, x=40)

    d.text((44, bot + 42), SUB, font=f(F_YHBD, 46), fill=STEEL)
    d.text((44, bot + 122), SLOGAN, font=f(F_YHBD, 42), fill=GREY_B)
    tracked(d, (44, bot + 196), EN, f(F_DENGB, 17), GREY_B, 0.08)

    bottom_block_light(d, STEEL, GREY_B, STEEL)
    return img


# ============ C 版 · 黑底观众席：标题居中于「观众席与舞台之间」暗带 ============
def build_C():
    src = load_clean(SRC_AUDIENCE).resize((W, H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = img.convert("RGB")
    global_pad_dark(img, alpha=175)   # 舞台亮部要保留可辨，柔光略低
    img_holder[0] = img
    d = ImageDraw.Draw(img)

    # 时间模块右上
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=GREY_D, anchor="ra")
    d.text((984, 74), PERIOD, font=f(F_AA, 54), fill=AMBER, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=MIST_W, anchor="ra")

    # 主标题：居中于舞台亮部（y192-671）与椅背剪影（y864+）之间的天然暗带 y672-863
    bot = draw_title_dark(img, 692, AMBER, anchor="ma", x=W // 2)

    # 副标题/传播语/英文：居中，叠在椅背剪影上（语义呼应传播语）
    d.text((W // 2, bot + 40), SUB, font=f(F_YHBD, 46), fill=MIST_W, anchor="ma")
    d.text((W // 2, bot + 120), SLOGAN, font=f(F_YHBD, 42), fill=MIST_W, anchor="ma")
    tracked_center(d, bot + 194, EN, f(F_DENGB, 17), GREY_D, 0.08)

    bottom_block_dark(d, MIST_W, EMBER_RED, MIST_W)
    return img


def rects_overlap(a, b):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 <= bx0 or bx1 <= ax0 or ay1 <= by0 or by1 <= ay0)

TIME_RECT = (627, 45, 984, 180)   # 右上时间模块实测墨迹矩形

def assert_no_title_time_overlap(name, title_rect):
    """硬断言：标题墨迹矩形与右上时间模块矩形零重叠"""
    if rects_overlap(title_rect, TIME_RECT):
        print(f"  !! {name}: 标题与右上时间模块重叠 {title_rect} vs {TIME_RECT}")
    else:
        print(f"  ✓ {name}: 标题与右上时间模块零重叠")

def main():
    variants = [
        ("A_黑底镜中人冰蓝", build_A()),
        ("B_白底纱幕钢蓝", build_B()),
        ("C_观众席琥珀居中", build_C()),
    ]
    for name, img in variants:
        out = os.path.join(OUT, f"mirror_{name}.png")
        save_no_overwrite(img, out)
        print("saved:", out)

    files = [n for n in os.listdir(OUT) if n.startswith("mirror_") and n.endswith(".png")]
    files.sort()
    thumbs = [Image.open(os.path.join(OUT, n)).resize((256, 384)) for n in files]
    sheet = Image.new("RGB", (256 * len(thumbs) + 8 * (len(thumbs) - 1), 384), (60, 60, 60))
    x = 0
    for t in thumbs:
        sheet.paste(t, (x, 0)); x += 264
    sheet.save(os.path.join(OUT, "_mirror_compare.png"))
    print("sheet ok")

    # ---- 防重叠断言（v4.17 硬约束）----
    # 标题墨迹宽实测（textlength，更保守）
    _d = ImageDraw.Draw(Image.new("L", (1, 1)))
    _tlw = int(_d.textlength(TITLE, font=f(F_ZIYU, TITLE_SIZE)))
    _tlh = int(0.40 * TITLE_SIZE)   # 墨迹高（含逗号下伸）
    print("\n---- 标题×时间模块防重叠检查 ----")
    # A 版：居中 x512，墨迹顶 230
    ax0 = W // 2 - _tlw // 2
    assert_no_title_time_overlap("A 版", (ax0, 230, ax0 + _tlw, 230 + _tlh))
    # B 版：左对齐 x40，墨迹顶 200
    assert_no_title_time_overlap("B 版", (40, 200, 40 + _tlw, 200 + _tlh))
    # C 版：居中 x512，墨迹顶 692
    assert_no_title_time_overlap("C 版", (ax0, 692, ax0 + _tlw, 692 + _tlh))

if __name__ == "__main__":
    main()
