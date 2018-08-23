ls_date=`date +%Y%m%d_%H%M%S`
echo $ls_date

src_dir="/Volumes/RX100M5A/DCIM/100MSDCF"
video_src_dir="/Volumes/RX100M5A/PRIVATE/M4ROOT/CLIP"

pic_dir="/Users/zhuxu/Pictures/lr/photos"
echo $pic_dir/$ls_date
mkdir $pic_dir/$ls_date
cp -rf $src_dir/*.ARW $pic_dir/$ls_date

video_dir="/Users/zhuxu/Desktop/mmjswork/video"
# rm -rf video_dir/*
cp -rf $video_src_dir/*.MP4 $video_dir

video_dir="/Users/zhuxu/Pictures/lr/videos"
mkdir $video_dir/$ls_date
cp -rf $video_src_dir/*.MP4 $video_dir/$ls_date