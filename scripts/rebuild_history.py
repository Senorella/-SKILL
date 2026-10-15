# -*- coding: utf-8 -*-
"""重建《镜中人》A 版被覆盖的历史版本，供对比存档。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import make_poster_mirror as M
from typographic_halftone import render_size_halftone
from utils import save_no_overwrite


def _a_base():
    src = M.load_clean(M.SRC_MIRROR).resize((M.W, M.H), Image.LANCZOS)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = img.convert("RGB")
    M.global_pad_dark(img, alpha=185)
    M.img_holder[0] = img
    d = ImageDraw.Draw(img)
    d.text((984, 40), "时间 Time", font=M.f(M.F_YHBD, 22), fill=M.GREY_D, anchor="ra")
    d.text((984, 74), M.PERIOD, font=M.f(M.F_AA, 54), fill=M.MIRROR_BLUE, anchor="ra")
    d.text((984, 148), M.HOURS, font=M.f(M.F_YH, 26), fill=M.MIST_W, anchor="ra")
    return img, d


def build_A_v1():
    """v1：标题左对齐置于顶部暗带（墨迹顶 y44），与右上日期重叠"""
    img, d = _a_base()
    bot = M.draw_title_dark(img, 44, M.MIRROR_BLUE, x=40)
    d.text((44, bot + 42), M.SUB, font=M.f(M.F_YHBD, 46), fill=M.MIST_W)
    d.text((44, bot + 122), M.SLOGAN, font=M.f(M.F_YHBD, 42), fill=M.MIST_W)
    M.tracked(d, (44, bot + 196), M.EN, M.f(M.F_DENGB, 17), M.GREY_D, 0.08)
    M.bottom_block_dark(d, M.MIST_W, M.EMBER_RED, M.MIST_W)
    return img


def build_A_v2():
    """v2：标题居中（墨迹顶 y170），仍轻微压入右上时间模块墨迹底 y180"""
    img, d = _a_base()
    bot = M.draw_title_dark(img, 170, M.MIRROR_BLUE, anchor="ma", x=M.W // 2)
    d.text((M.W // 2, bot + 42), M.SUB, font=M.f(M.F_YHBD, 46), fill=M.MIST_W, anchor="ma")
    d.text((M.W // 2, bot + 122), M.SLOGAN, font=M.f(M.F_YHBD, 42), fill=M.MIST_W, anchor="ma")
    M.tracked_center(d, bot + 196, M.EN, M.f(M.F_DENGB, 17), M.GREY_D, 0.08)
    M.bottom_block_dark(d, M.MIST_W, M.EMBER_RED, M.MIST_W)
    return img


if __name__ == "__main__":
    save_no_overwrite(build_A_v1(), os.path.join(M.OUT, "mirror_A_黑底镜中人冰蓝_v1_标题顶部重叠.png"))
    save_no_overwrite(build_A_v2(), os.path.join(M.OUT, "mirror_A_黑底镜中人冰蓝_v2_标题居中轻微压右上.png"))
    print("done")
