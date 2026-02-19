#!/bin/bash

for file in *.m4a; do
  # 从文件名中提取“大明王朝123”的数字部分
  num=$(echo "$file" | grep -o '大明王朝[0-9]\+' | grep -o '[0-9]\+')

  # 如果未匹配到，跳过
  if [[ -z "$num" ]]; then
    echo "跳过未匹配：$file"
    continue
  fi

  # 格式化为三位数
  padded_num=$(printf "%03d" "$num")

  # 去掉最前面的 100. 或其他类似数字点前缀
  new_name=$(echo "$file" | sed -E 's/^[0-9]+\.//')

  # 去掉“大明王朝123.”部分
  new_name=$(echo "$new_name" | sed -E "s/大明王朝${num}\.//")

  # 最终新文件名
  final_name="${padded_num}.${new_name}"

  echo "重命名: $file -> $final_name"
  # mv -- "$file" "$final_name"
done