#!/usr/local/bin/python3

import wave
import requests
import json

def get_token():
    apiKey = "kG4V754LHNowhl1M0hsO8cZt"
    secretKey = "pavzHEY1KDam1M411mqMxr8q903lIrV7"

    auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + apiKey + "&client_secret=" + secretKey
    print(auth_url)
    response = requests.get(url=auth_url)
    jsondata = response.text
    return json.loads(jsondata)['access_token']

def use_cloud(token, wavefile):
    fp = wave.open(wavefile, 'rb')
    # 已经录好音的音频片段内容
    nframes = fp.getnframes()
    filelength = nframes*2
    audiodata = fp.readframes(nframes)

    # 百度语音接口的产品ID
    cuid = '71XXXX663'
    server_url = 'http://vop.baidu.com/server_api' + '?cuid={}&token={}'.format(cuid, token)
    headers = {
        'Content-Type': 'audio/pcm; rate=8000',
        'Content-Length': '{}'.format(filelength),
    }

    response = requests.post(url=server_url, headers=headers, data=audiodata)
    return response.text if response.status_code==200 else 'Something Wrong!'



if __name__ == '__main__':
    access_token = get_token()
    print(access_token)
    result = use_cloud(token=access_token, wavefile='./tq.wav')
    # result = use_cloud(token=access_token, wavefile='/Users/zhuxu/Downloads/20180327_专家聊天气.wav')
    print(result)



