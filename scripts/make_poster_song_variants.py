# -*- coding: utf-8 -*-
"""
make_poster_song_variants.py — 宋代美学特展三版海报
规则：只用 skill 两种版式（分区满版式 / 左置露白式），文字 ≤3 色（灰阶不计），颜色不必凑满三种。
文案不含「宋代美学特展」字样。配色为宋调低饱和（汝窑天青/月白/梅子青/绢本赭/朱砂淡）。

A 版 · 版式一（分区满版）黑底：点茶底图（裁剪填充饱满），汝窑天青标题
B 版 · 版式一（分区满版）白底：汝窑瓷灰点阵，天青灰蓝标题 + 朱砂淡传播语
C 版 · 版式二（左置露白）黑底：挂画立轴左移露出，粉青标题右对齐环绕
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import qrcode
import os
from typographic_halftone import render_size_halftone, GI

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "song_poster")
os.makedirs(OUT, exist_ok=True)

W, H = 1024, 1536

# ---- 宋调低饱和配色 ----
RUYAO       = (127, 180, 204)   # 汝窑天青（中等饱和，黑底清雅突出）标题/日期
TIANYUAN    = (94, 139, 163)    # 天青灰蓝（中等饱和，白底标题）
MEIQING     = (116, 180, 158)   # 粉青（中等饱和青绿，左置版标题）
JUANZHE     = (195, 164, 107)   # 绢本赭（中等饱和暖金，传播语/日期）
ZHUSHA      = (182, 88, 66)     # 朱砂（点缀色保留较高饱和，CTA）
GREY_W      = (238, 238, 238)
GREY_D      = (150, 150, 150)
INK         = (43, 43, 43)

F_ZIYU  = os.path.join(ROOT, "fonts", "ZiYuQuWeiXiangSu.ttf")
F_AA    = os.path.join(ROOT, "fonts", "AaXiaoGouGuaiGuaiXiangSuTi.ttf")
F_YHBD  = "C:/Windows/Fonts/msyhbd.ttc"
F_YH    = "C:/Windows/Fonts/msyh.ttc"
F_DENGB = "C:/Windows/Fonts/Dengb.ttf"

TITLE  = "如果宋朝有朋友圈"
EN     = "SONG DYNASTY AESTHETICS EXHIBITION"
SLOGAN = "看宋人如何点茶、挂画、过日子"
CTA    = "预约观展"
CTA_SUB = "扫码去微信小程序预约"
CTA_URL = "https://weixin.qq.com"
PERIOD = "2027.4.1 — 5.31"
HOURS  = "周二至周日 10:00–20:00"
VENUE  = "城市文化中心一层沉浸展厅"
HOST   = "城市文化中心"

SRC_DIANCHA = "宋代美学点茶场景_宋人手持茶筅击拂茶汤_茶盏茶筅细腻精致_黑_2026-10-09T20-06-19.png"
SRC_GUAHUA  = "宋代文人挂画场景_墙上挂一幅山水立轴_几案上置插花与香炉_文_2026-10-09T20-06-21.png"
SRC_RUYAO   = "宋代汝窑天青釉瓷器_温润素雅的青瓷瓶与茶盏_极简造型_黑白灰_2026-10-09T20-06-22.png"

def f(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)

def tracked(d, xy, text, font, fill, tracking=0.10):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        w = d.textlength(ch, font=font)
        x += w + w * tracking

def tracked_r(d, xy, text, font, fill, tracking=0.08):
    total = sum(d.textlength(ch, font=font) * (1 + tracking) for ch in text) - d.textlength(text[-1], font=font) * tracking
    x = xy[0] - total
    for ch in text:
        d.text((x, xy[1]), ch, font=font, fill=fill)
        w = d.textlength(ch, font=font)
        x += w + w * tracking

def gradient_text(img, xy, text, font, c_top, c_bottom,
                  anchor=None, glow=None, glow_alpha=22, glow_blur=10, stroke=1):
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

def global_pad_dark(img, alpha=190):
    overlay = Image.new("RGBA", img.size, (10, 10, 10, alpha))
    img.paste(overlay, (0, 0), overlay)

def global_pad_light(img, alpha=205):
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

# ---- 素材裁剪填充：把主体放大充满画幅，去除下部空 ----
def load_filled(src_name, crop_ratio=0.92):
    src = Image.open(os.path.join(GI, src_name)).convert("L")
    w, h = src.size
    cropped = src.crop((0, 0, w, int(h * crop_ratio)))
    return cropped.resize((W, H), Image.LANCZOS)


# ============ A 版 · 版式一（分区满版）黑底点茶 ============
def build_A():
    src = load_filled(SRC_DIANCHA, crop_ratio=0.90)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    global_pad_dark(img, alpha=175)   # 比敦煌版略低，让点茶人更可辨、底图更饱满
    d = ImageDraw.Draw(img)

    # 时间模块右上
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=GREY_D, anchor="ra")
    d.text((984, 74), PERIOD, font=f(F_AA, 54), fill=RUYAO, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=GREY_W, anchor="ra")

    # 标题（汝窑天青微弱高光）——下移到底图主体下方（主体下缘约 y1020）
    gradient_text(img, (40, 975), TITLE, f(F_ZIYU, 200),
                  _mix(RUYAO, (255,255,255), 0.18), RUYAO,
                  glow=RUYAO, glow_alpha=20, glow_blur=10)

    # 传播语（绢本赭）+ 英文
    d.text((44, 1230), SLOGAN, font=f(F_YHBD, 42), fill=JUANZHE)
    tracked(d, (44, 1298), EN, f(F_DENGB, 17), GREY_D, 0.08)

    # 地点/主办左下
    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=GREY_D)
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=GREY_W)
    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=GREY_D)
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=GREY_D)

    # 二维码右下
    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=ZHUSHA, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=GREY_W, anchor="ra")
    return img


# ============ B 版 · 版式一（分区满版）白底灰点阵汝窑瓷 ============
def build_B():
    src = load_filled(SRC_RUYAO, crop_ratio=0.90)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = ImageOps.invert(img).convert("L")
    px = img.load()
    for y in range(H):
        for x in range(W):
            v = px[x, y] / 255.0
            px[x, y] = int((v ** 1.7) * 255)
    img = img.convert("RGB")
    _whiten(img)
    global_pad_light(img, alpha=205)
    d = ImageDraw.Draw(img)

    # 时间模块右上
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=(98, 106, 110), anchor="ra")
    d.text((984, 74), PERIOD, font=f(F_AA, 54), fill=TIANYUAN, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=(98, 106, 110), anchor="ra")

    # 标题（天青灰蓝）——下移到底图主体下方（主体下缘约 y1030）
    d.text((40, 975), TITLE, font=f(F_ZIYU, 200), fill=TIANYUAN, stroke_width=1, stroke_fill=TIANYUAN)

    # 传播语（朱砂）+ 英文
    d.text((44, 1230), SLOGAN, font=f(F_YHBD, 42), fill=ZHUSHA)
    tracked(d, (44, 1298), EN, f(F_DENGB, 17), (98, 106, 110), 0.08)

    # 地点/主办左下
    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=(98, 106, 110))
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=TIANYUAN)
    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=(98, 106, 110))
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=(98, 106, 110))

    # 二维码右下
    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=ZHUSHA, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=(98, 106, 110), anchor="ra")
    return img


# ============ C 版 · 版式二（左置露白）挂画 ============
def build_C():
    src = Image.open(os.path.join(GI, SRC_GUAHUA)).convert("L")
    w, h = src.size
    side = min(w, h)
    cx, cy = w // 2, int(h * 0.42)
    half = side // 2
    sq = src.crop((max(0, cx - half), max(0, cy - half),
                   min(w, cx + half), min(h, cy + half)))
    big_w = int(W * 1.0)
    hal = render_size_halftone(sq, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    hal = hal.convert("RGB").resize((big_w, int(big_w * sq.size[1] / sq.size[0])), Image.LANCZOS)

    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    offset_x = int(W * 0.33) - big_w // 2
    offset_y = H // 2 - hal.size[1] // 2
    canvas.paste(hal, (offset_x, offset_y))

    overlay = Image.new("RGBA", canvas.size, (10, 10, 10, 185))
    canvas.paste(overlay, (0, 0), overlay)
    d = ImageDraw.Draw(canvas)

    # 时间模块右上
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=GREY_D, anchor="ra")
    d.text((984, 74), PERIOD, font=f(F_AA, 54), fill=JUANZHE, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=GREY_W, anchor="ra")

    # 标题右对齐（粉青微弱高光）
    gradient_text(canvas, (984, 360), TITLE, f(F_ZIYU, 150),
                  _mix(MEIQING, (255,255,255), 0.18), MEIQING,
                  anchor="ra", glow=MEIQING, glow_alpha=20, glow_blur=10)

    # 传播语 + 英文
    d.text((984, 560), SLOGAN, font=f(F_YHBD, 38), fill=GREY_W, anchor="ra")
    tracked_r(d, (984, 618), EN, f(F_DENGB, 15), GREY_D, 0.08)

    # 地点/主办右下
    d.text((984, 1310), "地点 Location", font=f(F_YHBD, 22), fill=GREY_D, anchor="ra")
    d.text((984, 1344), VENUE, font=f(F_YHBD, 30), fill=GREY_W, anchor="ra")
    d.text((984, 1420), "主办 Organizer", font=f(F_YHBD, 20), fill=GREY_D, anchor="ra")
    d.text((984, 1452), HOST, font=f(F_YH, 22), fill=GREY_D, anchor="ra")

    # 二维码左下
    qr = make_qr(CTA_URL)
    paste_qr(canvas, qr, (60, 1400), 64)
    d.text((140, 1404), CTA, font=f(F_YHBD, 24), fill=ZHUSHA)
    d.text((140, 1442), CTA_SUB, font=f(F_YH, 16), fill=GREY_D)
    return canvas


def main():
    variants = [
        ("A_黑底点茶汝窑天青", build_A()),
        ("B_白底汝窑灰点阵", build_B()),
        ("C_左置挂画粉青", build_C()),
    ]
    for name, img in variants:
        out = os.path.join(OUT, f"song_{name}.png")
        img.save(out, "PNG")
        print("saved:", out)

    files = [n for n in os.listdir(OUT) if n.startswith("song_") and n.endswith(".png")]
    files.sort()
    thumbs = [Image.open(os.path.join(OUT, n)).resize((256, 384)) for n in files]
    sheet = Image.new("RGB", (256 * len(thumbs) + 8 * (len(thumbs) - 1), 384), (60, 60, 60))
    x = 0
    for t in thumbs:
        sheet.paste(t, (x, 0)); x += 264
    sheet.save(os.path.join(OUT, "_variants_compare.png"))
    print("sheet ok")

if __name__ == "__main__":
    main()
