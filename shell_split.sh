
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

# 视频宽高
width=1280
height=720

# fps
# fps=15

# 视频码率bit/s
bv=3000k

MAX_SEC=50

if [ $2 ]
then
    width=$2
fi

if [ $3 ]
then
    heigth=$3
fi




for i in $1/*.MOV $1/*.mp4
do
video_secs=`ffprobe -i $i -show_entries stream=codec_type,duration -of compact=p=0:nk=1|grep video`
video_secs=${video_secs//video|/}
video_secs=${video_secs%.*}
echo $video_secs

loops=$(echo "(${video_secs} / ${MAX_SEC})"|bc)
echo loops:$loops
left=`expr $video_secs - $loops \* $MAX_SEC`
echo left:$left

if [ $left == 0 ]
then
    # echo `expr $loops - 1`
    loops=`expr $loops - 1`
fi
echo loops fix:$loops

filename=$(echo $i | awk -F'./' '{print $2}' | awk -F'.' '{print $1}')
echo $filename

    for j in $(seq 0 $loops)
    do

    echo ffmpeg -y -i $i -ss `expr $MAX_SEC \* $j` -t $MAX_SEC -vcodec mpeg4 -s $width*$height -b:v $bv output/$filename\_$j.mp4
    ffmpeg -y -i $i -ss `expr $MAX_SEC \* $j` -t $MAX_SEC -vcodec mpeg4 -s $width*$height -b:v $bv output/$filename\_$j.mp4
    done

done



