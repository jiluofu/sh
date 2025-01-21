#!/bin/bash

# 检查是否提供目录参数
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <directory>"
  exit 1
fi

DIR="$1"
OUTPUT_DIR="$DIR/output"

# 检查目标目录是否存在
if [[ ! -d "$DIR" ]]; then
  echo "Error: Directory $DIR does not exist."
  exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 遍历目录下的 .mkv 文件
find "$DIR" -maxdepth 1 -type f -name "*.mkv" | while IFS= read -r mkv_file; do
  # 获取 MKV 文件名（不带扩展名）
  BASENAME=$(basename "$mkv_file" .mkv)
  SAFE_BASENAME=$(echo "$BASENAME" | sed 's/[^a-zA-Z0-9._-]/_/g')
  OUTPUT_FILE="$OUTPUT_DIR/${SAFE_BASENAME}.mkv"

  echo "Processing MKV: $mkv_file"

  # 删除所有字幕并保存到 output 目录
  mkvmerge -o "$OUTPUT_FILE" -S "$mkv_file"
  if [[ $? -ne 0 ]]; then
    echo "  Failed to remove subtitles from $mkv_file"
    continue
  fi

  echo "  Subtitles removed: $OUTPUT_FILE"

  # 查找与 MKV 文件前缀（Friends.SxxExx）匹配的 .ass 文件
  MKV_PREFIX=$(echo "$BASENAME" | grep -oE "Friends\.S[0-9]{2}E[0-9]{2}")
  ASS_FILE=$(find "$DIR" -maxdepth 1 -type f -name "${MKV_PREFIX}*.chs&eng.ass")

  if [[ -n "$ASS_FILE" ]]; then
    echo "  Found matching subtitle: $ASS_FILE"

    # 重命名字幕为与 MKV 文件同名，并保存到 output 目录
    NEW_ASS_FILE="$OUTPUT_DIR/${SAFE_BASENAME}.ass"
    cp "$ASS_FILE" "$NEW_ASS_FILE"

    # 将字幕添加到处理后的 MKV 文件中
    mkvmerge -o "${OUTPUT_FILE}_temp.mkv" "$OUTPUT_FILE" --language 0:eng "$NEW_ASS_FILE"
    if [[ $? -eq 0 ]]; then
      mv "${OUTPUT_FILE}_temp.mkv" "$OUTPUT_FILE"
      echo "  Subtitle added successfully"
    else
      echo "  Failed to add subtitle: $NEW_ASS_FILE"
      rm -f "${OUTPUT_FILE}_temp.mkv"
    fi
  else
    echo "  No matching subtitle found for: $mkv_file"
  fi
done

echo "All files processed. Output saved to $OUTPUT_DIR"