
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output
rm list.txt

for f in *.MP4;
do echo "file '$PWD/$f'";
ffmpeg -y -i $PWD/$f -c:v libx264 -preset ultrafast -b:v 19000k $1/output/tmp_$f
done

printf "file '%s'\n" $1/output/tmp_*.MP4>$1/list.txt

ffmpeg -y -f concat -safe 0 -i list.txt -c copy $1/output/all.mp4
rm -rf $1/output/tmp_*





