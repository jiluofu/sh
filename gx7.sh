ls_date=`date +%Y%m%d_%H%M%S`
echo $ls_date

src_dir="/Volumes/RX100M5A/DCIM/183_PANA"

pic_dir="/Users/zhuxu/Pictures/lr/photos"
echo $pic_dir/$ls_date"_gx7"
mkdir $pic_dir/$ls_date"_gx7"
cp -rf $src_dir/*.RW2 $pic_dir/$ls_date"_gx7"

# video_dir="/Users/zhuxu/Desktop/mmjswork/video"
# rm -rf video_dir/*
# cp -rf $src_dir/*.MOV $video_dir

# video_dir="/Users/zhuxu/Pictures/lr/videos"
# mkdir $video_dir/$ls_date
# cp -rf $src_dir/*.MOV $video_dir/$ls_date