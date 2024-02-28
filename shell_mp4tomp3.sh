
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output


for i in *.mp4
do
echo ${i/mp4/mp3}
ffmpeg -i $i -vn -acodec libmp3lame -aq 2 output/${i/mp4/mp3}
done



