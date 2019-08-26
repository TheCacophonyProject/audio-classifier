#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 11:38:38 2019

@author: tim
"""

import os
import parameters
import functions
import json
import csv
import librosa.display



device_name = 'fpF7B9AFNn6hvfVgdrJB'


input_folder = './downloaded_recordings_for_counting/'
not_june_folder  = input_folder + 'not_june/'
#june_folder = input_folder + 'june/'
#june_unfiltered_folder = june_folder + 'unfiltered/'
#june_unfiltered_day_folder = june_unfiltered_folder + 'day/'
#june_unfiltered_night_folder = june_unfiltered_folder + 'night/'
#june_unfiltered_night_squawks_folder = june_unfiltered_night_folder + 'squawks/'

not_june_unfiltered_folder = not_june_folder + 'unfiltered/'

not_june_unfiltered_night_folder = not_june_unfiltered_folder + 'night/'
not_june_filtered_night_squawks_folder = not_june_folder + 'filtered_night/squawks/'
not_june_filtered_night_squawks_onset_pairs_per_recording_folder = not_june_filtered_night_squawks_folder + 'onset_pairs_per_recording/'

#not_june_filtered_night_squawks_onset_pairs_folder = not_june_filtered_night_squawks_folder + 'onset_pairs/'

#not_june_unfiltered_night_squawks_folder = not_june_unfiltered_night_folder + 'squawks/'

#not_june_unfiltered_day_folder = not_june_unfiltered_folder + 'day/'
#not_june_unfiltered_day_squawks_folder = not_june_unfiltered_day_folder + 'squawks/'

#squawks_folder = june_folder + 'squawks/'


def split_into_june_nonJune_recordings():
    #For recordings in months July 2018 to May 2019 inclusive, count the onsets
   
    path, dirs, files = next(os.walk(input_folder))
    
    print('number of files is', len(files))
    
    
    with os.scandir(input_folder) as entries:
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
            year = recordingDateTime.split('-')[0]
            month = recordingDateTime.split('-')[1]
            
            print(recordingDateTime)
            print('year', year)
            print('month', month)        
            
            input_path = input_folder +  filename
            
            if month == '06':
                output_path = june_folder +  filename
                
            else:
                 output_path = not_june_folder +  filename
                        
            os.rename(input_path, output_path)
            
def sort_unfiltered_into_day_or_night():
    print('started')
    input_folder = not_june_folder
    print('input_folder ', input_folder)
    
        
    errors_sub_folder = input_folder + '/errors'
    if not os.path.exists(errors_sub_folder):
        os.makedirs(errors_sub_folder)
    
    for filename in os.listdir(input_folder):
        if  not os.path.isfile(os.path.join(input_folder, filename)):
            continue
        
        audio_in_path = './' + input_folder + '/' + filename
      
        night_recording = False
        recording_id = os.path.splitext(filename)[0]
        recording_information = functions.get_recording_information_for_a_single_recording(recording_id)
        if recording_information == None:
            audio_out_path_error = './' + errors_sub_folder + '/' + filename
            print('audio_in_path is ', audio_in_path)
            print('audio_out_path_error',  audio_out_path_error)
            os.rename(audio_in_path, audio_out_path_error)
            print('renamed')
            continue
        
        recording = recording_information['recording']
        print('recording' , recording, '\n')
        relativeToDawn = recording['relativeToDawn']
        relativeToDusk = recording['relativeToDusk']
        
        print('relativeToDusk' , relativeToDusk, '\n')
        print('relativeToDawn' , relativeToDawn, '\n')
        
        if relativeToDusk is not None:
            if relativeToDusk > 0:
               night_recording = True 
        elif relativeToDawn is not None:
            if relativeToDawn < 0:
               night_recording = True 
               
        print('night_recording' , night_recording, '\n')

        if night_recording:          
            audio_out_path = not_june_unfiltered_night_folder + filename
        else:
            audio_out_path = not_june_unfiltered_day_folder + filename
            
        
        os.rename(audio_in_path, audio_out_path)
            
def create_squawks_from_night_unfiltered():            

    count = 0
    total_number_of_files = len(os.listdir(not_june_unfiltered_night_folder))
    print('total_number_of_files ', total_number_of_files)
    
    total_number_of_squawks = 0
    
    path, dirs, files = next(os.walk(not_june_unfiltered_night_folder))
    
    with os.scandir(not_june_unfiltered_night_folder) as entries:
        for entry in entries:
            print(entry.name)
            if entry.is_file():
                filename = entry.name
            else:
                continue
            
            recording_id = os.path.splitext(filename)[0]
            count +=1
            print('\nProcessing file ', count, ' of ', total_number_of_files, ' files.')
    
       
            audio_in_path = not_june_unfiltered_night_folder + filename
            print('audio_in_path ', audio_in_path)
            y, sr = librosa.load(audio_in_path)
            
        
            squawks = functions.FindSquawks(y, sr)
#            number_of_squawks = len(squawks)
    #        print('number_of_squawks for recording', number_of_squawks)
            
            
            for squawk in squawks:
    #            print(squawk)
                total_number_of_squawks += 1
                
                print('total_number_of_squawks ', total_number_of_squawks)
                start = squawk['start']
                
                f = open(not_june_unfiltered_night_squawks_folder + recording_id + '_' + str(start) + '.txt', 'w')
                json.dump(squawk, f)
                f.close()
                
def create_squawks_from_day_unfiltered():            

    count = 0
    total_number_of_files = len(os.listdir(not_june_unfiltered_day_folder))
    print('total_number_of_files ', total_number_of_files)
    
    total_number_of_squawks = 0
    
    path, dirs, files = next(os.walk(not_june_unfiltered_day_folder))
    
    with os.scandir(not_june_unfiltered_day_folder) as entries:
        for entry in entries:
            print(entry.name)
            if entry.is_file():
                filename = entry.name
            else:
                continue
            
            recording_id = os.path.splitext(filename)[0]
            count +=1
            print('\nProcessing file ', count, ' of ', total_number_of_files, ' files.')
    
       
            audio_in_path = not_june_unfiltered_day_folder + filename
            print('audio_in_path ', audio_in_path)
            y, sr = librosa.load(audio_in_path)
            
        
            squawks = functions.FindSquawks(y, sr)
#            number_of_squawks = len(squawks)
    #        print('number_of_squawks for recording', number_of_squawks)
            
            
            for squawk in squawks:
    #            print(squawk)
                total_number_of_squawks += 1
                
                print('total_number_of_squawks ', total_number_of_squawks)
                start = squawk['start']
                
                f = open(not_june_unfiltered_day_squawks_folder + recording_id + '_' + str(start) + '.txt', 'w')
                json.dump(squawk, f)
                f.close()
 
def create_squawks_from_night_filtered():            

    count = 0
    total_number_of_files = len(os.listdir(not_june_unfiltered_night_folder))
    print('total_number_of_files ', total_number_of_files)
    
    total_number_of_squawks = 0
    
    path, dirs, files = next(os.walk(not_june_unfiltered_night_folder))
    
    with os.scandir(not_june_unfiltered_night_folder) as entries:
        for entry in entries:
            print(entry.name)
            if entry.is_file():
                filename = entry.name
            else:
                continue
            
            recording_id = os.path.splitext(filename)[0]
            count +=1
            print('\nProcessing file ', count, ' of ', total_number_of_files, ' files.')
    
       
            audio_in_path = not_june_unfiltered_night_folder + filename
            print('audio_in_path ', audio_in_path)
            y, sr = librosa.load(audio_in_path)
            y = functions.apply_band_pass_filter(y, sr)
        
            squawks = functions.FindSquawks(y, sr)
#            number_of_squawks = len(squawks)
    #        print('number_of_squawks for recording', number_of_squawks)
            
            
            for squawk in squawks:
    #            print(squawk)
                total_number_of_squawks += 1
                
                print('total_number_of_squawks ', total_number_of_squawks)
                start = squawk['start']
                
                f = open(not_june_filtered_night_squawks_folder + recording_id + '_' + str(start) + '.txt', 'w')
                json.dump(squawk, f)
                f.close()       
        
def create_squawk_pairs_from_night_filtered():
    count_of_onset_pairs_including_more_than_20 = 0
    count_of_onset_pairs_including_not_including_more_20 = 0
    
    count = 0
    total_number_of_files = len(os.listdir(not_june_unfiltered_night_folder))
#    for filename in os.listdir(input_folder):
    with os.scandir(not_june_unfiltered_night_folder) as entries:
        for entry in entries:
            print(entry.name)
            if entry.is_file():
                filename = entry.name
            else:
                continue
        
            count+=1
            print('Processing file ', count, ' of ', total_number_of_files, ' files.')
    #    filename = '225217.wav'
       
            audio_in_path = not_june_unfiltered_night_folder + filename
            y, sr = librosa.load(audio_in_path)
            y = functions.apply_band_pass_filter(y, sr)            
        
            paired_squawks_sec = functions.find_paired_squawks_in_single_recordings(y, sr)
            #print('paired_squawks_sec', paired_squawks_sec)
            number_of_paired_squawks = len(paired_squawks_sec)
            if not number_of_paired_squawks == 0:
                if number_of_paired_squawks > 20:
                    count_of_onset_pairs_including_more_than_20 += number_of_paired_squawks
                else:
                    count_of_onset_pairs_including_more_than_20 += number_of_paired_squawks
                    count_of_onset_pairs_including_not_including_more_20 += number_of_paired_squawks
                    
                
                    
               # print('paired_squawks_sec ', paired_squawks_sec, '\n')
                recording_id = os.path.splitext(filename)[0]
                f = open(not_june_filtered_night_squawks_onset_pairs_per_recording_folder + recording_id + '.txt', 'w')
                json.dump(paired_squawks_sec, f)
                f.close()
            print('count_of_onset_pairs_including_more_than_20 ', count_of_onset_pairs_including_more_than_20)
            print('count_of_onset_pairs_including_not_including_more_20 ', count_of_onset_pairs_including_not_including_more_20)
            
    
def Main():    
    #split_into_june_nonJune_recordings()
#    sort_unfiltered_into_day_or_night()
    #create_squawks_from_night_unfiltered() 
    #create_squawks_from_day_unfiltered()
    #create_squawks_from_night_filtered()
   
    create_squawk_pairs_from_night_filtered()
       
            
        
        
        
Main()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        