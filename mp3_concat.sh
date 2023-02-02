
# 进入图片目录，运行脚本，第一个参数是当前目录，会在当前目录生成output目录，临时复制存放图片，生成output.mp4之后，清理临时图片
# 图片计数
x=0

# 删除输出目录，重建
rm -rf $1/output
rm -rf $1/output1
mkdir $1/output
mkdir $1/output1

for f in *.mp3;
do echo "file '$PWD/$f'";
done

ffmpeg -y -f concat -safe 0 -i <(for f in *.mp3; do echo "file '$PWD/$f'"; done) -c copy $1/output1/all.mp3

ffmpeg -y -i $1/output1/all.mp3 -filter:a "volume=9dB" $1/output/all.mp3

# ffmpeg -y -i $1/output/all.mp4 -filter_complex "[0:v]setpts=0.125*PTS[v]" -map "[v]"  $1/output/all_8.mp4






