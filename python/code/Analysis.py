#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 10:15:29 2019

@author: tim
"""

# Analysis

# Count number of 

import os
import parameters
import functions
import json
import csv



device_name = 'fpF7B9AFNn6hvfVgdrJB'
squawk_type = 'morepork'
#tag_csv_filename = 'morepork_tags_device_name.csv'
tag_csv_filename = squawk_type + '_tags_' + device_name + '_v3.csv'
input_folder = parameters.downloaded_recordings_folder + '/' + device_name
sorted_squawks_to_process_folder = './sorted_squawks/' + squawk_type + '/'
tags_created_on_server_folder = sorted_squawks_to_process_folder + 'tags_created_on_server/'
sorted_squawks_to_process_folder = './sorted_squawks/' + squawk_type + '/'
tags_created_on_server_folder = sorted_squawks_to_process_folder + 'tags_created_on_server/'
night_sub_folder = input_folder + '/night_recording'
day_sub_folder = input_folder + '/day_recording'

# Total time of all recordings
path, dirs, files = next(os.walk(night_sub_folder))
file_count_night = len(files)

path, dirs, files = next(os.walk(day_sub_folder))
file_count_day = len(files)

total_number_or_recordings = file_count_day + file_count_night

total_time_night_recordings_hours = int(file_count_night / 60)
total_time_day_recordings_hours = int(file_count_day / 60)


total_time_recording_hours = total_time_night_recordings_hours + total_time_day_recordings_hours


path, dirs, files = next(os.walk(day_sub_folder))
file_count_day = len(files)


print('Total number of recordings is: ', total_number_or_recordings)
print('Total Hours of recordings is: ', total_time_recording_hours)
print('Total number of night recordings is: ', file_count_night)
print('Hours of night recordings is: ', total_time_night_recordings_hours)
print('Total number of day recordings is: ', file_count_day)
print('Hours of day recordings is: ', total_time_day_recordings_hours)



# Number of morepork tags
path, dirs, files = next(os.walk(tags_created_on_server_folder))
file_count = len(files)
print('Total number of tags is: ', file_count)

# Create spreadsheet of tags and timestamp

header = ['recording id', 'timestamp', 'start_secs', 'what', 'Night Recording', 'Seconds after dusk', 'Seconds before dawn']

with open(tag_csv_filename, "w", newline='') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(header)

    with os.scandir(tags_created_on_server_folder) as entries:
        for entry in entries:       
            if entry.is_file():
                filename = entry.name
            else:
                continue  
            
            input_file = tags_created_on_server_folder + filename
            with open(input_file, 'r') as f:
                tag_info = json.load(f)
                print('tag_info ', tag_info)
                start_secs = tag_info['start_secs']
                print('start_secs ', start_secs)
                what = tag_info['what']
                print('what ', what)
                recording_id = tag_info['origin']        
    
                print('recording_id ', recording_id)
                
                # I stuffed up and didn't store datetime in the tag, so have to get it from the server :-()
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
                tag.append(start_secs)
                tag.append(what)
        
                night_recording = False
                if relativeToDusk is not None:
                    if relativeToDusk > 0:
                        night_recording = True
                        tag.append(night_recording)
                        tag.append(relativeToDusk)
                        tag.append('')
                         
                elif relativeToDawn is not None:
                    if relativeToDawn < 0:
                        night_recording = True 
                        tag.append(night_recording)
                        tag.append('')
                        tag.append(relativeToDawn)                      
                
                
                writer.writerow(tag)
                   
        
        


















































