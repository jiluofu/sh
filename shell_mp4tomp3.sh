
# 删除输出目录，重建
rm -rf $1/output
rm -rf $1/output1
mkdir $1/output
mkdir $1/output1


for i in $1/*.mkv
do

# ffmpeg -y -r $fps -i $i  -vcodec mpeg4 -s $width*$height -b:v $bv output/$i
# ffmpeg -i $i -c copy -c:v libx264 -vf scale=-2:720 output/$i
# echo `ffmpeg -i $1.mp4 -f mp3 -vn $1.mp3`
ffmpeg -i $i -f mp3 -vn output/${i/mkv/mp3}
ffmpeg -y -i output/${i/mkv/mp3} -filter:a "volume=9dB" $1/output1/${i/mkv/mp3}

done



