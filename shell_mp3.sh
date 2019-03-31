# ffmpeg -y -i liangliang.mp3 -ss 00:00:00 -t 00:04:14 -vn -acodec copy liangliang414.mp3


# ffmpeg -y -i liangliang414.mp3 -af 'afade=t=out:st=240:d=14' -b:a 128k -acodec mp3 -ar 44100 -ac 2 liangliang414_fade.mp3


ffmpeg -y -i jd.mp3 -ss 00:00:00 -t 00:01:56 -vn -acodec copy jd_sample.mp3
ffmpeg -y -i jd_sample.mp3 -af 'afade=t=out:st=106:d=10' -b:a 128k -acodec mp3 -ar 44100 -ac 2 jd_sample_fade.mp3

ffmpeg -y -i br.mp3 -ss 00:02:34 -t 00:02:20 -vn -acodec copy br_sample.mp3
ffmpeg -y -i br_sample.mp3 -af 'afade=t=out:st=135:d=5' -b:a 128k -acodec mp3 -ar 44100 -ac 2 br_sample_fade.mp3

ffmpeg -y -i "concat:jd_sample_fade.mp3|br_sample_fade.mp3" -acodec copy jd_br.mp3



# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output
ffmpeg -y -i $output/$name -ss 00:27:00 -to 00:42:30 -acodec copy $output/$weather_name