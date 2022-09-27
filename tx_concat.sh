# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

rm -rf list.txt
for f in *.ts;
do 
	echo "file '$PWD/$f'">>list.txt;
done

ffmpeg -y -f concat -safe 0 -i list.txt -c copy $1/output/all.mp4

# rm -rf tmp_*





