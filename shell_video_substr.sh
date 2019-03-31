
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

# 视频宽高
# width=640
# height=480

# fps
# fps=25

# 视频码率bit/s
bv=6000k




ffmpeg -y -i cheap_thrills.mp4 -ss 5 -t 83  -vcodec mpeg4 -b:v 3000k cheap_thrills_test.mp4




