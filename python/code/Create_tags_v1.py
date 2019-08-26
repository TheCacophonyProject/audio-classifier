#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 09:16:12 2019

@author: tim
"""

import functions
import parameters
import numpy as np
import IPython.display as ipd
import librosa
import matplotlib.pyplot as plt
import librosa.display
import json

import sounddevice as sd

import os

device_name = 'fpF7B9AFNn6hvfVgdrJB'
squawk_type = 'morepork'
sorted_squawks_to_process_folder = './sorted_squawks/' + squawk_type + '/'
tags_created_on_server_folder = sorted_squawks_to_process_folder + 'tags_created_on_server/'

if not os.path.exists(tags_created_on_server_folder):
        os.makedirs(tags_created_on_server_folder)


with os.scandir(sorted_squawks_to_process_folder) as entries:
    for entry in entries:
        print(entry.name)
        if entry.is_file():
            filename = entry.name
        else:
            continue
        
        file_in_path = sorted_squawks_to_process_folder + filename
        print('file_in_path ', file_in_path)
        with open(file_in_path, 'r') as f:
            squawk_json = json.load(f)
          
            recordingId = squawk_json["origin"]
            start_time = squawk_json["start_secs"]
            what = squawk_json["what"]
            duration = squawk_json["duration"]
    
            functions.add_tag_to_server(recordingId=recordingId, what=what, startTime=start_time, duration=duration)
        
        # Move file to processed  
        file_processed_path = tags_created_on_server_folder + filename
        os.rename(file_in_path, file_processed_path)       