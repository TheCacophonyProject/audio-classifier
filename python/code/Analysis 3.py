#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 14:01:00 2019

@author: tim
"""

print('hello world')

from python_speech_features import mfcc, logfbank
import librosa as librosa
import librosa.display
import sounddevice as sd
import numpy as np
import pandas as pd 
import pylab




y, sr = librosa.load('wavfiles/153035_more pork - classic_11.66.wav', sr=None)
#y, sr = librosa.load('temp/161960.wav', sr=None)

#mel = mfcc(signal[:rate], rate, numcep=13, nfilt=26, nfft=1103).T
#
#
#print('signal ', signal)
#print('mel ', mel)
#
#melT = mfcc(signal[:rate], rate, numcep=13, nfilt=26, nfft=1103)
#
#print('melT ', melT)

print('sr ', sr)

#y_1_5_sec = y[0:int(sr*1.5)]
y_1_5_sec = y[0:int(sr)]
#y_amplified = np.int16(y_1_5_sec/np.max(np.abs(y)) * 32767)
#sd.play(y_amplified, sr)
sd.play(y_1_5_sec, sr)
#print('y_1_5_sec shape ', y_1_5_sec.shape)
# http://conference.scipy.org/proceedings/scipy2015/pdfs/brian_mcfee.pdf
# https://librosa.github.io/librosa/generated/librosa.feature.melspectrogram.html#librosa.feature.melspectrogram
# https://librosa.github.io/librosa/generated/librosa.filters.mel.html#librosa.filters.mel
#mel_spectrogram_all_freq = librosa.feature.melspectrogram(y=y, n_mels=10)
#mel_spectrogram_800_1000_freq = librosa.feature.melspectrogram(y=y_1_5_sec, n_mels=10, fmin=800,fmax=1000)

mel_spectrogram_800_1000_freq = librosa.feature.melspectrogram(y=y_1_5_sec, sr=sr, n_fft=int(sr/10), hop_length=int(sr/10), n_mels=10, fmin=800,fmax=1000)
#
#print('mel_spectrogram ', mel_spectrogram)

#librosa.display.specshow(mel_spectrogram_all_freq)
#https://stackoverflow.com/questions/46031397/using-librosa-to-plot-a-mel-spectrogram
pylab.axis('off') # no axis
pylab.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[]) # Remove the white edge
librosa.display.specshow(mel_spectrogram_800_1000_freq)
pylab.savefig('tim.jpg', bbox_inches=None, pad_inches=0)
pylab.close()

#a = np.array([[1,2,3], [4,5,6]])
#print('a ', a)
#f = a.flatten()
#print('f ', f)

print(mel_spectrogram_800_1000_freq.shape)

mel_spectrogram_800_1000_freq_flattend = mel_spectrogram_800_1000_freq.flatten()
mel_spectrogram_800_1000_freq_flattend_labelled = np.append(mel_spectrogram_800_1000_freq_flattend, 0)

#print(mel_spectrogram_800_1000_freq_flattend.shape)
#print(mel_spectrogram_800_1000_freq_flattend)
#print(mel_spectrogram_800_1000_freq_flattend_labelled)

#np.savetxt(fname='tim_np.csv',X=mel_spectrogram_800_1000_freq_flattend,delimiter=',')
#np.savetxt('tim_np.csv',mel_spectrogram_800_1000_freq_flattend[None], delimiter=',')
#pd.DataFrame(mel_spectrogram_800_1000_freq_flattend).to_csv('tim_pd.csv')

np.savetxt('tim_np.csv',mel_spectrogram_800_1000_freq_flattend_labelled[None], delimiter=',')
#save_path = 'test.jpg'
#
#pylab.axis('off') # no axis
#pylab.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[]) # Remove the white edge
##S = librosa.feature.melspectrogram(y=sig, sr=fs)
#librosa.display.specshow(librosa.power_to_db(mel_spectrogram_800_1000_freq_flattend, ref=np.max))
#pylab.savefig(save_path, bbox_inches=None, pad_inches=0)
#pylab.close()
