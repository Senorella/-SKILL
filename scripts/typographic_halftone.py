# -*- coding: utf-8 -*-
"""
typographic_halftone.py — 字符半调印刷肖像渲染（Typographic Halftone Portrait）
原理：灰度图按网格分块 → 每块亮度映射到「字符 + 墨色」→ 真实等宽字体绘制
      → 可选纸张纹理 / 印刷颗粒。
字符本身参与明暗塑造：暗区用高覆盖率字符(@#%&)密排，亮区用稀疏的点/短线/留白。
可调：字符集、网格(cell)、字号、灰阶映射、墨色曲线、纸张颗粒强度。
运行：D:/python311/python.exe typographic_halftone.py
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import random, os

ROOT = os.path.dirname(os.path.abspath(__file__))
GI = os.path.join(ROOT, "generated-images")
OUT = os.path.join(ROOT, "output", "dunhuang_typographic_halftone")
os.makedirs(OUT, exist_ok=True)

# 等宽字体（字符半调需等宽以保证网格对齐）
FONT_MONO = "C:/Windows/Fonts/consola.ttf"

# 字符集：按“覆盖率/明度”从深到浅排列（暗→亮）
CHARSET = "@#%&*+=-:.;, "   # 最暗 @ 到最亮 空格
# 更精细的字符集（测试 A 用，符号多样）
CHARSET_FINE = "@#%8&*+=/\\|:;.,'` "

# 纸色与墨色
PAPER = (240, 238, 231)      # 米白纸色 #F0EEE7
INK   = (17, 17, 17)         # 墨黑 #111111


# 反白字符集：按覆盖率从疏到密排列（暗→留空，亮→密集字符）
CHARSET_INV = " .,:;-~=+*%&#@"

def _char_for(v, charset):
    """亮度 v(0黑~255白) → 字符索引。v 越高(亮)取覆盖率越高的字符。
    （反白模式：黑底上，亮部用密集浅色字符，暗部留黑）"""
    n = len(charset)
    idx = int(round(v / 255.0 * (n - 1)))
    return charset[max(0, min(n - 1, idx))]


def render_halftone(gray, cell=16, charset=CHARSET, ink_gamma=1.0,
                    contrast=1.0, jitter=0.0, seed=0, bg_dots=True):
    """核心字符半调渲染（反白：黑底 + 浅色字符）。返回 RGB 图。
    gray: 灰度图(0黑~255白)；亮部→密集浅色字符，暗部→稀疏字符/黑底
    cell: 字符网格边长（输出像素，即单字符字号的基准）
    ink_gamma: <1 加深墨色覆盖（亮部字符更密），>1 提亮
    contrast: 明暗对比系数
    jitter: 0~1 字符亮度抖动
    bg_dots: 背景暗区补稀疏暗点（黑底肌理）
    """
    w, h = gray.size
    # 明暗曲线：对比 + gamma（保持：亮部更亮、暗部更暗）
    g = ImageOps.autocontrast(gray.convert("L"), cutoff=1)
    px = g.load()
    for y in range(h):
        for x in range(w):
            v = px[x, y] / 255.0
            v = (v - 0.5) * contrast + 0.5
            v = max(0.0, min(1.0, v)) ** ink_gamma
            px[x, y] = int(v * 255)

    # 下采样到字符网格（BOX 均值，保持块面）
    gw, gh = w // cell, h // cell
    small = g.resize((gw, gh), Image.BOX)
    sp = small.load()

    rnd = random.Random(seed)
    # 结果画布：纯黑底
    img = Image.new("RGB", (w, h), (10, 10, 10))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_MONO, cell)

    for gy in range(gh):
        for gx in range(gw):
            v = sp[gx, gy]
            if jitter > 0:
                v = max(0, min(255, v + rnd.uniform(-1, 1) * jitter * 60))
            ch = _char_for(v, charset)
            # 暗区（近乎纯黑）补稀疏暗灰点，避免死黑
            if ch == " " and bg_dots and rnd.random() < 0.05:
                d.text((gx * cell, gy * cell), "·", font=font, fill=(50, 50, 50))
                continue
            # 墨色：亮部字符更浅（更白），暗部字符偏灰
            inkv = int(235 - (1 - v / 255.0) * 80)
            d.text((gx * cell, gy * cell), ch, font=font, fill=(inkv, inkv, inkv))
    return img


def add_paper_texture(img, strength=18, seed=1):
    """克制的纸张颗粒/印刷不均匀（不模糊字符轮廓）。"""
    rnd = random.Random(seed)
    w, h = img.size
    noise = Image.new("L", (w // 3, h // 3))
    np_ = noise.load()
    for y in range(noise.height):
        for x in range(noise.width):
            np_[x, y] = int(rnd.uniform(0, strength))
    noise = noise.resize((w, h), Image.BILINEAR).convert("RGB")
    return Image.blend(img, noise, 0.04)


if __name__ == "__main__":
    src = Image.open(os.path.join(GI, "Full_bleed_poster_background___2026-10-09T15-49-47.png"))
    src = src.convert("L").resize((1024, 1536), Image.LANCZOS)

    tests = {
        "A_精细字符": dict(cell=12, charset=CHARSET_FINE, ink_gamma=0.85, contrast=1.35, jitter=0.0),
        "B_高对比":   dict(cell=12, charset=CHARSET,      ink_gamma=0.6,  contrast=1.6,  jitter=0.0),
        "C_编辑印刷": dict(cell=12, charset=CHARSET_FINE, ink_gamma=0.75, contrast=1.45, jitter=0.15),
    }
    for name, kw in tests.items():
        out = render_halftone(src, **kw)
        if name == "C_编辑印刷":
            out = add_paper_texture(out, strength=22, seed=2)
        p = os.path.join(OUT, f"halftone_test_{name}.png")
        out.save(p, "PNG")
        print("saved:", p)

    # 并排对比图
    sheet = Image.new("RGB", (1024 * 3 // 2, 1536 // 2), (200, 200, 200))
    for i, name in enumerate(tests):
        t = Image.open(os.path.join(OUT, f"halftone_test_{name}.png")).resize((512, 768), Image.LANCZOS)
        sheet.paste(t, (i * 512, 0))
    sheet.save(os.path.join(OUT, "compare_sheet.png"), "PNG")
    print("saved: compare_sheet.png")


# ==================== 十字绣编织点阵（参考图大象风格） ====================

def render_crossstitch(gray, cell=9, contrast=1.5, ink_gamma=0.7,
                       line_w=None, seed=0):
    """十字绣式渲染：每个 cell 按亮度绘制不同针脚——
    暗：实心小方块 → 中暗：实心× → 中亮：细×/十 → 亮：中心小点 → 最亮：留空。
    黑底反白：亮部针脚浅色。cell 越小越精细（推荐 8-10）。
    """
    w, h = gray.size
    g = ImageOps.autocontrast(gray.convert("L"), cutoff=1)
    px = g.load()
    for y in range(h):
        for x in range(w):
            v = px[x, y] / 255.0
            v = (v - 0.5) * contrast + 0.5
            v = max(0.0, min(1.0, v)) ** ink_gamma
            px[x, y] = int(v * 255)
    gw, gh = w // cell, h // cell
    small = g.resize((gw, gh), Image.BOX)
    sp = small.load()

    img = Image.new("RGB", (w, h), (10, 10, 10))
    d = ImageDraw.Draw(img)
    lw = line_w or max(2, cell // 4)   # 针脚线宽

    for gy in range(gh):
        for gx in range(gw):
            v = sp[gx, gy] / 255.0
            cx, cy = gx * cell + cell // 2, gy * cell + cell // 2
            r = cell // 2 - 1
            if v < 0.10:
                continue                      # 最暗：留黑
            elif v < 0.30:
                col = (150, 150, 150)         # 暗灰针脚
            elif v < 0.55:
                col = (185, 185, 185)
            elif v < 0.80:
                col = (215, 215, 215)
            else:
                col = (240, 240, 240)         # 亮部针脚
            # 针脚形态按亮度：越亮越稀疏
            if v < 0.35:
                d.rectangle([cx - r, cy - r, cx + r, cy + r], fill=col)      # 实心块
            elif v < 0.60:
                # 实心 ×（两条对角线）
                d.line([cx - r, cy - r, cx + r, cy + r], fill=col, width=lw)
                d.line([cx - r, cy + r, cx + r, cy - r], fill=col, width=lw)
            elif v < 0.85:
                # 细 ×
                lw2 = max(1, lw - 1)
                d.line([cx - r, cy - r, cx + r, cy + r], fill=col, width=lw2)
                d.line([cx - r, cy + r, cx + r, cy - r], fill=col, width=lw2)
            else:
                d.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=col)        # 中心点
    return img


# ==================== 变尺寸半调（亮部大密 / 暗部小疏 + 轮廓光） ====================

def render_size_halftone_light(gray, cell=10, contrast=1.35, ink_gamma=0.85,
                               rim=True, rim_gain=1.6, seed=0, white_point=0.06):
    """白底变尺寸墨点半调（白主体/高调素材专用）：
    - 亮部（白纱本体）→ 留白，保住「白」的观感
    - 暗部（人影/褶皱阴影）→ 墨点大而密、色深
    - 明暗结构原样保留（正片逻辑），白主体禁用 invert 反相方案
    white_point: 留白阈值（暗度低于此值完全留白）。高调图（白纱）用默认 0.06；
                 中灰调静物可提到 0.28–0.35，避免背景中灰产生大片墨点淹没主体。
    """
    w, h = gray.size
    g = ImageOps.autocontrast(gray.convert("L"), cutoff=1)
    px = g.load()
    for y in range(h):
        for x in range(w):
            v = px[x, y] / 255.0
            v = (v - 0.5) * contrast + 0.5
            v = max(0.0, min(1.0, v)) ** ink_gamma
            px[x, y] = int(v * 255)

    gw, gh = w // cell, h // cell
    small = g.resize((gw, gh), Image.BOX)
    sp = small.load()
    rnd = random.Random(seed)
    wp = white_point

    img = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(img)

    for gy in range(gh):
        for gx in range(gw):
            v = sp[gx, gy] / 255.0
            dk = 1.0 - v                      # 暗度：0=白 1=最深
            if dk < wp:
                continue                      # 亮部留白
            # 暗度 → 墨点半径（越暗越大）与墨色（越暗越黑），分级随 wp 平移
            r = cell * (0.10 + 0.42 * ((dk - wp) / max(0.01, 1.0 - wp)) ** 0.65)
            if dk < wp + 0.19:   col = (215, 215, 215)   # 极浅灰（表面微纹理）
            elif dk < wp + 0.39: col = (175, 175, 175)   # 浅灰
            elif dk < wp + 0.59: col = (120, 120, 120)   # 中灰
            else:                col = (55, 55, 55)      # 深墨（主体暗部）
            # 稀疏区：wp 到 wp+0.27 之间按线性概率跳过
            if dk < wp + 0.27 and rnd.random() > (dk - wp) / 0.27:
                continue
            cx, cy = gx * cell + cell // 2, gy * cell + cell // 2
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    if rim:
        # 轮廓：梯度大处画深色小点，勾出主体边缘
        sp2 = small.load()
        for gy in range(1, gh - 1):
            for gx in range(1, gw - 1):
                gx_ = (abs(sp2[gx+1, gy] - sp2[gx-1, gy]) +
                       abs(sp2[gx, gy+1] - sp2[gx, gy-1])) / 255.0
                dk = 1.0 - sp2[gx, gy] / 255.0
                if gx_ * (0.4 + dk) > 0.34 * rim_gain and dk > wp + 0.04 and dk < 0.85:
                    cx, cy = gx * cell + cell // 2, gy * cell + cell // 2
                    r = cell * 0.38
                    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(35, 35, 35))
    return img


def render_size_halftone(gray, cell=10, contrast=1.35, ink_gamma=0.85,
                         rim=True, rim_gain=1.6, seed=0):
    """像素尺寸随亮度变化的半调（参考章鱼像成像逻辑）：
    - 亮部：像素大（接近满格）且密集 → 形成亮块面
    - 暗部：像素小而稀疏（微型点）→ 保留暗部层次，不死黑
    - 主体边缘（灰度梯度大处）叠加高亮轮廓光像素，与黑底强分离
    - 远看形体清晰，近看是大小错落的点阵
    cell: 基础网格；contrast/gamma 同前；rim: 是否加轮廓光
    """
    w, h = gray.size
    g = ImageOps.autocontrast(gray.convert("L"), cutoff=1)
    px = g.load()
    for y in range(h):
        for x in range(w):
            v = px[x, y] / 255.0
            v = (v - 0.5) * contrast + 0.5
            v = max(0.0, min(1.0, v)) ** ink_gamma
            px[x, y] = int(v * 255)

    gw, gh = w // cell, h // cell
    small = g.resize((gw, gh), Image.BOX)
    sp = small.load()
    rnd = random.Random(seed)

    img = Image.new("RGB", (w, h), (8, 8, 8))
    d = ImageDraw.Draw(img)

    for gy in range(gh):
        for gx in range(gw):
            v = sp[gx, gy] / 255.0
            cx, cy = gx * cell + cell // 2, gy * cell + cell // 2
            if v < 0.04:
                continue
            # 亮度 → 像素半径：亮部大块，暗部小点（面积∝亮度，视觉均匀）
            r = cell * (0.10 + 0.42 * (v ** 0.65))
            # 亮度 → 明度：亮部接近白，暗部保留深灰（不死黑）
            if v < 0.22:   col = (95 + int(v * 250),) * 3
            elif v < 0.50: col = (150, 150, 150)
            elif v < 0.78: col = (200, 200, 200)
            else:          col = (238, 238, 238)
            # 暗部稀疏：低亮度按概率跳过，制造疏密差
            if v < 0.30 and rnd.random() > 0.35 + v:
                continue
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    if rim:
        # 轮廓光：对下采样图做梯度检测，边缘格画高亮小像素
        sp2 = small.load()
        for gy in range(1, gh - 1):
            for gx in range(1, gw - 1):
                gx_ = (abs(sp2[gx+1, gy] - sp2[gx-1, gy]) +
                       abs(sp2[gx, gy+1] - sp2[gx, gy-1])) / 255.0
                v = sp2[gx, gy] / 255.0
                if gx_ * (0.4 + v) > 0.34 * rim_gain and 0.10 < v < 0.85:
                    cx, cy = gx * cell + cell // 2, gy * cell + cell // 2
                    r = cell * 0.38
                    d.ellipse([cx - r, cy - r, cx + r, cy + r],
                              fill=(255, 255, 255))
    return img
