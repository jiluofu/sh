import os
import sys
import subprocess
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF

# === 参数解析 ===
CROP_ENABLED = True

if "--no-crop" in sys.argv:
    CROP_ENABLED = False

# === 使用说明 ===
print("""
================ 使用说明 ================
python script.py [选项]

可选参数：
--no-crop        关闭PDF裁剪（默认开启裁剪）

默认行为：
1. 生成 PDF（output.pdf）
2. 自动裁剪（覆盖原文件）：
   pdf-crop-margins output.pdf -o 临时文件 -u -p 10

========================================
""")

# === 配置项 ===
IMAGE_FOLDER = "./"
OUTPUT_PDF = "output.pdf"
TOP_SPACING = 30
BOTTOM_SPACING = 300
TEXT_AREA_HEIGHT = 50
A4_WIDTH_PX = 1240
A4_HEIGHT_PX = 1754
FONT_SIZE = 24
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
EACH_IMAGE_ONE_PAGE = True
SHOW_FILENAME = True

# === 获取图片路径 ===
image_files = sorted([
    os.path.join(IMAGE_FOLDER, f)
    for f in os.listdir(IMAGE_FOLDER)
    if f.lower().endswith(('.heic', '.jpg', '.jpeg', '.png'))
])

# === 初始化 PDF ===
doc = fitz.open()
page = None
temp_files = []

for idx, img_path in enumerate(image_files):
    img = Image.open(img_path).convert("RGB")
    basename = os.path.basename(img_path)
    filename = os.path.splitext(basename)[0]

    # === 合集图片逻辑：图片旋转成竖图 + 文件名竖排放左侧白边，不压图片 ===
    if "合集" in filename:
        # 横图旋转成竖图
        if img.width > img.height:
            img = img.rotate(90, expand=True)

        # 默认左侧预留宽度
        label_strip_width = 0
        gap_between_label_and_image = 12  # 文字和图片之间的间距

        # === 文件名 → 小图 → 旋转 ===
        if SHOW_FILENAME:
            try:
                font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
            except Exception:
                font = ImageFont.load_default()

            draw_probe = ImageDraw.Draw(img)
            bbox = draw_probe.textbbox((0, 0), filename, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]

            pad = 8

            # 创建横向文字图
            label_img = Image.new(
                "RGB",
                (text_w + pad * 2, text_h + pad * 2),
                color=(255, 255, 255)
            )
            label_draw = ImageDraw.Draw(label_img)
            label_draw.text((pad, pad), filename, font=font, fill=(0, 0, 0))

            # 旋转成竖排
            label_img = label_img.rotate(90, expand=True)

            # 左侧白边宽度 = 文字宽度 + 间距 + 10
            label_strip_width = label_img.width + gap_between_label_and_image + 10
        else:
            label_img = None

        # === 先创建“左侧白边 + 图片”的新图，避免文字压住图片 ===
        merged_width = label_strip_width + img.width
        merged_height = img.height
        merged_img = Image.new("RGB", (merged_width, merged_height), color=(255, 255, 255))

        # 图片贴到右侧
        merged_img.paste(img, (label_strip_width, 0))

        # 文字贴到左下角白边区域
        if SHOW_FILENAME and label_img is not None:
            label_x = 10
            label_y = merged_height - label_img.height - 10
            merged_img.paste(label_img, (label_x, label_y))

        # === 放入PDF ===
        page = doc.new_page(width=A4_WIDTH_PX, height=A4_HEIGHT_PX)

        max_width = A4_WIDTH_PX - 20
        max_height = A4_HEIGHT_PX - TOP_SPACING - BOTTOM_SPACING

        scale = min(max_width / merged_img.width, max_height / merged_img.height)
        new_width = int(merged_img.width * scale)
        new_height = int(merged_img.height * scale)

        merged_img = merged_img.resize((new_width, new_height), Image.LANCZOS)

        x0 = 20
        y0 = TOP_SPACING
        x1 = x0 + new_width
        y1 = y0 + new_height

        rect = fitz.Rect(x0, y0, x1, y1)

        temp_path = f"temp_image_{idx}.jpg"
        merged_img.save(temp_path, format='JPEG', quality=85, optimize=True)
        temp_files.append(temp_path)

        page.insert_image(rect, filename=temp_path)
        continue

    # === 普通图片逻辑 ===
    w_percent = A4_WIDTH_PX / img.width
    new_height = int(img.height * w_percent)
    img = img.resize((A4_WIDTH_PX, new_height), Image.LANCZOS)

    total_height = TEXT_AREA_HEIGHT + new_height
    new_img = Image.new("RGB", (A4_WIDTH_PX, total_height), color=(255, 255, 255))

    if SHOW_FILENAME:
        draw = ImageDraw.Draw(new_img)
        try:
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        except Exception:
            font = ImageFont.load_default()
        draw.text((10, 10), filename, font=font, fill=(0, 0, 0))

    new_img.paste(img, (0, TEXT_AREA_HEIGHT))

    temp_path = f"temp_image_{idx}.jpg"
    new_img.save(temp_path, format='JPEG', quality=85, optimize=True)
    temp_files.append(temp_path)

    if EACH_IMAGE_ONE_PAGE or page is None:
        page = doc.new_page(width=A4_WIDTH_PX, height=A4_HEIGHT_PX)

    top = TOP_SPACING
    bottom = top + total_height
    rect = fitz.Rect(0, top, A4_WIDTH_PX, bottom)
    page.insert_image(rect, filename=temp_path)

# === 保存 PDF ===
doc.save(OUTPUT_PDF)
doc.close()
print(f"✅ PDF 已生成：{OUTPUT_PDF}")

# === 删除临时图片 ===
for f in temp_files:
    try:
        os.remove(f)
    except Exception as e:
        print(f"⚠️ 无法删除临时文件 {f}：{e}")

# === 自动裁剪 ===
if CROP_ENABLED:
    print("✂️ 开始裁剪 PDF...")

    cropped_tmp = OUTPUT_PDF.replace(".pdf", "_cropped_tmp.pdf")

    cmd = [
        "pdf-crop-margins",
        OUTPUT_PDF,
        "-o", cropped_tmp,
        "-u",
        "-p", "10"
    ]

    print("执行命令：", " ".join(cmd))

    result = subprocess.run(cmd)

    if result.returncode == 0 and os.path.exists(cropped_tmp):
        os.replace(cropped_tmp, OUTPUT_PDF)
        print("✅ 裁剪完成（已替换原始 output.pdf）")
    else:
        print("❌ 裁剪失败")
        if os.path.exists(cropped_tmp):
            os.remove(cropped_tmp)
else:
    print("🚫 已关闭裁剪")