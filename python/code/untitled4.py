#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 12:03:34 2019

@author: tim
"""

import json


squawk_json1 = {
    "origin": 1,
    "start_secs": 1,
    "what": "duck",
    "duration": 1.5}


with open('./temp/data1.json', 'w') as f:
  json.dump(squawk_json1, f, ensure_ascii=False)
  
squawk_json2 = {
    "origin": 2,
    "start_secs": 1,
    "what": "duck",
    "duration": 1.5}

with open('./temp/data2.json', 'w') as f:
  json.dump(squawk_json2, f, ensure_ascii=False)
  
squawk_json3 = {
    "origin": 3,
    "start_secs": 1,
    "what": "duck",
    "duration": 1.5}

with open('./temp/data3.json', 'w') as f:
  json.dump(squawk_json3, f, ensure_ascii=False)