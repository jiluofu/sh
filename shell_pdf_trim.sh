#!/bin/bash

# ==============================
# 用法检查
# ==============================
if [ -z "$1" ]; then
  echo "❌ 请提供包含 PDF 的目录路径"
  echo "用法: $0 /路径/到/pdf目录"
  exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="$INPUT_DIR/output"

# ==============================
# 检查目录是否存在
# ==============================
if [ ! -d "$INPUT_DIR" ]; then
  echo "❌ 目录不存在: $INPUT_DIR"
  exit 1
fi

# ==============================
# 创建输出目录
# ==============================
mkdir -p "$OUTPUT_DIR"

echo "📂 输入目录: $INPUT_DIR"
echo "📁 输出目录: $OUTPUT_DIR"
echo "🚀 开始处理 PDF..."

# ==============================
# 遍历 PDF 文件
# ==============================
for pdf in "$INPUT_DIR"/*.pdf; do
  # 没有匹配时跳过
  [ -e "$pdf" ] || continue

  filename=$(basename "$pdf")
  output_pdf="$OUTPUT_DIR/$filename"

  echo "➡️ 处理: $filename"

  pdfjam "$pdf" \
    --paper a4paper \
    --scale 1.1 \
    --trim '30mm 5mm 30mm 10mm' \
    --clip true \
    --outfile "$output_pdf"

  if [ $? -eq 0 ]; then
    echo "   ✅ 输出: output/$filename"
  else
    echo "   ❌ 失败: $filename"
  fi
done

echo "🎉 全部处理完成"