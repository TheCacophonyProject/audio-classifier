#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 25 15:31:59 2019

@author: tim
"""

import functions
import parameters
import os

os.system('clear')

# Create all necessary folders
functions.create_all_necessary_folders()

# Find id's of recordings that have audio tags
functions.get_audio_recordings_with_tags_with_basic_information_from_server_save_to_disk()

# Create list of recording ids that have tags. This will use the last
filename = parameters.name_of_latest_file_containing_basic_information_of_recordings_with_audio_tags
functions.extract_recordingIds_from_json_file_of_basic_recording_information(filename)

# Download the audio recordings with tags
filename = parameters.name_of_latest_file_containing_ids_of_recordings_with_audio_tags
functions.download_recordings_that_have_a_tag(filename)

# Retrieve detailed tag information for each recording with tags
filename = parameters.name_of_latest_file_containing_ids_of_recordings_with_audio_tags
functions.get_full_recording_information_using_file_list_of_recordings(filename)

# Extract indivual tag information
filename = parameters.file_containing_list_of_recording_with_full_information
functions.extract_individual_tags_from_file_containing_list_of_recording_with_full_information(filename)

# Create tagged clips using above downloaded recordings, and clip information
filename = parameters.name_of_file_containing_list_of_tags
functions.create_recording_clips_based_on_tags(filename)

