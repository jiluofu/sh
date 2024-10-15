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
    "https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/018d25833270835009805312598/drm/v.f421220.m3u8?sign=79c24f2d40b167fb5f9415a3f317b420&t=66df0c4c&us=ewSJESBuZD" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/49ee8b953270835009806121153/drm/v.f421220.m3u8?sign=5b361e619a7a1b3d7268673b31b161a7&t=66df0c65&us=fdMGfvMdPA" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/0d3766d93270835009805813024/drm/v.f421220.m3u8?sign=e43689ca8c423ebb3cd99d2f6ae6c457&t=66df0c75&us=GYTSjxiYBw" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/4a4ab3413270835009806174319/drm/v.f421220.m3u8?sign=8b351b5bb9282c5d787ec9a9202d94d1&t=66df0c87&us=EKxzQHJXBR" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/0da37ac83270835009805872367/drm/v.f421220.m3u8?sign=b3b45155240e392bcb6693325f4cd0e9&t=66df0c96&us=CVbWdVbAbG" \
"https://v-tos-k.xiaoeknow.com/529d8d60vodtransbj1252524126/af1546b23270835009203422560/drm/v.f421220.m3u8?sign=2c86c5b2bcfd5d360c6ca0496bc7d08e&t=66df0cad&us=OxnIkvIQxQ" \
"https://v-tos-k.xiaoeknow.com/529d8d60vodtransbj1252524126/85468e413270835009223327767/drm/v.f421220.m3u8?sign=f898c932af163b43c7368c89383e572d&t=66df0cd0&us=htJWuWOEOi" \
"https://v-tos-k.xiaoeknow.com/529d8d60vodtransbj1252524126/e6ef8c373270835009221166452/drm/v.f421220.m3u8?sign=c2dc2be9768c6383936b85eeed1ee11d&t=66df0ce3&us=kRkOrEfpPg" \
"https://v-tos-k.xiaoeknow.com/529d8d60vodtransbj1252524126/f0be99f93270835009245026345/drm/v.f421220.m3u8?sign=ee29fcf1eadd835df919c97410143718&t=66df0cf5&us=JnJyKKLLQt" \
"https://v-tos-k.xiaoeknow.com/529d8d60vodtransbj1252524126/039f49453270835009245858506/drm/v.f421220.m3u8?sign=110c6f40bf8c2bf7fdc41d021eeda4c0&t=66df0d09&us=XcOyvYPmnn" \
"https://v-tos-k.xiaoeknow.com/529d8d60vodtransbj1252524126/bb6aa41c3270835009305358703/drm/v.f421220.m3u8?sign=053e45a399a495641475eb213989aaa4&t=66df0d21&us=jWeFKPSnuQ" \
"https://v-tos-k.xiaoeknow.com/529d8d60vodtransbj1252524126/2ab5ef1c3270835009303743572/drm/v.f421220.m3u8?sign=a685b3e633354fada8f640f61cdbc796&t=66df0d2f&us=cqizHTTQtH" \
"https://v-tos-k.xiaoeknow.com/529d8d60vodtransbj1252524126/d43c87ad3270835009336669972/drm/v.f421220.m3u8?sign=fd2d13f77f05f66add0e5be908503a85&t=66df0d4b&us=ZhDqTAXKKF" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/64f3c4a63270835009362647826/drm/v.f421220.m3u8?sign=af4bca6ad4798fa8d748cb8a404d8cef&t=66df0d68&us=QhPEtjJveQ" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/78a56ab03270835009386982369/drm/v.f421220.m3u8?sign=ddf7d16991675fac3ca6192cb3e47d6c&t=66df0d7c&us=jjBcvaCIzb" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/b2c14b693270835009387154982/drm/v.f421220.m3u8?sign=7786afa46e603e49cce517e1fb1c9d19&t=66df0d8d&us=SRjKZpFtGd" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/7f7f5c653270835009406499425/drm/v.f421220.m3u8?sign=5ffbfa39cc487e496b539094a3211363&t=66df0da1&us=SVKWSeqIhL" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/3d85abc63270835009477281762/drm/v.f421220.m3u8?sign=73edd65fdc69aa54005ef815cc00a2a2&t=66df0dc0&us=RYQDCXMpdY" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/3ac69c5a3270835009477126311/drm/v.f421220.m3u8?sign=746e3abf74e499b86cc1e225c2e12466&t=66df0dd5&us=yEIRAICxOH" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/f964057d3270835009476616014/drm/v.f421220.m3u8?sign=f7899dcb87270e6873a55fafe22a81f3&t=66df0de7&us=OFwKYBzRlL" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/64cc48cb3270835009498309358/drm/v.f421220.m3u8?sign=db7633ff7d93ec8fe2e230c8727b3cce&t=66df0e01&us=qzwHemlwOP" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/b6fe65ce3270835009499583851/drm/v.f421220.m3u8?sign=a1987302e6ec23905f1f678454663f86&t=66df0e13&us=xXquSlPWxv" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/81c356e13270835009525580329/drm/v.f421220.m3u8?sign=bf09c1edaa217e1c30a4972915302c91&t=66df0e2e&us=XHdFObXcoH" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/d802f5ac3270835009526975970/drm/v.f421220.m3u8?sign=085347e155f044e67fdf9275a76d4911&t=66df0e42&us=RKQpfUyYOR" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/119d2b403270835009544731428/drm/v.f421220.m3u8?sign=156011eebd0c5aee52a1c4acc6b2fcd6&t=66df0e56&us=FXjSzsodpG" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/c98389423270835009543961426/drm/v.f421220.m3u8?sign=73585a501504d2483987823c643b6b12&t=66df0e6d&us=MltxIuwDJP" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/946d16003270835009570129617/drm/v.f421220.m3u8?sign=d5c8f7a5941a3839187fd57e2fb65016&t=66df0e81&us=tDGrujTmBt" \
"https://v-tos-k.xiaoeknow.com/9764a7a5vodtransgzp1252524126/68b1236c3270835009569635961/drm/v.f421220.m3u8?sign=37f61b55c9d6c61333d95b01e09a1ba0&t=66df0e91&us=PWQotnFGhl"
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