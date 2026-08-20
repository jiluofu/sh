#!/bin/bash

# 用法：
# ./boost_m4a_volume.sh "/路径/到/音频目录" 1.5
#
# 例如：
# ./boost_m4a_volume.sh "/Users/zhuxu/Downloads/课文音频" 1.5

set -u
shopt -s nullglob

INPUT_DIR="${1:-.}"
VOLUME="${2:-1.5}"
OUTPUT_DIR="${INPUT_DIR%/}/louder"

if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "未找到 ffmpeg，请先安装：brew install ffmpeg"
    exit 1
fi

if [[ ! -d "$INPUT_DIR" ]]; then
    echo "目录不存在：$INPUT_DIR"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

count=0

for file in "$INPUT_DIR"/*.m4a "$INPUT_DIR"/*.M4A; do
    [[ -f "$file" ]] || continue

    filename="$(basename "$file")"
    stem="${filename%.*}"
    output="$OUTPUT_DIR/${stem}.m4a"

    echo "----------------------------------------"
    echo "输入：$file"
    echo "输出：$output"

    ffmpeg -y \
        -i "$file" \
        -map '0:a:0?' \
        -vn \
        -af "volume=${VOLUME}" \
        -c:a aac \
        -b:a 192k \
        "$output"

    ((count++))
done

echo "----------------------------------------"
echo "完成：共处理 $count 个文件"
echo "输出目录：$OUTPUT_DIR"