
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output


for i in $1/*.mp4
do

# ffmpeg -y -r $fps -i $i  -vcodec mpeg4 -s $width*$height -b:v $bv output/$i
# ffmpeg -i $i -c copy -c:v libx264 -vf scale=-2:720 output/$i
# echo `ffmpeg -i $1.mp4 -f mp3 -vn $1.mp3`
ffmpeg -i $i -f mp3 -vn output/${i/mp4/mp3}

done



