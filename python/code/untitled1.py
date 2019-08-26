#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 11:11:48 2019

@author: tim
"""

import numpy as np
import IPython.display as ipd
import librosa
import matplotlib.pyplot as plt
import librosa.display

y, sr = librosa.load(librosa.util.example_audio_file())
D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
#plt.subplot(4, 2, 1)
librosa.display.specshow(D, y_axis='linear')
plt.colorbar(format='%+2.0f dB')
plt.title('Linear-frequency power spectrogram')