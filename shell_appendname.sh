#!/bin/bash


exec 3< "./append_list.txt"

for oldfile in *.mp3; do

    # 从卷轴中读取下一行，也就是新的文件名
    read -r newname <&3 || break
    extension="${oldfile##*.}"
    f=${oldfile%.*}
    f=$(echo "$f" | sed -E 's/^fry_[0-9]+_//')
    # 构造新文件的完整路径，但是不包括原始的扩展名
    newfile=$f"_"$newname"."$extension
    mv -- "$oldfile" "$newfile"
    echo $newfile
done


