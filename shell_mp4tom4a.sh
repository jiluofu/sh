
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

counter=1
for i in *.mp4
do

#printf -v paddedCounter "%02d" $counter
# 构造新的文件名并添加序号
#f="${paddedCounter}.${i%.*}.m4a"
f="${i%.*}.m4a"
echo ${f}
ffmpeg -i $i -vn -c:a copy output/$f
done



