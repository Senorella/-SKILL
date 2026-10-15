# -*- coding: utf-8 -*-
"""utils.py — 海报脚本通用工具：图片防覆盖保存

硬规则：生成的所有图片一律不允许覆盖同名文件。
所有海报脚本的 img.save() 一律改用 save_no_overwrite()。
"""
import os


def save_no_overwrite(img, path, fmt="PNG"):
    """保存图片，绝不覆盖已存在的同名文件。

    若 path 已存在，自动追加 _v2/_v3/... 后缀，直到找到不冲突的名字。
    返回实际保存的路径（供后续引用/对比）。
    """
    if not os.path.exists(path):
        img.save(path, fmt)
        print(f"[save] {path}")
        return path
    base, ext = os.path.splitext(path)
    i = 2
    while True:
        cand = f"{base}_v{i}{ext}"
        if not os.path.exists(cand):
            img.save(cand, fmt)
            print(f"[save_no_overwrite] 同名已存在，另存为: {cand}")
            return cand
        i += 1
