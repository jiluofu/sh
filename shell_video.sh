
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

# 视频宽高
width=640
height=480

# fps
fps=25

# 视频码率bit/s
bv=600k




for i in $1/*.mp4 *.MOV
do

# ffmpeg -y -r $fps -i $i  -vcodec mpeg4 -s $width*$height -b:v $bv output/$i
ffmpeg -i $i -c copy -c:v libx264 -vf scale=-2:720 output/$i

done



