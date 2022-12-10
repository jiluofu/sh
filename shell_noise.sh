
# 删除输出目录，重建
rm -rf $1/output
rm -rf $1/output1
mkdir $1/output
mkdir $1/output1

for i in $1/*.WAV
do

ffmpeg -y -i $i -filter:a "volume=1dB" $1/output1/$i

ffmpeg -y -i $1/output1/$i -ss 00:00:00.70 -t 00:00:01.70 noiseSample.wav

sox $1/noiseSample.wav -n noiseprof noisepf.prof
sox $1/output1/$i $1/output/$i noisered noisepf.prof 0.21
rm -rf noise*.*
done
rm -rf output1



