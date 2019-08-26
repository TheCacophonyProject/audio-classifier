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
import ast
import json

#device_name = '0070_v1_3_6'
device_name = 'fpF7B9AFNn6hvfVgdrJB'
sorted_squawks_folder = './sorted_squawks/'
squawks_input_folder = './squawks_from_filtered_recordings/' + device_name + '/'
squawks_processed_folder = './squawks_from_filtered_recordings/' + device_name + '/' + 'processed_squawks/'
audio_input_folder = './filtered_recordings/' + device_name + '/' + 'night_recording/processed_recordings/'
morepork_folder = sorted_squawks_folder + 'morepork/'
duck_folder = sorted_squawks_folder + 'duck/'
not_morepork_folder = sorted_squawks_folder + 'not_morepork/'
unknown_folder = sorted_squawks_folder + 'unknown/' # going to tag this as unknown
noise_folder = sorted_squawks_folder + 'noise/' # going to tag this as unknown
not_used_more_than_20_squawks_folder = squawks_processed_folder + 'not_used_more_than_20_squawks' + '/'

what = 'more pork - classic'
duration = 1.5

print('squawks_input_folder ', squawks_input_folder)
finish = False

if not os.path.exists(sorted_squawks_folder):
        os.makedirs(sorted_squawks_folder)
        
if not os.path.exists(morepork_folder):
        os.makedirs(morepork_folder)
        
if not os.path.exists(duck_folder):
        os.makedirs(duck_folder)        
  
if not os.path.exists(unknown_folder):
        os.makedirs(unknown_folder)
        
if not os.path.exists(noise_folder):
        os.makedirs(noise_folder)
        
if not os.path.exists(squawks_processed_folder):
        os.makedirs(squawks_processed_folder)
        


#for filename in os.listdir(squawks_input_folder):
with os.scandir(squawks_input_folder) as entries:
    for entry in entries:       
        if entry.is_file():
            filename = entry.name
        else:
            continue        
        
        recordingId = os.path.splitext(filename)[0]
        squawk_in_path = squawks_input_folder + filename
        squawk_processed_path = squawks_processed_folder + filename
        with open(squawk_in_path, 'r') as f:
            squawks = ast.literal_eval(f.read())
        
        if len(squawks) > 20:
            squawk_processed_path = not_used_more_than_20_squawks_folder + filename
            os.rename(squawk_in_path, squawk_processed_path)
            continue
        audio_in_path = audio_input_folder + recordingId + '.wav'
        print('audio_in_path', audio_in_path)
        y, sr = librosa.load(audio_in_path, sr=None) 
        y_amplified = np.int16(y/np.max(np.abs(y)) * 32767)
        
        for squawk in squawks:
            
            y_amplified_start = sr * squawk
            y_amplified_end = (sr * squawk) + (sr * 1.5)
            y_amplified_to_play = y_amplified[int(y_amplified_start):int(y_amplified_end)]
            y_to_display = y[int(y_amplified_start):int(y_amplified_end)]
                
            repeat = True
            
            while repeat:
                print('Squawk start time is ', squawk)
                sd.play(y_amplified_to_play, sr)
                print('Recording ', recordingId)
                librosa.display.waveplot(y_to_display, sr=sr)
                plt.show()
                # https://librosa.github.io/librosa/generated/librosa.display.specshow.html
                D = librosa.amplitude_to_db(np.abs(librosa.stft(y_to_display)), ref=np.max)
                librosa.display.specshow(D, y_axis='linear')
                plt.colorbar(format='%+2.0f dB')
                plt.title('Linear-frequency power spectrogram')
                plt.show()
                reply = input("What is this (m (classic morepork), d (duck), u (unknown), n (noise), enter (to play again), p (play original 1 minute recording), or x to exit)? ")
                if reply == 'm':
                    print('pressed m')
                    squawk_json_m = {
                            "origin": recordingId,
                            "start_secs": squawk,
                            "what": "more pork - classic",
                            "duration": 1.5}
                    
                    morepork_squawk_out_path = morepork_folder +  recordingId + '_' + str(squawk) + '.json'
                    print('morepork_squawk_out_path ', morepork_squawk_out_path)               
    
                    with open(morepork_squawk_out_path, 'w') as f:
                        json.dump(squawk_json_m, f, ensure_ascii=False) 
    
                    repeat = False
                    
                if reply == 'd': # duck
                    print('pressed d')
                    squawk_json_d = {
                        "origin": recordingId,
                        "start_secs": squawk,
                        "what": "duck",
                        "duration": 1.5}
                    
                    duck_squawk_out_path = duck_folder + recordingId + '_' + str(squawk) + '.json'
                    print('duck_squawk_out_path ', duck_squawk_out_path)
    
                    with open(duck_squawk_out_path, 'w') as f:
                        json.dump(squawk_json_d, f, ensure_ascii=False)
                        
                    repeat = False
                    
                if reply == 'u': # duck
                    print('pressed u')
                    squawk_json_u = {
                        "origin": recordingId,
                        "start_secs": squawk,
                        "what": "unknown",
                        "duration": 1.5}
                    
                    unknown_squawk_out_path = unknown_folder + recordingId + '_' + str(squawk) + '.json'
                    print('unknown_squawk_out_path ', unknown_squawk_out_path)
                    with open(unknown_squawk_out_path, 'w') as f:
                        json.dump(squawk_json_u, f, ensure_ascii=False)
       
                    repeat = False
                    
                if reply == 'n': # noise
                    print('pressed n')
                    squawk_json_n = {
                        "origin": recordingId,
                        "start_secs": squawk,
                        "what": "noise",
                        "duration": 1.5}
                    noise_squawk_out_path = noise_folder + recordingId + '_' + str(squawk) + '.json'
                    
                    with open(noise_squawk_out_path, 'w') as f:
                        json.dump(squawk_json_n, f, ensure_ascii=False)
                    
                
                    repeat = False           
                
                
                elif reply == 'x':
                    print('Exiting')
                    repeat = False
                    finish = True
                elif reply == 'p': # play from the original recording
       
                    recording_id = recordingId
                    print('recording_id is ', recording_id)
                    filename_of_full_recording  = recording_id + '.m4a'
                    audio_in_path_to_full_recording = './' + parameters.downloaded_recordings_folder + '/' + device_name + '/night_recording/' + filename_of_full_recording
                    y_original, sr_original = librosa.load(audio_in_path_to_full_recording, sr=None)
                    
                    y_amplified_original = np.int16(y_original/np.max(np.abs(y_original)) * 32767)
                    y_amplified_to_play_original = y_amplified_original[int(y_amplified_start):int(y_amplified_end)]
                    sd.play(y_amplified_to_play_original, sr_original)
                    
                    input('Press any key to continue ')
                    
                else:
                    print('going to replay the same recording')
                
                    
            if finish:
                # 
                break
    #    print('squawk_in_path ', squawk_in_path,'\n') 
    #    print('squawk_processed_path ', squawk_processed_path,'\n') 
        os.rename(squawk_in_path, squawk_processed_path)
print('All squawk files have been processed')






