ls_date=`date +%Y%m%d_%H%M%S`
echo $ls_date

src_dir="/Volumes/RX100M5A/DCIM/100MSDCF"
video_src_dir="/Volumes/RX100M5A/PRIVATE/M4ROOT/CLIP"

pic_dir="/Users/zhuxu/Pictures/lr/photos"
echo $pic_dir/$ls_date"_rx100"
mkdir $pic_dir/$ls_date"_rx100"
cp -rf $src_dir/*.ARW $pic_dir/$ls_date"_rx100"

video_dir="/Users/zhuxu/Desktop/mmjswork/video"
# rm -rf video_dir/*
cp -rf $video_src_dir/*.MP4 $video_dir"_rx100"

video_dir="/Users/zhuxu/Pictures/lr/videos"
mkdir $video_dir/$ls_date"_rx100"
cp -rf $video_src_dir/*.MP4 $video_dir/$ls_date"_rx100"