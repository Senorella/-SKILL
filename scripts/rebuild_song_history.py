# -*- coding: utf-8 -*-
"""重建宋代海报所有被覆盖的历史版本（plan1/2/3 + variants v1/v2/v3）。

说明：
- plan1/2/3：make_poster_song.py 代码仍在，直接复用，精确重建。
- variants v2（低饱和）/ v3（高饱和）：配色值与标题位置有精确记录，基于 v4 逻辑参数化重建，精确。
- variants v1（含 B 居中印章式）：B 版式代码已被覆盖，按记忆描述近似重建。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageOps
import make_poster_song_variants as V   # 复用辅助函数、常量、素材名
import make_poster_song as P            # plan1/2/3 原始函数
from typographic_halftone import render_size_halftone
from utils import save_no_overwrite

HIST = os.path.join(V.ROOT, "output", "song_poster_history")
os.makedirs(HIST, exist_ok=True)

# ---- 各版本配色 ----
V1 = dict(RUYAO=(74, 144, 196), TIANYUAN=(74, 144, 196), MEIQING=(63, 165, 138),
          JUANZHE=(200, 74, 50), ZHUSHA=(200, 74, 50))          # v1 天青/石绿/朱砂（鲜艳）
V2 = dict(RUYAO=(159, 190, 203), TIANYUAN=(110, 139, 153), MEIQING=(168, 195, 184),
          JUANZHE=(201, 183, 154), ZHUSHA=(184, 87, 74))        # v2 低饱和宋调
V3 = dict(RUYAO=(74, 160, 202), TIANYUAN=(40, 118, 160), MEIQING=(58, 152, 136),
          JUANZHE=(196, 142, 52), ZHUSHA=(190, 52, 40))         # v3 高饱和

POS_UP    = dict(title=240, slogan=540, en=600)    # v1/v2：标题未下移
POS_DOWN  = dict(title=975, slogan=1230, en=1298)  # v3：标题下移到底图下方


def build_A(pal, pos):
    """黑底点茶满版"""
    src = V.load_filled(V.SRC_DIANCHA, crop_ratio=0.90)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    V.global_pad_dark(img, alpha=175)
    d = ImageDraw.Draw(img)
    d.text((984, 40), "时间 Time", font=V.f(V.F_YHBD, 22), fill=V.GREY_D, anchor="ra")
    d.text((984, 74), V.PERIOD, font=V.f(V.F_AA, 54), fill=pal["RUYAO"], anchor="ra")
    d.text((984, 148), V.HOURS, font=V.f(V.F_YH, 26), fill=V.GREY_W, anchor="ra")
    V.gradient_text(img, (40, pos["title"]), V.TITLE, V.f(V.F_ZIYU, 200),
                    V._mix(pal["RUYAO"], (255, 255, 255), 0.18), pal["RUYAO"],
                    glow=pal["RUYAO"], glow_alpha=20, glow_blur=10)
    d.text((44, pos["slogan"]), V.SLOGAN, font=V.f(V.F_YHBD, 42), fill=pal["JUANZHE"])
    V.tracked(d, (44, pos["en"]), V.EN, V.f(V.F_DENGB, 17), V.GREY_D, 0.08)
    d.text((44, 1330), "地点 Location", font=V.f(V.F_YHBD, 22), fill=V.GREY_D)
    d.text((44, 1364), V.VENUE, font=V.f(V.F_YHBD, 32), fill=V.GREY_W)
    d.text((44, 1428), "主办 Organizer", font=V.f(V.F_YHBD, 22), fill=V.GREY_D)
    d.text((44, 1462), V.HOST, font=V.f(V.F_YH, 24), fill=V.GREY_D)
    qr = V.make_qr(V.CTA_URL); V.paste_qr(img, qr, (892, 1420), 64)
    d.text((858, 1424), V.CTA, font=V.f(V.F_YHBD, 24), fill=pal["ZHUSHA"], anchor="ra")
    d.text((858, 1462), V.CTA_SUB, font=V.f(V.F_YH, 17), fill=V.GREY_W, anchor="ra")
    return img


def build_B(pal, pos):
    """白底汝窑灰点阵"""
    src = V.load_filled(V.SRC_RUYAO, crop_ratio=0.90)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = ImageOps.invert(img).convert("L")
    px = img.load()
    for y in range(V.H):
        for x in range(V.W):
            v = px[x, y] / 255.0
            px[x, y] = int((v ** 1.7) * 255)
    img = img.convert("RGB")
    V._whiten(img)
    V.global_pad_light(img, alpha=205)
    d = ImageDraw.Draw(img)
    d.text((984, 40), "时间 Time", font=V.f(V.F_YHBD, 22), fill=(98, 106, 110), anchor="ra")
    d.text((984, 74), V.PERIOD, font=V.f(V.F_AA, 54), fill=pal["TIANYUAN"], anchor="ra")
    d.text((984, 148), V.HOURS, font=V.f(V.F_YH, 26), fill=(98, 106, 110), anchor="ra")
    d.text((40, pos["title"]), V.TITLE, font=V.f(V.F_ZIYU, 200), fill=pal["TIANYUAN"],
           stroke_width=1, stroke_fill=pal["TIANYUAN"])
    d.text((44, pos["slogan"]), V.SLOGAN, font=V.f(V.F_YHBD, 42), fill=pal["ZHUSHA"])
    V.tracked(d, (44, pos["en"]), V.EN, V.f(V.F_DENGB, 17), (98, 106, 110), 0.08)
    d.text((44, 1330), "地点 Location", font=V.f(V.F_YHBD, 22), fill=(98, 106, 110))
    d.text((44, 1364), V.VENUE, font=V.f(V.F_YHBD, 32), fill=pal["TIANYUAN"])
    d.text((44, 1428), "主办 Organizer", font=V.f(V.F_YHBD, 22), fill=(98, 106, 110))
    d.text((44, 1462), V.HOST, font=V.f(V.F_YH, 24), fill=(98, 106, 110))
    qr = V.make_qr(V.CTA_URL); V.paste_qr(img, qr, (892, 1420), 64)
    d.text((858, 1424), V.CTA, font=V.f(V.F_YHBD, 24), fill=pal["ZHUSHA"], anchor="ra")
    d.text((858, 1462), V.CTA_SUB, font=V.f(V.F_YH, 17), fill=(98, 106, 110), anchor="ra")
    return img


def build_C(pal, pos=None):
    """左置露白挂画"""
    src = Image.open(os.path.join(V.GI, V.SRC_GUAHUA)).convert("L")
    w, h = src.size
    side = min(w, h)
    cx, cy = w // 2, int(h * 0.42)
    half = side // 2
    sq = src.crop((max(0, cx - half), max(0, cy - half), min(w, cx + half), min(h, cy + half)))
    big_w = int(V.W * 1.0)
    hal = render_size_halftone(sq, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    hal = hal.convert("RGB").resize((big_w, int(big_w * sq.size[1] / sq.size[0])), Image.LANCZOS)
    canvas = Image.new("RGB", (V.W, V.H), (0, 0, 0))
    offset_x = int(V.W * 0.33) - big_w // 2
    offset_y = V.H // 2 - hal.size[1] // 2
    canvas.paste(hal, (offset_x, offset_y))
    overlay = Image.new("RGBA", canvas.size, (10, 10, 10, 185))
    canvas.paste(overlay, (0, 0), overlay)
    d = ImageDraw.Draw(canvas)
    d.text((984, 40), "时间 Time", font=V.f(V.F_YHBD, 22), fill=V.GREY_D, anchor="ra")
    d.text((984, 74), V.PERIOD, font=V.f(V.F_AA, 54), fill=pal["JUANZHE"], anchor="ra")
    d.text((984, 148), V.HOURS, font=V.f(V.F_YH, 26), fill=V.GREY_W, anchor="ra")
    V.gradient_text(canvas, (984, 360), V.TITLE, V.f(V.F_ZIYU, 150),
                    V._mix(pal["MEIQING"], (255, 255, 255), 0.18), pal["MEIQING"],
                    anchor="ra", glow=pal["MEIQING"], glow_alpha=20, glow_blur=10)
    d.text((984, 560), V.SLOGAN, font=V.f(V.F_YHBD, 38), fill=V.GREY_W, anchor="ra")
    V.tracked_r(d, (984, 618), V.EN, V.f(V.F_DENGB, 15), V.GREY_D, 0.08)
    d.text((984, 1310), "地点 Location", font=V.f(V.F_YHBD, 22), fill=V.GREY_D, anchor="ra")
    d.text((984, 1344), V.VENUE, font=V.f(V.F_YHBD, 30), fill=V.GREY_W, anchor="ra")
    d.text((984, 1420), "主办 Organizer", font=V.f(V.F_YHBD, 20), fill=V.GREY_D, anchor="ra")
    d.text((984, 1452), V.HOST, font=V.f(V.F_YH, 22), fill=V.GREY_D, anchor="ra")
    qr = V.make_qr(V.CTA_URL); V.paste_qr(canvas, qr, (60, 1400), 64)
    d.text((140, 1404), V.CTA, font=V.f(V.F_YHBD, 24), fill=pal["ZHUSHA"])
    d.text((140, 1442), V.CTA_SUB, font=V.f(V.F_YH, 16), fill=V.GREY_D)
    return canvas


def build_B_seal():
    """v1 B 版：白底留白 + 居中印章式（近似重建）"""
    src = V.load_filled(V.SRC_RUYAO, crop_ratio=0.90)
    img = render_size_halftone(src, cell=7, contrast=1.35, ink_gamma=0.85, rim=True)
    img = ImageOps.invert(img).convert("L")
    px = img.load()
    for y in range(V.H):
        for x in range(V.W):
            v = px[x, y] / 255.0
            px[x, y] = int((v ** 1.7) * 255)
    img = img.convert("RGB")
    V._whiten(img)
    V.global_pad_light(img, alpha=205)
    d = ImageDraw.Draw(img)
    TQ = V1["TIANYUAN"]   # 天青
    INK = (43, 43, 43)
    d.text((984, 40), "时间 Time", font=V.f(V.F_YHBD, 22), fill=(98, 106, 110), anchor="ra")
    d.text((984, 74), V.PERIOD, font=V.f(V.F_AA, 54), fill=TQ, anchor="ra")
    d.text((984, 148), V.HOURS, font=V.f(V.F_YH, 26), fill=(98, 106, 110), anchor="ra")
    # 标题两行居中 168px 墨黑
    d.text((512, 430), "如果宋朝", font=V.f(V.F_ZIYU, 168), fill=INK, anchor="ma")
    d.text((512, 660), "有朋友圈", font=V.f(V.F_ZIYU, 168), fill=INK, anchor="ma")
    # 朱砂方印章「宋」
    seal = 130
    x0, y0 = 512 - seal // 2, 880
    d.rectangle([x0, y0, x0 + seal, y0 + seal], fill=V1["ZHUSHA"])
    d.text((512, y0 + seal // 2 + 4), "宋", font=V.f(V.F_ZIYU, 92), fill=(255, 255, 255), anchor="mm")
    # 传播语 + 英文 居中
    d.text((512, 1100), V.SLOGAN, font=V.f(V.F_YHBD, 40), fill=INK, anchor="ma")
    V.tracked(d, (512 - 180, 1160), V.EN, V.f(V.F_DENGB, 16), (98, 106, 110), 0.08)
    # 地点/主办 底部居中
    d.text((512, 1320), V.VENUE, font=V.f(V.F_YHBD, 28), fill=TQ, anchor="ma")
    d.text((512, 1372), "主办  " + V.HOST, font=V.f(V.F_YH, 22), fill=(98, 106, 110), anchor="ma")
    qr = V.make_qr(V.CTA_URL); V.paste_qr(img, qr, (480, 1416), 64)
    d.text((512, 1490), V.CTA, font=V.f(V.F_YHBD, 24), fill=V1["ZHUSHA"], anchor="ma")
    return img


def main():
    # plan1/2/3（含「宋代美学特展」文案版，复用原始函数）
    for name, fn in [("plan1_黑底天青", P.draw_plan1), ("plan2_白底汝窑", P.draw_plan2),
                     ("plan3_白底灰点阵", P.draw_plan3)]:
        save_no_overwrite(fn(P.render_plan1() if "plan1" in name else
                             P.render_plan2() if "plan2" in name else P.render_plan3()),
                          os.path.join(HIST, f"song_{name}_含宋代美学特展.png"))

    # variants v1
    save_no_overwrite(build_A(V1, POS_UP), os.path.join(HIST, "song_v1_A_黑底满版天青.png"))
    save_no_overwrite(build_B_seal(),      os.path.join(HIST, "song_v1_B_白底留白朱砂印章.png"))
    save_no_overwrite(build_C(V1),         os.path.join(HIST, "song_v1_C_左置露白青绿山水.png"))
    # variants v2（低饱和，标题未下移）
    save_no_overwrite(build_A(V2, POS_UP), os.path.join(HIST, "song_v2_A_黑底点茶低饱和.png"))
    save_no_overwrite(build_B(V2, POS_UP), os.path.join(HIST, "song_v2_B_白底汝窑灰点阵低饱和.png"))
    save_no_overwrite(build_C(V2),         os.path.join(HIST, "song_v2_C_左置挂画低饱和.png"))
    # variants v3（高饱和，标题下移）
    save_no_overwrite(build_A(V3, POS_DOWN), os.path.join(HIST, "song_v3_A_黑底点茶高饱和.png"))
    save_no_overwrite(build_B(V3, POS_DOWN), os.path.join(HIST, "song_v3_B_白底汝窑灰点阵高饱和.png"))
    save_no_overwrite(build_C(V3),           os.path.join(HIST, "song_v3_C_左置挂画高饱和.png"))
    print("all done ->", HIST)


if __name__ == "__main__":
    main()
