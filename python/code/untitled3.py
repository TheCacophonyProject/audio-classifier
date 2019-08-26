import librosa
import numpy as np
import sounddevice as sd

audio_in_path = './madmom/153036.wav'
y, sr = librosa.load(audio_in_path, sr=None) 
# https://stackoverflow.com/questions/10357992/how-to-generate-audio-from-a-numpy-array
y_amplified = np.int16(y/np.max(np.abs(y)) * 32767)
sd.play(y_amplified, sr)