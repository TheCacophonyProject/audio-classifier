#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 10:16:13 2019

@author: tim
"""

# Generate a sound
#import numpy as np
#import IPython.display as ipd
#import librosa
#
##framerate = 44100
##t = np.linspace(0,5,framerate*5)
##data = np.sin(2*np.pi*220*t) + np.sin(2*np.pi*224*t)
#input_folder = './clips_from_filtered_recordings/'
#filename = '20190611161936_026_02278_153003.m4a'
#audio_in_path = input_folder + '/' + filename
#y, sr = librosa.load(audio_in_path, sr=None) 
##ipd.Audio( ,rate=framerate)
#ipd.Audio( y,rate=sr)

presidents =["a","b"]
for num, name in enumerate(presidents):
    print(name)