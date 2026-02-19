#!/bin/bash

for file in *.m4a; do
  # 提取中括号内“大明王朝数字”的数字部分
  num=$(echo "$file" | grep -o '【大明王朝[0-9]\+】' | grep -o '[0-9]\+')

  # 如果未匹配到数字，跳过
  if [[ -z "$num" ]]; then
    echo "❌ 跳过未匹配：$file"
    continue
  fi

  # 格式化数字为三位数
  padded_num=$(printf "%03d" "$num")

  # 去掉开头如000.或其他数字.前缀
  new_name=$(echo "$file" | sed -E 's/^[0-9]+\.//')

  # 去掉中括号的“大明王朝数字”
  new_name=$(echo "$new_name" | sed -E "s/【大明王朝${num}】//")

  # 最终文件名拼接
  final_name="${padded_num}.${new_name}"

  echo "🔁 重命名: '$file' -> '$final_name'"
  mv -- "$file" "$final_name"
done