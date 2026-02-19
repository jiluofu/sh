#!/bin/bash

# 参数1为目录路径
dir="$1"
# 参数2为排序方式（asc 或 desc）
sort_order="${2:-asc}"  # 默认为asc（升序）

# 删除输出目录并重建
rm -rf "$dir/output"
mkdir -p "$dir/output"

# 清理旧的 xml 文件
rm -rf "$dir"/*.xml

# 调用处理脚本
~/Documents/sh/shell_cleanname.sh "$dir"
~/Documents/sh/shell_namenumber.sh "$dir" "$sort_order"

# 切换到目标目录
cd "$dir" || exit

# 按修改时间获取 .mp4 文件列表
if [[ "$sort_order" == "desc" ]]; then
  file_list=$(ls -1t *.mp4)
else
  file_list=$(ls -1tr *.mp4)
fi

# 遍历处理
for i in $file_list; do
  f="${i%.*}.m4a"
  echo "正在处理：$i → output/$f"
  ffmpeg -i "$i" -vn -c:a copy "output/$f"
done