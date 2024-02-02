# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output


<<<<<<< HEAD
# for i in $1/*.mp4
# do
# ffmpeg -i $i -vn -codec copy ${i/mp4/m4a}
# done



ffmpeg -i "videoplayback.mp4" -i "1.m4a" -vcodec copy -acodec copy $1/output/all.mp4
=======
# ffmpeg -i "11.webm" -i "11.mp3" -vcodec copy -acodec copy $1/output/all.mp4
for i in $1/*.mp4
do

# ffmpeg -y -r $fps -i $i  -vcodec mpeg4 -s $width*$height -b:v $bv output/$i
# ffmpeg -i $i -c copy -c:v libx264 -vf scale=-2:720 output/$i
# echo `ffmpeg -i $1.mp4 -f mp3 -vn $1.mp3`
# ffmpeg -i $i -f mp3 -vn ${i/mp4/mp3}
ffmpeg -i $i -vn -codec copy ${i/mp4/m4a}
done



ffmpeg -i "videoplayback.webm" -i "videoplayback.m4a" -vcodec copy -acodec copy $1/output/all.mp4
>>>>>>> 2355b63b02b8626fc4c6cbdd88355cd7b833b909




