
# 删除输出目录，重建
# rm -rf $1/output
# mkdir $1/output

# 视频宽高
# width=640
# height=480

# fps
# fps=25

# 视频码率bit/s
bv=6000k




# ffmpeg -y -i cheap_thrills.mp4 -ss 00:00:00 -t 00:00:17  -vcodec mpeg4 -b:v 3000k cheap_thrills_01.mp4
# ffmpeg -y -i cheap_thrills.mp4 -ss 00:00:16 -t 00:00:22  -vcodec mpeg4 -b:v 3000k cheap_thrills_02.mp4
# ffmpeg -y -i cheap_thrills.mp4 -ss 00:00:22 -t 00:00:27  -vcodec mpeg4 -b:v 3000k cheap_thrills_03.mp4
# ffmpeg -y -i cheap_thrills.mp4 -ss 00:00:26 -t 00:00:38  -vcodec mpeg4 -b:v 3000k cheap_thrills_04.mp4
# ffmpeg -y -i cheap_thrills.mp4 -ss 00:00:38 -t 00:00:49  -vcodec mpeg4 -b:v 3000k cheap_thrills_05.mp4
# ffmpeg -y -i cheap_thrills.mp4 -ss 00:00:48 -t 00:00:54  -vcodec mpeg4 -b:v 3000k cheap_thrills_06.mp4
# ffmpeg -y -i cheap_thrills.mp4 -ss 00:00:54 -t 00:01:00  -vcodec mpeg4 -b:v 3000k cheap_thrills_07.mp4
# ffmpeg -y -i cheap_thrills.mp4 -ss 00:01:00 -t 00:01:10  -vcodec mpeg4 -b:v 3000k cheap_thrills_08.mp4
# ffmpeg -y -i cheap_thrills.mp4 -ss 00:01:09 -t 00:01:20  -vcodec mpeg4 -b:v 3000k cheap_thrills_09.mp4
# ffmpeg -y -i cheap_thrills.mp4 -ss 00:01:20 -t 00:01:28  -vcodec mpeg4 -b:v 3000k cheap_thrills_10.mp4


ffmpeg -y -i cheap_thrills.mp4 -ss 00:00:00 -t 00:00:17  -vcodec mpeg4 -b:v 3000k cheap_thrills_01.mp4
ffmpeg -y -i cheap_thrills.mp4 -ss 00:00:16 -t 00:00:06  -vcodec mpeg4 -b:v 3000k cheap_thrills_02.mp4
ffmpeg -y -i cheap_thrills.mp4 -ss 00:00:22 -t 00:00:05  -vcodec mpeg4 -b:v 3000k cheap_thrills_03.mp4
ffmpeg -y -i cheap_thrills.mp4 -ss 00:00:26 -t 00:00:12  -vcodec mpeg4 -b:v 3000k cheap_thrills_04.mp4
ffmpeg -y -i cheap_thrills.mp4 -ss 00:00:38 -t 00:00:11  -vcodec mpeg4 -b:v 3000k cheap_thrills_05.mp4
ffmpeg -y -i cheap_thrills.mp4 -ss 00:00:48 -t 00:00:06  -vcodec mpeg4 -b:v 3000k cheap_thrills_06.mp4
ffmpeg -y -i cheap_thrills.mp4 -ss 00:00:54 -t 00:00:06  -vcodec mpeg4 -b:v 3000k cheap_thrills_07.mp4
ffmpeg -y -i cheap_thrills.mp4 -ss 00:01:00 -t 00:00:10  -vcodec mpeg4 -b:v 3000k cheap_thrills_08.mp4
ffmpeg -y -i cheap_thrills.mp4 -ss 00:01:09 -t 00:00:11  -vcodec mpeg4 -b:v 3000k cheap_thrills_09.mp4
ffmpeg -y -i cheap_thrills.mp4 -ss 00:01:20 -t 00:00:08  -vcodec mpeg4 -b:v 3000k cheap_thrills_10.mp4

