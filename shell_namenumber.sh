
# 删除输出目录，重建
#rm -rf $1/output
#mkdir $1/output

counter=1
for i in $(ls -tr *.mp4)
do
#echo ${i}
printf -v paddedCounter "%02d" $counter
# 构造新的文件名并添加序号
f="${paddedCounter}.$i"
echo ${f}
mv --  "$i" "$f"
((counter++))
done



