#!/usr/local/bin/python3

import sys
import subprocess
import re

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

# arr = ['20180320']

path = '~/Downloads'
def getWeather(date):

	# a = subprocess.check_output('./shell_down_weather.sh ' + date, shell=True)
	a = subprocess.check_output('rm -rf ' + path + '/noise.prof', shell=True)
	a = subprocess.check_output('sox ' + path + '/noise.wav -n noiseprof ' + path + '/noise.prof', shell=True)
	a = subprocess.check_output('rm -rf ' + path + '/tianqi_clean.wav', shell=True)
	a = subprocess.check_output('sox ' + path + '/' + date + '_专家聊天气.wav ' + path + '/tianqi_clean.wav noisered ' + path + '/noise.prof 0.3', shell=True)
	a = subprocess.check_output('aubioquiet ' + path + '/tianqi_clean.wav', shell=True)

	print(str(a))
	out = []
	pos = re.findall(r"NOISY: ([\d\.]{1,})", str(a))
	for i in range(0, len(pos)):
		sec = float(pos[i])
		if i > 0:
			if sec - float(pos[i - 1]) >= 10 and sec - float(pos[i - 1]) <= 14:
				print(sec)
				print(sec - float(pos[i - 1]))
				out.append(str(sec))

	for i in range(0, len(out)):
		subprocess.check_output('ffmpeg -y -i ' + path + '/' + date + '_专家聊天气.wav -ss ' + out[i] + ' -to ' + str(float(out[i]) + 200) + '  -f wav ' + path + '/wout/' + date + '_专家聊天气' + str(i) + '.wav', shell=True)
		if i == 1:
			break

if len(sys.argv) == 2 and sys.argv[1] != '':
	getWeather(sys.argv[1])
else:
	for i in range(0, len(arr)):
		getWeather(arr[i])




