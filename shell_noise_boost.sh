
# 删除输出目录，重建
rm -rf $1/output
rm -rf $1/output1
mkdir $1/output
mkdir $1/output1

for i in $1/*.WAV
do

ffmpeg -y -i $i -filter:a "volume=9dB" $1/output1/$i

ffmpeg -y -ss 00:00:03 -to 00:03:07 -i $1/output1/$i $1/output/$i
# ffmpeg -y -ss 00:00:03 -to 00:08:17 -i $1/output1/$i -ab 320k $1/output/${i%.*}.m4a

# sox $1/noiseSample.wav -n noiseprof noisepf.prof
# sox $1/output1/$i $1/output/$i noisered noisepf.prof 0.21
# rm -rf noise*.*
done
rm -rf output1



