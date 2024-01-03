ls_date=`date +%Y%m%d_%H%M%S`
echo $ls_date

# src_dir="/Volumes/SD/DCIM/100OLYMP"

pic_dir="/Users/zhuxu/Pictures/lr/photos"
echo $pic_dir/$ls_date
mkdir $pic_dir/$ls_date
cp -rf /Volumes/64/DCIM/100MSDCF/*.ARW $pic_dir/$ls_date

# video_dir="/Users/zhuxu/Desktop/mmjswork/video"
# rm -rf video_dir/*
# cp -rf /Volumes/64/PRIVATE/M4ROOT/CLIP/*.MP4 $video_dir

video_dir="/Users/zhuxu/Pictures/lr/videos"
mkdir $video_dir/$ls_date
cp -rf /Volumes/64/PRIVATE/M4ROOT/CLIP/*.MP4 $video_dir/$ls_date