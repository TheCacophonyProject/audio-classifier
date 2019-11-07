#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 16:03:50 2019

@author: tim
"""

# Grants shed analysis
import functions
import parameters
device_name = 'grants-shed'

audio_input_folder_for_extracting_tags = parameters.downloaded_recordings_folder + '/' + device_name + '/night_recording/'
onset_pairs_folder = audio_input_folder_for_extracting_tags + 'onset_pairs'
images_out_folder = onset_pairs_folder + '/images'

#functions.sort_into_day_or_night(device_name)


#functions.create_squawk_pairs_from_unfiltered(audio_input_folder_for_extracting_tags, onset_pairs_folder)

functions.create_800_1000_freq_mel_spectrogram_jps_using_onset_pairs(audio_input_folder_for_extracting_tags, onset_pairs_folder, images_out_folder)


                
           