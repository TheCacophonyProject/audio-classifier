#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 10:16:13 2019

@author: tim
"""

import functions
import parameters
import numpy as np
import IPython.display as ipd
import librosa
import matplotlib.pyplot as plt
import librosa.display

import sounddevice as sd

import os
device_name = '0070_v1_3_6'
device_name = 'fpF7B9AFNn6hvfVgdrJB'
input_folder = './clips_from_filtered_recordings/' + device_name + '/'
morepork_folder = './sorted_clips/morepork/'
duck_folder = './sorted_clips/duck/'
not_morepork_folder = './sorted_clips/not_morepork/'
#not_sure_folder = './sorted_clips/not_sure_folder/'
unknown_folder = './sorted_clips/unknown_folder/' # going to tag this as unknown
noise_folder = './sorted_clips/noise_folder/' # going to tag this as unknown

what = 'more pork - classic'
duration = 1.5

print('input_folder ', input_folder)
finish = False

if not os.path.exists(morepork_folder):
        os.makedirs(morepork_folder)
        
if not os.path.exists(duck_folder):
        os.makedirs(duck_folder)        
  
if not os.path.exists(unknown_folder):
        os.makedirs(unknown_folder)
        
if not os.path.exists(noise_folder):
        os.makedirs(noise_folder)
        


for filename in os.listdir(input_folder):
    
    recordingId = filename.split("_")[0]
    start_time_with_ext = filename.split("_")[1]
    start_time = start_time_with_ext.split(".")[0]
    
   
    audio_in_path = input_folder + '/' + filename
   
#    y, sr = librosa.load(audio_in_path, sr=None) 
#    # https://stackoverflow.com/questions/10357992/how-to-generate-audio-from-a-numpy-array
#    y_amplified = np.int16(y/np.max(np.abs(y)) * 32767)
    
    repeat = True
    
    while repeat:
        y, sr = librosa.load(audio_in_path, sr=None) 
        # https://stackoverflow.com/questions/10357992/how-to-generate-audio-from-a-numpy-array
        y_amplified = np.int16(y/np.max(np.abs(y)) * 32767)
        sd.play(y_amplified, sr)
        print('Recording ', filename)
        librosa.display.waveplot(y, sr=sr)
        plt.show()
        # https://librosa.github.io/librosa/generated/librosa.display.specshow.html
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        librosa.display.specshow(D, y_axis='linear')
        plt.colorbar(format='%+2.0f dB')
        plt.title('Linear-frequency power spectrogram')
        plt.show()
        reply = input("Is this a Morepork (y (yes), d (duck), u (unknown), n (noise), enter (to play again), p (play original 1 minute recording), or x to exit)? ")
        if reply == 'y':
            print('pressed y')
            audio_out_path = morepork_folder + '/' + filename
            os.rename(audio_in_path, audio_out_path)            
            functions.add_tag_to_server(recordingId, what='more pork - classic', startTime=start_time, duration=duration)
            repeat = False
            
        if reply == 'd': # duck
            print('pressed d')
            audio_out_path = duck_folder + '/' + filename
            os.rename(audio_in_path, audio_out_path)            
            functions.add_tag_to_server(recordingId, what='duck', startTime=start_time, duration=duration)            
            repeat = False
            
        if reply == 'u': # duck
            print('pressed u')
            audio_out_path = unknown_folder + '/' + filename
            os.rename(audio_in_path, audio_out_path)            
            functions.add_tag_to_server(recordingId, what='unknown', startTime=start_time, duration=duration)            
            repeat = False
            
        if reply == 'n': # noise
            print('pressed n')
            audio_out_path = noise_folder + '/' + filename
            os.rename(audio_in_path, audio_out_path)            
            functions.add_tag_to_server(recordingId, what='noise', startTime=start_time, duration=duration)            
            repeat = False           
        
        
        elif reply == 'x':
            print('Exiting')
            repeat = False
            finish = True
        elif reply == 'p': # play the whole original 1 minute recording
#            print('filename is ', filename)
            recording_id = filename.split('_')[0]
            print('recording_id is ', recording_id)
            filename_of_full_recording  = recording_id + '.m4a'
            audio_in_path_to_full_recording = './' + parameters.downloaded_recordings_folder + '/' + device_name + '/night_recording/' + filename_of_full_recording
            y, sr = librosa.load(audio_in_path_to_full_recording, sr=None)
            y_amplified = np.int16(y/np.max(np.abs(y)) * 32767)
            sd.play(y_amplified, sr)
            input('Press any key to continue ')
            
        else:
            print('going to replay the same recording')
            
    if finish:
        break








