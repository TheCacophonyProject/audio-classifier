#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 15:20:24 2019

@author: tim
"""
import os

base_folder = '/home/tim/Work/Cacophony/Audio Analysis/training_images/data_for_second_iteration/input_to_model/'
hammond_park = '/fpF7B9AFNn6hvfVgdrJB/'
grants_shed = '/grants_shed/'

#morepork_images_in_folder = 'base_folder/morepork/'
#unknown_images_in_folder = 'base_folder/unknown/'
arff_filename = base_folder + 'input_for_second_iteration.arff'
print ('arff_filename ', arff_filename)

def replace_spaces_in_filenames(directory, filename):
    
    os.rename(f, f.replace(' ', '_'))
    
    

f= open(arff_filename,"w+")

f.write("%% mel_spectrogram data of audio using\n")
f.write("%% librosa.feature.melspectrogram(y=y, n_mels=10, fmin=800,fmax=1000)\n")
f.write("%% i.e. 10 mell bands, min freq 800 Hz, max freq 1000 - the Classic more-pork call freq range\n")
f.write("%% 1.5 seconds of data\n")
f.write("\n")
f.write("@relation input_for_second_iteration\n")
f.write("@attribute filename string\n")
f.write("@attribute class {MOREPORK, MAYBE_MOREPORK, MOREPORK_BUT_NOISY, QUIET_MOREPORK, NOT_MOREPORK, UNKNOWN}\n")
f.write("\n")
f.write("@data\n")




for filename in os.listdir(base_folder + hammond_park + 'maybe_morepork'):
    print(filename) 
   
#    recording_id = filename.split("_")[0]
    f.write(hammond_park + "maybe_morepork/" + filename + ",MAYBE_MOREPORK\n")
    
for filename in os.listdir(base_folder + hammond_park + 'morepork'):
    print(filename)    
#    recording_id = filename.split("_")[0]
    f.write(hammond_park + "morepork/" + filename + ",MOREPORK\n")
    
for filename in os.listdir(base_folder + hammond_park + 'morepork_but_noisy'):
    print(filename)    
#    recording_id = filename.split("_")[0]
    f.write(hammond_park + "morepork_but_noisy/" + filename + ",MOREPORK_BUT_NOISY\n")
    
for filename in os.listdir(base_folder + hammond_park + 'not_morepork'):
    print(filename)    
#    recording_id = filename.split("_")[0]
    f.write(hammond_park + "not_morepork/" + filename + ",NOT_MOREPORK\n")
    
for filename in os.listdir(base_folder + hammond_park + 'quiet_morepork'):
    print(filename)    
#    recording_id = filename.split("_")[0]
    f.write(hammond_park + "quiet_morepork/" + filename + ",QUIET_MOREPORK\n")
    
for filename in os.listdir(base_folder + hammond_park + 'unknown'):
    print(filename)    
#    recording_id = filename.split("_")[0]
    f.write(hammond_park + "unknown/" + filename + ",UNKNOWN\n")
    
    
    
for filename in os.listdir(base_folder + grants_shed + 'maybe_morepork'):   
    os.rename(base_folder + grants_shed + 'maybe_morepork/' + filename, base_folder + grants_shed + 'maybe_morepork/' + filename.replace('s ', 's_'))
for filename in os.listdir(base_folder + grants_shed + 'maybe_morepork'):   
    os.rename(base_folder + grants_shed + 'maybe_morepork/' + filename, base_folder + grants_shed + 'maybe_morepork/' + filename.replace(" ", ""))
   
for filename in os.listdir(base_folder + grants_shed + 'maybe_morepork'):
    print(filename)     
    f.write("/grants_shed/maybe_morepork/" + filename + ",MAYBE_MOREPORK\n")
    
for filename in os.listdir(base_folder + grants_shed + 'morepork'):    
    os.rename(base_folder + grants_shed + 'morepork/' + filename, base_folder + grants_shed + 'morepork/' + filename.replace('s ', 's_'))
for filename in os.listdir(base_folder + grants_shed + 'morepork'):
    os.rename(base_folder + grants_shed + 'morepork/' + filename, base_folder + grants_shed + 'morepork/' + filename.replace(" ", ""))
    
for filename in os.listdir(base_folder + grants_shed + 'morepork'):
    print(filename)       
    f.write("/grants_shed/morepork/" + filename + ",MOREPORK\n")
    
for filename in os.listdir(base_folder + grants_shed + 'morepork_but_noisy'):    
    os.rename(base_folder + grants_shed + 'morepork_but_noisy/' + filename, base_folder + grants_shed + 'morepork_but_noisy/' + filename.replace('s ', 's_'))
for filename in os.listdir(base_folder + grants_shed + 'morepork_but_noisy'):
    os.rename(base_folder + grants_shed + 'morepork_but_noisy/' + filename, base_folder + grants_shed + 'morepork_but_noisy/' + filename.replace(" ", ""))
    
for filename in os.listdir(base_folder + grants_shed + 'morepork_but_noisy'):
    print(filename)  
    fileNameWithoutSpace = filename.replace(" ", "")
    f.write("/grants_shed/morepork_but_noisy/" + fileNameWithoutSpace + ",MOREPORK_BUT_NOISY\n")
    
for filename in os.listdir(base_folder + grants_shed + 'not_morepork'):    
    os.rename(base_folder + grants_shed + 'not_morepork/' + filename, base_folder + grants_shed + 'not_morepork/' + filename.replace('s ', 's_'))
for filename in os.listdir(base_folder + grants_shed + 'not_morepork'):
    os.rename(base_folder + grants_shed + 'not_morepork/' + filename, base_folder + grants_shed + 'not_morepork/' + filename.replace(" ", ""))
    
for filename in os.listdir(base_folder + grants_shed + 'not_morepork'):
    print(filename)
    fileNameWithoutSpace = filename.replace(" ", "")
    f.write("/grants_shed/not_morepork/" + fileNameWithoutSpace + ",NOT_MOREPORK\n")
    
#for filename in os.listdir(base_folder + grants_shed + 'quiet_morepork'):    
#    os.rename(base_folder + grants_shed + 'quiet_morepork/' + filename, base_folder + grants_shed + 'quiet_morepork/' + filename.replace('s ', 's_'))
#for filename in os.listdir(base_folder + grants_shed + 'quiet_morepork'):
#    os.rename(base_folder + grants_shed + 'quiet_morepork/' + filename, base_folder + grants_shed + 'quiet_morepork/' + filename.replace(" ", ""))
    
#for filename in os.listdir(base_folder + grants_shed + 'quiet_morepork'):
#    print(filename)   
#    fileNameWithoutSpace = filename.replace("_ ", "")
#    recording_id = filename.split("_")[0]
#    f.write("/grants_shed/quiet_morepork/" + fileNameWithoutSpace + ",QUIET_MOREPORK\n")
    
for filename in os.listdir(base_folder + grants_shed + 'unknown'):    
    os.rename(base_folder + grants_shed + 'unknown/' + filename, base_folder + grants_shed + 'unknown/' + filename.replace('s ', 's_'))
for filename in os.listdir(base_folder + grants_shed + 'unknown'):
    os.rename(base_folder + grants_shed + 'unknown/' + filename, base_folder + grants_shed + 'unknown/' + filename.replace(" ", ""))
    
for filename in os.listdir(base_folder + grants_shed + 'unknown'):
    print(filename) 
    fileNameWithoutSpace = filename.replace(" ", "")
    f.write("/grants_shed/unknown/" + fileNameWithoutSpace + ",UNKNOWN\n")
        
    
f.close()