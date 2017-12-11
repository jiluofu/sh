ffmpeg -y -i liangliang.mp3 -ss 00:00:00 -t 00:04:14 -vn -acodec copy liangliang414.mp3


ffmpeg -y -i liangliang414.mp3 -af 'afade=t=out:st=240:d=14' -b:a 128k -acodec mp3 -ar 44100 -ac 2 liangliang414_fade.mp3