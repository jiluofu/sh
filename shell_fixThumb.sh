#!/bin/bash

# ==============================
# 默认目录
# ==============================
DEFAULT_DIR="$HOME/Documents/awaken"

# 目录参数
DIR="${1:-$DEFAULT_DIR}"

# 最近多少天（默认 8）
DAYS="${2:-8}"

if [ ! -d "$DIR" ]; then
  echo "❌ 目录不存在: $DIR"
  exit 1
fi

echo "📂 扫描目录: $DIR"
echo "📅 处理最近 $DAYS 天内修改的 JPG"
echo "📑 按文件名逆序处理"
echo "----------------------------------"

total=0
processed=0
skipped=0

find "$DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" \) -mtime -"$DAYS" \
| sort -V -r \
| while read file; do

  total=$((total+1))
  filename=$(basename "$file")
  echo "[$total] 🔍 处理: $filename"

  if exiftool -s -ThumbnailImage "$file" | grep -q "ThumbnailImage"; then
    echo "   🧹 检测到嵌入缩略图"

    # 读取修改时间
    orig_epoch=$(stat -f "%m" "$file" 2>/dev/null)

    # 如果修改时间不存在 → 用创建时间
    if [ -z "$orig_epoch" ] || [ "$orig_epoch" -eq 0 ]; then
      echo "   ⚠️ 修改时间不存在，使用创建时间"
      orig_epoch=$(stat -f "%B" "$file" 2>/dev/null)
    fi

    if [ -z "$orig_epoch" ] || [ "$orig_epoch" -eq 0 ]; then
      echo "   ❌ 无法读取时间信息，跳过"
      skipped=$((skipped+1))
      continue
    fi

    tmp_ref="$(mktemp "/tmp/fixthumb_time_XXXXXX")"
    touch -t "$(date -r "$orig_epoch" "+%Y%m%d%H%M.%S")" "$tmp_ref"

    exiftool -overwrite_original -ThumbnailImage= "$file" >/dev/null
    rc=$?

    if [ $rc -eq 0 ]; then
      touch -r "$tmp_ref" "$file"
      echo "   ✅ 删除成功，已恢复时间"
      processed=$((processed+1))
    else
      echo "   ❌ 删除失败"
      skipped=$((skipped+1))
    fi

    rm -f "$tmp_ref"

  else
    echo "   ⏭ 无嵌入缩略图，跳过"
    skipped=$((skipped+1))
  fi

done

echo "----------------------------------"
echo "📊 统计结果:"
echo "   总文件数: $total"
echo "   已处理:  $processed"
echo "   跳过:    $skipped"
echo "🎉 完成"