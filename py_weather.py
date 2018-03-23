#!/usr/local/bin/python3

import subprocess
import re

arr = [
	# '20180203',
	'20180323',
	# '20180205'
]

def getWeather(date):

	a = subprocess.check_output('./shell_down_weather.sh ' + date, shell=True)
	a = subprocess.check_output('rm -rf ~/Downloads/noise.prof', shell=True)
	a = subprocess.check_output('sox ~/Downloads/noise.wav -n noiseprof ~/Downloads/noise.prof', shell=True)
	a = subprocess.check_output('rm -rf ~/Downloads/tianqi_clean.wav', shell=True)
	a = subprocess.check_output('sox ~/Downloads/' + date + '_专家聊天气.wav ~/Downloads/tianqi_clean.wav noisered ~/Downloads/noise.prof 0.3', shell=True)
	a = subprocess.check_output('aubioquiet ~/Downloads/tianqi_clean.wav', shell=True)

	print(str(a))
	pos = re.findall(r"([\d\.]{1,})", str(a))
	for i in range(0, len(pos)):
		sec = float(pos[i])
		if i > 0:
			if sec - float(pos[i - 1]) >= 10 and sec - float(pos[i - 1]) <= 16:
				print(sec)
				print(sec - float(pos[i - 1]))
				subprocess.check_output('ffmpeg -y -i ~/Downloads/' + date + '_专家聊天气.wav -ss ' + pos[i] + ' -to ' + str(sec + 100) + '  -f wav ~/Downloads/' + date + '_' + pos[i] + '.wav', shell=True)

for i in range(0, len(arr)):
	getWeather(arr[i])




