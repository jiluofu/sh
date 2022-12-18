
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

for i in $1/*.WAV
do

ffmpeg -y -i $i -ab 320k $1/output/${i%.*}.m4a


done



