# 下载交通台早上一路畅通，截取天气部分00:31:50-00:37:30
# http://playback.rbc.cn/audioD/fm1039/20180319/0730007200_mp4/073000_7200_96K.mp4

if [ "$1" = "" ];then
time=$(date "+%Y%m%d")
else
time=$1
fi

output="/Users/zhuxu/Downloads"
# output="/home/zhuxu/mmjs_server/gohttps_loader/static/weather"

# # 下载直播
# # ffmpeg -y -i http://audiolive.rbc.cn:1935/live/fm1039/96K/tzwj_video.m3u8 -ss 0 -to 120  test.mp4
# url="http://audiolive.rbc.cn:1935/live/fm1039/96K/tzwj_video.m3u8"
# name=$time"_ylct.mp4"
# echo $url
# echo $name
# # wget -O $output/$name $url
# weather_name=$time"_weather.mp4"
# echo $weather_name
# ffmpeg -y -i $url -ss 00:00:00 -to 00:08:30 $output/$weather_name


# 下载回放
url="http://playback.rbc.cn/audioD/fm1039/$time/0730007200_mp4/073000_7200_96K.mp4"
name=$time"_ylct.mp4"
echo $url
echo $name
wget -O $output/$name $url
weather_name=$time"_weather.mp4"
echo $weather_name
ffmpeg -y -i $output/$name -ss 00:27:00 -to 00:42:30 -acodec copy $output/$weather_name


rm -rf $output/$name
weather_file_name=$time"_专家聊天气.mp3"
weather_file_name_wav=$time"_专家聊天气.wav"
ffmpeg -y -i $output/$weather_name  -f mp3 -vn $output/$weather_file_name
ffmpeg -y -i $output/$weather_name  -f wav $output/$weather_file_name_wav
rm -rf $output/$weather_name

# echo $time"_专家聊天气" | mailx -s $time"_天气和专家" -a $output/$weather_file_name  1077246@qq.com
# ./py_weather.py $time

 



