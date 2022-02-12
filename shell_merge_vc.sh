# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output


ffmpeg -i "test.mp4" -i "test.m4a" -vcodec copy -acodec copy $1/output/all.mp4





