
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

# ffmpeg -y -i yequ.mp3 -ss 12 -t 290 -acodec copy $1/yequ0030.mp3



# ffmpeg -ss 12 -t 278 -y -i *.mp4 -codec copy cut.mp4

# ffmpeg -y -i *.mp4 -ss 00:00:12 -t 00:04:38 -vcodec copy cut.mp4

# ffmpeg -y -i *.mp4 -ss 00:00:12 -t 00:04:38 -vn -acodec copy cut.aac



# for f in *.mp4;
# do echo "file '$PWD/$f'";

# ffmpeg -y -i $PWD/"$f" -ss 00:00:12 -t 00:04:38 -vn -acodec copy $1/output/"$f".aac
# done


for f in *.aac;
do echo "file '$PWD/$f'";

ffmpeg -y -i $PWD/"$f" -c:a libmp3lame -ac 2 -b:a 60k $1/output/"$f".mp3

done
