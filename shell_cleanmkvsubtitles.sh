#!/bin/bash

# 检查 ffmpeg 是否可用
if ! command -v ffmpeg &> /dev/null; then
  echo "ffmpeg not found. Please install ffmpeg and try again."
  exit 1
fi

# 获取目标目录（默认为当前目录）
DIR="${1:-.}"

# 检查目标目录是否存在
if [[ ! -d "$DIR" ]]; then
  echo "Error: Directory $DIR does not exist."
  exit 1
fi

# 创建输出目录
OUTPUT_DIR="$DIR/output"
mkdir -p "$OUTPUT_DIR"

# 遍历指定目录中的 .mkv 文件
for video in "$DIR"/*.mkv; do
  # 检查文件是否存在
  [ -e "$video" ] || continue

  # 获取文件名，不带目录路径
  base_name=$(basename "$video")

  echo "Removing subtitles from: $video"

  # 删除字幕流并保存到 output 目录
  output_file="$OUTPUT_DIR/$base_name"
  if ffmpeg -i "$video" -map 0 -map -0:s -c copy "$output_file"; then
    echo "Processed: $video -> $output_file"
  else
    echo "Failed to remove subtitles from $video"
  fi
done

echo "All processing completed. Files saved in $OUTPUT_DIR."