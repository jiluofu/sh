
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

for i in *.mp3
do
echo $i
ffmpeg -y -i $i -filter:a "volume=6dB" -codec:a libmp3lame -q:a 0 -b:a 160k $1/output/$i
done



