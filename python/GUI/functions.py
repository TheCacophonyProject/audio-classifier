'''
Created on 5 Sep 2019

@author: tim
'''
import sqlite3
from sqlite3 import Error
import requests

database = "audio_analysis_db"

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
 
    return conn
    
def select_names(conn):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    cur = conn.cursor()
    cur.execute("select * from users")
 
    rows = cur.fetchall()
 
    for row in rows:
        print(row)
        
def update_recordings_folder(conn, recordings_folder):
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
    cur = conn.cursor()
    cur.execute(sql, recordings_folder)
    conn.commit()
        
def getNames():
    database = "audio_analysis_db"
    conn = create_connection(database)
    with conn:
        print("1. Query task by priority:")
        select_names(conn)
        
def getRecordingsFolder():
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("select * from settings")
 
    rows = cur.fetchall()
 
    for row in rows:
        #print(row)
        return row[0]
    
def saveSettings(recordings_folder):
    conn = create_connection(database)
    with conn:
        #https://stackoverflow.com/questions/16856647/sqlite3-programmingerror-incorrect-number-of-bindings-supplied-the-current-sta
        update_recordings_folder(conn, (recordings_folder,))
    
        
        