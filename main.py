#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
幻影坦克图片生成工具

用法：
  交互模式：python mirage_tank.py
  命令行：python mirage_tank.py white.png black.png output.png
"""

import sys
import os
import argparse
from PIL import Image
import numpy as np


def load_image(path, size=None):
    """加载图片并转为 RGB，可选缩放到指定尺寸"""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"文件不存在: {path}")
    img = Image.open(path).convert("RGB")
    if size is not None and img.size != size:
        img = img.resize(size, Image.LANCZOS)
    return img


def generate_mirage(white_path, black_path, output_path):
    """
    生成幻影坦克图片。
    white_path: 白色背景下希望显示的图片
    black_path: 黑色背景下希望显示的图片
    output_path: 输出 PNG 路径
    """
    # 以白底图尺寸为准
    white_img = load_image(white_path)
    w, h = white_img.size
    black_img = load_image(black_path, size=(w, h))

    # 转为 numpy 数组，float32 方便计算
    W = np.asarray(white_img, dtype=np.float32)   # 目标：白底显示
    B = np.asarray(black_img, dtype=np.float32)   # 目标：黑底显示

    # 理论公式：
    # 白底显示：W = alpha * C + (1 - alpha) * 255
    # 黑底显示：B = alpha * C
    # 所以：W - B = (1 - alpha) * 255
    # => alpha = 1 - (W - B) / 255 = (B - W + 255) / 255
    alpha_c = (B - W + 255.0) / 255.0          # 形状 (h, w, 3)
    alpha = alpha_c.mean(axis=2)               # 三通道取平均，得到统一 alpha
    alpha = np.clip(alpha, 0.01, 1.0)          # 限制范围，避免除零和异常值

    # 计算前景色 C = B / alpha
    C = B / alpha[..., np.newaxis]
    C = np.clip(C, 0, 255)

    # 合成 RGBA
    alpha_255 = (alpha * 255.0).astype(np.uint8)
    rgba = np.dstack([C.astype(np.uint8), alpha_255])

    out_img = Image.fromarray(rgba, mode="RGBA")
    out_img.save(output_path, "PNG")

    print(f"已生成幻影坦克图片: {output_path}")
    print("提示：在聊天软件中请勾选“发送原图”，否则透明通道可能被压缩破坏。")


def main():
    if len(sys.argv) == 1:
        # 无参数，进入交互模式
        print("=== 幻影坦克图片生成工具（交互模式）===")
        white_path = input("请输入【白色背景】下显示的图片路径: ").strip().strip('"\'')
        black_path = input("请输入【黑色背景】下显示的图片路径: ").strip().strip('"\'')
        output_path = input("请输入输出 PNG 路径（默认 mirage_tank.png）: ").strip().strip('"\'')
        if not output_path:
            output_path = "mirage_tank.png"
    else:
        # 有参数，使用 argparse 位置参数
        parser = argparse.ArgumentParser(
            description="生成幻影坦克图片：白底显示一张图，黑底显示另一张图。"
        )
        parser.add_argument("white", help="白色背景显示的图片路径")
        parser.add_argument("black", help="黑色背景显示的图片路径")
        parser.add_argument(
            "output", nargs="?", default="mirage_tank.png",
            help="输出 PNG 路径（默认 mirage_tank.png）"
        )
        args = parser.parse_args()
        white_path = args.white
        black_path = args.black
        output_path = args.output

    try:
        generate_mirage(white_path, black_path, output_path)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()