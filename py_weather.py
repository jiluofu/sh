#!/usr/local/bin/python3

import sys
import subprocess
import re

import librosa
# import tkinter
# import matplotlib.pyplot as plt
from dtw import dtw
from numpy.linalg import norm

arr = [
	'20180203',
	'20180205',
	'20180207',
	'20180208',
	'20180210',
	'20180211',
	'20180304',
	'20180305',
	'20180306',
	'20180311',
	'20180312',
	'20180313',
	'20180314',
	'20180315',
	'20180316',
	'20180317',
	'20180320',
	'20180321',
	'20180322',

]

# arr = [
# 	'20180207',
# 	'20180314',
# 	'20180322',

# ]

arr = ['20180328']

path = '/Users/zhuxu/Downloads'
# path = '/home/zhuxu/mmjs_server/gohttps_loader/static/weather'

def getDistance(model, sample):
	
	#print(model)
	#print(sample)
	
	#Loading audio files
	y1, sr1 = librosa.load(model) 
	y2, sr2 = librosa.load(sample) 

	#Showing multiple plots using subplot
	# plt.subplot(1, 2, 1) 
	mfcc1 = librosa.feature.mfcc(y1,sr1)   #Computing MFCC values
	# librosa.display.specshow(mfcc1)

	# plt.subplot(1, 2, 2)
	mfcc2 = librosa.feature.mfcc(y2, sr2)
	# librosa.display.specshow(mfcc2)

	# dist, cost, path = dtw(mfcc1.T, mfcc2.T)
	dist, cost, acc_cost, path = dtw(mfcc1.T, mfcc2.T, dist=lambda x, y: norm(x - y, ord=1))
	# print("The normalized distance between the two : ",dist)   # 0 for similar audios 

	# plt.imshow(cost.T, origin='lower', cmap=plt.get_cmap('gray'), interpolation='nearest')
	# plt.plot(path[0], path[1], 'w')   #creating plot for DTW

	# plt.show()  #To display the plots graphically

	return dist

def getSecPos(date, title, modelName, modelSecLength, searchStart = 0, searchEnd = 80):

	
	distArr = []
	distDict = {}

	stopAfterNum = 5
	closeToTarget = False

	for i in range(searchStart, searchEnd, 3):
		sampleName = path + '/wout/' + date + '_' + title + str(i) + '.wav'
		subprocess.check_output('ffmpeg -loglevel quiet -y -i ' + path + '/' + date + '_专家聊天气.wav -ss ' + str(i) + ' -to ' + str(i + modelSecLength) + '  -f wav ' + sampleName, shell=True)
		dist = getDistance(modelName, sampleName)
		distArr.append(dist)
		distDict[dist] = i
		# print(min(distArr))
		print('sec:' + str(i) + ',dist:' + str(dist))
		if min(distArr) < 80:
			closeToTarget = True
		if closeToTarget:
			if stopAfterNum == 0:
				break
			else:
				stopAfterNum = stopAfterNum - 1
	distMin = min(distArr)
	print('min dist:' + str(distMin))
	print('min sec:' + str(distDict[distMin]))

	#a = subprocess.check_output('rm -rf ' + path + '/wout/*', shell=True)
	return distDict[distMin]

def getWeather(date):

	# a = subprocess.check_output('./shell_down_weather.sh ' + date, shell=True)
	a = subprocess.check_output('rm -rf ' + path + '/wout/*', shell=True)
	secTq = getSecPos(date, '天气预报', './model_tq.wav', 9, 20) + 1
	output(date, secTq, 400, '天气预报')

	secZj = getSecPos(date, '专家聊天气', './model_zhuanjia.wav', 12, secTq + 9 + 20, secTq + 9 + 30 + 200)
	output(date, secZj, 350, '专家聊天气')
	
def output(date, secStart, secLength, name):

	outputName = path + '/output/' + date + '_' + name + '.wav'
	outputNameMp3 = path + '/output/' + date + '_' + name + '.mp3'
	subprocess.check_output('ffmpeg -loglevel quiet -y -i ' + path + '/' + date + '_专家聊天气.wav -ss ' + str(secStart) + ' -to ' + str(secStart + secLength) + '  -f wav ' + outputName, shell=True)
	subprocess.check_output('ffmpeg -loglevel quiet -y -i ' + path + '/' + date + '_专家聊天气.wav -ss ' + str(secStart) + ' -to ' + str(secStart + secLength) + '  -f mp3 ' + outputNameMp3, shell=True)
	title = date + '_' + name
	# subprocess.check_output('nohup echo ' + title + ' | mailx -s ' + title + ' -a ' + outputNameMp3 + '  1077246@qq.com &', shell=True)
	


if len(sys.argv) == 2 and sys.argv[1] != '':
	getWeather(sys.argv[1])
else:
	for i in range(0, len(arr)):
		getWeather(arr[i])


