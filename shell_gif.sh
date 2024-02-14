echo $1;
rm -rf $1/output;
mkdir $1/output;
echo "output:"$1
echo "resize photos"
cd $1

# find . -type f -name "*.jpg"|xargs -I {} convert -resize 300x300 {} output/{}
# echo "compress photos"
# cd output
# convert *.jpg ani.gif
# rm *.jpg
# ffmpeg -i ani.gif -vcodec mpeg4  -b:v 20M ani.mp4

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
ffmpeg -f image2 -r 10 -i $1/output/image%4d.jpg -vcodec mpeg4  -b:v 20M ./$1/output/output.mp4
rm -f ./$1/output/*.jpg


