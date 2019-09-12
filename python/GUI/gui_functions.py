'''
Created on 5 Sep 2019

@author: tim
'''
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

import parameters


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
        
    
# def create_connection(db_file):
#     """ create a database connection to the SQLite database
#         specified by the db_file
#     :param db_file: database file
#     :return: Connection object or None
#     """
# #     conn = None
# #     try:
# #         conn = sqlite3.connect(db_file)
# #     except Error as e:
# #         print(e)
# #  
# #     return conn
#     if conn == None:
#         try:
#             conn = sqlite3.connect(db_file)
#         except Error as e:
#             print(e)
#   
#     return conn

def get_tags_from_server(device_id):
    print('about to get tags from server for device ', device_id)
    

def get_recordings_from_server(device_name, device_super_name):
    if not device_name:
        print('Device name can NOT be null')
        return
    
    if not device_super_name:
        print('Device Super name can NOT be null')
        return
    
#     latest_recording_on_local_db = get_latest_recording_id_from_local_db(device_name, device_super_name)
#     print(latest_recording_on_local_db)    
        
    print('About to get recordings from server')
    retrieve_available_recordings_from_server(device_name, device_super_name)
    
def get_latest_recording_id_from_local_db(device_name, device_super_name):
    # Need the last recording ID for this device, that we already have    
#     conn = create_connection(database) 

#     https://docs.python.org/2/library/sqlite3.html
    sql = ''' SELECT audio_file_id FROM audio_files WHERE device_super_name = ? ORDER BY audio_file_id DESC LIMIT 1'''
    cur = get_database_connection().cursor()  
   
    cur.execute(sql,(device_super_name,))   
 
    rows = cur.fetchall() 
    for row in rows:
#         print(row)
        return row[0]
    
def retrieve_available_recordings_from_server(device_name, device_super_name):  
    
#     home = str(Path.home())
#     print('home ', home)
#     recordings_folder = home + '/' + getRecordingsFolder()   
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
        

#         recording_local_filename = './'+ parameters.downloaded_recordings_folder + '/' + device_name + '/' + recording_id + '.m4a'
        recording_local_filename = getRecordingsFolder() + '/' + recording_id + '.m4a'
            
        # Don't download it if we already have it.       
       
        if not os.path.exists(recording_local_filename):
#             print('\tDownloading recording', str(recording_id),'\n')
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
#            print('offset ', offset)
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
#         print('Already have user_token')
        return parameters.cacophony_user_token
    
    print('About to get user_token from server')
    username = parameters.cacophony_user_name
    if parameters.cacophony_user_password == '':
        parameters.cacophony_user_password = input("Enter password for Cacophony user " + username + " (or change cacophony_user_name in parameters file): ")
        
   # requestBody = {"nameOrEmail": "timhot", "password": parameters.cacophony_user_password }
    requestBody = {"nameOrEmail": username, "password": parameters.cacophony_user_password }
    login_endpoint = parameters.server_endpoint + parameters.login_user_url
    resp = requests.post(login_endpoint, data=requestBody)
    if resp.status_code != 200:
        # This means something went wrong.
        sys.exit('Could not connect to Cacophony Server - exiting')
    
    data = resp.json()
#     token = data['token']
    parameters.cacophony_user_token = data['token']
#     return token
    return parameters.cacophony_user_token
    
def load_recordings_from_local_folder(device_name, device_super_name):
# def load_recordings_from_local_folder(device_su/per_name):
    # This was used to index recordings that had already been downloaded
    
    
    input_folder = filedialog.askdirectory()
#     print('input_folder ',input_folder)

    recordings_folder = getRecordingsFolder()
#     print('recordings_folder ', recordings_folder)
    
    for filename in os.listdir( input_folder):
#         recording_id = filename.split('.')[0]
        recording_id = filename.replace('-','.').split('.')[0]
        filename2 = recording_id +'.m4a'


        insert_recording_into_database(recording_id,filename2,device_name,device_super_name)
#         insert_recording_into_database(recording_id,filename2,device_super_name)
        
        # Now move file to recordings folder
        audio_in_path = input_folder + '/' + filename       
        audio_out_path = recordings_folder + '/' + filename2
#         print('audio_in_path ', audio_in_path)
#         print('audio_out_path ', audio_out_path)
        
        print('Moving ', filename, ' to ', audio_out_path)
        os.rename(audio_in_path, audio_out_path)
#         return
        # Now need to get information about this recording from server
        update_recording_information_for_single_recording(recording_id)
        
