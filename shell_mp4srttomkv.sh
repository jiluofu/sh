#!/bin/bash

# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output


for i in *.mp4
do
f=${i%.*}
#f=$(echo "$f" | sed -E 's/ //g')
echo $f
ffmpeg -i "$f.mp4" -i "$f.srt" -c copy -c:s srt output/"$f.mkv"
done



