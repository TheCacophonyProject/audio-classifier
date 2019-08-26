#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 10:01:48 2019

@author: tim
"""

from pydub import AudioSegment
import os

input_folder = './downloaded_recordings/fpF7B9AFNn6hvfVgdrJB/night_recording/'
filename = '161954.m4a'
input_path =  input_folder + filename

output_folder = './temp/'
wav_filename = '161954.wav'
output_path =  output_folder + wav_filename


song = AudioSegment.from_file(input_path, "m4a")
song.export(output_path, format="wav")

#with os.scandir(input_folder) as entries:
#        for entry in entries:    
#            try:
#                if entry.is_file():
#                    filename = entry.name
#                else:
#                    continue 
#             
#                input_path= input_folder + filename
#                print('input_path ', input_path)
#                recording = AudioSegment.from_file(input_path, "m4a")
#                
#                recording_id = os.path.splitext(filename)[0]
#                output_path = output_folder +  recording_id + '.wav'
#                
#                recording.export(output_path, format="wav")
#                print('output_path ', output_path)
#            except:
#                print('Could not process file ',filename)
                
        