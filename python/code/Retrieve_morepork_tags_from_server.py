#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 08:41:38 2019

@author: tim
"""

import functions
import parameters
import requests
import sys
import json
from pydub import AudioSegment
import os

device_name = 'fpF7B9AFNn6hvfVgdrJB'
specified_tag = 'more pork - classic'
out_file_path_name = 'list_of_tags2.txt'

wavs_for_AviaNZ_folder = 'Analysis/wavs_for_AviaNZ/'
downloaded_recordings_folder = 'downloaded_recordings/all_recordings/'
#recordings_folder = downloaded_recordings_folder + device_name + '/night_recording/'


def get_audio_recordings_with_tags_information_from_server(user_token, device_id, offset):
    print('Retrieving recordings basic information from Cacophony Server\n')
    print('offset is ', offset)
    url = parameters.server_endpoint + parameters.query_available_recordings
    
    where_param = {}
#    where_param['type'] = recording_type   
    where_param['duration'] = 59,60,61,62
    where_param['DeviceId'] = device_id
    json_where_param = json.dumps(where_param)
    #querystring = {"tagMode":"human-only", "where":json_where_param}   
#    querystring = {"where":json_where_param}  
    querystring = {"offset":offset, "where":json_where_param} 
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

def get_device_id_using_device_name(device_name):
    user_token = functions.get_cacophony_user_token()
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


        
def retrieve_list_of_recordings_with_specified_tag(device_name, specified_tag):
    print('retrieve_list_of_recordings_with_specified_tag')
    user_token = functions.get_cacophony_user_token()
    device_id = get_device_id_using_device_name(device_name)
    
    recording_basic_information = []
    offset = 0
    while True:   
#    while True and offset < 2000: # for testing
        page_of_recording_basic_information = get_audio_recordings_with_tags_information_from_server(user_token, device_id, offset)
        recording_basic_information += page_of_recording_basic_information
        if (len(page_of_recording_basic_information) > 0):
            offset+=300
#            print('offset ', offset)
        else:
            break
#        print(recording_basic_information)
       

    list_of_recording_ids_with_specified_tag = []
    for item in recording_basic_information:
#        print(item)
        recording_id = item['id']
#        print('recording_id ', recording_id)
        
        tags = item['Tags']
#        print('tags ', tags)
#        recording_has_morepork_classic_tag = False
        for tag in tags:
#            print('tag is ', tag)
            what = tag['what']
            print('what is ', what)
            if what == 'more pork - classic':
                list_of_recording_ids_with_specified_tag.append(recording_id)
                break
        
        
    print('List of recordings with ', specified_tag, ' tags: ', list_of_recording_ids_with_specified_tag)
    print('Number of recordings with ', specified_tag, ' tags: ', str(len(list_of_recording_ids_with_specified_tag)))
    return list_of_recording_ids_with_specified_tag

def retrieve_full_recording_info(list_of_recording_ids):
    print('starting retrieve_full_recording_info')
    list_of_full_information_of_recordings = []
    
    for recording_id in list_of_recording_ids: 
        print('\tRetrieve_full_recording_info for ', recording_id)
        
        # get the recording information
        recording_data_for_single_recording = get_recording_information_for_a_single_recording(recording_id)
        
        # append the recording information to list
        list_of_full_information_of_recordings.append(recording_data_for_single_recording)
        
#    # save list to disk
#    with open(out_file_path_name, 'w') as json_file:  
#        json.dump(list_of_full_information_of_recordings_with_tags, json_file)
        
    return list_of_full_information_of_recordings

def get_recording_information_for_a_single_recording(recording_id):
    user_token = functions.get_cacophony_user_token()

    get_a_token_for_recording_endpoint = parameters.server_endpoint + parameters.get_information_on_single_recording + str(recording_id)

    headers = {'Authorization': user_token}

    resp_for_getting_a_recordingToken = requests.request("GET", get_a_token_for_recording_endpoint, headers=headers)
    if resp_for_getting_a_recordingToken.status_code != 200:
        print('Could not get download token')
        return None
    recording_data_for_single_recording = resp_for_getting_a_recordingToken.json()
    
    return recording_data_for_single_recording

def extract_tags_for_single_audio_recording_from_single_recording_information(recording_info_for_single_recording, specified_tag): 
    tag_to_return = {}
    tags_to_return = []
    recording = recording_info_for_single_recording['recording']
    recording_id = recording['id']
    tags = {'tags':recording['Tags']}  
    tags2 = tags['tags']
    for tag in tags2:
        tag_to_return['recording_id'] = recording_id
#        what = tag['what']
        tag_to_return['what'] = tag['what']
#        start_time = tag['startTime']
        tag_to_return['startTime'] = tag['startTime']
#        print('tag_to_return ', tag_to_return)
        tags_to_return.append(tag_to_return)
        
#     print(tags2)
     
    return tags_to_return
 
def extract_tags_from_list_of_full_recording_info(full_recording_info_of_recordings_with_specified_tag, specified_tag):
    print('extract_tags_from_list_of_full_recording_info')
    all_specified_tags = []
    for recording_info_for_single_recording in full_recording_info_of_recordings_with_specified_tag:
        tags = extract_tags_for_single_audio_recording_from_single_recording_information(recording_info_for_single_recording, specified_tag)
        for tag in tags:
            if tag['what'] == specified_tag:
#                print('Found a ', specified_tag, ' tag')
#                print(tag)
                all_specified_tags.append(tag)    
        
        
    return all_specified_tags

def create_wav_clips_from_tags_file(tags_file):    
    
    with open(out_file_path_name, 'r') as f:
        tags = json.load(f)
        
        for tag in tags:
            try:
                recording_id = tag['recording_id']
                start_time = tag['startTime']
                clip_start = 1000 * start_time
                clip_end = clip_start + (1000 * 1.5)                      
               
                filename = str(recording_id) + '.m4a'
                print('filename is ', filename)
                audio_in_path = './' + downloaded_recordings_folder + filename
    
                if not os.path.exists(audio_in_path):
                    print('Do not have recording ', audio_in_path)
                    continue
                
                print('About to segment recording clip ', audio_in_path)    
                song = AudioSegment.from_file(audio_in_path, "m4a")
                recording_clip = song[int(clip_start):int(clip_end)]
                
               
                output_path = wavs_for_AviaNZ_folder +  str(recording_id) + '_' + str(start_time) + '.wav'
                print('About to create clip ', output_path)
                
                recording_clip.export(output_path, format="wav")
                print('Created clip')
            except Exception as e:
                print(e, '\n')
                print('Could not create clip ', str(start_time), ' from ', str(recording_id))
    
def get_recording_from_server(audio_out_path, recording_id):
    successfully_retrieved_recording = False
    try:
#        recording_local_filename = downloaded_recordings_folder + str(recording_id) + '.m4a'
        token_for_retrieving_recording = get_token_for_retrieving_recording(str(recording_id))
        if token_for_retrieving_recording is None:
            return False
       
        print('\tDownloading recording', str(recording_id),'\n')
        url = parameters.server_endpoint + parameters.get_a_recording
        querystring = {"jwt":token_for_retrieving_recording}     
       
        resp_for_getting_a_recording = requests.request("GET", url, params=querystring)
       
        if resp_for_getting_a_recording.status_code != 200:
            # This means something went wrong.
            print('Error from server is: ', resp_for_getting_a_recording.text)
            return False
#                sys.exit('Could not download file - exiting')
           
        #recording_local_filename = './'+ parameters.downloaded_recordings_folder + '/' + recording_id + '.mp4a'    
        with open(audio_out_path, 'wb') as f:  
            f.write(resp_for_getting_a_recording.content)
            
        print('Downloaded recording ', recording_id)
        successfully_retrieved_recording = True
#        else:
#            print('\t\tAlready have recording ', str(recording_id) , ' - so will not download again\n')
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to download recording ' + str(recording_id), '\n') 
        
    return successfully_retrieved_recording

def get_token_for_retrieving_recording(recording_id):
    recording_download_token = None
    user_token = functions.get_cacophony_user_token()

    get_a_token_for_recording_endpoint = parameters.server_endpoint + parameters.get_a_token_for_getting_a_recording_url + recording_id

    headers = {'Authorization': user_token}

    resp_for_getting_a_recordingToken = requests.request("GET", get_a_token_for_recording_endpoint, headers=headers)
    if resp_for_getting_a_recordingToken.status_code != 200:
        print('resp_for_getting_a_recordingToken ', resp_for_getting_a_recordingToken)
#        sys.exit('Could not get download token - exiting')
    recording_data = resp_for_getting_a_recordingToken.json()
    recording_download_token = recording_data['downloadFileJWT']
    
    return recording_download_token             

def main():
    
#    list_of_recordings_with_specified_tag = retrieve_list_of_recordings_with_specified_tag(device_name, specified_tag)
#    full_recording_info_of_recordings_with_specified_tag = retrieve_full_recording_info(list_of_recordings_with_specified_tag)
#    print(full_recording_info_of_recordings_with_specified_tag)
#    all_specified_tags = extract_tags_from_list_of_full_recording_info(full_recording_info_of_recordings_with_specified_tag, specified_tag)
#    print(all_specified_tags)
#
#
#    with open(out_file_path_name, 'w') as json_file:  
#        json.dump(all_specified_tags, json_file)
     
    # For each tag, find local copy of recording
    create_wav_clips_from_tags_file(out_file_path_name)
    
   
    
    
    
    
    
main()




















