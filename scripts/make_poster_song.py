# -*- coding: utf-8 -*-
"""
make_poster_song.py — 宋代美学特展海报（复用 SKILL v4.13 三方案 + v4.14 左置露白）
文案：名称「如果宋朝有朋友圈」/ 传播语「看宋人如何点茶、挂画、过日子」
展期 2027.4.1–5.31 / 时间 周二至周日 10:00-20:00 / 地点 城市文化中心一层沉浸展厅
配色：宋代矿物色（天青 #4A90C4 / 汝窑青绿 #3FA58A / 朱砂 #C84A32 / 赭石 #B5763A / 墨 #2B2B2B）

方案一：黑底天青光泽（对应 v4.13 方案一）
方案二：白底单色汝窑青绿（对应 v4.13 方案二 S1）
方案三：白底灰点阵 + 天青标题 + 朱砂传播语（对应 v4.13 方案三 W2）
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import qrcode
import os
import sys
from typographic_halftone import render_size_halftone, GI

# 底图源：默认点茶，可用命令行参数切换素材文件名
DEFAULT_SRC = "宋代美学点茶场景_宋人手持茶筅击拂茶汤_茶盏茶筅细腻精致_黑_2026-10-09T20-06-19.png"
SRC = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output", "song_poster")
os.makedirs(OUT, exist_ok=True)

W, H = 1024, 1536

# ---- 宋代矿物色 ----
TIANQING_TOP = (120, 190, 235)   # 天青渐变·亮端
TIANQING_BOT = (54, 118, 168)    # 天青渐变·深端（色差收窄，微弱高光）
TIANQING     = (74, 144, 196)    # 天青纯色
RUYAO        = (63, 165, 138)    # 汝窑青绿
ZHUSHA       = (200, 74, 50)     # 朱砂红
ZHESHI       = (181, 118, 58)    # 赭石
INK          = (43, 43, 43)      # 墨黑（白底黑字用）
GREY_W       = (238, 238, 238)   # 亮灰白
GREY_D       = (150, 150, 150)   # 中灰

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
    """光泽感渐变文字：垂直渐变填充 + 可选同色系外发光。"""
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

# ---- 文案 ----
TITLE   = "如果宋朝有朋友圈"
SUBTITLE = "宋代美学特展"
EN      = "SONG DYNASTY AESTHETICS EXHIBITION"
SLOGAN  = "看宋人如何点茶、挂画、过日子"
CTA     = "预约观展"
CTA_SUB = "扫码去微信小程序预约"
CTA_URL = "https://weixin.qq.com"
PERIOD  = "2027.4.1 — 5.31"
EN_DATE = "APR 1 — MAY 31, 2027"
HOURS   = "周二至周日 10:00–20:00"
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

def global_pad(img, alpha=190):
    """黑底全图柔光层（铁律：一张、全图、贴文字前铺）。"""
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

def load_l():
    src = Image.open(os.path.join(GI, SRC))
    return src.convert("L").resize((W, H), Image.LANCZOS)

# ================= 方案一：黑底天青光泽 =================
def render_plan1():
    src = load_l()
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    global_pad(img, alpha=190)
    return img

def draw_plan1(img):
    d = ImageDraw.Draw(img)
    # 展期模块（右上）
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=GREY_D, anchor="ra")
    d.text((984, 74), PERIOD, font=f(F_AA, 54), fill=TIANQING, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=GREY_W, anchor="ra")

    # 展览名称（第一焦点）：天青微弱高光
    gradient_text(img, (40, 220), TITLE, f(F_ZIYU, 200),
                  TIANQING_TOP, TIANQING_BOT, glow=TIANQING_BOT, glow_alpha=22, glow_blur=10, stroke=1)
    d.text((44, 500), SUBTITLE, font=f(F_YHBD, 76), fill=TIANQING)

    # 传播语（朱砂）+ 英文行
    d.text((44, 680), SLOGAN, font=f(F_YHBD, 42), fill=ZHUSHA)
    tracked(d, (44, 740), EN, f(F_DENGB, 17), GREY_D, 0.08)

    # 地点模块（左下）
    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=GREY_D)
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=GREY_W)

    # 主办方模块
    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=GREY_D)
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=GREY_D)

    # 二维码 + CTA
    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=ZHUSHA, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=GREY_W, anchor="ra")
    return img

# ================= 方案二：白底单色汝窑青绿 =================
def render_plan2():
    src = load_l()
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    inv = ImageOps.invert(img).convert("L")
    px = inv.load()
    for y in range(H):
        for x in range(W):
            v = px[x, y] / 255.0
            px[x, y] = int((v ** 2.3) * 255)
    light_hue = _mix(RUYAO, (255, 255, 255), 0.45)
    img = ImageOps.colorize(inv, black=light_hue, white=(255, 255, 255))
    _whiten(img)
    global_pad_light(img, alpha=140)
    return img.convert("RGB")

def draw_plan2(img):
    d = ImageDraw.Draw(img)
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=_mix(RUYAO, (255,255,255), 0.35), anchor="ra")
    d.text((984, 74), PERIOD, font=f(F_AA, 54), fill=RUYAO, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=_mix(RUYAO, (255,255,255), 0.25), anchor="ra")

    d.text((40, 220), TITLE, font=f(F_ZIYU, 200), fill=RUYAO, stroke_width=1, stroke_fill=RUYAO)
    d.text((44, 500), SUBTITLE, font=f(F_YHBD, 76), fill=RUYAO)

    d.text((44, 680), SLOGAN, font=f(F_YHBD, 42), fill=RUYAO)
    tracked(d, (44, 740), EN, f(F_DENGB, 17), _mix(RUYAO, (255,255,255), 0.4), 0.08)

    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=_mix(RUYAO, (255,255,255), 0.35))
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=RUYAO)

    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=_mix(RUYAO, (255,255,255), 0.35))
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=_mix(RUYAO, (255,255,255), 0.3))

    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=RUYAO, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=_mix(RUYAO, (255,255,255), 0.25), anchor="ra")
    return img

# ================= 方案三：白底灰点阵 + 天青标题 + 朱砂传播语 =================
def render_plan3():
    src = load_l()
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
    return img

def draw_plan3(img):
    d = ImageDraw.Draw(img)
    d.text((984, 40), "时间 Time", font=f(F_YHBD, 22), fill=(98, 106, 110), anchor="ra")
    d.text((984, 74), PERIOD, font=f(F_AA, 54), fill=TIANQING, anchor="ra")
    d.text((984, 148), HOURS, font=f(F_YH, 26), fill=(98, 106, 110), anchor="ra")

    d.text((40, 220), TITLE, font=f(F_ZIYU, 200), fill=TIANQING, stroke_width=1, stroke_fill=TIANQING)
    d.text((44, 500), SUBTITLE, font=f(F_YHBD, 76), fill=TIANQING)

    d.text((44, 680), SLOGAN, font=f(F_YHBD, 42), fill=ZHUSHA)
    tracked(d, (44, 740), EN, f(F_DENGB, 17), (98, 106, 110), 0.08)

    d.text((44, 1330), "地点 Location", font=f(F_YHBD, 22), fill=(98, 106, 110))
    d.text((44, 1364), VENUE, font=f(F_YHBD, 32), fill=TIANQING)

    d.text((44, 1428), "主办 Organizer", font=f(F_YHBD, 22), fill=(98, 106, 110))
    d.text((44, 1462), HOST, font=f(F_YH, 24), fill=(98, 106, 110))

    qr = make_qr(CTA_URL)
    paste_qr(img, qr, (892, 1420), 64)
    d.text((858, 1424), CTA, font=f(F_YHBD, 24), fill=ZHESHI, anchor="ra")
    d.text((858, 1462), CTA_SUB, font=f(F_YH, 17), fill=(98, 106, 110), anchor="ra")
    return img

def main():
    plans = [
        ("plan1_黑底天青", draw_plan1(render_plan1())),
        ("plan2_白底汝窑", draw_plan2(render_plan2())),
        ("plan3_白底灰点阵", draw_plan3(render_plan3())),
    ]
    for name, img in plans:
        out = os.path.join(OUT, f"dunhuang_typo_song_{name}.png")
        img.save(out, "PNG")
        print("saved:", out)

    # 对比拼图
    files = [n for n in os.listdir(OUT) if n.endswith(".png") and not n.startswith("_")]
    files.sort()
    thumbs = [Image.open(os.path.join(OUT, n)).resize((256, 384)) for n in files]
    sheet = Image.new("RGB", (256 * len(thumbs) + 8 * (len(thumbs) - 1), 384), (60, 60, 60))
    x = 0
    for t in thumbs:
        sheet.paste(t, (x, 0)); x += 264
    sheet.save(os.path.join(OUT, "_compare_sheet.png"))
    print("sheet ok")

if __name__ == "__main__":
    main()
