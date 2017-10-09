
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

ffmpeg -y -i yequ.mp3 -ss 0 -t 30 -acodec copy $1/yequ0030.mp3



