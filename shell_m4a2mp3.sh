
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

# for f in *.aac;
# do echo "file '$PWD/$f'";

# ffmpeg -y -i $PWD/"$f" -c:a libmp3lame -ac 2 -b:a 60k $1/output/"$f".mp3

# done

for f in *.mp3;
do echo "file '$PWD/$f'";
ffmpeg -y -i $f -filter:a "volume=15dB" $1/output/$f
done


