#!/bin/zsh

# 创建临时文件列表
tmpfile="filelist.txt"
rm -f "$tmpfile"
touch "$tmpfile"

for f in *.mp4; do
  echo "file '$PWD/$f'" >> "$tmpfile"
  echo "file '$PWD/$f'"
done

# 合并
ffmpeg -y -f concat -safe 0 -i "$tmpfile" -c copy "$1/output/all.mp4"

# 清理
rm -f "$tmpfile"
rm -rf tmp_*