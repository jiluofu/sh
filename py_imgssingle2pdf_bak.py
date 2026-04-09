import os
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF

# === 配置项 ===
IMAGE_FOLDER = "./"                    # 图片目录
OUTPUT_PDF = "output.pdf"              # 输出 PDF 文件名
TOP_SPACING = 30                       # 页面顶端留白
BOTTOM_SPACING = 300                   # 页面底部留白
TEXT_AREA_HEIGHT = 50                  # 文件名区域高度
A4_WIDTH_PX = 1240                     # A4 宽（150dpi）
A4_HEIGHT_PX = 1754                    # A4 高（150dpi）
FONT_SIZE = 24                         # 字体大小
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"  # macOS 中文字体
EACH_IMAGE_ONE_PAGE = True             # 每张图一页
SHOW_FILENAME = True                   # 是否显示文件名

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

    # === 合集图片逻辑：横图旋转成竖图 + 保持比例尽量铺满 + 顶部对齐 ===
    if "合集" in filename:
        # 横图旋转成竖图
        if img.width > img.height:
            img = img.rotate(90, expand=True)

        page = doc.new_page(width=A4_WIDTH_PX, height=A4_HEIGHT_PX)

        # 可用区域
        max_width = A4_WIDTH_PX
        max_height = A4_HEIGHT_PX - TOP_SPACING - BOTTOM_SPACING

        # fit模式：不裁剪，尽量铺满
        scale = min(max_width / img.width, max_height / img.height)
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)

        # 顶部对齐，水平居中
        x0 = (A4_WIDTH_PX - new_width) / 2
        y0 = TOP_SPACING
        x1 = x0 + new_width
        y1 = y0 + new_height

        rect = fitz.Rect(x0, y0, x1, y1)

        # 合集图片先保存成临时 JPG 再插入
        temp_path = f"temp_image_{idx}.jpg"
        img.save(temp_path, format='JPEG', quality=85, optimize=True)
        temp_files.append(temp_path)

        page.insert_image(rect, filename=temp_path)
        continue

    # === 普通图片逻辑：保持原样 ===
    w_percent = A4_WIDTH_PX / img.width
    new_height = int(img.height * w_percent)
    img = img.resize((A4_WIDTH_PX, new_height), Image.LANCZOS)

    # === 创建新图像，加上文字区域 ===
    total_height = TEXT_AREA_HEIGHT + new_height
    new_img = Image.new("RGB", (A4_WIDTH_PX, total_height), color=(255, 255, 255))

    # === 加文字 ===
    if SHOW_FILENAME:
        draw = ImageDraw.Draw(new_img)
        try:
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        except:
            font = ImageFont.load_default()
        draw.text((10, 10), filename, font=font, fill=(0, 0, 0))

    # === 拼接图片 ===
    new_img.paste(img, (0, TEXT_AREA_HEIGHT))

    # === 保存临时 JPG ===
    temp_path = f"temp_image_{idx}.jpg"
    new_img.save(temp_path, format='JPEG', quality=85, optimize=True)
    temp_files.append(temp_path)

    # === 插入 PDF 页面 ===
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

# === 删除临时文件 ===
for f in temp_files:
    try:
        os.remove(f)
    except Exception as e:
        print(f"⚠️ 无法删除临时文件 {f}：{e}")