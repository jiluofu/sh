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
OUTPUT_DIR="$DIR/outputUlu"
mkdir -p "$OUTPUT_DIR"

# 遍历指定目录中的 .mkv 文件
for video in "$DIR"/*.mkv; do
  # 检查文件是否存在
  [ -e "$video" ] || continue

  # 获取文件名，不带扩展名
  base_name=$(basename "$video" .mkv)

  # 检查对应的 .ass 字幕文件是否存在
  subtitle="$DIR/${base_name}.ass"
  if [[ ! -f "$subtitle" ]]; then
    echo "No .ass subtitle file found for $video"
    continue
  fi

  echo "Adding soft subtitles to: $video using $subtitle"

  # 添加软字幕到视频中
  output_file="$OUTPUT_DIR/${base_name}.mkv"
  if ffmpeg -i "$video" -i "$subtitle" -map 0 -map 1 -c copy -c:s ass -metadata:s:s:0 language=eng "$output_file"; then
    echo "Processed: $video -> $output_file"
  else
    echo "Failed to add subtitles to $video"
  fi
done

echo "All processing completed. Files saved in $OUTPUT_DIR."