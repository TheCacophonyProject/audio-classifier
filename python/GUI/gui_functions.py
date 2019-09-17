
import sqlite3
from sqlite3 import Error
import requests
import os
import sys
import json
from pathlib import Path
from tkinter import filedialog
from tkinter import *
import re
from scipy.io import wavfile
import shutil
# import scikits.audiolab
# import sckikits as sc
# 
# from sc import Sndfile, Format

import parameters


import glob

import numpy as np
import soundfile as sf
import librosa

# from soundfile import SoundFile

# import scipy.io
# 
# import wavio
# from code.Analysis import what
# 
# ffmpegEXE = 'ffmpeg'  # or ffmpeg.exe on windows etc
# import subprocess as sp
# 
# from pydub import AudioSegment
# from scipy.io.wavfile import read


#path to configs
# sys.path.append('/home/jonah/Documents/opensmile-2.3.0/config/')
sys.path.append('/home/tim/opensmile-2.3.0/config/')
#path to input files
search_path = '/home/tim/Work/Cacophony/opensmile_weka/TestAudioInput'
#path to where we want the output
arff_path = '/home/tim/Work/Cacophony/opensmile_weka/TestAudioOutput'


db_file = "audio_analysis_db"
conn = None

def get_database_connection():
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """

    # https://stackoverflow.com/questions/8587610/unboundlocalerror-local-variable-conn-referenced-before-assignment
    global conn
    if conn is None:
        try:
            conn = sqlite3.connect(db_file)           
        except Error as e:
            print(e)
  
    return conn       
    

def get_tags_from_server(device_id):
    print('about to get tags from server for device ', device_id)
    

def get_recordings_from_server(device_name, device_super_name):
    if not device_name:
        print('Device name can NOT be null')
        return
    
    if not device_super_name:
        print('Device Super name can NOT be null')
        return    
        
    print('About to get recordings from server')
    retrieve_available_recordings_from_server(device_name, device_super_name)
    
def get_latest_recording_id_from_local_db(device_name, device_super_name):
    # Need the last recording ID for this device, that we already have   

#     https://docs.python.org/2/library/sqlite3.html
    sql = ''' SELECT audio_file_id FROM audio_files WHERE device_super_name = ? ORDER BY audio_file_id DESC LIMIT 1'''
    cur = get_database_connection().cursor()  
   
    cur.execute(sql,(device_super_name,))   
 
    rows = cur.fetchall() 
    for row in rows:
        return row[0]
    
def retrieve_available_recordings_from_server(device_name, device_super_name):      

    recordings_folder = getRecordingsFolder()     

    ids_of_recordings_to_download = get_recording_ids_for_device_name(device_name)
    
    # remove ids of recordings that we already have
    already_downloaded = []
    for file in os.listdir(recordings_folder):
        already_downloaded.append(os.path.splitext(file)[0])
       
    already_downloaded_set = set(already_downloaded)  
        
    ids_of_recordings_to_still_to_download = []
    
    for recording_id in ids_of_recordings_to_download:
        if not recording_id in already_downloaded_set:
            ids_of_recordings_to_still_to_download.append(recording_id)
        else:
            print('Aleady have recording ',recording_id, ' so will not download')
       
    for recording_id in ids_of_recordings_to_still_to_download:
#         print('About to get token for downloading ',recording_id)
        token_for_retrieving_recording = get_token_for_retrieving_recording(recording_id)
        print('About to get recording ',recording_id)
        get_recording_from_server(token_for_retrieving_recording, recording_id, device_name, device_super_name)
        
        # Also get recording information from server
        update_recording_information_for_single_recording(recording_id)
     
    print('Finished retrieving recordings')  
    print('Now going to retrieve tags')  
    get_all_tags_for_all_devices_in_local_database()
    print('Finished retrieving tags') 
    print('Finished all')  
        
def get_recording_from_server(token_for_retrieving_recording, recording_id, device_name, device_super_name):
    try:
      
        recording_local_filename = getRecordingsFolder() + '/' + recording_id + '.m4a'
            
        # Don't download it if we already have it.       
       
        if not os.path.exists(recording_local_filename):
            url = parameters.server_endpoint + parameters.get_a_recording
            querystring = {"jwt":token_for_retrieving_recording}     
           
            resp_for_getting_a_recording = requests.request("GET", url, params=querystring)
           
            if resp_for_getting_a_recording.status_code != 200:
                # This means something went wrong.
                print('Error from server is: ', resp_for_getting_a_recording.text)
                return               
             
            with open(recording_local_filename, 'wb') as f:  
                f.write(resp_for_getting_a_recording.content)
                
            # Update local database
            insert_recording_into_database(recording_id,recording_id + '.m4a' ,device_name,device_super_name)
            
        else:
            print('\t\tAlready have recording ', str(recording_id) , ' - so will not download again\n')
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to download recording ' + str(recording_id), '\n')
        
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
    
def get_recording_ids_for_device_name(device_name): 
        
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
        else:
            break
    return ids_recordings_for_device_name

def get_ids_of_recordings_to_download_using_deviceId(deviceId, offset):
    # This will get a list of the recording ids for every recording of length 59,60,61,62 from device_name
    user_token = get_cacophony_user_token()
   
    url = parameters.server_endpoint + parameters.query_available_recordings
    
    where_param = {}
    where_param['DeviceId'] = deviceId
    where_param['duration'] = 59,60,61,62
    json_where_param = json.dumps(where_param) 
    querystring = {"offset":offset, "where":json_where_param}   
    
    headers = {'Authorization': user_token}  

    resp = requests.request("GET", url, headers=headers, params=querystring)
   
    if resp.status_code != 200:
        # This means something went wrong.
        print('Error from server is: ', resp.text)
        sys.exit('Could not download file - exiting')            
    
    data = resp.json() 
    
    
    recordings = data['rows'] 
    
    print('Number of recordings is ', len(recordings))

    ids_of_recordings_to_download = []    
    for recording in recordings:        
        recording_id = str(recording['id'])
        ids_of_recordings_to_download.append(recording_id)
        
    return ids_of_recordings_to_download    

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
            
def get_cacophony_user_token():
    if parameters.cacophony_user_token:
        return parameters.cacophony_user_token
    
    print('About to get user_token from server')
    username = parameters.cacophony_user_name
    if parameters.cacophony_user_password == '':
        parameters.cacophony_user_password = input("Enter password for Cacophony user " + username + " (or change cacophony_user_name in parameters file): ")
           
    requestBody = {"nameOrEmail": username, "password": parameters.cacophony_user_password }
    login_endpoint = parameters.server_endpoint + parameters.login_user_url
    resp = requests.post(login_endpoint, data=requestBody)
    if resp.status_code != 200:
        # This means something went wrong.
        sys.exit('Could not connect to Cacophony Server - exiting')
    
    data = resp.json()
    parameters.cacophony_user_token = data['token']
    return parameters.cacophony_user_token
    
def load_recordings_from_local_folder(device_name, device_super_name):
    
    input_folder = filedialog.askdirectory()

    recordings_folder = getRecordingsFolder()
    
    for filename in os.listdir( input_folder):
        recording_id = filename.replace('-','.').split('.')[0]
        filename2 = recording_id +'.m4a'

        insert_recording_into_database(recording_id,filename2,device_name,device_super_name)
        
        # Now move file to recordings folder
        audio_in_path = input_folder + '/' + filename       
        audio_out_path = recordings_folder + '/' + filename2
        
        print('Moving ', filename, ' to ', audio_out_path)
        os.rename(audio_in_path, audio_out_path)

        # Now need to get information about this recording from server
        update_recording_information_for_single_recording(recording_id)
        
def insert_recording_into_database(recording_id,filename,device_name,device_super_name):
    try:
        sql = ''' INSERT INTO recordings(recording_id,filename,device_name,device_super_name)
                  VALUES(?,?,?,?) '''
        cur = get_database_connection().cursor()
        cur.execute(sql, (recording_id,filename,device_name,device_super_name))
       
        get_database_connection().commit()
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to insert recording ' + str(recording_id), '\n')
        

def update_recordings_folder(recordings_folder):
    print("new_recording_folder ", recordings_folder)
    """
    update priority, begin_date, and end date of a task
    :param conn:
    :param recordings_folder:
    :return: project id
    """
    sql = ''' UPDATE settings
              SET downloaded_recordings_folder = ?               
              WHERE ID = 1'''
    cur = get_database_connection().cursor()
    cur.execute(sql, (recordings_folder,))
    get_database_connection().commit()      
        
def getRecordingsFolder():

    cur = get_database_connection().cursor()
    cur.execute("select * from settings")
 
    rows = cur.fetchall()
    home = str(Path.home())
    print('home ', home)
 
    for row in rows:       
        return  home + '/' + row[0] 
    
    
def getRecordingsFolderWithOutHome():
    cur = get_database_connection().cursor()
    cur.execute("select * from settings")
 
    rows = cur.fetchall()   
 
    for row in rows:     
        return row[0] 
    
def saveSettings(recordings_folder):
    print('recordings_folder ', recordings_folder)
    #https://stackoverflow.com/questions/16856647/sqlite3-programmingerror-incorrect-number-of-bindings-supplied-the-current-sta
    update_recordings_folder(recordings_folder)
        
def update_recording_information_for_single_recording(recording_id):
    print('About to update recording information for recording ', recording_id)    
    recording_information = get_recording_information_for_a_single_recording(recording_id)
    print('recording_information ', recording_information)    
    if recording_information == None:        
        print('recording_information == None')     
        return
         
    recording = recording_information['recording']    
    recordingDateTime = recording['recordingDateTime']    
    relativeToDawn = recording['relativeToDawn']    
    relativeToDusk = recording['relativeToDusk']    
    duration = recording['duration'] 
       
    location = recording['location']        
    coordinates = location['coordinates']    
    locationLat = coordinates[0]    
    locationLong = coordinates[1]  
       
    version = recording['version']    
    batteryLevel = recording['batteryLevel']    
    
    additionalMetadata = recording['additionalMetadata']    
    phoneModel = additionalMetadata['Phone model']    
    androidApiLevel = additionalMetadata['Android API Level']  
    
    Device = recording['Device']    
    deviceId = Device['id']
    device_name = Device['devicename']
         
    nightRecording =  'false'
    
    if relativeToDusk is not None:
        if relativeToDusk > 0:
            nightRecording = 'true' 
    elif relativeToDawn is not None:
        if relativeToDawn < 0:
            nightRecording = 'true'   
                   
    update_recording_in_database(recordingDateTime, relativeToDawn, relativeToDusk, duration, locationLat, locationLong, version, batteryLevel, phoneModel, androidApiLevel, deviceId, nightRecording, device_name, recording_id)
    print('Finished updating recording information for recording ', recording_id)
               
def test_update_recording_information_for_single_recording():
    update_recording_information_for_single_recording('291047')
    
def update_recording_in_database(recordingDateTime, relativeToDawn, relativeToDusk, duration, locationLat, locationLong, version, batteryLevel, phoneModel,androidApiLevel, deviceId, nightRecording, device_name, recording_id):
    try:
        conn = get_database_connection()
        # https://www.sqlitetutorial.net/sqlite-python/update/
        sql = ''' UPDATE recordings 
                  SET recordingDateTime = ?,
                      relativeToDawn = ?,
                      relativeToDusk = ?,
                      duration = ?,
                      locationLat = ?,
                      locationLong = ?,
                      version = ?,
                      batteryLevel = ?,
                      phoneModel = ?,
                      androidApiLevel = ?,
                      deviceId = ?,
                      nightRecording = ?,
                      device_name = ?
                  WHERE recording_id = ? '''
        cur = get_database_connection().cursor()
        cur.execute(sql, (recordingDateTime, relativeToDawn, relativeToDusk, duration, locationLat, locationLong, version, batteryLevel, phoneModel, androidApiLevel, deviceId, nightRecording, device_name, recording_id))
        get_database_connection().commit()
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to insert recording ' + str(recording_id), '\n')
        
def test_update_recording_in_database():
    update_recording_in_database('2018-04-04T17:07:01.000Z', 3, 1, 2, -22.2, 178.1, '23b', 77, 'ZTE phone',7, 1234, 'true', 'grants shed3', 291047)
      
    
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
    recording_data = get_recording_information_for_a_single_recording('197294')
    print('recording_data is: ', recording_data)

def update_recording_information_for_all_local_database_recordings():
#     conn = get_database_connection()
    cur = get_database_connection().cursor()
    cur.execute("SELECT recording_id, recordingDateTime FROM recordings")
 
    rows = cur.fetchall()
 
    for row in rows:
        # Don't update if we already have recordingDateTime
        recordingDateTime = row[1]
        if not recordingDateTime:
            print(recordingDateTime, ' is empty so will update record')
            recording_id = row[0]
            update_recording_information_for_single_recording(recording_id)
        print('Finished updating recording information')
    
def test_update_recording_information_for_all_local_database_recordings():
    update_recording_information_for_all_local_database_recordings()

def get_audio_recordings_with_tags_information_from_server(user_token, recording_type, deviceId):
    print('Retrieving recordings basic information from Cacophony Server\n')
    url = parameters.server_endpoint + parameters.query_available_recordings
    
    where_param = {}
    where_param['type'] = recording_type    
    where_param['DeviceId'] = deviceId
    json_where_param = json.dumps(where_param)
    querystring = {"tagMode":"tagged", "where":json_where_param}    
    headers = {'Authorization': user_token}  

    resp = requests.request("GET", url, headers=headers, params=querystring)
   
    if resp.status_code != 200:
        # This means something went wrong.
        print('Error from server is: ', resp.text)
        sys.exit('Could not download file - exiting')    
        
    
    data = resp.json()
   
    recordings = data['rows']
    
    return recordings   

def test_get_audio_recordings_with_tags_information_from_server():
    user_token = get_cacophony_user_token()
    recording_type = 'audio'
    deviceId = 379
    recordings = get_audio_recordings_with_tags_information_from_server(user_token, recording_type, str(deviceId))
    for recording in recordings:
        print(recording, '\n')

def get_and_store_tag_information_for_recording(recording_id, deviceId, device_name, device_super_name):
    single_recording_full_information = get_recording_information_for_a_single_recording(recording_id)
    recording = single_recording_full_information['recording']  
    tags = recording['Tags']   
    for tag in tags:
        server_Id = tag['id']
        what = tag['what']
        detail = tag['detail']
        confidence = tag['confidence']
        startTime = tag['startTime']
        duration = tag['duration']
        automatic = tag['automatic']
        version = tag['version']
        createdAt = tag['createdAt']
        tagger =tag['tagger']        
        tagger_username = tagger['username']
        what = tag['what']
        insert_tag_into_database(recording_id,server_Id, what, detail, confidence, startTime, duration, automatic, version, createdAt, tagger_username, deviceId, device_name, device_super_name)
    
    
def test_get_and_store_tag_information_for_recording():
    get_and_store_tag_information_for_recording(str(197294), 123)
    
def insert_tag_into_database(recording_id,server_Id, what, detail, confidence, startTime, duration, automatic, version, createdAt, tagger_username, deviceId, device_name, device_super_name ):
    # Use this for tags that have been downloaded from the server
    try:
        if check_if_tag_alredy_in_database(server_Id) == True:
            print('tag exists')
            return
        else:
            print('going to insert tag')

        sql = ''' INSERT INTO tags(recording_id,server_Id, what, detail, confidence, startTime, duration, automatic, version, createdAt, tagger_username, deviceId, device_name, device_super_name)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur = get_database_connection().cursor()
        cur.execute(sql, (recording_id,server_Id, what, detail, confidence, startTime, duration, automatic, version, createdAt, tagger_username, deviceId, device_name, device_super_name))
        get_database_connection().commit()
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to insert tag ' + str(recording_id), '\n')   
        
def insert_locally_created_tag_into_database(recording_id,what, detail, confidence, startTime, duration, createdAt, tagger_username, deviceId, device_name, device_super_name ):
    # Use this is the tag was created in this application, rather than being downloaded from the server - becuase some fiels are mission e.g. server_Id
    try:        

        sql = ''' INSERT INTO tags(recording_id, what, detail, confidence, startTime, duration, createdAt, tagger_username, deviceId, device_name, device_super_name)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
        cur = get_database_connection().cursor()
        cur.execute(sql, (recording_id, what, detail, confidence, startTime, duration, createdAt, tagger_username, deviceId, device_name, device_super_name))
        get_database_connection().commit()
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to insert tag ' + str(recording_id), '\n')   
       
def test_insert_tag_into_database():
    insert_tag_into_database(1,135940, 'bat', 'detail', 'confidence', 1.2, 2.5, 'automatic', 256, '2019-06-20T04:14:24.811Z', 'timhot', 'deviceId', 'device_name', 'device_super_name')
    
def check_if_tag_alredy_in_database(server_Id):
    cur = get_database_connection().cursor()
    cur.execute("SELECT server_Id FROM tags WHERE server_Id = ?", (server_Id,))
    data=cur.fetchone()
    if data is None:
        return False
    else:
        return True

def test_check_if_tag_alredy_in_database(): 
    check_if_tag_alredy_in_database(135939)  
 
def get_all_tags_for_all_devices_in_local_database():
    user_token = get_cacophony_user_token()
    unique_devices = get_unique_devices_stored_locally()

    for unique_device in unique_devices:  
        deviceId = unique_device[0]
        device_name = unique_device[1]
        device_super_name = unique_device[2]        
      
        recording_type = 'audio'
        recordings_with_tags = get_audio_recordings_with_tags_information_from_server(user_token, recording_type, deviceId)

        for recording_with_tag in recordings_with_tags:
            print('device is', deviceId, '\n') 
            recording_id =recording_with_tag['id']
            print('recording_id ', recording_id, '\n')
            get_and_store_tag_information_for_recording(str(recording_id), deviceId, device_name, device_super_name)
    print('Finished getting tags from server')
            
def test_get_all_tags_for_all_devices_in_local_database():
    get_all_tags_for_all_devices_in_local_database()            
     
def get_unique_devices_stored_locally():
    cur = get_database_connection().cursor()
    cur.execute("SELECT DISTINCT deviceId, device_name, device_super_name FROM recordings") 
    rows = cur.fetchall()
    return rows   
    
     
def test_get_unique_devices_stored_locally():
    unique_devices = get_unique_devices_stored_locally()
    for unique_device in unique_devices:
        print(unique_device, '\n')
    
def scan_local_folder_for_recordings_not_in_local_db_and_update(device_name, device_super_name):
    recordings_folder = getRecordingsFolder()
    for filename in os.listdir(recordings_folder):
        recording_id = filename.replace('-','.').split('.')[0]
        print(recording_id)
        cur = get_database_connection().cursor()
        cur.execute("SELECT * FROM recordings WHERE recording_id = ?",(recording_id,))
        
        # https://stackoverflow.com/questions/16561362/python-how-to-check-if-a-result-set-is-empty
        row = cur.fetchone()
        if row == None:
           # Get the information for this recording from server and insert into local db
    #            update_recording_information_for_single_recording(recording_id)
            filename = recording_id + '.m4a'
            insert_recording_into_database(recording_id,filename, device_name,device_super_name) # The device name will be updated next when getting infor from server
            # Now update this recording with information from server
            update_recording_information_for_single_recording(recording_id)
        
def test_scan_local_folder_for_recordings_not_in_local_db_and_update():
    scan_local_folder_for_recordings_not_in_local_db_and_update('grants shed')
           
def create_tags_from_folder_of_unknown_images():
    # This will probably only get used to recreate the unknown tags from the unknown images - as I'm not sure where the text file of this is/exists
    home = str(Path.home())
    unknown_images_folder =  home + '/Work/Cacophony/images/unknown'
    for filename in os.listdir(unknown_images_folder):
        fileparts = filename.replace('_','.').split('.')
        recording_id = fileparts[0]
        print('recording_id ', recording_id)
        startWholeSecond = fileparts[1]
        print('startWholeSecond ', startWholeSecond)
        startPartSecond = fileparts[2]
        print('startPartSecond ', startPartSecond)
        startTimeSeconds = startWholeSecond + '.' + startPartSecond
        insert_locally_created_tag_into_database(recording_id=recording_id, what='unknown', detail=None, confidence=None, startTime=startTimeSeconds, duration=1.5, createdAt='2019-06-20T05:39:28.391Z', tagger_username='timhot', deviceId=378, device_name='fpF7B9AFNn6hvfVgdrJB', device_super_name='Hammond Park')
    print('Finished creating unknown tags from image files')
    
def test_create_tags_from_folder_of_unknown_images():
    create_tags_from_folder_of_unknown_images()
    
def update_local_tags_with_version():
    # This is probably only used the once to modify intial rows to indicate they are from my first morepork tagging of Hammond Park
    cur = get_database_connection().cursor()
    cur.execute("select ID from tags")
 
    rows = cur.fetchall()     
 
    for row in rows:              
        ID =  row[0] 
        print('ID ', ID) 
        sql = ''' UPDATE tags
                  SET version = ?               
                  WHERE ID = ?'''
        cur = get_database_connection().cursor()
        cur.execute(sql, ('morepork_base', ID))
    
    get_database_connection().commit()    
    
def test_update_local_tags_with_version():
    update_local_tags_with_version()
    
# def create_clips(device_super_name, what, version, clips_ouput_folder):
def create_clips(device_super_name, what, version, run_base_folder, run_folder):
    print(device_super_name, what, version, run_base_folder, run_folder) 
#     what_without_spaces = re.sub(' ', '', what)
#     what_without_spaces_dashes = re.sub('-', '_', what_without_spaces) 
#     clips_ouput_folder = run_base_folder + '/' + run_folder + '/' + 'audio_clips' + '/' + what_without_spaces_dashes
# 
#     
#     sql = ''' SELECT recording_Id, startTime, duration FROM tags WHERE device_super_name=? AND what=? AND version=? '''          
#     cur = get_database_connection().cursor()
#     cur.execute(sql, (device_super_name, what, version,)) 
#     rows = cur.fetchall()  
#     
#     count = 0
#  
#     for row in rows: 
#         print('Creating clip ', count, ' of ', len(rows))
#         recording_Id = row[0]
#         start_time_seconds = row[1]
#         duration_seconds = row[2]
#         create_wav_clip(recording_Id, start_time_seconds, duration_seconds, clips_ouput_folder)   
#         count = count + 1     
    
def create_wav_clip(recording_Id, start_time_seconds, duration_seconds, clips_ouput_folder):
    print(recording_Id)
    audio_in_path = getRecordingsFolder() + '/' + str(recording_Id) + '.m4a'
#     audio_out_folder = getRecordingsFolder() + '/' + what
    if not os.path.exists(clips_ouput_folder):
#         os.mkdir(clips_ouput_folder)
        os.makedirs(clips_ouput_folder)    
    
    audio_out_path = clips_ouput_folder + '/' + str(recording_Id) + '_' + str(start_time_seconds) + '_' + str(duration_seconds) + '.wav'
#     print('audio_in_path ', audio_in_path)
#     print('audio_out_path ', audio_out_path)
#     if not os.path.exists(audio_in_path):
#         print('Can not find ', audio_in_path)
#     else:
#         print('Found it')
        
    create_wav(audio_in_path, audio_out_path, start_time_seconds, duration_seconds)
     
        
def create_folder(folder_to_create):
    if folder_to_create is None:
        print("Please enter a folder name")
        return
    if not folder_to_create:
        print("Please enter a folder name")
        return
    
    if not os.path.exists(folder_to_create):
        os.mkdir(folder_to_create)
        print("Folder " , folder_to_create ,  " Created ")    
    
      


            
def run_processDir():
    processDir(search_path,arff_path)
    
    
def create_wav(audio_in_path, audio_out_path, start_time_seconds, duration_seconds): 
    print('start_time_seconds ', start_time_seconds) 
    print('duration_seconds ', duration_seconds)  
    y, sr = librosa.load(audio_in_path) 
    
    clip_start_array = int((sr * start_time_seconds))
    print('clip_start_array ', clip_start_array)
    clip_end_array = clip_start_array + int((sr * duration_seconds))    
 
     
    if clip_end_array > y.shape[0]:
        print('Clip would end after end of recording')
        return
     
    clip_call_by_array = y[clip_start_array:clip_end_array]  
     
     
 
     
    #Save the file 
#     wavfile.write(filename=audio_out_path, rate=sr, data=clip_call_by_array)
#     sf.write(file, data, samplerate, subtype, endian, format, closefd)
#     sf.write(file=audio_out_path, data=clip_call_by_array, samplerate=sr, subtype, endian, format, closefd)
    # https://pysoundfile.readthedocs.io/en/0.9.0/
    sf.write(audio_out_path, clip_call_by_array, sr, 'PCM_24')
#     sf.write(audio_out_path, y, sr, 'PCM_24')      
    

#     run_processDir()


def test_create_wav():
    create_wav('/home/tim/Work/Cacophony/opensmile_weka/m4a_files/161945.m4a', '/home/tim/Work/Cacophony/opensmile_weka/TestAudioInput/161945.wav')  
    create_wav('/home/tim/Work/Cacophony/opensmile_weka/m4a_files/161946.m4a', '/home/tim/Work/Cacophony/opensmile_weka/TestAudioInput/161946.wav')  
    processDir(search_path,arff_path)

        
def create_arff_file(base_folder, run_folder, clip_folder, openSmile_config_file):
    clip_folder_without_spaces = re.sub(' ', '_', clip_folder)
    print('base_folder ', base_folder)
    cwd = os.getcwd()
       
    openSmile_config_file_template = cwd + '/template_files/openSmile_config_files/' + openSmile_config_file
    openSmile_config_file_for_this_run = base_folder + '/' + run_folder + '/' + openSmile_config_file
    shutil.copy2(openSmile_config_file_template, openSmile_config_file_for_this_run)
    
#     arff_template_file_path = cwd + '/template_files/' + arff_template_file
#     arff_template_file_for_this_run = base_folder + '/' + run_folder + '/' + arff_template_file
#     shutil.copy2(arff_template_file_path, arff_template_file_for_this_run)
    
    print('clip_folder', clip_folder_without_spaces)
   
    
    searchDir = base_folder + '/' + run_folder + '/audio_clips/' + clip_folder_without_spaces
    arffDir = base_folder + '/' + run_folder + '/arff_files' 
    if not os.path.exists(arffDir):
        os.mkdir(arffDir)
    
    print('searchDir', searchDir)
    print('arffDir', arffDir)
    
    processDir(searchDir, arffDir, openSmile_config_file_for_this_run)
    
# First version written by Jonah Dearden
def processDir( searchDir, arffDir, openSmile_config_file_for_this_run):
    print('openSmile_config_file_for_this_run ', openSmile_config_file_for_this_run)
    
    os.chdir(searchDir)
    i=0
    list_of_files=[]
    # https://www.tutorialspoint.com/python/os_walk.htm
    for root,dir,files in os.walk(searchDir):
        for f in files:
            if re.match(r'.*\.wav',f):
                list_of_files.append(root+'/'+f)
                
    os.chdir(arffDir)
    
    for i in list_of_files: 
        print(i)
    
    print('openSmile_config_file_for_this_run ', openSmile_config_file_for_this_run)
    
    for i in list_of_files:     
        name1=re.sub(r'(' + searchDir + '/)(.*)(\.wav)',r'\2',i)
        os.system('SMILExtract -C ' + openSmile_config_file_for_this_run + ' -I '+i+' -O '+arffDir+'/'+name1+'.mfcc.arff')
 

       
def merge_arffs(base_folder, run_folder, arff_template_file):
    #path to directory with arffs
    arffDir = base_folder + '/' + run_folder + '/arff_files'
    arrf_filename = re.sub('_template', '', arff_template_file)
    cwd = os.getcwd()
    arff_template_file_path = cwd + '/template_files/arff_template_files/' + arff_template_file
    arff_template_file_for_this_run = base_folder + '/' + run_folder + '/arff_files/' + arrf_filename
    shutil.copy2(arff_template_file_path, arff_template_file_for_this_run)
    
    os.chdir(arffDir)
    
    counter = 0

    #Opens joinedArff.arff and appends
    with open(arrf_filename, "a") as f:
        #for each file with the .arff ext in the directroy
        for file in glob.glob("*.arff"):
            #Open the file and read line 996
            print(file)
            a = open(file, "r")
            lines = a.readlines()
    
            x = lines[995]
            #Replace class label if necessary
            #This is unnecessary if you have already assigned the classes using the OpenSmile conf.
            #x = x.replace("unknown", "person")
            #Writes that line to the joinedArff file
            f.write(x + "\n")
            a.close()
    
    f.close()   
    
    arff_template_file_for_this_run_in_run_folder = base_folder + '/' + run_folder + '/' + arrf_filename
#     os.rename(arff_template_file_for_this_run, arff_template_file_for_this_run_in_run_folder)
    shutil.move(arff_template_file_for_this_run, arff_template_file_for_this_run_in_run_folder)
    
    print('Merged arff file created in ', base_folder, '/',run_folder)
    
def get_unique_whats_from_local_db():
    cur = get_database_connection().cursor()
    cur.execute("SELECT DISTINCT what FROM tags") 
    rows = cur.fetchall()  
    
    unique_whats = []
    for row in rows:
         unique_whats.append(row[0])
    return unique_whats  

def getOpenSmileConfigFiles():
    cwd = os.getcwd()
    openSmileConfigFileDir = cwd + '/template_files/openSmile_config_files/'
    openSmileConfigFiles = []
    for file in os.listdir(openSmileConfigFileDir):
        openSmileConfigFiles.append(file)        
   
    return openSmileConfigFiles
    
def getArffTemplateFiles():
    cwd = os.getcwd()
    arrTemplateFileDir = cwd + '/template_files/arff_template_files/'

    arffTemplateFiles = []
    for file in os.listdir(arrTemplateFileDir):
        arffTemplateFiles.append(file)        
   
    return arffTemplateFiles     



def choose_clip_folder(base_folder, run_folder):
    start_folder = base_folder + '/' + run_folder + '/audio_clips/'
    clip_folder = filedialog.askdirectory(initialdir=start_folder,  title = "Open the folder you want (Just selecting it won't choose it)")
    parts = re.split('/', clip_folder)
    clip_folder =  parts[len(parts)-1]     
    return clip_folder      

   

 
       
       
    