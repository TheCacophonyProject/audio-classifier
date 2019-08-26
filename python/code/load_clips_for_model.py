#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 10:02:44 2019

@author: tim
"""

# Going to put clips and information into same format as tutorial
# Could change this at a later date, by changing format that the tutorial accepts
# but for the moment, I'll keep using the instruments.csv file to record the
# the files and their class

# So, loop through sub directories in the tagged_recordings folder
# copy them into the audio_files_cacophony folder (cf wavfiles folder in the tutorial)
# and insert a row in the tags.csv file (cf the instruments folder of the tutorial)

# Test can load the file format
import os
from tqdm import tqdm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.io.wavfile import read as read_wav
from python_speech_features import mfcc, logfbank
import librosa as librosa

sampling_rate, data=read_wav('wavfiles/'+wav_file) 