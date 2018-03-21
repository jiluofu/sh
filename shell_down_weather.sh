# 下载交通台早上一路畅通，截取天气部分00:31:30-00:36:30
# http://playback.rbc.cn/audioD/fm1039/20180319/0730007200_mp4/073000_7200_96K.mp4

if [ "$1" = "" ];then
time=$(date "+%Y%m%d")
else
time=$1
fi

url="http://playback.rbc.cn/audioD/fm1039/$time/0730007200_mp4/073000_7200_96K.mp4"
name=$time"_ylct.mp4"
echo $url
echo $name
output="/Users/zhuxu/Downloads"
#output="/home/zhuxu/gohttps_loder/static/weather"

wget -O $output/$name $url
weather_name=$time"_weather.mp4"
echo $weather_name

ffmpeg -y -i $output/$name -ss 00:31:50 -to 00:36:30 -acodec copy $output/$weather_name
rm -rf $output/$name

weather_file_name=$time"_专家聊天气.mp3"
ffmpeg -y -i $output/$weather_name  -f mp3 -vn $output/$weather_file_name
rm -rf $output/$weather_name

 


