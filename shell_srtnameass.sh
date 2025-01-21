#!/bin/bash

# 使用第一个参数作为目录路径，如果未传递参数，默认使用当前目录
DIR="${1:-./}"

# 检查目录是否存在
if [ ! -d "$DIR" ]; then
  echo "Error: Directory '$DIR' does not exist."
  exit 1
fi

# 初始化数组
srt_files=()
ass_files=()

# 获取 .srt 文件列表
find "$DIR" -maxdepth 1 -type f -name "*.srt" ! -name ".*" -print0 | sort -z > srt_list.tmp
while IFS= read -r -d '' file; do
  srt_files+=("$file")
done < srt_list.tmp

# 获取 .ass 文件列表
find "$DIR" -maxdepth 1 -type f -name "*.ass" ! -name ".*" -print0 | sort -z > ass_list.tmp
while IFS= read -r -d '' file; do
  ass_files+=("$file")
done < ass_list.tmp

# 删除临时文件
rm -f srt_list.tmp ass_list.tmp

# 打印文件数量
echo "Directory: $DIR"
echo "Number of .srt files: ${#srt_files[@]}"
echo "Number of .ass files: ${#ass_files[@]}"

# 检查文件数量是否一致
if [ ${#srt_files[@]} -ne ${#ass_files[@]} ]; then
  echo "Error: The number of .srt files and .ass files do not match."
  echo "Check the following files:"
  echo "SRT files:"
  for srt_file in "${srt_files[@]}"; do
    echo "  $srt_file"
  done
  echo "ASS files:"
  for ass_file in "${ass_files[@]}"; do
    echo "  $ass_file"
  done
  exit 1
fi

# 遍历文件并重命名
for ((i = 0; i < ${#srt_files[@]}; i++)); do
  srt_file=${srt_files[$i]}
  ass_file=${ass_files[$i]}

  # 获取 .srt 文件的文件名（不带扩展名）
  base_name=$(basename "$srt_file" .srt)

  # 目标文件名
  new_ass_file="$DIR/$base_name.ass"

  # 重命名 .ass 文件
  mv "$ass_file" "$new_ass_file"

  # 输出重命名结果
  echo "Renamed: \"$ass_file\" -> \"$new_ass_file\""
done

echo "Renaming completed."