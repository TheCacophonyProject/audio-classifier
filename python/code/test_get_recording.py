#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 20:12:04 2019

@author: tim
"""
import requests
url = "https://api-test.cacophony.org.nz/api/v1/signedUrl"

querystring = {"jwt":"JWT yJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfdHlwZSI6ImZpbGVEb3dubG9hZCIsImtleSI6IjVmZTBhY2NjLTdjNGQtMTFlOS1hNjc1LTQyYjg5YTY4NTZjOSIsImZpbGVuYW1lIjoiMjAxOTA1MjItMTY1MjAwLm1wMyIsIm1pbWVUeXBlIjoiYXVkaW8vbXAzIiwiaWF0IjoxNTU4NTEyMDgxLCJleHAiOjE1NTg1MTI2ODF9.3NPveavHav4bgEROk0H1VkkmkZWs9BFlZ-rlA2hqwSI"}

headers = {
    'User-Agent': "PostmanRuntime/7.13.0",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "1d2a2aa7-749b-481e-becc-0beb8c8b20a9,a26a1229-6d15-4099-834e-a9f8ece2d8e6",
    'Host': "api-test.cacophony.org.nz",
    'accept-encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)