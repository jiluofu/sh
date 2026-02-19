#!/bin/bash

# 检查参数
if [ -z "$1" ]; then
    echo "用法: $0 目录路径"
    exit 1
fi

DIR="$1"

if [ ! -d "$DIR" ]; then
    echo "目录不存在: $DIR"
    exit 1
fi

# 进入目录
cd "$DIR" || exit 1

# 逆序遍历 jpg 文件
ls -r *.jpg 2>/dev/null | while read -r file
do
    echo "处理: $file"

    # 提取时间部分（文件名前 19 个字符）
    datetime_part="${file:0:19}"

    # 格式应为：YYYY-MM-DD HH-MM-SS
    # 转换为 touch 需要的格式：YYYYMMDDhhmm.ss
    year=${datetime_part:0:4}
    month=${datetime_part:5:2}
    day=${datetime_part:8:2}
    hour=${datetime_part:11:2}
    minute=${datetime_part:14:2}
    second=${datetime_part:17:2}

    touch_time="${year}${month}${day}${hour}${minute}.${second}"

    echo "  -> 修改时间为: $touch_time"

    touch -m -t "$touch_time" "$file"

done

echo "完成"
