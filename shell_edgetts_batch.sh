#!/bin/bash

# =========================
# Word → TXT → MP3
# 用法：
# ./word2mp3.sh 目录
# =========================

if [ $# -ne 1 ]; then
    echo "用法: $0 目录"
    exit 1
fi

DIR="$1"

if [ ! -d "$DIR" ]; then
    echo "目录不存在: $DIR"
    exit 1
fi

# Edge-TTS 参数
VOICE="zh-CN-XiaoxiaoNeural"
RATE="+10%"
VOLUME="+30%"

# 遍历当前目录下的 Word 文件
find "$DIR" -maxdepth 1 -type f \( -iname "*.docx" -o -iname "*.doc" \) -print0 |
while IFS= read -r -d '' file; do

    # 文件名去掉扩展名
    base="${file%.*}"

    txt="${base}.txt"
    mp3="${base}.mp3"

    echo "========================================"
    echo "Word: $file"

    # -------------------------
    # 1. Word → UTF-8 TXT
    # -------------------------

    echo "转换 TXT: $txt"

    textutil \
        -convert txt \
        -encoding UTF-8 \
        -output "$txt" \
        "$file"

    if [ $? -ne 0 ]; then
        echo "❌ Word 转 TXT 失败: $file"
        continue
    fi

    # -------------------------
    # 2. TXT → MP3
    # -------------------------

    echo "生成 MP3: $mp3"

    edge-tts \
        --voice "$VOICE" \
        --rate="$RATE" \
        --volume="$VOLUME" \
        --file "$txt" \
        --write-media "$mp3"

    if [ $? -eq 0 ]; then
        echo "✓ 完成: $mp3"
    else
        echo "❌ MP3 生成失败: $file"
    fi

done

echo "========================================"
echo "全部处理完成"