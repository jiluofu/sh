import os
from PIL import Image
import fitz  # PyMuPDF

# === 配置项 ===
IMAGE_FOLDER = "./"             # 图片目录
OUTPUT_PDF = "output.pdf"       # 输出 PDF 文件名
TOP_SPACING = 30                # 每张图上方空隙
BOTTOM_SPACING = 300             # 每张图下方空隙
A4_WIDTH_PX = 1240              # A4 尺寸宽度（150dpi）
A4_HEIGHT_PX = 1754             # A4 尺寸高度（150dpi）

# === 获取所有图片路径 ===
image_files = sorted([
    os.path.join(IMAGE_FOLDER, f)
    for f in os.listdir(IMAGE_FOLDER)
    if f.lower().endswith(('.jpg', '.jpeg', '.png'))
])

# === 初始化 PDF 文档 ===
doc = fitz.open()
page = None
current_y = 0
temp_files = []

for idx, img_path in enumerate(image_files):
    img = Image.open(img_path).convert("RGB")

    # === 缩放图像到 A4 宽度 ===
    w_percent = A4_WIDTH_PX / img.width
    new_height = int(img.height * w_percent)
    img = img.resize((A4_WIDTH_PX, new_height), Image.LANCZOS)

    # === 判断是否需要新页 ===
    block_height = TOP_SPACING + new_height + BOTTOM_SPACING
    if page is None or (current_y + block_height > A4_HEIGHT_PX):
        page = doc.new_page(width=A4_WIDTH_PX, height=A4_HEIGHT_PX)
        current_y = 0

    # === 保存临时 JPG 压缩图 ===
    temp_path = f"temp_image_{idx}.jpg"
    img.save(temp_path, format='JPEG', quality=85, optimize=True)
    temp_files.append(temp_path)

    # === 插入图片到 PDF 当前页 ===
    top = current_y + TOP_SPACING
    bottom = top + new_height
    rect = fitz.Rect(0, top, A4_WIDTH_PX, bottom)
    page.insert_image(rect, filename=temp_path)

    # === 更新当前插入位置 ===
    current_y += block_height

# === 保存 PDF ===
doc.save(OUTPUT_PDF)
doc.close()
print(f"✅ PDF 已生成：{OUTPUT_PDF}")

# === 清理临时文件 ===
for f in temp_files:
    try:
        os.remove(f)
    except Exception as e:
        print(f"⚠️ 无法删除临时文件 {f}：{e}")
