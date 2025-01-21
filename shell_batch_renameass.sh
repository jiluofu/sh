#!/bin/bash

# 检查是否提供目录参数
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <directory>"
  exit 1
fi

DIR="$1"

# 检查目标目录是否存在
if [[ ! -d "$DIR" ]]; then
  echo "Error: Directory $DIR does not exist."
  exit 1
fi

# 遍历目录下的字幕文件（ass 和 srt）
find "$DIR" -maxdepth 1 -type f \( -name "*.ass" -o -name "*.srt" \) | while IFS= read -r subtitle_file; do
  # 提取字幕文件的前缀 Friends.SxxExx
  SUBTITLE_BASENAME=$(basename "$subtitle_file")
  SUBTITLE_PREFIX=$(echo "$SUBTITLE_BASENAME" | grep -oE "Friends\.S[0-9]{2}E[0-9]{2}")

  # 查找对应的 MKV 文件
  MKV_FILE=$(find "$DIR" -maxdepth 1 -type f -name "${SUBTITLE_PREFIX}*.mkv")

  if [[ -n "$MKV_FILE" ]]; then
    # 构造新的 MKV 文件名
    NEW_MKV_FILE="${subtitle_file%.*}.mkv"

    echo "Matching subtitle: $SUBTITLE_BASENAME"
    echo "Renaming MKV: $(basename "$MKV_FILE") -> $(basename "$NEW_MKV_FILE")"

    # 重命名 MKV 文件（处理特殊字符）
    mv -- "$MKV_FILE" "$NEW_MKV_FILE"
    if [[ $? -eq 0 ]]; then
      echo "Renamed successfully"
    else
      echo "Failed to rename: $MKV_FILE"
    fi
  else
    echo "No matching MKV found for subtitle: $subtitle_file"
  fi
done

echo "All files processed."