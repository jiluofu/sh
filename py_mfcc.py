#!/usr/local/bin/python3

# from python_speech_features import mfcc
# from python_speech_features import delta
# from python_speech_features import logfbank
# import scipy.io.wavfile as wav

# (rate,sig) = wav.read('noise.wav')
# mfcc_feat = mfcc(sig,rate)
# d_mfcc_feat = delta(mfcc_feat, 2)
# fbank_feat = logfbank(sig,rate)

# print(fbank_feat[1:3,:])

# (rate,sig) = wav.read('tq.wav')
# mfcc_feat = mfcc(sig,rate)
# d_mfcc_feat = delta(mfcc_feat, 2)
# fbank_feat = logfbank(sig,rate)

# print(fbank_feat[1:3,:])

import sys

import librosa
import matplotlib.pyplot as plt
from dtw import dtw
from numpy.linalg import norm

if len(sys.argv) == 2 and sys.argv[1] != '':
    tqname = 'tq' + sys.argv[1]
else:
    tqname = 'tq'


#Loading audio files
y1, sr1 = librosa.load('zj.wav') 
y2, sr2 = librosa.load(tqname + '.wav') 

#Showing multiple plots using subplot
plt.subplot(1, 2, 1) 
mfcc1 = librosa.feature.mfcc(y1,sr1)   #Computing MFCC values
# librosa.display.specshow(mfcc1)

plt.subplot(1, 2, 2)
mfcc2 = librosa.feature.mfcc(y2, sr2)
# librosa.display.specshow(mfcc2)

# dist, cost, path = dtw(mfcc1.T, mfcc2.T)
dist, cost, acc_cost, path = dtw(mfcc1.T, mfcc2.T, dist=lambda x, y: norm(x - y, ord=1))
print("The normalized distance between the two : ",dist)   # 0 for similar audios 

# plt.imshow(cost.T, origin='lower', cmap=plt.get_cmap('gray'), interpolation='nearest')
# plt.plot(path[0], path[1], 'w')   #creating plot for DTW

# plt.show()  #To display the plots graphically


