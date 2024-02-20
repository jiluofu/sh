#!/bin/bash


for f in *;
do echo "file '$PWD/$f'";echo "name '$f'";

for f1 in $PWD/$f/*.m4a;
do echo "file1 '$f1'";
done
# 删除输出目录，重建
rm -rf $PWD/$f/output
mkdir $PWD/$f/output
ffmpeg -y -f concat -safe 0 -i <(for ff in $PWD/$f/*.m4a; do echo "file '$ff'"; done) -c copy $PWD/$f/output/$f.m4a

done






