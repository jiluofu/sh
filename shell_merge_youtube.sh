# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output


ffmpeg -i "11.webm" -i "11.mp3" -vcodec copy -acodec copy $1/output/all.mp4





