#!/usr/bin/env python3
"""
init_workspace.py - 把 skill 字体复制到目标 workspace
用法：python init_workspace.py <workspace_path>

效果：
- 在 <workspace>/fonts/ 下创建字体三件套
- 在 <workspace>/ 准备空的 make_posters.py（带 schedule + 框架）
"""
import sys
import os
import shutil
from pathlib import Path

SKILL_FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
FONT_FILES = [
    "ZiYuQuWeiXiangSu.ttf",
    "AaXiaoGouGuaiGuaiXiangSuTi.ttf",
    "fonts.css",
]


def main():
    if len(sys.argv) < 2:
        print("用法: python init_workspace.py <workspace_path>")
        print("示例: python init_workspace.py C:/path/to/my-workspace")
        sys.exit(1)

    workspace = Path(sys.argv[1]).resolve()
    if not workspace.exists():
        print(f"❌ Workspace 不存在: {workspace}")
        sys.exit(1)

    fonts_dir = workspace / "fonts"
    fonts_dir.mkdir(exist_ok=True)
    for name in FONT_FILES:
        src = SKILL_FONTS_DIR / name
        if not src.exists():
            print(f"⚠️  跳过缺失字体: {name}")
            continue
        dst = fonts_dir / name
        shutil.copy2(src, dst)
        print(f"✅ {name} → {dst}")

    print(f"\n🎉 字体已就绪于: {fonts_dir}")
    print(f"   下一步：把 skill scripts/make_posters.py 复制到 {workspace}，编辑 EXHIBITIONS/TASKS")


if __name__ == "__main__":
    main()