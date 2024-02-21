#!/bin/bash

# ffmpeg -i $1/videoplayback.mp4 -vn -codec copy $1/videoplayback.m4a

# ffmpeg -i "videoplayback.mp4" -i "videoplayback.m4a" -vcodec copy -acodec copy $1/videoplaybackall.mp4

# for f in *;
# do echo "file '$PWD/$f'";echo "name '$f'";


# # 删除输出目录，重建
# rm -rf $PWD/$f/output
# mkdir $PWD/$f/output
# ffmpeg -y -f concat -safe 0 -i <(for ff in $PWD/$f/*.m4a; do echo "file '$ff'"; done) -c copy $PWD/$f/output/$f.m4a

# done

# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

for f in *.webm;
do prefix="${f%.*}";echo "$prefix";echo "video '$f'";
# ffmpeg -i $f -i $prefix.mp4 -c:v hevc_videotoolbox -preset medium -acodec copy $1/output/$prefix.mp4;
ffmpeg -i $f -i $prefix.mp4 -vcodec copy -acodec copy $1/output/$prefix.mp4;
done




