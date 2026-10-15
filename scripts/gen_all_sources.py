# -*- coding: utf-8 -*-
"""
gen_all_sources.py — 用多个底图素材，按 SKILL v4.13 三套方案分别生成海报，
输出到独立子目录，便于对比选择。
"""
import os, subprocess, sys, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
GI = os.path.join(ROOT, "generated-images")
BASE_OUT = os.path.join(ROOT, "output", "dunhuang_typographic_halftone")
PY = "D:/python311/python.exe"

# 素材：主题 -> 源文件名
SOURCES = {
    "九色鹿":   "敦煌莫高窟九色鹿本生故事壁画中的九色鹿形象_黑白灰单色_纯黑_2026-10-09T19-16-05.png",
    "反弹琵琶": "敦煌莫高窟壁画中的反弹琵琶舞伎_飞天乐舞姿态_黑白灰单色_纯_2026-10-09T19-16-05.png",
    "藻井纹样": "敦煌莫高窟藻井顶部的华丽纹样_莲花纹与卷草纹交织_黑白灰单色_2026-10-09T19-16-03.png",
    "菩萨像":   "敦煌莫高窟彩塑菩萨像_慈悲安详的面容与宝冠璎珞_黑白灰单色__2026-10-09T19-16-07.png",
}

# 三套方案：脚本 -> 产出子目录
PLANS = {
    "plan1_黑底石绿": ("make_poster_typographic.py", "dunhuang_typo_A_飞天主体.png"),
    "plan2_白底单色": ("make_poster_final_two.py", None),   # 多张
    "plan3_白底彩字": ("make_poster_light_variants.py", None),  # 多张
}

def run(script, src, out_dir):
    """运行脚本并把该脚本产出目录下所有 png 复制到素材专属目录。"""
    scrip_out_map = {
        "make_poster_typographic.py": os.path.join(BASE_OUT),
        "make_poster_final_two.py": os.path.join(BASE_OUT, "final_two"),
        "make_poster_light_variants.py": os.path.join(BASE_OUT, "light_variants"),
    }
    od = scrip_out_map[script]
    r = subprocess.run([PY, os.path.join(ROOT, script), src], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print("  [ERR]", r.stderr.strip()[:500]); return
    os.makedirs(out_dir, exist_ok=True)
    # 复制该脚本产出的所有 png（不含 _compare_sheet/_ 前缀对比图）
    for f in os.listdir(od):
        if f.endswith(".png") and not f.startswith("_"):
            shutil.copy2(os.path.join(od, f), os.path.join(out_dir, f))

def main():
    for theme, src in SOURCES.items():
        print("=" * 60)
        print(f"[素材] {theme}  <-  {src}")
        src_path = os.path.join(GI, src)
        if not os.path.exists(src_path):
            print("  缺失，跳过"); continue
        # 方案一：黑底石绿
        out1 = os.path.join(BASE_OUT, f"src_{theme}", "plan1")
        run("make_poster_typographic.py", src, out1)
        # 方案二：白底单色
        out2 = os.path.join(BASE_OUT, f"src_{theme}", "plan2")
        run("make_poster_final_two.py", src, out2)
        # 方案三：白底彩字
        out3 = os.path.join(BASE_OUT, f"src_{theme}", "plan3")
        run("make_poster_light_variants.py", src, out3)
    print("ALL DONE")

if __name__ == "__main__":
    main()
