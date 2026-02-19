import os
import sys
from PIL import Image
import pillow_heif  # pip install pillow-heif
from pathlib import Path

# === 设置输入参数 ===
if len(sys.argv) < 2:
    print("❌ 请提供 HEIC 图片所在目录路径")
    print("用法: python compress_heic_to_jpg.py /路径/到/图片目录")
    sys.exit(1)

INPUT_DIR = Path(sys.argv[1])
OUTPUT_DIR = INPUT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 注册 HEIC 支持
pillow_heif.register_heif_opener()

# === 遍历所有 HEIC 文件 ===
for file in INPUT_DIR.glob("*.heic"):
    try:
        with Image.open(file) as img:
            width, height = img.size
            print(f"📸 原始图像: {file.name} ({width}x{height})")

            # 计算压缩后尺寸（最长边减半）
            if width >= height:
                new_width = width // 2
                new_height = int(height * (new_width / width))
            else:
                new_height = height // 2
                new_width = int(width * (new_height / height))

            img_resized = img.resize((new_width, new_height), Image.LANCZOS)

            # 转为 RGB（JPG 不支持透明通道）
            if img_resized.mode != "RGB":
                img_resized = img_resized.convert("RGB")

            # 保存为 JPG 格式
            output_file = OUTPUT_DIR / f"{file.stem}.jpg"
            img_resized.save(output_file, format="JPEG", quality=85)
            print(f"✅ 压缩并保存为 JPG: {output_file.name} ({new_width}x{new_height})")

    except Exception as e:
        print(f"❌ 无法处理 {file.name}：{e}")

print(f"\n🎉 所有 HEIC 图片已压缩为 JPG 并保存至：{OUTPUT_DIR}")