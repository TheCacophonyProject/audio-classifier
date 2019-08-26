#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 14:01:00 2019

@author: tim
"""

print('hello world')

import os
from python_speech_features import mfcc, logfbank
import librosa as librosa

signal, rate = librosa.load('wavfiles/153035_more pork - classic_11.66.wav', sr=None)

print('signal ', signal)