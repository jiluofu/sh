#https://mps-video.yzcdn.cn/multi_trans_hls/H-dLq2HUjLiUkxcvM18ObJg91RojV_j6.mp4.f30_556.ts?sign=29b686b8b0aa6fed242ad0cf89c38252&t=618e5a70
#https://mps-video.yzcdn.cn/multi_trans_hls/H-dLq2HUjLiUkxcvM18ObJg91RojV_j6.mp4.f30_1.ts?sign=29b686b8b0aa6fed242ad0cf89c38252&t=618e5a70
#https://mps-trans.yzcdn.cn/multi_trans_hls_fhd/pmHVH1uasPi7UvGPJFzH3DKX1jIJ5yUJRNmPwQ_HD_$f.ts?sign=fe0d9a1eb2e527d87906f5a985a15156&t=63133844
#https://mps-trans.yzcdn.cn/multi_trans_hls_fhd/0GBOuq0E0uRuzfaKyRUR6pJA4EEbJHki-C0bQQ_HD_$f.ts?sign=50c861abb60e777c5169466b32d5f9aa&t=63133b69

# 01_发展孩子的安全感 146
# https://mps-trans.yzcdn.cn/multi_trans_hls_fhd/pmHVH1uasPi7UvGPJFzH3DKX1jIJ5yUJRNmPwQ_HD_$f.ts?sign=5f7c291e92a65cac5e6cc861887e4a8f&t=63133f4a

# 02_游戏力循环的力量 194
# https://mps-trans.yzcdn.cn/multi_trans_hls_fhd/0GBOuq0E0uRuzfaKyRUR6pJA4EEbJHki-C0bQQ_HD_$f.ts?sign=a07e7876257bc9ca44eec649f7eb6205&t=63133d9e
# 03_游戏中联结与引导 143 
# https://mps-trans.yzcdn.cn/multi_trans_hls_fhd/OEifL3_0tYs2FLRfucrPi39lCBiod8o7pX6eDA_HD_$f.ts?sign=ed7d400ce35878f21042e2148851b96d&t=63133bd6
# 04_迎接情绪 162
# https://mps-trans.yzcdn.cn/multi_trans_hls_fhd/AQW1WkYhf_1iCQdzumcwkMln9D-QspO5_HD_$f.ts?sign=bf714f542ae55a43a34e206eb36cb797&t=63133c4f
# 05_带着联结设限 205
# https://mps-trans.yzcdn.cn/multi_trans_hls_fhd/y8z8eejNKWgWLV24GAFiacpMnFBH1iQV_HD_$f.ts?sign=809d74c9d7d267d68330bff8486ad2ba&t=63133c97
# 06_重新定义问题行为 181
# https://mps-trans.yzcdn.cn/multi_trans_hls_fhd/piYZQF73rIJOPmLFVzW3wY9SPqJ3-ZsH_HD_$f.ts?sign=3bce4fe2cddafc7718f6b953ff6fbbb7&t=63133ce0
# 07_内在功课与相互支持 114
# https://mps-trans.yzcdn.cn/multi_trans_hls_fhd/_gxVdFcErG_DjSUjGpZ4nFUdW81N_OpF_HD_$f.ts?sign=9a7092a0ab516f5f99b2b3b419706576&t=63133d1c
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output
a="1001"

for f in {0..114};
do 
    j=$(printf "%03d" $f)
    wget "https://mps-trans.yzcdn.cn/multi_trans_hls_fhd/_gxVdFcErG_DjSUjGpZ4nFUdW81N_OpF_HD_$f.ts?sign=9a7092a0ab516f5f99b2b3b419706576&t=63133d1c" -O ./$j.ts ;
    sleep 1;
done

rm -rf list.txt
for f in *.ts;
do 
    echo "file '$PWD/$f'">>list.txt;
done

ffmpeg -y -f concat -safe 0 -i list.txt -c copy $1/output/all.mp4