#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 25 12:13:15 2019

@author: tim
"""
import parameters
import librosa
import os
from scipy import signal
from scipy.io import wavfile
import pickle
import requests
import sys
import json
from datetime import datetime
import numpy as np
import csv
import matplotlib.pyplot as plt
import IPython.display as ipd
from playsound import playsound
from pydub import AudioSegment
from pydub.playback import play
from mplayer import Player

from scipy.signal import butter, lfilter, freqz

import ast
import librosa.display

import madmom

from scipy.ndimage.filters import maximum_filter
import pylab




def create_all_necessary_folders():
    print('Checking and/or creating folders\n')
    if not os.path.exists(parameters.downloaded_recordings_folder):
        os.makedirs(parameters.downloaded_recordings_folder)
        print(parameters.downloaded_recordings_folder, ' created\n')
        
    if not os.path.exists(parameters.basic_information_on_recordings_with_audio_tags_folder):
        os.makedirs(parameters.basic_information_on_recordings_with_audio_tags_folder)
        print(parameters.basic_information_on_recordings_with_audio_tags_folder, ' created\n')
        
    if not os.path.exists(parameters.files_for_testing_folder):
        os.makedirs(parameters.files_for_testing_folder)
        print(parameters.files_for_testing_folder, ' created\n')
        
    if not os.path.exists(parameters.full_information_on_recordings_with_tags_folder):
        os.makedirs(parameters.full_information_on_recordings_with_tags_folder)
        print(parameters.full_information_on_recordings_with_tags_folder, ' created\n')
        
    if not os.path.exists(parameters.ids_of_recordings_with_audio_tags_folder):
        os.makedirs(parameters.ids_of_recordings_with_audio_tags_folder)
        print(parameters.ids_of_recordings_with_audio_tags_folder, ' created\n')
        
    if not os.path.exists(parameters.list_of_tags_folder):
        os.makedirs(parameters.list_of_tags_folder)
        print(parameters.list_of_tags_folder, ' created\n')
        
    if not os.path.exists(parameters.tagged_recordings_folder):
        os.makedirs(parameters.tagged_recordings_folder) 
        print(parameters.tagged_recordings_folder, ' created\n')
        
        
#    if not os.path.exists(parameters.tagged_recordings_as_array_pickles_folder):
#        os.makedirs(parameters.tagged_recordings_as_array_pickles_folder)
        
def test_create_all_necessary_folders():
        create_all_necessary_folders()                

def create_recording_clips_based_on_tags(name_of_file_containing_list_of_tags):
    # Using the information about the individual tags, and having already downloaded 
    # the associated recordings we can now create a clip (actual recording file)
    # using the start and duration information, and store the clip in a folder 
    # corresponding to the tag name
    
    print('Create audio file clips using tag details\n')
    
    # Get the list of tags
    in_file_path_name = './' + parameters.list_of_tags_folder + '/' + name_of_file_containing_list_of_tags   
    # Get the list of tags
    if in_file_path_name:
        with open(in_file_path_name, 'r') as f:
            list_of_tags = json.load(f)
    
    # For each tag: 1) create a folder using tag name if it doesn't exist, 2) Create the clip and put in the folder
    for tag in list_of_tags:
        #create_tagged_recording(recording_Id=tag['RecordingId'], start_time_seconds=tag['startTime'], duration_seconds=tag['duration'], tag_name=tag['animal'], tag_id=tag['id'])
#        create_tagged_recording_as_array(recording_Id=tag['RecordingId'], start_time_seconds=tag['startTime'], duration_seconds=tag['duration'], tag_name=tag['animal'], tag_id=tag['id'])
#        create_tagged_recording_as_wav(recording_Id=tag['RecordingId'], start_time_seconds=tag['startTime'], duration_seconds=tag['duration'], tag_name=tag['animal'], tag_id=tag['id'])
        create_tagged_recording_as_wav(recording_Id=tag['RecordingId'], start_time_seconds=tag['startTime'], duration_seconds=2, tag_name=tag['animal'], tag_id=tag['id'])
        
    print('SUCCESS  Audio file clips have been created.\n')
    print('sound_clips.csv file (used for training model) has been updated with a list of these clips and their corresponding tag names\n')
    
def test_create_recording_clips_based_on_tags():
    name_of_file_containing_list_of_tags = '2019-06-06-17-44-24.json'
    print('About to create tagged recording clips \n')
    create_recording_clips_based_on_tags(name_of_file_containing_list_of_tags)
    print('Check clips have been created in tagged_recordings folder')

def download_recordings_that_have_a_tag(name_of_file_containing_list_of_recording_ids):
    # This takes a list of all the recordings that have tags and then downloads the actual (playable) recording file (file if we don't already have it) 
    
    print('Downloading recordings from Cacophony Server\n')
    in_file_path_name = './' + parameters.ids_of_recordings_with_audio_tags_folder + '/' + name_of_file_containing_list_of_recording_ids
        
    if in_file_path_name:
        with open(in_file_path_name, 'r') as f:
            list_of_recording_ids = json.load(f) 
    
    for recording_id in list_of_recording_ids:
       
        # get token for downloading a recording
        token_for_retrieving_recording = get_token_for_retrieving_recording(recording_id)
        get_recording_from_server(token_for_retrieving_recording, recording_id)
        
    
    
def test_download_recordings_that_have_a_tag():
    name_of_file_containing_list_of_recording_ids = '2019-05-28-11-05-50.json'
    download_recordings_that_have_a_tag(name_of_file_containing_list_of_recording_ids)
    print('Check recordings are in downloaded_recordings_folder')
    
    

def extract_tags_for_single_audio_recording_from_single_recording_information(recording_data_for_single_recording):     
     recording = recording_data_for_single_recording['recording']
     tags = {'tags':recording['Tags']}  
     tags2 = tags['tags']
#     print(tags2)
     
     return tags2
 
def test_extract_tags_for_single_audio_recording_from_single_recording_information():
     recording_data_for_single_recording = get_recording_information_for_a_single_recording('158523')
     tags = extract_tags_for_single_audio_recording_from_single_recording_information(recording_data_for_single_recording)
     
     print('tags are: ', tags)
     
     for tag in tags:
         print(tag)
    

def get_recording_information_for_a_single_recording(recording_id):
    user_token = get_cacophony_user_token()

    get_a_token_for_recording_endpoint = parameters.server_endpoint + parameters.get_information_on_single_recording + recording_id

    headers = {'Authorization': user_token}

    resp_for_getting_a_recordingToken = requests.request("GET", get_a_token_for_recording_endpoint, headers=headers)
    if resp_for_getting_a_recordingToken.status_code != 200:
        print('Could not get download token')
        return None
    recording_data_for_single_recording = resp_for_getting_a_recordingToken.json()   
   
    
    return recording_data_for_single_recording

def test_get_recording_information_for_a_single_recording():
    recording_data = get_recording_information_for_a_single_recording('158523')
    print('recording_data is: ', recording_data)
        

def add_tag_to_recording(user_token, recordingId, json_data):
    url = parameters.server_endpoint + parameters.tags_url
    

    payload = "recordingId=" + recordingId + \
        "&tag=" \
        + json_data        
        
    headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Authorization': user_token
            }

    response = requests.request("POST", url, data=payload, headers=headers)

    return response

def test_add_tag_to_recording():
    user_token = get_cacophony_user_token()
    tag = {}
    tag['animal'] = 'bigBirdYY'
    tag['startTime'] = 1
    tag['duration'] = 2
    json_tag = json.dumps(tag)
    resp = add_tag_to_recording(user_token, "158698", json_tag)
    print('resp is: ', resp.text)

def add_tag_to_server(recordingId, what, startTime, duration):
    user_token = get_cacophony_user_token()
    tag = {}
#    tag['what'] = what # use this when tag api updated
    tag['animal'] = what
    tag['startTime'] = startTime
    tag['duration'] = duration
    json_tag = json.dumps(tag)
    print('json_tag ', json_tag)
    resp = add_tag_to_recording(user_token, recordingId, json_tag)
    print('resp is: ', resp.text)

def test_add_tag_to_server():
    add_tag_to_server('153036', 'morepork classic', '4', '1.5')

def get_audio_recordings_with_tags_information_from_server(user_token, recording_type):
    print('Retrieving recordings basic information from Cacophony Server\n')
    url = parameters.server_endpoint + parameters.query_available_recordings
    
    where_param = {}
    where_param['type'] = recording_type    
    json_where_param = json.dumps(where_param)
    querystring = {"tagMode":"human-only", "where":json_where_param}    
    headers = {'Authorization': user_token}  

    resp = requests.request("GET", url, headers=headers, params=querystring)
   
    if resp.status_code != 200:
        # This means something went wrong.
        print('Error from server is: ', resp.text)
        sys.exit('Could not download file - exiting')    
        
    
    data = resp.json()
#    print('data is ', data)
   
    recordings = data['rows']
    
    return recordings

def test_get_audio_recordings_with_tags_information_from_server():
    user_token = get_cacophony_user_token()
    recording_type = 'audio'
    recordings = get_audio_recordings_with_tags_information_from_server(user_token, recording_type)
    print('recordings are ', recordings)
   


def get_ids_of_recordings_to_download(user_token, device_name, offset):
    # This will get a list of the recording ids for every recording of length 59,60,61,62 from device_name
    print('Retrieving recordings basic information from Cacophony Server\n')
    url = parameters.server_endpoint + parameters.query_available_recordings
    
    where_param = {}
    where_param['type'] = 'audio'
    where_param['duration'] = 59,60,61,62
    json_where_param = json.dumps(where_param)  
#    querystring = {"where":json_where_param} 
    querystring = {"offset":offset, "where":json_where_param} 
    
#    print('querystring is ',querystring, '\n')
    
    headers = {'Authorization': user_token}  

    resp = requests.request("GET", url, headers=headers, params=querystring)
   
    if resp.status_code != 200:
        # This means something went wrong.
        print('Error from server is: ', resp.text)
        sys.exit('Could not download file - exiting')    
        
    
    data = resp.json() 
    
    
    recordings = data['rows'] 
    
#    print(recordings, '\n')
    
    print('Number of recordings is ', len(recordings))

    ids_of_recordings_to_download = []    
    for recording in recordings:        
        device_str = str(recording['Device'])         
        # https://stackoverflow.com/questions/988228/convert-a-string-representation-of-a-dictionary-to-a-dictionary
        device = ast.literal_eval(device_str)
        devicename = device['devicename']
        
        if devicename == device_name: 
            deviceId = str(recording['DeviceId'])              
            print('Device id is ', deviceId)
            recording_id = str(recording['id'])
            ids_of_recordings_to_download.append(recording_id)
        
    return ids_of_recordings_to_download

def test_get_ids_of_recordings_to_download():
    user_token = get_cacophony_user_token()
    device_name = '0070_v1_3_6'
    offset = 0

    ids_of_recordings_to_download = get_ids_of_recordings_to_download(user_token=user_token, device_name=device_name, offset=offset)
    print('recording_information_for_device ', device_name, ' is ', ids_of_recordings_to_download)
    
    offset = 300

    ids_of_recordings_to_download = get_ids_of_recordings_to_download(user_token=user_token, device_name=device_name, offset=offset)
    print('recording_information_for_device ', device_name, ' is ', ids_of_recordings_to_download)
    
def get_ids_of_recordings_to_download_using_deviceId(deviceId, offset):
    # This will get a list of the recording ids for every recording of length 59,60,61,62 from device_name
    user_token = get_cacophony_user_token()
   
    url = parameters.server_endpoint + parameters.query_available_recordings
    
    where_param = {}
    where_param['DeviceId'] = deviceId
    where_param['duration'] = 59,60,61,62
    json_where_param = json.dumps(where_param)  
#    querystring = {"where":json_where_param} 
    querystring = {"offset":offset, "where":json_where_param} 
    
#    print('querystring is ',querystring, '\n')
    
    headers = {'Authorization': user_token}  

    resp = requests.request("GET", url, headers=headers, params=querystring)
   
    if resp.status_code != 200:
        # This means something went wrong.
        print('Error from server is: ', resp.text)
        sys.exit('Could not download file - exiting')    
        
    
    data = resp.json() 
    
    
    recordings = data['rows'] 
    
#    print(recordings, '\n')
    
    print('Number of recordings is ', len(recordings))

    ids_of_recordings_to_download = []    
    for recording in recordings:        
        recording_id = str(recording['id'])
        ids_of_recordings_to_download.append(recording_id)
        
    return ids_of_recordings_to_download    
    
##def get_ids_of_recordings_to_download(user_token, device_name):
#def get_ids_of_recordings_for_device(user_token, device_name):
#    print('Retrieving recordings basic information from Cacophony Server\n')
#    url = parameters.server_endpoint + parameters.query_available_recordings
#    
#    where_param = {}
##    where_param['type'] = 'audio'     
#
##    where_param['Group.groupname'] = 'tim1'
##    where_param['device'] = 1
##    where_param['id'] = 159645
#    where_param['type'] = 'audio'
##    where_param['DeviceId'] = 1586
##    where_param['GroupId'] = 6
##    where_param['Group.groupname'] = 'tim1'
##    where_param['location.type'] = 'Point'
##    where_param['Tags.what'] = 'bird'
##    where_param['Group'] = '["groupname", "tim1"]'
#     
##    where_param['groupname'] = 'tim1'
##    where_param['Device'.'devicename'] = '0064_20190605a' 
#    where_param['duration'] = 59,60,61,62
#    json_where_param = json.dumps(where_param)
#    print('json_where_param is ', json_where_param,'\n')
##    querystring = {"tagMode":"human-only", "where":json_where_param} 
#    querystring = {"where":json_where_param}  
##    querystring = {"where":"\"Group\":[\"groupname\", \"tim1\""}  
#    print('querystring is ',querystring)
#    headers = {'Authorization': user_token}  
#
#    resp = requests.request("GET", url, headers=headers, params=querystring)
#   
#    if resp.status_code != 200:
#        # This means something went wrong.
#        print('Error from server is: ', resp.text)
#        sys.exit('Could not download file - exiting')    
#        
#    
#    data = resp.json()
#   
#    recordings = data['rows']
#    
#    ids_of_recordings_for_device = []
#    
#    for recording in recordings:
#        recording_id = str(recording['id'])
#        ids_of_recordings_for_device.append(recording_id)
#        
#    return ids_of_recordings_for_device
#
#def test_get_ids_of_recordings_for_device():
#    user_token = get_cacophony_user_token()
#    device_name = '0070_v1_3_6'
#    ids_of_recordings_to_download = get_ids_of_recordings_to_download(user_token, device_name)
#    print('recording_information_for_device is ', ids_of_recordings_to_download)
    
def get_list_of_devices_for_group(group_name):
    user_token = get_cacophony_user_token()
    url = parameters.server_endpoint + parameters.groups
    where_param = {}
    where_param['groupname'] = 'tim1'
    json_where_param = json.dumps(where_param)
    querystring = {"where":json_where_param} 
    headers = {'Authorization': user_token}  

    resp = requests.request("GET", url, headers=headers, params=querystring)
   
    if resp.status_code != 200:
        # This means something went wrong.
        print('Error from server is: ', resp.text)
        sys.exit('Could not download file - exiting')
    
    data = resp.json()   
   
    groups = data['groups']
    
    device_ids = []
    
    for group in groups:
        devices = group['Devices']
        for device in devices:
            print('devicename is ', device['devicename'],'\n')
            device_id = str(device['id'])
            device_ids.append(device_id)
           
    return device_ids
    
    
def test_get_list_of_devices_for_group():
    device_ids = get_list_of_devices_for_group('tim1')
    print('device_ids are ', device_ids)

def get_device_id_using_device_name(device_name):
    user_token = get_cacophony_user_token()
    url = parameters.server_endpoint + parameters.devices
      
    headers = {'Authorization': user_token}  

    resp = requests.request("GET", url, headers=headers)
   
    if resp.status_code != 200:
        # This means something went wrong.
        print('Error from server is: ', resp.text)
        sys.exit('Could not download file - exiting')
    
    data = resp.json()

    devices = data['devices'] 
    rows = devices['rows']
    for row in rows:
        devicename = row['devicename']        
        if devicename == device_name:
                device_id = row['id']
                return device_id     
           
    
def test_get_device_id_using_device_name():
    device_name = '0070_v1_3_6'
    device_id = get_device_id_using_device_name(device_name)
    print('device_id for ',device_name, ' is ',  device_id, '\n')
    
    
def get_full_recording_information_using_file_list_of_recordings(filename):
    # Retrieve the full information about all the audio tags for a recording
    print('Retrieving full recording information (i.e. all tag details) from Cacophony Server\n')
    parameters.file_containing_list_of_recording_with_full_information = filename
    in_file_path_name = './' + parameters.ids_of_recordings_with_audio_tags_folder + '/' + filename
    out_file_path_name = './' + parameters.full_information_on_recordings_with_tags_folder + '/' + filename
    if in_file_path_name:
        with open(in_file_path_name, 'r') as f:
            list_of_recording_ids = json.load(f) 
    
    list_of_full_information_of_recordings_with_tags = []
    
    for recording_id in list_of_recording_ids:      
        
        # get the recording information
        recording_data_for_single_recording = get_recording_information_for_a_single_recording(recording_id)
        
        # append the recording information to list
        list_of_full_information_of_recordings_with_tags.append(recording_data_for_single_recording)
        
    # save list to disk
    with open(out_file_path_name, 'w') as json_file:  
        json.dump(list_of_full_information_of_recordings_with_tags, json_file)
    
    
    
    
def test_get_full_recording_information_using_file_list_of_recordings():
    # Check this file exists in the folder
    filename = '2019-05-28-11-05-50.json'
    get_full_recording_information_using_file_list_of_recordings(filename=filename)
    print('Check ids_of_recordings_with_audio_tags folder for new file') 
    
def extract_individual_tags_from_file_containing_list_of_recording_with_full_information(filename):
    # To aid further processing, extract just the tag information from the rest of the information about the recording
    print('Extract full details of each tag from from recording information\n')
    parameters.name_of_file_containing_list_of_tags = filename
    in_file_path_name = './' + parameters.full_information_on_recordings_with_tags_folder + '/' + filename
    out_file_path_name = './' + parameters.list_of_tags_folder + '/' + filename
    if in_file_path_name:
        with open(in_file_path_name, 'r') as f:
            list_full_information_on_recordings_with_tags = json.load(f) 
    
    list_of_tags = []
    
    for recording_data_for_single_recording in list_full_information_on_recordings_with_tags:
        tags = extract_tags_for_single_audio_recording_from_single_recording_information(recording_data_for_single_recording)
        for tag in tags:
            list_of_tags.append(tag)           
    
    with open(out_file_path_name, 'w') as json_file:  
        json.dump(list_of_tags, json_file)
    
    return list_of_tags
    
def test_extract_individual_tags_from_file_containing_list_of_recording_with_full_information():
    # Check this file exists in the folder
    filename = '2019-05-28-11-05-50.json'   
    list_of_tags = extract_individual_tags_from_file_containing_list_of_recording_with_full_information(filename=filename)
    print('All audio tags for all recordings (that this user has access to) are: \n')
    for tag in list_of_tags:
        print(tag)
        print('\n')
        
    print('\n Check list_of_tags folder for new file') 

def extract_recordingIds_from_json_file_of_basic_recording_information(filename):
    # This takes a list of recordings along with basic information about the tags for each recording
    # The list will be used to create a list of just the recording Ids
    print('Extracting recording Ids from basic recording information\n')
    parameters.name_of_latest_file_containing_ids_of_recordings_with_audio_tags = filename
    file_path_name = './' + parameters.basic_information_on_recordings_with_audio_tags_folder + '/' + filename   
    if file_path_name:
        with open(file_path_name, 'r') as f:
            list_of_recordings_with_basic_information = json.load(f)   
    
    ids_of_recordings_with_audio_tags = []
    
    for recording in list_of_recordings_with_basic_information:
        recording_id = str(recording['id'])
        ids_of_recordings_with_audio_tags.append(recording_id)      
           
    filename = './'+ parameters.ids_of_recordings_with_audio_tags_folder + '/' + filename
    with open(filename, 'w') as json_file:  
        json.dump(ids_of_recordings_with_audio_tags, json_file)
    
           
def test_extract_recordingIds_from_json_file_of_basic_recording_information():
    # Use the previously created json file that has basic information    
    extract_recordingIds_from_json_file_of_basic_recording_information('2019-05-28-11-05-50.json') 
    print('Check ids_of_recordings_with_audio_tags folder for new file')       
    
def get_audio_recordings_with_tags_with_basic_information_from_server_save_to_disk():
    # This does NOT download the actual audio files, just information
    # It tells us all the recordings that have tags - but unfortunately does not have all the tag information
    print('Retrieving basic information about recordings that have audio tags')
    print('Note: Later, this information will be used to get full tag information for these recordings\n')
    filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = str(filename) + '.json'
    
    # store this filename for use in the next step
    parameters.name_of_latest_file_containing_basic_information_of_recordings_with_audio_tags = filename
    
    filename = './'+ parameters.basic_information_on_recordings_with_audio_tags_folder + '/' + filename
    user_token = get_cacophony_user_token()
    recording_type = 'audio'
    recordings_with_tags = get_audio_recordings_with_tags_information_from_server(user_token=user_token, recording_type=recording_type)
    with open(filename, 'w') as json_file:  
        json.dump(recordings_with_tags, json_file)
    
    
        

    
def test_get_audio_recordings_with_tags_with_basic_information_from_server_save_to_disk():    
    get_audio_recordings_with_tags_with_basic_information_from_server_save_to_disk()
    

def get_recording_from_server(token_for_retrieving_recording, recording_id, device_name):
    try:
        
#        if not device_name:
#            recording_local_filename = './'+ parameters.downloaded_recordings_folder + '/' + recording_id + '.m4a'
#        else:
        recording_local_filename = './'+ parameters.downloaded_recordings_folder + '/' + device_name + '/' + recording_id + '.m4a'
            
        # Don't download it if we already have it.
        #recording_local_filename = './'+ parameters.downloaded_recordings_folder + '/' + recording_id + '.mp4a'
#        recording_local_filename = './'+ parameters.downloaded_recordings_folder + '/' + recording_id + '.m4a'
       
        if not os.path.exists(recording_local_filename):
            print('\tDownloading recording', str(recording_id),'\n')
            url = parameters.server_endpoint + parameters.get_a_recording
            querystring = {"jwt":token_for_retrieving_recording}     
           
            resp_for_getting_a_recording = requests.request("GET", url, params=querystring)
           
            if resp_for_getting_a_recording.status_code != 200:
                # This means something went wrong.
                print('Error from server is: ', resp_for_getting_a_recording.text)
                return
#                sys.exit('Could not download file - exiting')
               
            #recording_local_filename = './'+ parameters.downloaded_recordings_folder + '/' + recording_id + '.mp4a'    
            with open(recording_local_filename, 'wb') as f:  
                f.write(resp_for_getting_a_recording.content)
        else:
            print('\t\tAlready have recording ', str(recording_id) , ' - so will not download again\n')
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to download recording ' + str(recording_id), '\n')
        
        
def test_get_recording_from_server(recording_id):
    token_for_retrieving_recording = get_token_for_retrieving_recording(recording_id)
    get_recording_from_server(token_for_retrieving_recording, recording_id)
    print('Check downloaded_recordings folder for recording')

def get_cacophony_user_token():
    username = parameters.cacophony_user_name
    if parameters.cacophony_user_password == '':
        parameters.cacophony_user_password = input("Enter password for Cacophony user " + username + " (or change cacophony_user_name in paramters file): ")
        
   # requestBody = {"nameOrEmail": "timhot", "password": parameters.cacophony_user_password }
    requestBody = {"nameOrEmail": username, "password": parameters.cacophony_user_password }
    login_endpoint = parameters.server_endpoint + parameters.login_user_url
    resp = requests.post(login_endpoint, data=requestBody)
    if resp.status_code != 200:
        # This means something went wrong.
        sys.exit('Could not connect to Cacophony Server - exiting')
    
    data = resp.json()
    token = data['token']
    return token

def test_get_cacophony_user_token():
    print('cacophony_user_token is: ' + get_cacophony_user_token())
    
def get_token_for_retrieving_recording(recording_id):
    user_token = get_cacophony_user_token()

    get_a_token_for_recording_endpoint = parameters.server_endpoint + parameters.get_a_token_for_getting_a_recording_url + recording_id

    headers = {'Authorization': user_token}

    resp_for_getting_a_recordingToken = requests.request("GET", get_a_token_for_recording_endpoint, headers=headers)
    if resp_for_getting_a_recordingToken.status_code != 200:
        sys.exit('Could not get download token - exiting')
    recording_data = resp_for_getting_a_recordingToken.json()
    recording_download_token = recording_data['downloadFileJWT']
    
    return recording_download_token

def test_get_token_for_retrieving_recording(recording_id): 
    token_for_retrieving_recording = get_token_for_retrieving_recording(recording_id)
    print('token_for_retrieving_recording is: ',  token_for_retrieving_recording)
    
#https://dsp.stackexchange.com/questions/41184/high-pass-filter-in-python-scipy/41185#41185
def highpass_filter(y, sr ):
  #filter_stop_freq = 70  # Hz
  #filter_pass_freq = 100  # Hz

  filter_stop_freq = 1150  # Hz
  filter_pass_freq = 1200  # Hz
  filter_order = 1001

  # High-pass filter
  nyquist_rate = sr / 2.
  desired = (0, 0, 1, 1)
  bands = (0, filter_stop_freq, filter_pass_freq, nyquist_rate)
  filter_coefs = signal.firls(filter_order, bands, desired, nyq=nyquist_rate)

  # Apply high-pass filter
  filtered_audio = signal.filtfilt(filter_coefs, [1], y)
  return filtered_audio

#https://dsp.stackexchange.com/questions/41184/high-pass-filter-in-python-scipy/41185#41185
def highpass_filter_with_parameters(y, sr, filter_stop_freq, filter_pass_freq ):
  
  filter_order = 1001

  # High-pass filter
  nyquist_rate = sr / 2.
  desired = (0, 0, 1, 1)
  bands = (0, filter_stop_freq, filter_pass_freq, nyquist_rate)
  filter_coefs = signal.firls(filter_order, bands, desired, nyq=nyquist_rate)

  # Apply high-pass filter
  filtered_audio = signal.filtfilt(filter_coefs, [1], y)
  return filtered_audio

# https://stackoverflow.com/questions/25191620/creating-lowpass-filter-in-scipy-understanding-methods-and-units
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y
    
def apply_lowpass_filter(y, sr):
    # Filter requirements.
    order = 6
   
    cutoff = 1000  # desired cutoff frequency of the filter, Hz
    
    y = butter_lowpass_filter(y, cutoff, sr, order)
    
    return y
    

#def create_tagged_recording_as_array(recording_Id, start_time_seconds, duration_seconds, tag_name, tag_id):
#    # And here is where the actual recording clip is created.
#    # Also took the opportunity to remove any low frequency noise
#    try:
#        audio_in_path = './' + parameters.downloaded_recordings_folder + '/' + str(recording_Id) + '.m4a'
#                
#        audio_file_name = tag_name + '_'  + str(start_time_seconds).zfill(3) + '_' + str(duration_seconds).zfill(3)  + '_'+ str(recording_Id) + '.p'
#        audio_out_path = './' + parameters.tagged_recordings_as_array_pickles_folder + '/' + audio_file_name
#                 
#        y, sr = librosa.load(audio_in_path, sr=None)
#        
#        clip_start_array = int((sr * start_time_seconds/8))
#        clip_end_array = clip_start_array + int((sr * duration_seconds))
#        
#        clip_call_by_array = y[clip_start_array:clip_end_array] 
#        
#        #Save the file as array in pickle   
#        with open(audio_out_path, 'wb') as f:
#            pickle.dump(clip_call_by_array, f, pickle.HIGHEST_PROTOCOL)
#            
#        # Also update the csv file that is used for telling the model what recording is what
#        add_information_to_csv_file(audio_file_name, tag_name)
#    except Exception as e:
#        print(str(e))
#        print('Unable to create clip_id ' + str(tag_id) + ' from recording ' +  str(recording_Id) + ' Probably an incorrect testing tag\n')
#        
#def test_create_tagged_recording_as_array():
#    create_tagged_recording_as_array(recording_Id='158824', start_time_seconds=1, duration_seconds=1, tag_name='possum', tag_id=5)

def create_tagged_recording_as_wav(recording_Id, start_time_seconds, duration_seconds, tag_name, tag_id):
    # And here is where the actual recording clip is created.
    # Also took the opportunity to remove any low frequency noise
    try:    
        audio_in_path = './' + parameters.downloaded_recordings_folder + '/' + str(recording_Id) + '.m4a'       
#        audio_file_name = tag_name + '_'  + str(start_time_seconds).zfill(3) + '_' + str(duration_seconds).zfill(3)  + '_'+ str(recording_Id) + '.wav'              
        audio_file_name = str(recording_Id) + '_' + tag_name + '_'  + str(start_time_seconds).zfill(3)  + '.wav'              
       
        audio_out_path = './' + parameters.tagged_recordings_folder + '/' + audio_file_name
      
        y, sr = librosa.load(audio_in_path, sr=None) 
        
#        print('y shape is', y.shape)
        
#        clip_start_array = int((sr * start_time_seconds/8))
        clip_start_array = int((sr * start_time_seconds))
        clip_end_array = clip_start_array + int((sr * duration_seconds))
        
#        print('length of y is ', y.shape[0], '\n')
#        print('end of clip is ', clip_end_array, '\n')
        
        if clip_end_array > y.shape[0]:
            print('Clip would end after end of recording')
            return
        
        clip_call_by_array = y[clip_start_array:clip_end_array]  
        
        
#        print('clip_call_by_array shape is ', clip_call_by_array.shape, '\n')
#        print('clip_call_by_array length is ', clip_call_by_array.shape[0], '\n')
        
#        clip_length_secs = clip_call_by_array.shape[0] / sr
        
#        print(audio_file_name, ' has a length of ', clip_length_secs, ' seconds \n')
        
        #Save the file 
        wavfile.write(filename=audio_out_path, rate=sr, data=clip_call_by_array)
        
        # Also update the csv file that is used for telling the model what recording is what
        add_information_to_csv_file(audio_file_name, tag_name)
      
#        print('\tCreated a ' + str(tag_name) + ' clip from recording ' +  str(recording_Id) + '\n')
#        print('\tCreated clip ', audio_out_path, ' \n')
    except Exception as e:       
        print('\t\tUnable to create clip_id ' + str(tag_id) + ' from recording ' +  str(recording_Id) + '. Probably an incorrect tag\n')
    

def test_create_tagged_recording_as_wav():
    create_tagged_recording_as_wav(recording_Id='158824', start_time_seconds=1, duration_seconds=1, tag_name='possum', tag_id=5)

        
def add_information_to_csv_file(audio_file_name, tag_name):
    row = [audio_file_name, tag_name]
    
    with open('sound_clips.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)

    csvFile.close()
    
def test_add_information_to_csv_file():
    add_information_to_csv_file(audio_file_name='ab2.123', tag_name='boo')
    

def test_convert_file_from_raw_to_librosa_array():
    
    test_file = '158698.m4a'
    audio_in_path = './raw_recordings/' + test_file
    pickled_path = './converted_recordings/' + test_file
    
    y, sr = librosa.load(audio_in_path)
    print(y, sr, y.shape)
        
#    # Good time to remove low frequency noise
#    y = highpass_filter(y, sr)
    
    with open(pickled_path, 'wb') as f:
        pickle.dump(y, f, pickle.HIGHEST_PROTOCOL)
        
    with open(pickled_path, 'rb') as f:
        # The protocol version used is detected automatically, so we do not
        # have to specify it.
        data = pickle.load(f)  
#        
#   
   # print(pickled_path)    
    y, sr = librosa.load(data)
    print(sr)
    print(y)
        
    
            
     
def test_create_tagged_recording():
    recording_Id = 156258
    start_time_seconds = 2.2
    duration_seconds = 6.34
    tag_name = 'test_moa'
    tag_id = 123456
    create_tagged_recording(recording_Id= recording_Id, start_time_seconds=start_time_seconds, duration_seconds=duration_seconds, tag_name=tag_name, tag_id=tag_id)
    
 
#https://stackoverflow.com/questions/26835477/pickle-load-variable-if-exists-or-create-and-save-it
def get_id_of_last_processed_tag():
    path = './pickles/last_tag.p'
    default = 1
    if os.path.isfile(path):
        with open(path, "rb") as f:
            try:
                return pickle.load(f)
            except Exception: # so many things could go wrong, can't be more specific.
                pass 
    with open(path, "wb") as f:
        pickle.dump(default, f)
    return default

def retrieve_available_recordings_from_server(device_name):  
#    device_name = input("Enter the device name ")
    # Create directory for recordings
    folder_for_device = parameters.downloaded_recordings_folder + '/' + device_name
    if not os.path.exists(folder_for_device):
        os.makedirs(folder_for_device)
  
    ids_of_recordings_to_download = get_recording_ids_for_device_name(device_name)
    
    # remove ids of recordings that we already have
    already_downloaded = []
    for file in os.listdir(folder_for_device):
        already_downloaded.append(os.path.splitext(file)[0])
       
    already_downloaded_set = set(already_downloaded)  
        
    ids_of_recordings_to_still_to_download = []
    
    for recording_id in ids_of_recordings_to_download:
         if not recording_id in already_downloaded_set:
           ids_of_recordings_to_still_to_download.append(recording_id)
         else:
             print('Aleady have recording ',recording_id, ' so will not download')
       
    for recording_id in ids_of_recordings_to_still_to_download:
        print('About to get token for downloading ',recording_id)
        token_for_retrieving_recording = get_token_for_retrieving_recording(recording_id)
        print('About to get recording ',recording_id)
        get_recording_from_server(token_for_retrieving_recording, recording_id, device_name)
        

def plot_recording(filename): 

    audio_in_path = './' + parameters.downloaded_recordings_folder + '/' + str(filename)     
      
    y, sr = librosa.load(audio_in_path, sr=None) 
    plt.plot(y)
    plt.show()
        

def test_plot_recording():   
    plot_recording('153003.m4a')
    
def plot_all_recordings():
    count = 0
    for filename in os.listdir(parameters.downloaded_recordings_folder):
        print('filename is ', filename)
        
        plot_recording(filename)
        count += 1
        if count > 10:
            print('count ',count)
            break

def test_plot_all_recordings():
    plot_all_recordings()
    
#def apply_low_and_high_pass_filter(filename):
#    audio_in_path = './' + parameters.downloaded_recordings_folder + '/' + str(filename)   
#    y, sr = librosa.load(audio_in_path, sr=None)
#    y = highpass_filter(y, sr)
#    return y, sr

def apply_low_and_high_pass_filter(y, sr):    
    y = highpass_filter(y, sr)
    plot_mel_scaled_power_spectrogram (y, sr)
    y = apply_lowpass_filter(y, sr)
    plot_mel_scaled_power_spectrogram (y, sr)
    return y, sr

def test_highpass_filter():
    filename = '153003.m4a'
    audio_in_path = './' + parameters.downloaded_recordings_folder + '/' + str(filename) 
    y, sr = librosa.load(audio_in_path, sr=None)
    plot_mel_scaled_power_spectrogram (y, sr)
    y = highpass_filter(y, sr)
    plot_mel_scaled_power_spectrogram (y, sr)
    
def test_lowpass_filter():
    filename = '153003.m4a'
    audio_in_path = './' + parameters.downloaded_recordings_folder + '/' + str(filename) 
    y, sr = librosa.load(audio_in_path, sr=None)
    plot_mel_scaled_power_spectrogram (y, sr)
    y = apply_lowpass_filter(y, sr)
    plot_mel_scaled_power_spectrogram (y, sr)
    
def apply_band_pass_filter(y, sr):
#    y = highpass_filter(y, sr)
    y = highpass_filter_with_parameters(y=y, sr=sr, filter_stop_freq=750, filter_pass_freq=800 )
    y = apply_lowpass_filter(y, sr)    
    return y
    
    
        
def test_apply_low_and_high_pass_filter():
    filename = '153003.m4a'
    audio_in_path = './' + parameters.downloaded_recordings_folder + '/' + str(filename) 
    
    y, sr = librosa.load(audio_in_path, sr=None)
    plot_mel_scaled_power_spectrogram (y, sr)
    
    y = highpass_filter(y, sr)
    y = apply_lowpass_filter(y, sr)
    
    plot_mel_scaled_power_spectrogram (y, sr)
    
    
def plot_mel_scaled_power_spectrogram (y, sr):
        
    S = librosa.feature.melspectrogram(y, sr=sr, n_mels=128)
    
    plt.plot(S)
    plt.show()


def play_sound_file(filename):
    audio_in_path = './' + parameters.downloaded_recordings_folder + '/' + filename
    
#    audio_in_path = './' + parameters.downloaded_recordings_folder + '/' + str(filename)
#    audio_in_path = './' + parameters.tagged_recordings_folder + '/' + str(filename)
    
#    audio_in_path = './' + parameters.tagged_recordings_folder + '/' + filename
#    audio_in_path = './' + parameters.downloaded_recordings_folder + '/' + filename
#    song = AudioSegment.from_wav(audio_in_path)
#    play(song)
    
#    player = Player()
#    player.loadfile(audio_in_path)
#    os.system("mpg123 " + audio_in_path)
    import librosa
    #x, sr = librosa.load('./UrbanSound8K/audio/fold1/7061-6-0-0.wav')
#    x, sr = librosa.load(parent_dir + "/fold1//7061-6-0-0.wav") 
    x, sr = librosa.load(audio_in_path) 
    print(x.shape)
    print(sr)
#    import IPython.display as ipd
    ipd.Audio(x, rate=sr) # load a NumPy array
    
def test_play_sound_file():
#    filename = '151837_bird_27.18.wav'
#    filename = '153003.m4a'
#    play_sound_file(filename)
#    play_sound_file('153003.m4a')
#    play_sound_file('151837_bird_27.18.wav')
#    audio_in_path = './' + parameters.tagged_recordings_folder + '/' + '151837_bird_27.18.wav'
#    song = AudioSegment.from_wav(audio_in_path)
#    play(song)
    filename = '20190611161936_026_02278_153003.m4a'
    input_folder = './clips_from_filtered_recordings/'
    audio_in_path = input_folder + '/' + filename
    playsound(audio_in_path)
    


def create_filtered_files(device_name):
#    input_folder = 'morepork_recordings'
    input_folder = parameters.downloaded_recordings_folder + '/' + device_name + '/' + 'night_recording'
    
    output_folder = parameters.filtered_recordings_folder + '/' + device_name + '/' + 'night_recording'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    print('About to create filtered recordings in: ', output_folder, '\n')
    
    for filename in os.listdir(input_folder):
        audio_in_path = './' + input_folder + '/' + str(filename)
        output_filename =  filename = os.path.splitext(filename)[0] + '.wav'
        audio_out_path = './' + output_folder + '/' + str(output_filename) 
        y, sr = librosa.load(audio_in_path, sr=None)
        y = apply_band_pass_filter(y, sr)
        wavfile.write(filename=audio_out_path, rate=sr, data=y)
        print('Created filtered recording: ', filename, '\n')
    
    print('Finished creating filtered recordings from device: ', device_name, '\n')
    
def create_onsets_from_unfiltered(input_folder):

    
    output_folder = input_folder + 'filtered_recordings' + device_name + '/' + 'night_recording'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    print('About to create filtered recordings in: ', output_folder, '\n')
    
    for filename in os.listdir(input_folder):
        audio_in_path = './' + input_folder + '/' + str(filename)
        output_filename =  filename = os.path.splitext(filename)[0] + '.wav'
        audio_out_path = './' + output_folder + '/' + str(output_filename) 
        y, sr = librosa.load(audio_in_path, sr=None)
        y = apply_band_pass_filter(y, sr)
        wavfile.write(filename=audio_out_path, rate=sr, data=y)
        print('Created filtered recording: ', filename, '\n')
    
    print('Finished creating filtered recordings from device: ', device_name, '\n')
    
def remove_cicada_noise():
    import noisereduce as nr
#    audio_in_path = './' + input_folder + '/' + str(filename)
    cicada_audio_in_path = './Noise examples/cicadas.wav'
#    rate, noisey_data = wavfile.read(cicada_audio_in_path)
    noisey_data, rate = librosa.load(cicada_audio_in_path, sr=None)
    
    recording_to_clean = './files_for_testing/153036.m4a'
#    rate, to_clean_data = wavfile.read(recording_to_clean)
    to_clean_data, rate = librosa.load(recording_to_clean, sr=None)
    
    # select section of data that is noise
#    noisy_part = data[10000:15000]
    # perform noise reduction
    reduced_noise = nr.reduce_noise(audio_clip=to_clean_data, noise_clip=noisey_data, verbose=True)
    print(reduced_noise)
    
#    ipd.Audio( reduced_noise,rate=rate)
#    ipd.plot()
    
    
    
#    audio_out_path = './test_samples/153036_noise_reduced.wav'
#    wavfile.write(filename=audio_out_path, rate=rate, data=reduced_noise)
    
def test_remove_cicada_noise():
    remove_cicada_noise()
    
    
def NoiseReduction(data, sampleRate, verbose, device_name ):
    input_folder = parameters.downloaded_recordings_folder + '/' + device_name
    
    output_folder = parameters.filtered_recordings_folder + '/' + device_name
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    print('About to create filtered recordings in: ', output_folder, '\n')
    
    
    originalSampleCount = data.shape[0]

    dctWidth = 2048
    window = TukeyWindow(dctWidth)
    trimWidth = int(dctWidth/8)
    stride = dctWidth-trimWidth*3

    blockCount = int((originalSampleCount+stride-1)/stride)
    dataPad = numpy.pad(data, (stride, stride*2), 'reflect')
    spectrogram = numpy.empty((blockCount, dctWidth))

    if verbose:
        print('Building spectrogram')

    for index in range(blockCount):
        blockIndex = index*stride
        block = dataPad[blockIndex:blockIndex+dctWidth]*window
        dct = scipy.fftpack.dct(block)
        spectrogram[index] = dct

    # build the tolerance
    binMedians = numpy.median(abs(spectrogram), axis=0)
    tolerance = 4*numpy.convolve(binMedians, numpy.ones(8)/8)[4:-3]

    spectrogramTrimmed = numpy.empty((blockCount, dctWidth))

    bassCutOffFreq = 500  # anything below bassCutOffFreq requires specialised techniques
    bassCutOffBand = int(bassCutOffFreq*2*dctWidth/sampleRate)

    trebleCutOffFreq = 1000
    trebleCutOffBand = int(trebleCutOffFreq*2*dctWidth/sampleRate)

    if verbose:
        print('Creating bins for noise reduction')

    rmsTab = numpy.empty(blockCount)
    for index in range(blockCount):
        blockIndex = index*stride
        block = dataPad[blockIndex:blockIndex+dctWidth]*window
        dct = scipy.fftpack.dct(block)

        mask = numpy.ones_like(dct)

        mask[:bassCutOffBand] *= 0
        mask[trebleCutOffBand:] *= 0
        rmsTab[index] = rms(dct*mask)

        for band in range(dctWidth):
            if abs(dct[band]) < tolerance[band]:
                mask[band] *= 0.0

        maskCon = 10*numpy.convolve(mask, numpy.ones(8)/8)[4:-3]

        maskBin = numpy.where(maskCon > 0.1, 0, 1)
        spectrogramTrimmed[index] = maskBin

    resultPad = numpy.zeros_like(dataPad)

    if verbose:
        print('noise floor..')
    rmsCutoff = numpy.median(rmsTab)

    if verbose:
        print('Reconstruction...')

    for index in range(1, blockCount-1):
        blockIndex = index*stride
        block = dataPad[blockIndex:blockIndex+dctWidth]*window
        dct = scipy.fftpack.dct(block)

        trim3 = spectrogramTrimmed[index-1] * \
            spectrogramTrimmed[index]*spectrogramTrimmed[index+1]
        dct *= (1-trim3)

        if rms(dct) < rmsCutoff:
            continue  # too soft
# if rms_nonzero(dct)*4>max(dct):
# continue #white noise

        rt = scipy.fftpack.idct(dct)/(dctWidth*2)
        resultPad[blockIndex+trimWidth*1:blockIndex+trimWidth *
                  2] += rt[trimWidth*1:trimWidth*2]*numpy.linspace(0, 1, trimWidth)
        resultPad[blockIndex+trimWidth*2:blockIndex+trimWidth *
                  6] = rt[trimWidth*2:trimWidth*6]  # *numpy.linspace(1,1,stride8*4)
        resultPad[blockIndex+trimWidth*6:blockIndex+trimWidth *
                  7] = rt[trimWidth*6:trimWidth*7]*numpy.linspace(1, 0, trimWidth)

    result = resultPad[stride:stride+originalSampleCount]

    if verbose:
        stereoPad = numpy.zeros((dataPad.shape[0], 2))
        stereoPad[:, 0] = dataPad
        stereoPad[:, 1] = resultPad
        wavio.write('temp/stereoPad.wav', stereoPad,
                    sampleRate, (-1, 1), sampwidth=2)

        stereo = numpy.zeros((originalSampleCount, 2))
        stereo[:, 0] = data
        stereo[:, 1] = result
        wavio.write('temp/stereoCompare.wav', stereo,
                    sampleRate, (-1, 1), sampwidth=2)

#    tempOut = 'temp/noiseReduce.wav'
    tempOut = 'temp/noiseReduce.wav'
    if verbose:
        print('Write to %s' % 'temp/noiseReduce.wav')
        wavio.write(tempOut, result, sampleRate, (-1, 1), sampwidth=2)

        print('Convert to MP3 (requires libmp3lame)')
        cmd = '%s -y -i %s -codec:a libmp3lame -qscale:a 2 noiseReduce.mp3' % (
            ffmpegEXE, 'temp/noiseReduce.wav')
        print(cmd)
        sys.stdout.flush()
        os.system(cmd)

    return result

def create_filtered_files_Chris(device_name):
#    input_folder = 'morepork_recordings'
    input_folder = parameters.downloaded_recordings_folder + '/' + device_name
    
    output_folder = parameters.filtered_recordings_folder + '/' + device_name
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    print('About to create filtered recordings in: ', output_folder, '\n')
    
    for filename in os.listdir(input_folder):
        audio_in_path = './' + input_folder + '/' + str(filename)
        output_filename =  filename = os.path.splitext(filename)[0] + '.wav'
        audio_out_path = './' + output_folder + '/' + str(output_filename) 
        y, sr = librosa.load(audio_in_path, sr=None)
#        y = apply_band_pass_filter(y, sr)
        
        
        
        
        
        wavfile.write(filename=audio_out_path, rate=sr, data=y)
        print('Created filtered recording: ', filename, '\n')
    
    print('Finished creating filtered recordings from device: ', device_name, '\n')
    

        
# Extract clips from single file
#def extract_clips_from_single_filtered_reocording(device_name, file_to_process):
#    input_folder = './' + parameters.filtered_recordings_folder + '/' + device_name +'/night_recording/'
##    input_folder = parameters.filtered_recordings_folder + '/' + device_name
##    input_folder = parameters.downloaded_recordings_folder + '/' + device_name
#    output_folder = parameters.clips_from_filtered_recordings + '/' + device_name
#    if not os.path.exists(output_folder):
#        os.makedirs(output_folder)
#    
#    audio_in_path = './' + input_folder + '/' + str(file_to_process)
#    
##    print('audio_in_path', audio_in_path)
#    y, sr = librosa.load(audio_in_path)
##    print(sr, sr)
##    librosa.display.waveplot(y, sr=sr)
##    plt.show()
#    
##    y = y / max(y) * 16384 # Suggested by Chris Blackbourn to fix problem with finding onsets - didn't work
##    y = y * 30 # Suggested by Chris Blackbourn to fix problem with finding onsets - didn't work
#    y = y / max(y) # Suggested by Chris Blackbourn to fix problem with finding onsets - didn't work
##    y = y*1000
##    librosa.display.waveplot(y, sr=sr)
##    plt.show()
#    
##    librosa.output.write_wav('./' + output_folder + '/' + 'test1.wav' , y, sr)
##    print('y', y)
#    hop_length = 256
##    onset_envelope = librosa.onset.onset_strength(y, sr, hop_length=hop_length)
##    onset_envelope = librosa.onset.onset_strength(y=y, sr=sr)
##    librosa.display.waveplot(onset_envelope, sr=sr)
##    plt.show()
#    
##    y, sr = librosa.load(librosa.util.example_audio_file(),
##                      duration=10.0)
#    
#    y, sr = librosa.load(audio_in_path)
#    
#    librosa.display.waveplot(y, sr=sr)
#    plt.show()
#    
#    D = np.abs(librosa.stft(y))
#    times = librosa.frames_to_time(np.arange(D.shape[1]))
#    plt.figure()
#    ax1 = plt.subplot(2, 1, 1)
#    librosa.display.specshow(librosa.amplitude_to_db(D, ref=np.max),
#                          y_axis='log', x_axis='time')
#    plt.title('Power spectrogram')    
#    
#    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
#    plt.subplot(2, 1, 2, sharex=ax1)
#    plt.plot(times, 2 + onset_env / onset_env.max(), alpha=0.8,
#          label='Mean (mel)')
#    
#    onset_env = librosa.onset.onset_strength(y=y, sr=sr,
#                                          aggregate=np.median,
#                                          fmax=8000, n_mels=256)
#    plt.plot(times, 1 + onset_env / onset_env.max(), alpha=0.8,
#          label='Median (custom mel)')
#    
#    onset_env = librosa.onset.onset_strength(y=y, sr=sr,
#                                          feature=librosa.cqt)
#    plt.plot(times, onset_env / onset_env.max(), alpha=0.8,
#          label='Mean (CQT)')
#    plt.legend(frameon=True, framealpha=0.75)
#    plt.ylabel('Normalized strength')
#    plt.yticks([])
#    plt.axis('tight')
#    plt.tight_layout()
#    
##    D = np.abs(librosa.stft(y))
##    times = librosa.frames_to_time(np.arange(D.shape[1]))
##    plt.figure()
##    ax1 = plt.subplot(2, 1, 1)
##    librosa.display.specshow(librosa.amplitude_to_db(D, ref=np.max),
##                          y_axis='log', x_axis='time')
##    plt.title('Power spectrogram')
###    plt.show()
##    
##    onset_env = librosa.onset.onset_strength(y=y, sr=sr,aggregate=np.median, fmax=8000, n_mels=256)
##    
###    librosa.display.waveplot(onset_env / onset_env.max(), sr=sr)
###    plt.show()
##    
##    plt.plot(times, 1 + onset_env / onset_env.max(), alpha=0.8,
##    label='Median (custom mel)')
###    plt.show()
##    
##    print('onset_envelope.shape', onset_envelope.shape)
##    print('onset_envelope ', onset_envelope)
##    print('onset_envelope.shape ', onset_envelope.shape)
##    N = len(y)
##    T = N/float(sr)
##    t = np.linspace(0, T, len(onset_envelope))
##    plt.figure(figsize=(14, 5))
##    plt.plot(t, onset_envelope)
##    plt.xlabel('Time (sec)')
##    plt.xlim(xmin=0)
##    plt.ylim(0)
##    plt.show()
##    
#    
#    
#    # Use function to pick the peaks - I still need to learn how to adjust the parameters - these are straight from example
##    onset_frames = librosa.util.peak_pick(onset_envelope, 7, 7, 7, 7, 0.5, 5)
##    onset_frames = librosa.onset.onset_detect(y, sr=sr, wait=1, pre_avg=1, post_avg=1, pre_max=1, post_max=1)
##    
##    print('onset_frames ', onset_frames)
##    
##    # If more onsets than 10, assume it is cicadas/rain or someother issue
##    if len(onset_frames) > 10:
##        print('Too many onsets, so skipping this file')
##        return
##    # Create and save the clips
##    clip_length_secs = 1
##    previous_start_postion_in_seconds = -1
##    for onset in onset_frames:
###        now = datetime.now() 
##        bird_start_array = (onset * hop_length) - int((sr * clip_length_secs/8))
##        bird_end_array = bird_start_array + int((sr * clip_length_secs))
##        bird_call_by_array = y[bird_start_array:bird_end_array]
##        start_position_in_seconds = str(int(bird_start_array / sr))
##        if start_position_in_seconds != previous_start_postion_in_seconds:
##                        
##            audio_out_filename = os.path.splitext(file_to_process)[0] + '_' + start_position_in_seconds + '.wav'
##            audio_out_path = './' + output_folder + '/' + audio_out_filename
##            print('Created ', audio_out_filename)
##            librosa.output.write_wav(audio_out_path, bird_call_by_array, sr)       
##
##        previous_start_postion_in_seconds = start_position_in_seconds   
        
def FindSquawks2(source, sampleRate):
    result = []
    source = source / max(source)
    startIndex = None
    stopIndex = None
    smallTime = int(sampleRate*0.1)
    tolerance = 0.2
    for index in range(source.shape[0]):
        if not startIndex:
            if abs(source[index]) > tolerance:
                startIndex = index
                stopIndex = index
            continue
        if abs(source[index]) > tolerance:
            stopIndex = index
        elif index > stopIndex+smallTime:
            duration = (stopIndex-startIndex)/sampleRate
            if duration > 0.05:
                squawk = {'start': startIndex,
                          'stop': stopIndex, 'duration': duration}
                squawk['rms'] = rms(source[startIndex:stopIndex])
                result.append(squawk)
            startIndex = None
    return result        

#def extract_clips_from_folder_of_filtered_reocordings(device_name):
#    input_folder = './' + parameters.filtered_recordings_folder + '/' + device_name +'/night_recording/'
#    output_folder = './' + parameters.clips_from_filtered_recordings + '/' + device_name
#    
#    for filename in os.listdir(input_folder):
##    filename = '153036.wav'
#       
#        audio_in_path = input_folder + filename
#        y, sr = librosa.load(audio_in_path)
#        squawks_to_keep = extract_more_pork_squawks_from_single_filtered_reocording(y, sr)
#        if len(squawks_to_keep) > 10:
#            print(filename, ' has more than 10 squawks so discarding them all\n')
#            squawks_to_keep = []
#            
#        for squawk in squawks_to_keep:
#            recording_id = os.path.splitext(filename)[0]
#            start_positon = int(squawk['start'])
#            end_position = int(start_positon + (1.5 * sr))
#            start_positon_seconds = int(start_positon/sr)
#            filename_with_start_time = recording_id + '_' + str(start_positon_seconds) + '.wav'
#            audio_out_path = output_folder + '/' + filename_with_start_time
#            
#    #            bird_start_array = (onset * hop_length) - int((sr * clip_length_secs/8))
#    #            bird_end_array = bird_start_array + int((sr * clip_length_secs))
#            bird_call_by_array = y[start_positon:end_position]
#            
#            librosa.output.write_wav(audio_out_path, bird_call_by_array, sr)
#            
#        
#        
##    extract_clips_from_single_filtered_reocording('0070_v1_3_6', '153036.wav')
##    extract_clips_from_single_filtered_reocording('0070_v1_3_6', '153036.m4a')

#def find_paired_peaks_in_single_recordings(audio_in_path, sr):
#    log_filt_spec = madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(audio_in_path, num_bands=24)
#    superflux_3 = madmom.features.onsets.superflux(log_filt_spec)
#    librosa.display.waveplot(superflux_3, sr=sr)
#    plt.plot()
##    peak_frames = librosa.util.peak_pick(superflux_3, 10, 10, 10, 10, 0.1, 10)
#    peak_frames = librosa.util.peak_pick(superflux_3, 7, 7, 7, 7, 0.1, 5)
##    print('peak_frames', peak_frames)
#    peaks_secs = librosa.frames_to_time(peak_frames, sr=sr)
#    print('peaks_secs ', peaks_secs, '\n')
#    
#    paired_peaks_sec = []
#    prev_peak_sec = None
#    for peak_sec in enumerate(peaks_secs):      
#        if prev_peak_sec == None:
#            prev_peak_sec = peak_sec
#            continue
#        
##        start_current_peak = (num, peaks_sec)[1]
##        
##        start_previous_peak = (prev_num, peaks_sec)[1]  
##        
##        print('start_current_peak ', start_current_peak, '\n')
##        print('start_previous_peak ', start_previous_peak, '\n')
#                
##        time_between_peaks = start_current_peak - start_previous_peak
#            
##        print('peak_sec ', peak_sec[1], '\n')
##        print('prev_peak_sec ', prev_peak_sec[1], '\n')
#        
#        time_between_peaks = peak_sec[1] - prev_peak_sec[1]
#        print('time_between_peaks ', time_between_peaks)
#        
#        if time_between_peaks < 0.8: # sr is one second, so hoping this is the second part of more pork
#            print('Going to keep peak\n')
#            paired_peaks_sec.append(prev_peak_sec[1])
#        else:
#             print('Going to Disguard peak\n')
#        
#        prev_peak_sec = peak_sec
#        
#    return paired_peaks_sec
    
def FindSquawks(source, sampleRate):
    result = []
    source = source / max(source)
    startIndex = None
    stopIndex = None
    smallTime = int(sampleRate*0.1)
    tolerance = 0.2
    for index in range(source.shape[0]):
        if not startIndex:
            if abs(source[index]) > tolerance:
                startIndex = index
                stopIndex = index
            continue
        if abs(source[index]) > tolerance:
            stopIndex = index
        elif index > stopIndex+smallTime:
            duration = (stopIndex-startIndex)/sampleRate
            if duration > 0.05:
                squawk = {'start': startIndex,
                          'stop': stopIndex, 'duration': duration}
                squawk['rms'] = rms(source[startIndex:stopIndex])
                result.append(squawk)
            startIndex = None
    return result


#def find_paired_squawks_in_single_recordings(audio_in_path, sr):
#    log_filt_spec = madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(audio_in_path, num_bands=24)
#    superflux_3 = madmom.features.onsets.superflux(log_filt_spec)
#    librosa.display.waveplot(superflux_3, sr=sr)
#    plt.plot()
##    peak_frames = librosa.util.peak_pick(superflux_3, 10, 10, 10, 10, 0.1, 10)
#    peak_frames = librosa.util.peak_pick(superflux_3, 7, 7, 7, 7, 0.1, 5)
##    print('peak_frames', peak_frames)
#    peaks_secs = librosa.frames_to_time(peak_frames, sr=sr)
#    print('peaks_secs ', peaks_secs, '\n')
def find_paired_squawks_in_single_recordings(y, sr):
#    y, sr = librosa.load(audio_in_path)
    squawks = FindSquawks(y, sr)
#    print('squawks ', squawks)
    squawks_secs = []
#    print(squawks)
    for squawk in squawks:
        squawk_start = squawk['start']
#        print('squawk_start ', squawk_start, '\n')
        squawk_start_sec = squawk_start / sr
#        print('squawk_start_sec ', squawk_start_sec, '\n\n')
        squawks_secs.append(round(squawk_start_sec, 1))
    
#    print('squawks ,' squawks, '\n')
    
    paired_squawks_sec = []
    prev_squawk_sec = None
    
    for squawk_sec in enumerate(squawks_secs):      
        if prev_squawk_sec == None:
            prev_squawk_sec = squawk_sec
            continue     
        
        time_between_squawks = squawk_sec[1] - prev_squawk_sec[1]
#        print('time_between_squawks ', time_between_squawks)
        
        if time_between_squawks < 0.8: # sr is one second, so hoping this is the second part of more pork
#            print('Going to keep squawk\n')
            paired_squawks_sec.append(prev_squawk_sec[1])
#        else:
#             print('Going to Disguard squawk\n')
        
        prev_squawk_sec = squawk_sec
        
    return paired_squawks_sec
            
def create_squawks_from_recordings(device_name):
    input_folder = './' + parameters.filtered_recordings_folder + '/' + device_name +'/night_recording/'
    output_folder_for_processed_recordings = './' + parameters.filtered_recordings_folder + '/' + device_name +'/night_recording/processed_recordings' 
    output_folder_for_squawk_info = './' + parameters.squawks_from_filtered_recordings + '/' + device_name
    
    
    if not os.path.exists(output_folder_for_squawk_info):
        os.makedirs(output_folder_for_squawk_info)
        
    if not os.path.exists(output_folder_for_processed_recordings):
        os.makedirs(output_folder_for_processed_recordings)
    
    count = 0
    total_number_of_files = len(os.listdir(input_folder))
#    for filename in os.listdir(input_folder):
    with os.scandir(input_folder) as entries:
        for entry in entries:
            print(entry.name)
            if entry.is_file():
                filename = entry.name
            else:
                continue
        
            count+=1
            print('Processing file ', count, ' of ', total_number_of_files, ' files.')
    #    filename = '225217.wav'
       
            audio_in_path = input_folder + filename
            y, sr = librosa.load(audio_in_path)
            
        
            paired_squawks_sec = find_paired_squawks_in_single_recordings(y, sr)
            print('paired_squawks_sec', paired_squawks_sec)
            if not len(paired_squawks_sec) == 0:
                print('paired_squawks_sec ', paired_squawks_sec, '\n')
                recording_id = os.path.splitext(filename)[0]
                f = open(output_folder_for_squawk_info + '/' + recording_id + '.txt', 'w')
                json.dump(paired_squawks_sec, f)
                f.close()
            
            # move filtered recording to clips_info_made folder
            audio_out_path = output_folder_for_processed_recordings + '/' + filename
            print('Moving ', filename, ' to ', audio_out_path)
            os.rename(audio_in_path, audio_out_path)
        
      

    
def extract_more_pork_peaks_from_single_filtered_reocording(audio_in_path):
    y, sr = librosa.load(audio_in_path) # just need sr for later
    log_filt_spec = madmom.audio.spectrogram.LogarithmicFilteredSpectrogram('madmom/151980.wav', num_bands=24)
    superflux_3 = madmom.features.onsets.superflux(log_filt_spec)
    peaks = librosa.util.peak_pick(superflux_3, 10, 10, 10, 10, 0.1, 10)
    peaks_to_keep = []
    for num, peak in enumerate(peaks):
        if num == 0:
            continue
        start_previous_peak = peaks[num -1]
        start_current_peak = peaks[num]
        time_between_peaks = start_current_peak - start_previous_peak
        if time_between_peaks < sr: # sr is one second, so hoping this is the second part of more pork
             peaks_to_keep.append(peaks[num -1])
     
    return peaks_to_keep
    
#def extract_more_pork_squawks_from_single_filtered_reocording(y, sr):  
#  
##    y, sr = librosa.load(audio_in_path)
#    ##squawks = FindSquawks2(y, sr)
#    
#    print('Number of squawks is ', len(squawks)) 
##    print('sr ', sr)
#    squawks_to_keep = []   
##    for squawk in squawks:
#    for num, squawk in enumerate(squawks):
#        if num == 0:
#            continue
#        start_previous_squawk = squawks[num -1]['start']
#        start_current_squawk = squawks[num]['start']
#        time_between_squawks = start_current_squawk - start_previous_squawk
#        if time_between_squawks < sr: # sr is one second, so hoping this is the second part of more pork
#             squawks_to_keep.append(squawks[num -1])
#             print('Start time ', start_previous_squawk / sr) 
#    
##    print('Number of squawks to keep is ', len(squawks_to_keep), '\n')
#     
#    return squawks_to_keep
#    
   
            
            
def test_extract_clips_from_folder_of_filtered_reocordings():
    device_name = '0070_v1_3_6'
    extract_clips_from_folder_of_filtered_reocordings(device_name)     
       
    
def rms(x):
        # Root-Mean-Square
    return np.sqrt(x.dot(x)/x.size)

def FindSquawks_Tim(device_name, file_to_process):
    input_folder = parameters.filtered_recordings_folder + '/' + device_name
    output_folder = parameters.clips_from_filtered_recordings + '/' + device_name
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    audio_in_path = './' + input_folder + '/' + str(file_to_process)
    
#    print('audio_in_path', audio_in_path)
    source, sampleRate = librosa.load(audio_in_path)
#    print('sampleRate', sampleRate)
    librosa.display.waveplot(source, sr=sampleRate)
    plt.show()
    
    result = []
    source = source / max(source)
    startIndex = None
    stopIndex = None
    smallTime = int(sampleRate*0.1)
    moreporkCallTime = int(sampleRate*1.5)
#    tolerance = 0.2
#    tolerance = 0.4
    tolerance = 0.6
    prevStartIndex = -1
    for index in range(source.shape[0]):
        # Ignore if index is too close to previous
        if (prevStartIndex >= 0):
            if (index - prevStartIndex) < moreporkCallTime:
                continue
        if not startIndex:
            if abs(source[index]) > tolerance:
                startIndex = index
                stopIndex = index
            continue
        if abs(source[index]) > tolerance:
            stopIndex = index
        elif index > stopIndex+smallTime:
            duration = (stopIndex-startIndex)/sampleRate
            if duration > 0.05:
                prevStartIndex = startIndex 
                squawk = {'start': startIndex,
                          'stop': stopIndex, 'duration': duration}
                squawk['rms'] = rms(source[startIndex:stopIndex])
                bird_start_array = startIndex
                bird_end_array = bird_start_array + moreporkCallTime
                bird_call_by_array = source[bird_start_array:bird_end_array]
                audio_out_filename = os.path.splitext(file_to_process)[0] + '_' + str(int(startIndex/sampleRate)) + '.wav'
                audio_out_path = './' + output_folder + '/' + audio_out_filename
                print('Created ', audio_out_filename)
                librosa.output.write_wav(audio_out_path, bird_call_by_array, sampleRate) 
                result.append(squawk)
            startIndex = None
    return result

def test_FindSquawks_Tim():
   device_name = '0070_v1_3_6'
   file_to_process = '153036.wav'
   FindSquawks_Tim(device_name, file_to_process)
    
def create_clips(result):
    for result in result:
        print (result)
        

    
def extract_clips_from_all_filtered_recordings_from_single_device(device_name):
    input_folder = './' + parameters.filtered_recordings_folder + '/' + device_name +'/night_recording/'
    print('About to extract clips from filtered recordings')
    for filename in os.listdir(input_folder):
        extract_clips_from_single_filtered_reocording(device_name, filename)
#        FindSquawks_Tim(device_name, filename)
    
    print('Finished extracting clips from filtered recordings')

def get_recording_ids_for_device_name(device_name):
    
#    if not device_name_arg:
#        device_name = input("Enter the device name ")
##        print('device_name ', device_name)
#    else:
#        device_name = device_name_arg
        
    print('device_name ', device_name)
    
    device_id = get_device_id_using_device_name(device_name)
    print('device_id is ', device_id)
    ids_recordings_for_device_name = []
    offset = 0
    while True:
        ids_of_recordings_to_download= get_ids_of_recordings_to_download_using_deviceId(device_id,offset)
        print('ids_of_recordings_to_download ', ids_of_recordings_to_download)
        ids_recordings_for_device_name += ids_of_recordings_to_download
        if (len(ids_of_recordings_to_download) > 0):
            offset+=300
#            print('offset ', offset)
        else:
            break
    return ids_recordings_for_device_name

def test_get_recording_ids_for_device_name():
    ids_recordings_for_device_name = get_recording_ids_for_device_name('0064_20190605a')
    print('ids_of_recordings_to_download \n', ids_recordings_for_device_name)
    

def sort_into_day_or_night(device_name):
    input_folder = parameters.downloaded_recordings_folder + '/' + device_name
    night_sub_folder = input_folder + '/night_recording'
    if not os.path.exists(night_sub_folder):
        os.makedirs(night_sub_folder)
        
    day_sub_folder = input_folder + '/day_recording'
    if not os.path.exists(day_sub_folder):
        os.makedirs(day_sub_folder)
        
    errors_sub_folder = input_folder + '/errors'
    if not os.path.exists(errors_sub_folder):
        os.makedirs(errors_sub_folder)
    
    for filename in os.listdir(input_folder):
        if  not os.path.isfile(os.path.join(input_folder, filename)):
            continue     
                
        audio_in_path = './' + input_folder + '/' + filename
      
        night_recording = False
        
        # For recordings given to me by Menno, the filename is not just 123456.mp4, but has - in it.
        recording_id = filename.split('-')[0]
        #recording_id = os.path.splitext(filename)[0]
        recording_information = get_recording_information_for_a_single_recording(recording_id)
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
            audio_out_path = './' + night_sub_folder + '/' + filename
        else:
            audio_out_path = './' + day_sub_folder + '/' + filename
            
        
        os.rename(audio_in_path, audio_out_path)
       
            
     
     
     
           
def test_sort_into_day_or_night():
    device_name = '0070_v1_3_6'
    input_folder = parameters.downloaded_recordings_folder + '/' + device_name    
    sort_into_day_or_night(device_name, input_folder)
    
    
def create_squawk_pairs_from_unfiltered(inputFolder, onset_pairs_output_folder):
   
    count_of_onset_pairs_including_more_than_20 = 0
    count_of_onset_pairs_including_not_including_more_20 = 0
    
    count = 0
    total_number_of_files = len(os.listdir(inputFolder))
#    for filename in os.listdir(input_folder):
    with os.scandir(inputFolder) as entries:
        for entry in entries:
            try:
                print(entry.name)
                if entry.is_file():                  
                    filename = entry.name
                else:
                    continue
            
                count+=1
                print('Processing file ', count, ' of ', total_number_of_files, ' files.')
        #    filename = '225217.wav'
           
                audio_in_path = inputFolder + filename
                
                y, sr = librosa.load(audio_in_path)
                y = apply_band_pass_filter(y, sr)            
            
                paired_squawks_sec = find_paired_squawks_in_single_recordings(y, sr)
                #print('paired_squawks_sec', paired_squawks_sec)
                number_of_paired_squawks = len(paired_squawks_sec)
                if not number_of_paired_squawks == 0:
                    if number_of_paired_squawks > 20:
                        count_of_onset_pairs_including_more_than_20 += number_of_paired_squawks
                    else:
                        count_of_onset_pairs_including_more_than_20 += number_of_paired_squawks
                        count_of_onset_pairs_including_not_including_more_20 += number_of_paired_squawks                        
                   
                        # For recordings given to me by Menno, the filename is not just 123456.mp4, but has - in it.
                        recording_id = filename.split('-')[0]  
                        print('recording_id', recording_id)
                        output_filename = onset_pairs_output_folder +'/' + filename.split('.')[0] + '.txt'
                        print('output_filename', output_filename)
                        #recording_id = os.path.splitext(filename)[0]
                        #f = open(onset_pairs_output_folder + recording_id + '.txt', 'w')
                        f = open(output_filename, 'w')
                        json.dump(paired_squawks_sec, f)
                        f.close()
                print('count_of_onset_pairs_including_more_than_20 ', count_of_onset_pairs_including_more_than_20)
                print('count_of_onset_pairs_including_not_including_more_20 ', count_of_onset_pairs_including_not_including_more_20)
        
            except:
                print('Error processing file ', filename)


def create_800_1000_freq_mel_spectrogram_jps_using_onset_pairs(audio_files_folder, onset_pairs_input_folder, images_out_folder):
    count = 0
    total_number_of_files = len(os.listdir(onset_pairs_input_folder))
    
    for entry in os.scandir(onset_pairs_input_folder): 
        try:
            print('Processing file ', count, ' of ', total_number_of_files, ' files.')
            count+=1
    
            if entry.is_file():
                filename = entry.name       
            else:
                continue    
                    
            input_file_path = onset_pairs_input_folder + '/' + filename            
            file = open(input_file_path,"r+") 
            onset_pairs = file.read()
           
            # I stuffed up with the format of the onset_pairs text file, so had to do the following hack
            onset_pairs2 = onset_pairs.replace('[', '')
            onset_pairs3 = onset_pairs2.replace(']', '')
            onset_pairs4 = onset_pairs3.split(',')
            file.close
             
            for start_time_seconds in onset_pairs4:

                duration_seconds = 1.5                
   
                audio_filename = filename.split('.')[0] + '.mp4'
                audio_in_path = audio_files_folder + audio_filename
            
                image_out_path = images_out_folder + '/' + filename.split('.')[0] + '_' + start_time_seconds + '.jpg'
           
                y, sr = librosa.load(audio_in_path, sr=None) 
           
                start_time_seconds_float = float(start_time_seconds)            
                
                start_position_array = int(sr * start_time_seconds_float)              
                           
                end_position_array = start_position_array + int((sr * duration_seconds))
                           
                if end_position_array > y.shape[0]:
                    print('Clip would end after end of recording')
                    continue
                    
                y_part = y[start_position_array:end_position_array]  
                mel_spectrogram_800_1000_freq = librosa.feature.melspectrogram(y=y_part, sr=sr, n_fft=int(sr/10), hop_length=int(sr/10), n_mels=10, fmin=800,fmax=1000)
                
                pylab.axis('off') # no axis
                pylab.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[]) # Remove the white edge
                librosa.display.specshow(mel_spectrogram_800_1000_freq)
                pylab.savefig(image_out_path, bbox_inches=None, pad_inches=0)
                pylab.close()
            
        except:
                print('Error processing file ', filename)
                
        
                
    
    




















    
