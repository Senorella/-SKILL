# -*- coding: utf-8 -*-
"""
展览海报合成脚本 v3.5（信息区高度按内容自适应）
两步法第二步：AI 灰阶画面 + Pillow 真实字体排字 -> 完整 PNG (1024x1536)
v3.5 变更：信息区高度不再写死——先在空白画布干跑测量内容实际高度，
          再贴底落位（底部只留 PAD_BOTTOM 呼吸）。解决"内容少的展览
          底部留白一大块、同时信息区上边缘遮挡画面主体"的双重问题。
v3.4 变更：信息区整体下移（INFO_H 640->560），同步收紧间距，线上下对称。
v3.2 变更：块高自适应（左右两列取较高者）+ 块内行间距统一 + 块间距统一，
          解决"小字与线条之间间距不平衡 / 块内不居中"问题。
v3.0 变更：把展览信息参数化（EXHIBITIONS 字典），换展览只改数据不动布局
v2.3 规范：标题区 ty=32 整体上移、draw_safe 右边界护栏、联系方式拆三行
规范：主标题180px字语像素(灰#404040) / 副标题36px等线粗体 / 英文16px /
      大日期96px小狗乖乖粗笔画 / 信息区五级层级 + 2px #E0E0E0 分隔线
"""
from PIL import Image, ImageDraw, ImageFont
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def _find_font(name):
    """按优先级查找字体：1) workspace/fonts/ 2) skill assets/fonts/"""
    candidates = [
        os.path.join(os.getcwd(), "fonts", name),
        os.path.join(ROOT, "fonts", name),
        os.path.expanduser("~/.workbuddy/skills/exhibition-poster-two-step-pipeline/assets/fonts/" + name),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"字体 {name} 未找到，请先运行 init_workspace.py 或放到 workspace/fonts/")


F_ZIYU   = _find_font("ZiYuQuWeiXiangSu.ttf")
F_AA     = _find_font("AaXiaoGouGuaiGuaiXiangSuTi.ttf")
F_YHBD   = "C:/Windows/Fonts/msyhbd.ttc"
F_YH     = "C:/Windows/Fonts/msyh.ttc"
F_DENGB  = "C:/Windows/Fonts/Dengb.ttf"

INK      = (64, 64, 64, 255)
GREY_333 = (51, 51, 51, 255)
GREY_666 = (102, 102, 102, 255)
GREY_999 = (153, 153, 153, 255)
LINE     = (224, 224, 224, 255)
WHITE    = (255, 255, 255, 255)

# ============ 全局排版常量（v3.5 信息区高度按内容自适应）============
MAX_INFO_H     = 560    # 信息区高度上限（实际高度 = 内容干跑测量 + 底部呼吸，不超过此值）
PAD_TOP        = 20     # 信息区顶部呼吸
PAD_BOTTOM     = 20     # 信息区底部呼吸
BLOCK_GAP      = 18     # 块与块之间总间距（含 2px 线 + 上下各 8px）
INNER_LINE_GAP = 14     # 块内两行之间的间距（主行-副行）
LINE_OFFSET    = 8      # 横线距上一块底的距离（线距下一块顶 = BLOCK_GAP - LINE_OFFSET - 2 = 8，上下对称）
LABEL_X        = 60     # 左列标签起点（与外边距对齐）
LABEL_GAP      = 10     # 标签与色条之间间距
BAR_W          = 4      # 色条宽
BAR_H          = 24     # 色条高
CONTENT_X      = 180    # 右列起点
RIGHT          = 964    # 右边界护栏

def f(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)

