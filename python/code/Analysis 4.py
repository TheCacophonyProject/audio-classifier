#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 14:10:02 2019

@author: tim
"""

import librosa.display
import sounddevice as sd
import numpy as np
import pandas as pd 
import pylab
import os

#tags_input_folder = './sorted_squawks/morepork/tags_created_on_server/'
tags_input_folder = './sorted_squawks/unknown/'
audio_files_folder = './downloaded_recordings/fpF7B9AFNn6hvfVgdrJB/night_recording/'
images_out_folder = './images/unknown/'

for filename in os.listdir(tags_input_folder):
    print(filename)
    
    recording_id = filename.split("_")[0]
    
    start_time_with_ext = filename.split("_")[1]
    start_time_seconds = start_time_with_ext.split(".")[0] + '.' + start_time_with_ext.split(".")[1]
    duration_seconds = 1.5 
    
#    print(recording_id)
#    print(start_time_seconds)
    
    audio_in_path = audio_files_folder + recording_id + '.m4a'
    image_out_path = images_out_folder + recording_id + '_' + start_time_seconds + '.jpg'
#    print('image_out_path ', image_out_path)
    y, sr = librosa.load(audio_in_path, sr=None) 
#    librosa.display.waveplot(y, sr=sr)
#    print('sr ', sr)
    
    
#    print('start_time_seconds ', start_time_seconds)
    start_time_seconds_float = float(start_time_seconds)
#    print('start_time_seconds_float ', start_time_seconds_float)
    
    start_position_array = int(sr * start_time_seconds_float)
    
#    print('start_position_array ', start_position_array)
    
#    clip_start_array = int((sr * start_time_seconds))
    
    
    end_position_array = start_position_array + int((sr * duration_seconds))
               
    if end_position_array > y.shape[0]:
        print('Clip would end after end of recording')
        continue
        
    y_part = y[start_position_array:end_position_array]  
    mel_spectrogram_800_1000_freq = librosa.feature.melspectrogram(y=y_part, sr=sr, n_fft=int(sr/10), hop_length=int(sr/10), n_mels=10, fmin=800,fmax=1000)
    
    pylab.axis('off') # no axis
    pylab.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[]) # Remove the white edge
    librosa.display.specshow(mel_spectrogram_800_1000_freq)
    pylab.savefig(image_out_path, bbox_inches=None, pad_inches=0)
    pylab.close()
    
  
#    break
    