
# 删除输出目录，重建
rm -rf $1/output
rm -rf $1/output1
mkdir $1/output
mkdir $1/output1

for i in $1/*.WAV
do

# ffmpeg -y -i $i -filter:a "volume=1dB" $1/output1/$i


ffmpeg -y -i $i -ss 00:00:01.00 -t 00:00:02.00 noiseSample.wav

sox $1/noiseSample.wav -n noiseprof noisepf.prof
sox $i $1/output1/$i noisered noisepf.prof 0.21
# rm -rf noise*.*
ffmpeg -y -i $1/output1/$i -af loudnorm=I=-16:LRA=6:tp=-1 $1/output/$i
done
rm -rf output1



