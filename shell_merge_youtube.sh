# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output


# for i in $1/*.mp4
# do
# ffmpeg -i $i -vn -codec copy ${i/mp4/m4a}
# done



ffmpeg -i "videoplayback.mp4" -i "1.m4a" -vcodec copy -acodec copy $1/output/all.mp4