def insert_recording_into_database(recording_id,filename,device_name,device_super_name):
# def insert_recording_into_database(recording_id,filename,device_super_name):
    try:
#         conn = create_connection(database)
        sql = ''' INSERT INTO recordings(recording_id,filename,device_name,device_super_name)
                  VALUES(?,?,?,?) '''
        cur = get_database_connection().cursor()
        cur.execute(sql, (recording_id,filename,device_name,device_super_name))
       
        get_database_connection().commit()
    except Exception as e:
        print(e, '\n')
        print('\t\tUnable to insert recording ' + str(recording_id), '\n')
        


    
# def select_names(conn):
#     """
#     Query tasks by priority
#     :param conn: the Connection object
#     :param priority:
#     :return:
#     """
#     cur = get_database_connection().cursor()
#     cur.execute("select * from users")
#  
#     rows = cur.fetchall()
#  
#     for row in rows:
#         print(row)
        
# def update_recordings_folder(conn, recordings_folder):
# #     new_recording_folder = recordings_folder[0]
#     print("new_recording_folder ", recordings_folder)
#     """
#     update priority, begin_date, and end date of a task
#     :param conn:
#     :param recordings_folder:
#     :return: project id
#     """
#     sql = ''' UPDATE settings
#               SET downloaded_recordings_folder = ?               
#               WHERE ID = 1'''
#     cur = conn.cursor()
#     cur.execute(sql, recordings_folder)
#     conn.commit()

def update_recordings_folder(recordings_folder):
#     new_recording_folder = recordings_folder[0]
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
#     cur = conn.cursor()
    cur = get_database_connection().cursor()
    cur.execute(sql, (recordings_folder,))
#     conn.commit()
    get_database_connection().commit()
        
# def getNames():
#     database = "audio_analysis_db"
#     conn = create_connection(database)
#     with conn:
#         print("1. Query task by priority:")
#         select_names(conn)
        
def getRecordingsFolder():
#     conn = create_connection(database)
    cur = get_database_connection().cursor()
    cur.execute("select * from settings")
 
    rows = cur.fetchall()
    home = str(Path.home())
    print('home ', home)
 
    for row in rows:
        #print(row)
        return  home + '/' + row[0]    
   
    
    
def getRecordingsFolderWithOutHome():
#     conn = get_database_connection()
    cur = get_database_connection().cursor()
    cur.execute("select * from settings")
 
    rows = cur.fetchall()
   
 
    for row in rows:
        #print(row)
        return row[0]
    
    
    
def saveSettings(recordings_folder):
#     print('recordings_folder ', recordings_folder)
#     conn = get_database_connection()
#     with conn:
#         #https://stackoverflow.com/questions/16856647/sqlite3-programmingerror-incorrect-number-of-bindings-supplied-the-current-sta
#         update_recordings_folder(conn, (recordings_folder,))
     print('recordings_folder ', recordings_folder)
#         conn = get_database_connection()
#         with conn:
            #https://stackoverflow.com/questions/16856647/sqlite3-programmingerror-incorrect-number-of-bindings-supplied-the-current-sta
#     update_recordings_folder(conn, (recordings_folder,))
     update_recordings_folder(recordings_folder)
        
def update_recording_information_for_single_recording(recording_id):
    print('About to update recording information for recording ', recording_id)    
    recording_information = get_recording_information_for_a_single_recording(recording_id)
    print('recording_information ', recording_information)    
    if recording_information == None:        
        print('recording_information == None')     
        return
         
    recording = recording_information['recording']
#     print('recording' , recording, '\n')
    
    recordingDateTime = recording['recordingDateTime']
#     print('recordingDateTime' , recordingDateTime, '\n')
    
    relativeToDawn = recording['relativeToDawn']
#     print('relativeToDawn' , relativeToDawn, '\n')
    
    relativeToDusk = recording['relativeToDusk']
#     print('relativeToDusk' , relativeToDusk, '\n')
    
    duration = recording['duration']
#     print('duration' , duration, '\n')
    
    location = recording['location']
#     print('location' , location, '\n') 
        
    coordinates = location['coordinates']
#     print('coordinates' , coordinates, '\n')
    
    locationLat = coordinates[0]
#     print('locationLat' , locationLat, '\n')
    
    locationLong = coordinates[1]
#     print('locationLong' , locationLong, '\n')
     
    version = recording['version']
#     print('version' , version, '\n') 
    
    batteryLevel = recording['batteryLevel']
