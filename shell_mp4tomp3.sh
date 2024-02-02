
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output


for i in $1/*.aac
do

ffmpeg -i $i -c:v copy -c:a libmp3lame -q:a 4 output/${i/aac/mp3}

done



