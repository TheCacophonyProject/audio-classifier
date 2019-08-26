#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 30 17:20:38 2019

@author: tim
"""
import os
import librosa
import pickle
import parameters

def convert_wav_files_to_array_pickles():
    # Created this to covert all the wav files that came with the tutorial
    # to numpy arrays, so can test if this approach will work for clips 
    # created from recordings from Cacophony server ()
    wav_folder =  './wavfiles'
    
    for filename in os.listdir(wav_folder):
        try:
            print(filename)
            audio_in_path = './' + wav_folder + '/' + filename
            y, sr = librosa.load(audio_in_path, sr=None)
             #Save the file as array in pickle 
             # But first need to change the extension of the file from .wav to .p
            filename = os.path.splitext(filename)[0] + '.p'
            audio_out_path = './' + parameters.tagged_recordings_as_array_pickles_folder + '/' + filename
            with open(audio_out_path, 'wb') as f:
                pickle.dump(y, f, pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print(str(e))
# Test convert_wav_files_to_array_pickles()
convert_wav_files_to_array_pickles()    