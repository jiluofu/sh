#https://mps-video.yzcdn.cn/multi_trans_hls/H-dLq2HUjLiUkxcvM18ObJg91RojV_j6.mp4.f30_556.ts?sign=29b686b8b0aa6fed242ad0cf89c38252&t=618e5a70
#https://mps-video.yzcdn.cn/multi_trans_hls/H-dLq2HUjLiUkxcvM18ObJg91RojV_j6.mp4.f30_1.ts?sign=29b686b8b0aa6fed242ad0cf89c38252&t=618e5a70

# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

for f in {0..408};
do wget "https://mps-video.yzcdn.cn/multi_trans_hls/BGSGhFq7gkxTnp1Y6xZbAauWuYJNw1W5.mp4.f30_$f.ts?sign=cc9f600f41cd43abebd855304b357868&t=618e63d4" -O ./output/$f.ts ;
done

ffmpeg -y -f concat -safe 0 -i <(for f in $1/output/*.ts; do echo "file '$PWD/$f'"; done) -c copy $1/output/all.mp4