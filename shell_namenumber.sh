#!/bin/bash

# 使用方法： ./script.sh [目录路径] [sort_order]
# 示例：     ./script.sh . asc   （按时间升序排序）
#           ./script.sh . desc  （按时间降序排序）

# 参数
dir_path="$1"
sort_order="${2:-asc}"  # 默认升序

cd "$dir_path" || exit 1

# 删除输出目录，重建（如需保留，去掉注释）
# rm -rf "$dir_path/output"
# mkdir -p "$dir_path/output"

counter=1

# 判断排序顺序
if [[ "$sort_order" == "desc" ]]; then
    file_list=$(ls -t *.mp4)
else
    file_list=$(ls -tr *.mp4)
fi

for i in $file_list; do
    printf -v paddedCounter "%02d" $counter
    f="${paddedCounter}.$i"
    echo "$f"
    mv -- "$i" "$f"
    ((counter++))
done