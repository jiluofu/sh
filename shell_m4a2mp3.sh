
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

for f in *.m4a;
do echo "file '$PWD/$f'";
ffmpeg -y -i $PWD/"$f" -acodec libmp3lame -aq 2 "$1/output/${f%.m4a}.mp3"
done

#for f in *.mp3;
#do echo "file '$PWD/$f'";
#ffmpeg -y -i $f -filter:a "volume=15dB" $1/output/$f
#done