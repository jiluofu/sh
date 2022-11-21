
# 删除输出目录，重建
rm -rf $1/output
mkdir $1/output

for i in $1/*.WAV
do
ffmpeg -y -i $i -ss 00:00:00.70 -t 00:00:01.10 noiseSample.wav

sox $1/noiseSample.wav -n noiseprof noisepf.prof
sox $i $1/output/$i noisered noisepf.prof 0.21
rm -rf noise*.*
done



