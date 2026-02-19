import fitz
import sys
from PIL import Image
import io

def recompress_pdf(input_pdf, output_pdf, quality):
    doc = fitz.open(input_pdf)
    new_doc = fitz.open()

    total_pages = len(doc)
    print(f"📄 共 {total_pages} 页")

    for i, page in enumerate(doc):
        print(f"▶️ 渲染第 {i+1}/{total_pages} 页…")

        # 渲染整页为 RGB 位图（不会变黑的关键！）
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)  
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # JPEG 压缩
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        img_bytes = buf.getvalue()

        # 插入到新 PDF
        # 页面大小使用原始 page 的尺寸
        rect = page.rect
        new_page = new_doc.new_page(width=rect.width, height=rect.height)
        new_page.insert_image(rect, stream=img_bytes)

    new_doc.save(output_pdf)
    print(f"\n🎉 压缩完成：{output_pdf}")
    new_doc.close()
    doc.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法: python py_pdf_recompress.py input.pdf output.pdf 50")
        sys.exit(1)

    recompress_pdf(sys.argv[1], sys.argv[2], int(sys.argv[3]))