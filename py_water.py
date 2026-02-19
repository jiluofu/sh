# from PIL import Image, ImageDraw, ImageFont
# import math

# # === 配置 ===
# image_path = "/Users/zhuxu/Downloads/tt/2025-01-29 11-03-36___DSC0336.jpg"  # 替换为你的图片路径
# output_path = "/Users/zhuxu/Downloads/tt/2025-01-29 11-03-36___DSC0336_watermarked.jpg"
# watermark_text = "© 朱醒之"  # 替换为你的品牌名或网站
# font_path = "/System/Library/Fonts/STHeiti Medium.ttc"  # 或你安装的中文字体路径
# angle = -30  # 水印倾斜角度

# # === 加载原图 ===
# original = Image.open(image_path).convert("RGBA")
# width, height = original.size
# font_size = int(min(width, height) / 12.0)

# # === 创建大图层（旋转后需要更大画布） ===
# diag = int(math.hypot(width, height))  # 对角线长度，保证旋转不截断
# layer = Image.new("RGBA", (diag, diag), (255, 255, 255, 0))
# draw = ImageDraw.Draw(layer)


# # === 加载字体 ===
# font = ImageFont.truetype(font_path, font_size, index=0)

# # 获取文字尺寸（用于计算间距）
# bbox = draw.textbbox((0, 0), watermark_text, font=font)
# text_width = bbox[2] - bbox[0]
# text_height = bbox[3] - bbox[1]

# # 避免重叠的间距设置
# x_spacing = int(text_width * 1.5)
# y_spacing = int(text_height * 3)

# # === 平铺水印文字 ===
# for y in range(0, diag, y_spacing):
#     for x in range(0, diag, x_spacing):
#         draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 60))

# # === 旋转文字图层 ===
# rotated = layer.rotate(angle, expand=True)

# # === 裁剪回原图大小 ===
# cx, cy = rotated.size[0] // 2, rotated.size[1] // 2
# left = cx - width // 2
# top = cy - height // 2
# cropped = rotated.crop((left, top, left + width, top + height))

# # === 合成水印到原图 ===
# combined = Image.alpha_composite(original, cropped)
# combined.convert("RGB").save(output_path)

# print("✅ 水印已添加：", output_path)


from PIL import Image, ImageDraw, ImageFont
import os
import math

# === 配置 ===
watermark_text = "© 朱醒之"
font_path = "/System/Library/Fonts/STHeiti Medium.ttc"
angle = -30
font_index = 0
font_scale = 12.0  # 字体大小 = 图像最小边 / 此数值
x_scale = 1.5  # X方向间距倍数
y_scale = 3.0  # Y方向间距倍数

# === 文件目录 ===
input_dir = "."  # 当前目录
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# === 处理所有 .jpg 文件 ===
for file_name in os.listdir(input_dir):
    if file_name.lower().endswith(".jpg"):
        image_path = os.path.join(input_dir, file_name)
        output_path = os.path.join(output_dir, file_name)

        # 加载图像
        original = Image.open(image_path).convert("RGBA")
        width, height = original.size
        font_size = int(min(width, height) / font_scale)

        # 计算旋转后所需画布大小
        diag = int(math.hypot(width, height))
        layer = Image.new("RGBA", (diag, diag), (255, 255, 255, 0))
        draw = ImageDraw.Draw(layer)

        # 加载字体
        font = ImageFont.truetype(font_path, font_size, index=font_index)

        # 计算文字尺寸
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # 设置间距
        x_spacing = int(text_width * x_scale)
        y_spacing = int(text_height * y_scale)

        # 绘制水印
        for y in range(0, diag, y_spacing):
            for x in range(0, diag, x_spacing):
                draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 60))

        # 旋转水印图层
        rotated = layer.rotate(angle, expand=True)

        # 裁剪到原图尺寸
        cx, cy = rotated.size[0] // 2, rotated.size[1] // 2
        left = cx - width // 2
        top = cy - height // 2
        cropped = rotated.crop((left, top, left + width, top + height))

        # 合成并保存
        result = Image.alpha_composite(original, cropped).convert("RGB")
        result.save(output_path)
        print(f"✅ 水印已添加到: {output_path}")