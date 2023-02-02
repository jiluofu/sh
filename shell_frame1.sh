# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

x=0

# 遍历脚本第1个参数，表示图片资源目录，遍历目录里的jpg
for i in $1/*.jpg
do
# x计数器自增
x=`expr $x + 1`
# 设定4位数长度的数字
num=$((10000+$x))
# 截掉开头的1，保持数字都是4位
num=${num:1}

# 图片改名复制到output
echo ./$i ./$1/output/image$num.jpg
cp "${i}" ./$1/output/image$num.jpg
done

ffmpeg -f image2 -r 7 -i $1/output/image%4d.jpg ./$1/output/output.mp4
rm -f $1/output/*.jpg