def draw_tracked(d, xy, text, font, fill, tracking=0.0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        w = d.textlength(ch, font=font)
        x += w + w * tracking

def wrap_by_width(d, text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=font) <= max_w:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines

def draw_safe(d, xy, text, font, fill, right_edge, line_gap=INNER_LINE_GAP):
    """右边界护栏：超宽自动折行，绝不超出 right_edge。
    返回 (最后一行文字的起点 y, 行数)——底部 = 起点 y + font.size。"""
    x, y = xy
    max_w = right_edge - x
    lines = wrap_by_width(d, text, font, max_w)
    step = font.size + line_gap
    for i, ln in enumerate(lines):
        d.text((x, y + i * step), ln, font=font, fill=fill)
    last_start = y + (len(lines) - 1) * step
    return last_start, len(lines)

def draw_label(d, text, cy, accent):
    """绘制左列：标签文字 + 色条，与右列首行顶部对齐。"""
    d.text((LABEL_X, cy), text, font=LBL_FONT, fill=INK)
    lw = d.textlength(text, font=LBL_FONT)
    bx = LABEL_X + lw + LABEL_GAP
    d.rectangle([bx, cy + 2, bx + BAR_W, cy + 2 + BAR_H], fill=accent)

def hline(d, yy):
    d.rectangle([0, yy, W, yy + 2], fill=LINE)

# 字体（延迟到 make_poster 内，因 W 是 1024 模块级常量）
LBL_FONT    = f(F_YHBD, 24)
L2_FONT     = f(F_YHBD, 36)
L3_FONT     = f(F_YH,    28)
L4_FONT     = f(F_YH,    22)
DATE_FONT   = f(F_AA,     96)
PERIOD_FONT = f(F_YHBD,  36)

W = 1024
H = 1536

def render_info(d, info, iy0, accent):
    """绘制信息区（白色底由调用方铺）。返回内容实际底部 y（最后一行文字底部）。
    iy0 可传 0 用于干跑测量。"""
    hline(d, iy0)
    y = iy0 + PAD_TOP

    # ---- 块 1：大日期 ----
    cy = y
    draw_label(d, "时间", cy, accent)
    # 右列左：96px 大日期
    d.text((CONTENT_X, cy), info["date_digits"], font=DATE_FONT, fill=INK,
           stroke_width=3, stroke_fill=INK)
    dw = d.textlength(info["date_digits"], font=DATE_FONT)
    # 右列右：展期 + 下划线 + 时间说明（三段间距始终 14 / 20）
    px = CONTENT_X + dw + 28
    per_y = cy + 12
    draw_safe(d, (px, per_y), info["date_period"], PERIOD_FONT, INK, RIGHT)
    puw = d.textlength(info["date_period"], font=PERIOD_FONT)
    d.rectangle([px, per_y + PERIOD_FONT.size + 8, px + puw, per_y + PERIOD_FONT.size + 12],
                fill=accent)  # 下划线在展期下方 8px
    hours_y = per_y + PERIOD_FONT.size + 12 + 14  # 下划线下方 14px
    draw_safe(d, (px, hours_y), info["date_hours"], L4_FONT, GREY_999, RIGHT)
    # 块 1 高度：取 max(大日期 96, 右列总高 per_y+offset+L4)
    block1_right_h = (hours_y - cy) + L4_FONT.size
    block1_h = max(24, DATE_FONT.size, block1_right_h)
    y += block1_h
    hline(d, y + BLOCK_GAP - LINE_OFFSET)
    y += BLOCK_GAP

    # ---- 块 2：地点 ----
    cy = y
    draw_label(d, "地点", cy, accent)
    end_y, _ = draw_safe(d, (CONTENT_X, cy), info["venue_main"], L2_FONT, INK, RIGHT)
    end_y2, _ = draw_safe(d, (CONTENT_X, end_y + L2_FONT.size + INNER_LINE_GAP), info["venue_addr"], L4_FONT, GREY_999, RIGHT)
    block2_h = max(24, end_y2 + L4_FONT.size - cy)
    y += block2_h
    hline(d, y + BLOCK_GAP - LINE_OFFSET)
    y += BLOCK_GAP

    # ---- 块 3：票务 ----
    cy = y
    draw_label(d, "票务", cy, accent)
    end_y, _ = draw_safe(d, (CONTENT_X, cy), info["ticket_line"], L3_FONT, GREY_333, RIGHT)
    end_y2, _ = draw_safe(d, (CONTENT_X, end_y + L3_FONT.size + INNER_LINE_GAP), info["ticket_sub"], L4_FONT, GREY_999, RIGHT)
    block3_h = max(24, end_y2 + L4_FONT.size - cy)
    y += block3_h
    hline(d, y + BLOCK_GAP - LINE_OFFSET)
    y += BLOCK_GAP

    # ---- 块 4：主办 ----
    cy = y
    draw_label(d, "主办", cy, accent)
    end_y, _ = draw_safe(d, (CONTENT_X, cy), info["host_line"], L3_FONT, GREY_333, RIGHT)
    next_y = end_y + L3_FONT.size + INNER_LINE_GAP
    if info.get("contact_line1"):
        end_y, _ = draw_safe(d, (CONTENT_X, next_y), info["contact_line1"], L4_FONT, GREY_999, RIGHT)
        next_y = end_y + L4_FONT.size + INNER_LINE_GAP
    if info.get("contact_line2"):
        end_y, _ = draw_safe(d, (CONTENT_X, next_y), info["contact_line2"], L4_FONT, GREY_999, RIGHT)
        next_y = end_y + L4_FONT.size + INNER_LINE_GAP
    block4_h = max(24, next_y - INNER_LINE_GAP + L4_FONT.size - cy)
    y += block4_h
    hline(d, y + BLOCK_GAP - LINE_OFFSET)
    y += BLOCK_GAP

    # ---- 块 5：简介 ----
    cy = y
    draw_label(d, "简介", cy, accent)
    intro_lines = wrap_by_width(d, info["intro"], L4_FONT, RIGHT - CONTENT_X)
    if len(intro_lines) > 2:
        intro_lines = intro_lines[:2]
        last = intro_lines[-1]
        while d.textlength(last + "…", font=L4_FONT) > RIGHT - CONTENT_X and len(last) > 0:
            last = last[:-1]
        intro_lines[-1] = last + "…"
    ly = cy
    for ln in intro_lines:
        d.text((CONTENT_X, ly), ln, font=L4_FONT, fill=GREY_666)
        ly += L4_FONT.size + INNER_LINE_GAP
    # 内容底部 = 最后一行文字底部（ly 每轮多加了一个 INNER_LINE_GAP）
    content_bottom = ly - INNER_LINE_GAP
    return content_bottom

def make_poster(bg_path, out_path, accent, info):
    img = Image.open(bg_path).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(img)

    # ---------- 标题区 ----------
    ty = 32
    main_font = f(F_ZIYU, 180)
    d.text((LABEL_X, ty), info["title"], font=main_font, fill=INK,
           stroke_width=2, stroke_fill=INK)
    mw = d.textlength(info["title"], font=main_font) + LABEL_X + 24
    d.rectangle([mw, ty + 150, mw + 28, ty + 178], fill=accent)

    sub_font = f(F_DENGB, 36)
    sy = ty + int(180 * 1.02) + 14
    d.text((LABEL_X, sy), info["subtitle"], font=sub_font, fill=INK)

    en_font = f(F_DENGB, 16)
    ey = sy + int(36 * 1.3) + 8
    draw_tracked(d, (LABEL_X, ey), info["en_title"], en_font, INK, tracking=0.10)

    # ---------- 信息区（v3.5 高度按内容自适应）----------
    # 干跑测量：在空白画布上以 iy0=0 跑一遍布局，得到内容实际高度
    dummy = Image.new("RGB", (W, H), WHITE)
    dd = ImageDraw.Draw(dummy)
    content_bottom_rel = render_info(dd, info, 0, accent)
    info_h = content_bottom_rel + PAD_BOTTOM
    assert info_h <= MAX_INFO_H, f"信息区内容过高：{info_h} > {MAX_INFO_H}"
    iy0 = H - info_h
    d.rectangle([0, iy0, W, H], fill=WHITE)
    render_info(d, info, iy0, accent)

    img.save(out_path, "PNG")
    print("saved:", out_path)

# ===================== 展览信息参数库 =====================
EXHIBITIONS = {}

EXHIBITIONS["borders"] = dict(
    title="边界之外",
    subtitle="当代艺术的跨域对话",
    en_title="BEYOND BORDERS: A CROSS-DOMAIN DIALOGUE OF CONTEMPORARY ART",
    date_digits="03.15",
    date_period="2025.3.15 — 6.30",
    date_hours="周二至周日 10:00–18:00 ｜ 周一闭馆",
    venue_main="上海当代艺术博物馆 三层展厅 & 特别项目空间",
    venue_addr="上海市黄浦区苗江路678号",
    ticket_line="全价 80元 ｜ 学生/老人 40元 ｜ 会员免费",
    ticket_sub="线上预约：博物馆官方小程序或官网",
    host_line="上海当代艺术博物馆",
    contact_line1="联合主办：歌德学院 ｜ 英国文化协会",
    contact_line2="咨询 021-xxxx-xxxx ｜ www.powerstationofart.example",
    intro="本次展览汇集六国十二位当代艺术家，以绘画、装置、影像与沉浸式体验，探讨当代艺术如何突破地理、文化与身份的边界。",
)

EXHIBITIONS["bamboo"] = dict(
    title="指尖上的传承",
    subtitle="传统竹编手作体验季",
    en_title="INHERITANCE AT FINGERTIPS: TRADITIONAL BAMBOO WEAVING WORKSHOP",
    date_digits="03.22",
    date_period="2025.3.22 — 4.27",
    date_hours="每周六、日 14:00–17:00",
    venue_main="成都市青羊区非遗博览园 · 手作工坊",
    venue_addr="成都市青羊区光华大道二段",
    ticket_line="68元 / 人（含材料）",
    ticket_sub="每场限 20 人 · 需提前预约",
    host_line="青羊区文化馆 × 川西竹编合作社",
    contact_line1="",
    contact_line2="",
    intro="川西竹编非遗传承人现场亲授，亲手制作竹篮、竹灯或茶席垫，成品可带走；适合亲子与手作爱好者。",
)

# ===================== 任务列表 =====================
TASKS = {
    "borders": [
        (r"generated-images\竖版艺术展览插画设计_1024x1536_马赛克像素十字绣风_2026-10-08T09-20-34.png",
         (255, 165, 232),
         "borders-poster-1-相框隧道.png"),
        (r"generated-images\竖版艺术展览插画设计_1024x1536_马赛克像素十字绣风_2026-10-08T09-21-01.png",
         (54, 182, 255),
         "borders-poster-2-门与门槛.png"),
        (r"generated-images\竖版艺术展览插画设计_1024x1536_马赛克像素十字绣风_2026-10-08T09-20-55.png",
         (255, 191, 52),
         "borders-poster-3-跨越边界.png"),
    ],
    "bamboo": [
        (r"generated-images\竖版艺术展览插画设计_1024x1536_马赛克像素十字绣风_2026-10-09T02-10-14.png",
         (255, 191, 52),
         "bamboo-poster-1-工坊桌面.png"),
        (r"generated-images\竖版艺术展览插画设计_1024x1536_马赛克像素十字绣风_2026-10-09T02-10-58.png",
         (112, 233, 0),
         "bamboo-poster-2-大手传小手.png"),
        (r"generated-images\竖版艺术展览插画设计_1024x1536_马赛克像素十字绣风_2026-10-09T02-11-17.png",
         (255, 165, 232),
         "bamboo-poster-3-篾丝隧道.png"),
    ],
}

if __name__ == "__main__":
    gi = os.path.join(ROOT, "generated-images")
    for key, tasks in TASKS.items():
        info = EXHIBITIONS[key]
        for bg_rel, accent, name in tasks:
            bg = os.path.join(ROOT, bg_rel)
            out = os.path.join(gi, name)
            make_poster(bg, out, accent, info)