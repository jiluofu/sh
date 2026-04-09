#!/bin/bash

# === 参数处理 ===
INPUT_DIR="${1:-.}"

# 转成绝对路径
INPUT_DIR="$(cd "$INPUT_DIR" && pwd)"

# 输出目录
OUTPUT_DIR="$INPUT_DIR/crop"

mkdir -p "$OUTPUT_DIR"

echo "📂 输入目录: $INPUT_DIR"
echo "📁 输出目录: $OUTPUT_DIR"
echo "----------------------------------"

# === 遍历 PDF 文件（递归）===
find "$INPUT_DIR" -maxdepth 1 -type f -iname "*.pdf" | sort | while read -r file; do

    # 跳过 crop 目录本身（防止死循环）
    if [[ "$file" == "$OUTPUT_DIR"* ]]; then
        continue
    fi

    filename=$(basename "$file")
    output_file="$OUTPUT_DIR/$filename"

    echo "➡️ 处理: $file"
    
    pdf-crop-margins "$file" \
        -o "$output_file" \
        -u -p 10

    if [[ $? -eq 0 ]]; then
        echo "✅ 完成: $output_file"
    else
        echo "❌ 失败: $file"
    fi

    echo "----------------------------------"

done

echo "🎉 全部处理完成"