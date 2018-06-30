brew install libass

先把ass转成srt
ffmpeg -i subtitle.ass subtitle.srt

srt和视频合并
ffmpeg -i input.mp4 -i subtitles.srt -c:s mov_text -c:v copy -c:a copy output_subtitle.mp4