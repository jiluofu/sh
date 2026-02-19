#!/bin/bash

# 检查输入参数
if [ -z "$1" ]; then
  echo "❌ 请提供 HEIC 图片所在目录路径"
  echo "用法: $0 /路径/到/图片目录"
  exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="$INPUT_DIR/output"
mkdir -p "$OUTPUT_DIR"

# 遍历 HEIC 文件
for file in "$INPUT_DIR"/*.HEIC "$INPUT_DIR"/*.heic; do
  [ -e "$file" ] || continue

  base=$(basename "$file")
  name="${base%.*}"

  # 获取宽高
  width=$(sips -g pixelWidth "$file" | awk '/pixelWidth/ {print $2}')
  height=$(sips -g pixelHeight "$file" | awk '/pixelHeight/ {print $2}')

  # 计算新最长边的一半
  if [ "$width" -ge "$height" ]; then
    max_new=$((width / 2))
  else
    max_new=$((height / 2))
  fi

  echo "📉 压缩 $file → 最长边=$max_new px → 保存为 HEIC"

  # 缩放并保存为新的 HEIC（先转中间文件，再转回 HEIC）
  tmp_png="$OUTPUT_DIR/${name}_tmp.png"
  out_heic="$OUTPUT_DIR/${name}.heic"

  sips -Z "$max_new" "$file" --out "$tmp_png"

  # 再转回 heic（macOS 仅限支持的系统）
  if sips -s format heic "$tmp_png" --out "$out_heic" &>/dev/null; then
    echo "✅ 完成: $out_heic"
    rm -f "$tmp_png"
  else
    echo "⚠️ 无法保存 HEIC，仅保留压缩 PNG：$tmp_png"
  fi
done

echo "🎉 所有 HEIC 图片已压缩保存至：$OUTPUT_DIR"