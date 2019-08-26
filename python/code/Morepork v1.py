#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  8 17:27:04 2019

@author: tim
"""


import functions

#device_name = '0070_v1_3_6' # copy this from Device column of https://browse.cacophony.org.nz/recordings (or test server)
device_name = 'fpF7B9AFNn6hvfVgdrJB'

functions.retrieve_available_recordings_from_server(device_name)

functions.sort_into_day_or_night(device_name)

functions.create_filtered_files(device_name)

functions.create_squawks_from_recordings(device_name)


