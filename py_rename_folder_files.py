#!/usr/local/bin/python3

import sys
import os
import re

srcPath = '/Users/zhuxu/Documents/tmp/src'
targetPath = '/Users/zhuxu/Documents/tmp/target'

def copyName(srcPath, targetPath):
	if len(os.listdir(srcPath)) != len(os.listdir(targetPath)):
		print(targetPath + '文件数和源目录不一致')
		return

	srcArr = os.listdir(srcPath)
	srcArr.sort()
	targetArr = os.listdir(targetPath)
	targetArr.sort()
	for i in range(0, len(srcArr)):
		# print(srcArr[i])
		# print(targetArr[i])
		srcPre = re.sub(r'^(Friends)\.S([\d]*)E([\d]*)(\.[^\.]+)+$', '\\2\\3', srcArr[i])
		targetPre = re.sub(r'^(friends)\.s([\d]*)e([\d]*)(\.[^\.]+)+$', '\\2\\3', targetArr[i])
		if srcPre != targetPre:
			print(srcPre + '不一致')
			break
		os.rename(targetPath + os.path.sep + targetArr[i], targetPath + os.path.sep + srcArr[i])
		print(targetPath + os.path.sep + srcArr[i])

copyName(srcPath, targetPath)










