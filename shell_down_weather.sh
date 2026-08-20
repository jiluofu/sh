# 下载交通台早上一路畅通，截取天气部分00:31:50-00:37:30
# http://playback.rbc.cn/audioD/fm1039/20180319/0730007200_mp4/073000_7200_96K.mp4

if [ "$1" = "" ];then
time=$(date "+%Y%m%d")
else
time=$1
fi

# output="/Users/zhuxu/Downloads"
output="/home/zhuxu/mmjs_server/gohttps_loader/static/weather"

# 下载直播
# ffmpeg -y -i http://audiolive.rbc.cn:1935/live/fm1039/96K/tzwj_video.m3u8 -ss 0 -to 120  test.mp4
#url="https://rtmp-push.tingtingfm.com/bjradio/fm1039.m3u8?auth_key=1774672183-ydWDv4YW-0-469988d52317238ed776c06499eae619"
url="https://brtv-radiolive.rbc.cn/alive/fm1039.m3u8?auth=2346235872047145@36@288EA47F2FB2233054F8C6A94FF01F6E"
name=$time"_ylct.mp4"
echo $url
echo $name
# wget -O $output/$name $url
weather_name=$time"_weather.mp4"
echo $weather_name
ffmpeg -y -i $url -ss 00:00:00 -to 00:12:30   $output/$weather_name


# # 下载回放
# url="http://playback.rbc.cn/audioD/fm1039/$time/0730007200_mp4/073000_7200_96K.mp4"
# name=$time"_ylct.mp4"
# echo $url
# echo $name
# wget -O $output/$name $url
# weather_name=$time"_weather.mp4"
# echo $weather_name
# ffmpeg -y -i $output/$name -ss 00:31:00 -to 00:38:30 -acodec copy $output/$weather_name


rm -rf $output/$name
weather_file_name=$time"_weather.mp3"
weather_file_name_wav=$time"_weather.wav"
ffmpeg -y -i $output/$weather_name  -f mp3 -vn $output/$weather_file_name
ffmpeg -y -i $output/$weather_name  -ac 1 -ar 16000 $output/$weather_file_name_wav
#rm -rf $output/$weather_name

/home/zhuxu/mmjs_server/sh/py_weather_serial.py $time
echo $time"_weather" | s-nail -s $time"_weather" -a $output/output/$weather_file_name  1077246@qq.com

 


