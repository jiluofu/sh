

# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

ffmpeg -y -f concat -safe 0 -i <(for f in *.WAV; do echo "file '$PWD/$f'"; done) -c copy $1/output/all.WAV

# rm -rf tmp_*





