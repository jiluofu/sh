
ffmpeg -i $1/videoplayback.mp4 -vn -codec copy $1/videoplayback.m4a
ffmpeg -i "videoplayback.webm" -i "videoplayback.m4a" -vcodec copy -acodec copy $1/videoplaybackall.mp4




