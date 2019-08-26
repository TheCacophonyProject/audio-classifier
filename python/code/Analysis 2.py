#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 10:15:29 2019

@author: tim
"""

# Analysis

# Need to calculate how many recordings were made each month (not just if a call was found)
# Need the number of recordings that were made for each hour (as more are made around dawn and dusk)

import os
import parameters
import functions
import json
import csv



device_name = 'fpF7B9AFNn6hvfVgdrJB'
squawk_type = 'morepork'

input_folder = parameters.downloaded_recordings_folder + '/' + device_name

night_sub_folder = input_folder + '/night_recording/'



path, dirs, files = next(os.walk(night_sub_folder))

night_recording_info_csv_filename = 'night_recording_info_' + device_name + '_v1.csv'

# Create spreadsheet of tags and timestamp

header = ['recording id', 'timestamp', 'Seconds after dusk', 'Seconds before dawn']

with open(night_recording_info_csv_filename, "w", newline='') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(header)

    with os.scandir(night_sub_folder) as entries:
        for entry in entries:       
            if entry.is_file():
                filename = entry.name
            else:
                continue  
            
            recording_id = os.path.splitext(filename)[0] 
            print('recording_id ', recording_id)
           
            recording_info_from_server = functions.get_recording_information_for_a_single_recording(recording_id)
    
            recording = recording_info_from_server['recording']
            recordingDateTime = recording['recordingDateTime']
            
            print(recordingDateTime)
            
            relativeToDawn = recording['relativeToDawn']
            relativeToDusk = recording['relativeToDusk']
    
            print('relativeToDusk' , relativeToDusk, '\n')
            print('relativeToDawn' , relativeToDawn, '\n')
            
            tag =[]
            tag.append(recording_id)
            tag.append(recordingDateTime)          
    
            
            if relativeToDusk is not None:
                if relativeToDusk > 0:                    
                    tag.append(relativeToDusk)
                    tag.append('')
                     
            elif relativeToDawn is not None:
                if relativeToDawn < 0:                  
                    tag.append('')
                    tag.append(relativeToDawn)                      
            
            
            writer.writerow(tag)
                   
        
        


















