#     print('batteryLevel' , batteryLevel, '\n') 
    
    additionalMetadata = recording['additionalMetadata']
#     print('additionalMetadata' , additionalMetadata, '\n')  
    
    phoneModel = additionalMetadata['Phone model']
#     print('phoneModel' , phoneModel, '\n')
    
    androidApiLevel = additionalMetadata['Android API Level']
#     print('androidApiLevel' , androidApiLevel, '\n')   
    
    Device = recording['Device']
#     print('Device' , Device, '\n')
    
    deviceId = Device['id']
#     print('deviceId' , deviceId, '\n')

    device_name = Device['devicename']
    
    
     
    nightRecording =  'false'
    
    if relativeToDusk is not None:
        if relativeToDusk > 0:
            nightRecording = 'true' 
    elif relativeToDawn is not None:
        if relativeToDawn < 0:
            nightRecording = 'true'    
    
#     print('nightRecording' , nightRecording, '\n')   
               
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
#         print(row)
#         print('recordingId ', row[0])
        # Don't update if we already have recordingDateTime
        recordingDateTime = row[1]
        if not recordingDateTime:
            print(recordingDateTime, ' is empty so will update record')
            recording_id = row[0]
            update_recording_information_for_single_recording(recording_id)
#         else:
#             print('Already have ', recordingDateTime, 'so not updating record')
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
#    print('data is ', data)
   
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
#     print('device ', device)
    single_recording_full_information = get_recording_information_for_a_single_recording(recording_id)
#     print(single_recording_full_information, '\n')
    recording = single_recording_full_information['recording']  
    tags = recording['Tags']   
    for tag in tags:
#         print(tag, '\n') 
        server_Id = tag['id']
#         print('server_Id ', server_Id)
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
    try:
        if check_if_tag_alredy_in_database(server_Id) == True:
            print('tag exists')
            return
        else:
             print('going to insert tag')
#         conn = get_database_connection()

        sql = ''' INSERT INTO tags(recording_id,server_Id, what, detail, confidence, startTime, duration, automatic, version, createdAt, tagger_username, deviceId, device_name, device_super_name)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur = get_database_connection().cursor()
#         print('unique_device 3 ', device)
        cur.execute(sql, (recording_id,server_Id, what, detail, confidence, startTime, duration, automatic, version, createdAt, tagger_username, deviceId, device_name, device_super_name))
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
#         print('tag does NOT exist')
        return False
    else:
#         print('tag exists')
        return True

def test_check_if_tag_alredy_in_database(): 
    check_if_tag_alredy_in_database(135939)  
 
def get_all_tags_for_all_devices_in_local_database():
    user_token = get_cacophony_user_token()
    unique_devices = get_unique_devices_stored_locally()
#     print('unique_devices ', unique_devices)
    for unique_device in unique_devices:  
        deviceId = unique_device[0]
        device_name = unique_device[1]
        device_super_name = unique_device[2]
           
      
#         recordings_with_tags = get_audio_recordings_with_tags_information_from_server(user_token, recording_type, str(unique_device))
        recording_type = 'audio'
# #         deviceId = 378
# #         recordings_with_tags = get_audio_recordings_with_tags_information_from_server(user_token, recording_type, str(deviceId))
        recordings_with_tags = get_audio_recordings_with_tags_information_from_server(user_token, recording_type, deviceId)
#         print('recordings_with_tags ', recordings_with_tags, '\n')
        for recording_with_tag in recordings_with_tags:
            print('device is', deviceId, '\n')  
#             print(recording_with_tag)
            recording_id =recording_with_tag['id']
            print('recording_id ', recording_id, '\n')

            get_and_store_tag_information_for_recording(str(recording_id), deviceId, device_name, device_super_name)
    print('Finished getting tags from server')
            
def test_get_all_tags_for_all_devices_in_local_database():
    get_all_tags_for_all_devices_in_local_database()            
     
def get_unique_devices_stored_locally():
#     conn = get_database_connection()
    cur = get_database_connection().cursor()
#     cur.execute("SELECT DISTINCT deviceId FROM recordings")
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
#         recording_id = filename.split('.')[0]
        recording_id = filename.replace('-','.').split('.')[0]
        print(recording_id)
#         conn = get_database_connection()
        cur = get_database_connection().cursor()
#     cur.execute("SELECT DISTINCT deviceId FROM recordings")
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
            
 
#         
#         
        
def test_scan_local_folder_for_recordings_not_in_local_db_and_update():
    scan_local_folder_for_recordings_not_in_local_db_and_update('grants shed')
           
       