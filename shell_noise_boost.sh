
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

for i in $1/*.m4a
do

ffmpeg -y -i $i -filter:a "volume=9dB" $1/output/$i
done



