
# 进入图片目录，运行脚本，第一个参数是当前目录，会在当前目录生成output目录，临时复制存放图片，生成output.mp4之后，清理临时图片
# 图片计数
x=0

# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

# 遍历脚本第1个参数，表示图片资源目录，遍历目录里的jpg
for i in $1/*.jpg
do
# x计数器自增
x=`expr $x + 1`
# 设定4位数长度的数字
num=$((10000+$x))
# 截掉开头的1，保持数字都是4位
num=${num:1}

# 图片改名复制到output
echo ./$i ./$1/output/image$num.jpg
cp "${i}" ./$1/output/image$num.jpg
done

# 视频宽高
# width=480
# height=320
width=1240
height=700

# fps
fps=7

# 视频码率bit/s
bv=6000k

# 图片合成视频，用于计算视频时长
ffmpeg -y -r $fps  -i ./$1/output/image%4d.jpg -vcodec mpeg4 -b:v $bv ./$1/output/output.mp4

# 获取视频的秒数
video_secs=`ffprobe -i ./$1/output/output.mp4 -show_entries stream=codec_type,duration -of compact=p=0:nk=1|grep video`
video_secs=${video_secs//video|/}
video_secs=${video_secs%.*}
echo $video_secs

# 获取音频的秒数
audio_secs=`ffprobe -i ../bg/bg.mp3 -show_entries stream=codec_type,duration -of compact=p=0:nk=1|grep audio`
audio_secs=${audio_secs//audio|/}
audio_secs=${audio_secs%.*}
echo $audio_secs

# 计算视频长度是音频的几倍
loops=$(echo "(${video_secs} / ${audio_secs})"|bc)
echo loops:$loops

# 淡入淡出的秒数
fade_len=2

# 淡出开始的秒数位置
st=`expr $video_secs - $fade_len`
echo st:$st


# 判断，loops为0，说明音频比视频长，不需要重复音频，直接按照视频长度截取音频
if [ $loops == 0 ]
then
    # 按照视频时长，复制一个音频
    ffmpeg -y -i ../bg/bg.mp3 -ss 0 -t $video_secs -acodec copy ./$1/bg_cut_final.mp3

# 视频时常比音频长
elif [ $loops > 0 ]
then
    echo "loops > 0"
    # 根据循环次数生成完整循环乐曲，这里不需要+1
    stream_loop=`expr $loops + 0`
    echo stream_loop:$stream_loop

    # 生成超过视频时常的最短音频循环
    ffmpeg -stream_loop $stream_loop -i ../bg/bg.mp3 -c copy -y ./$1/bg_loop.mp3

    # 按照视频时长，复制循环的音频
    ffmpeg -y -i ./$1/bg_loop.mp3 -ss 0 -t $video_secs -acodec copy ./$1/bg_cut_final.mp3

fi

# 合并音频和视频，生成最终的视频
# 音频和视频分别进行淡入和淡出
# ffmpeg -y -r $fps -i ./$1/bg_cut_final.mp3  -i ./$1/output/image%3d.jpg -af 'afade=t=in:ss=0:d='$fade_len',afade=t=out:st='$st':d='$fade_len -vf 'fade=t=in:st=0:d='$fade_len',fade=t=out:st='$st':d='$fade_len -vcodec mpeg4 -s $width*$height -b:v $bv ./$1/output/final.mp4
ffmpeg -y -r $fps -i ./$1/bg_cut_final.mp3  -i ./$1/output/output.mp4 -af 'afade=t=in:ss=0:d='$fade_len',afade=t=out:st='$st':d='$fade_len -vf 'fade=t=out:st='$st':d='$fade_len -vcodec mpeg4 -b:v $bv -s $width*$height ./$1/output/final.mp4

# 第1张图作封面
# atomicparsley ./$1/output/final.mp4 --artwork ./$1/image001.jpg

# 清理用于计算视频时长的output.mp4
rm -rf ./$1/output/output.mp4

# 清理中间环节的bg_*.mp3
rm -rf ./$1/bg_*.mp3

# 清理output下的图片
rm -rf ./$1/output/*.jpg

/Users/zhuxu/Documents/sh/shell_split.sh ./output/ 1240 827



