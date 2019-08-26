# https://www.youtube.com/watch?v=mUXkj1BKYk0&list=PLhA3b2k8R3t2Ng1WW_7MiXeh1pfQJQi_P&index=3
import os
from tqdm import tqdm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.io.wavfile import read as read_wav
from python_speech_features import mfcc, logfbank
import librosa as librosa

def plot_signals(signals):
    fig, axes = plt.subplots(nrows=2, ncols=5, sharex=False,
                             sharey=True, figsize=(20,5))
    fig.suptitle('Time Series', size=16)
    i = 0
    for x in range(2):
        for y in range(5):
            axes[x,y].set_title(list(signals.keys())[i])
            axes[x,y].plot(list(signals.values())[i])
            axes[x,y].get_xaxis().set_visible(False)
            axes[x,y].get_yaxis().set_visible(False)
            i += 1

def plot_fft(fft):
    fig, axes = plt.subplots(nrows=2, ncols=5, sharex=False,
                             sharey=True, figsize=(20,5))
    fig.suptitle('Fourier Transforms', size=16)
    i = 0
    for x in range(2):
        for y in range(5):
            data = list(fft.values())[i]
            Y, freq = data[0], data[1]
            axes[x,y].set_title(list(fft.keys())[i])
            axes[x,y].plot(freq, Y)
            axes[x,y].get_xaxis().set_visible(False)
            axes[x,y].get_yaxis().set_visible(False)
            i += 1

def plot_fbank(fbank):
    fig, axes = plt.subplots(nrows=2, ncols=5, sharex=False,
                             sharey=True, figsize=(20,5))
    fig.suptitle('Filter Bank Coefficients', size=16)
    i = 0
    for x in range(2):
        for y in range(5):
            axes[x,y].set_title(list(fbank.keys())[i])
            axes[x,y].imshow(list(fbank.values())[i],
                    cmap='hot', interpolation='nearest')
            axes[x,y].get_xaxis().set_visible(False)
            axes[x,y].get_yaxis().set_visible(False)
            i += 1

def plot_mfccs(mfccs):
    fig, axes = plt.subplots(nrows=2, ncols=5, sharex=False,
                             sharey=True, figsize=(20,5))
    fig.suptitle('Mel Frequency Cepstrum Coefficients', size=16)
    i = 0
    for x in range(2):
        for y in range(5):
            axes[x,y].set_title(list(mfccs.keys())[i])
            axes[x,y].imshow(list(mfccs.values())[i],
                    cmap='hot', interpolation='nearest')
            axes[x,y].get_xaxis().set_visible(False)
            axes[x,y].get_yaxis().set_visible(False)
            i += 1

def envelope(y, rate, threshold):
    mask = []
    y = pd.Series(y).apply(np.abs)
    y_mean = y.rolling(window=int(rate/10), min_periods=1, center=True).mean()
    for mean in y_mean:
        if mean > threshold:
            mask.append(True)
        else:
            mask.append(False)
    return mask
          
def calc_fft(y, rate):
    n = len(y)
    freq = np.fft.rfftfreq(n, d=1/rate)
    Y = abs(np.fft.rfft(y)/n)
    return (Y, freq)

#df = pd.read_csv('instruments.csv')
os.system('clear')
print('Step 1\n')
df = pd.read_csv('sound_clips.csv')
df.set_index('fname',inplace=True)

for f in df.index:
    try:    

        rate, signal = wavfile.read('wavfiles/'+f)        
        df.at[f,'length'] = signal.shape[0]/rate
        
    except Exception as e:
        print(str(e))    
    
classes = list(np.unique(df.label))
class_dist = df.groupby(['label'])['length'].mean()
count = df.groupby(['label'])['length'].count()
print('Tag name\tCount', count)

fig, ax = plt.subplots()
ax.set_title('Class Distribution', y=1.08)
ax.pie(class_dist, labels=class_dist.index, autopct='%1.1f%%',
       shadow=False, startangle=90)
ax.axis('equal')
plt.show()
df.reset_index(inplace=True)

signals = {}
fft = {}
fbank = {}
mfccs = {}

print('Step 2\n')

for c in classes:
    try:
        wav_file = df[df.label == c].iloc[0,0]    
        #signal, rate = librosa.load('wavfiles/'+wav_file, sr=44100)
        signal, rate = librosa.load('wavfiles/'+wav_file, sr=None)
        print('rate is ', rate)
#        mask = envelope(signal, rate, 0.0005)
#        signal = signal[mask]
        signals[c] = signal
        fft[c] = calc_fft(signal, rate)
        
        bank = logfbank(signal[:rate], nfilt=26, nfft=1103).T
        fbank[c] = bank
        nfft=int(rate/40)
        print('nfft is ',nfft)
        mel = mfcc(signal[:rate], rate, numcep=13, nfilt=26, nfft=1103).T
        mfccs[c] = mel
    except Exception as e:
        print(str(e))        
    
#plot_signals(signals)
#plt.show()
#
#plot_fbank(fbank)
#plt.show()
#
#plot_mfccs(mfccs)
#plt.show()
#
#print('Cleaning files\n')
#
#if not os.path.exists('./clean'):
#        os.makedirs('./clean') 
#
#if len(os.listdir('clean')) == 0:
#    for f in tqdm(df.fname):
#        try:
#            
#            signal, rate = librosa.load('wavfiles/'+f, sr=None)
#            mask = envelope(signal, rate, 0.0005)
#            wavfile.write(filename='clean/'+f, rate=rate, data=signal[mask])
#            
#        except Exception as e:
#            print(str(e))   
#            
#
#
#
#































