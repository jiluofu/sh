# ffmpeg -i "https://vodtest1.cretech.cn/10C201_00093F/index.m3u8" -vcodec copy -acodec copy -absf aac_adtstoasc output.mp4

# 删除输出目录，重建
output="$1/output_m3u8"
rm -rf $output
mkdir $output

# array=(
#     "https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/24fbd6063270835009232389836/drm/v.f421220.m3u8?sign=81a2bc2363e270655a2477e7c70b9adc&t=66d5c8cf&us=CcCvhmAMVY" \
#     "https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/1dc3dcbc3270835009232055728/drm/v.f421220.m3u8?sign=8a6567daa0b0fa5f0e1b4868d72fc43d&t=66d5cf5a&us=zzKfhLQCfv"
#     )
array=(
    "https://vod-plus.fjtv.net/video/2025/10/22/71b4ab19a9f7633a94a3ea368ca470c0.m3u8" \
"https://vod-plus.fjtv.net/video/2025/10/24/b6320415cceabe59477c85624c6166fc.m3u8"
    )
index=1
for item in "${array[@]}"
do
    # printf "%d:%s\n" "$index" "$item"
    num=$(printf "%02d" "$index")
    printf "%02d\n" "$num"
    cmd="ffmpeg -i \"$item\" -vcodec copy -acodec copy $output/$num..mp4"

    printf "%s\n" "$cmd"
    eval "$cmd"
    ((index++))
done