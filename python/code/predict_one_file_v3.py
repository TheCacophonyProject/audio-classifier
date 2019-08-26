print('Hello Tim')
import pickle
import os
import numpy as np
from tqdm import tqdm
from scipy.io import wavfile
from python_speech_features import mfcc
from keras.models import load_model
import pandas as pd
from sklearn.metrics import accuracy_score
import random

import sys
from sys import argv

import librosa



def predict(audio_dir, fn):
   
    y_true = []
    y_pred = []
    fn_prob = {}
    
    
    print('Extracting features from audio')
    filename = os.path.join(audio_dir, fn)
    print('Filename: ', filename)
    
    

#    rate, wav = wavfile.read(os.path.join(audio_dir, fn))
    wav, rate = librosa.load(filename, sr=16000)
    
    # save the file to see how it sounds
    librosa.output.write_wav('file_trim_5s.wav', wav, rate)
    
    print('rate is: ', rate)
    print('wav shape is: ' , wav.shape)
#    label = fn2class[fn]
#    c = classes.index(label)
    y_prob = []
    
    for i in range(0, wav.shape[0]-config.step, config.step):
        sample = wav[i:i+config.step]
        x = mfcc(sample, rate, numcep=config.nfeat,
                 nfilt=config.nfft, nfft=config.nfft)
        x = (x - config.min) / (config.max - config.min)
        
        if config.mode == 'conv':
            x = x.reshape(1, x.shape[0], x.shape[1], 1)
        elif config.mode == 'time':
            x = np.expand_dims(x, axis=0)
        y_hat = model.predict(x)

        y_prob.append(y_hat)
#        y_pred.append(np.argmax(y_hat))
#        y_true.append(c)
        
    fn_prob[fn] = np.mean(y_prob, axis=0).flatten()
    index_max = np.argmax(fn_prob[fn])
    prediction = classes[index_max]    
        
    return prediction
     

#audio_file = '0c67f402.wav' 
#audio_file = 'screech1.wav'
#audio_file = 'screech1.mp4a' 
#audio_file = '1c9a423f.wav'
#audio_file = 'screech1_rated.wav'
audio_file = 'duck1.wav' 
         
if len(sys.argv) > 1:
    audio_file = sys.argv[1]

    

print('Audio file is: ' + audio_file)

    
df = pd.read_csv('instruments.csv')
classes = list(np.unique(df.label))

fn2class = dict(zip(df.fname, df.label))
p_path = os.path.join('pickles', 'conv.p')

with open(p_path, 'rb') as handle:
    config = pickle.load(handle)
    
model = load_model(config.model_path)

#prediction = predict('clean', audio_file)
prediction = predict('bird_monitor', audio_file)

print('Prediction is: ' + prediction)







































