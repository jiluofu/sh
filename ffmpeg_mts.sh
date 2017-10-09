echo $1
rm -rf $1/output
mkdir $1/output

echo "output:"$1"/output"
cd $1
find . -type f -name "*.MOV"|xargs -I {} ffmpeg -y -i {} -vcodec mpeg4 -b:v 2184000 -ab 128000 -s 1280*720 output/{}.mp4

cd output
find . -name '*.MOV.mp4'| awk -F "." '{print $2}'|xargs -I {} mv .{}.MOV.mp4 .{}.mp4
