#!/usr/bin/env python

import json
import numpy
import os
import sys
import wavio
import scipy.fftpack

ffmpegEXE = 'ffmpeg'  # or ffmpeg.exe on windows etc


def rms(x):
        # Root-Mean-Square
    return numpy.sqrt(x.dot(x)/x.size)


def rms_nonzero(x):
    nz = x[x != 0]
    return rms(nz)


def TukeySide(window, x, alpha):
    mask = x < alpha
    window[mask] = (1-numpy.cos(numpy.pi*x[mask]/alpha))/2


def TukeyWindow(windowLength, alpha=0.5):
    result = numpy.ones(windowLength)
    TukeySide(result, numpy.linspace(0, 2, windowLength), alpha)
    TukeySide(result, numpy.linspace(2, 0, windowLength), alpha)
    return result


def ExtractCompressedAudioNTS(fileName):
    # Not Thread Safe!!

    os.system('mkdir -p temp')
    tempWav = 'temp/temp.wav'
    tempRaw = 'temp/temp.raw'

    sampleRate = 48000

    if True:
        cmd = '%s -y -i "%s" -ac 1 -ar %d %s' % (
            ffmpegEXE, fileName, sampleRate, tempWav)
        print(cmd)
        sys.stdout.flush()
        os.system(cmd)
        dw = wavio.read(tempWav)
        # sampleRate=dw.rate

    cmd = '%s -y -i "%s" -f f32le -c:a pcm_f32le -ac 1 -ar %d %s' % (
        ffmpegEXE, fileName, sampleRate, tempRaw)
    print(cmd)
    sys.stdout.flush()
    os.system(cmd)

    data = numpy.fromfile(tempRaw, dtype=numpy.dtype('<f'))
    return (data, sampleRate)


#def NoiseReduction(data, sampleRate, verbose):
#    originalSampleCount = data.shape[0]
#
#    dctWidth = 2048
#    window = TukeyWindow(dctWidth)
#    trimWidth = int(dctWidth/8)
#    stride = dctWidth-trimWidth*3
#
#    blockCount = int((originalSampleCount+stride-1)/stride)
#    dataPad = numpy.pad(data, (stride, stride*2), 'reflect')
#    spectrogram = numpy.empty((blockCount, dctWidth))
#
#    if verbose:
#        print('Building spectrogram')
#
#    for index in range(blockCount):
#        blockIndex = index*stride
#        block = dataPad[blockIndex:blockIndex+dctWidth]*window
#        dct = scipy.fftpack.dct(block)
#        spectrogram[index] = dct
#
#    # build the tolerance
#    binMedians = numpy.median(abs(spectrogram), axis=0)
#    tolerance = 4*numpy.convolve(binMedians, numpy.ones(8)/8)[4:-3]
#
#    spectrogramTrimmed = numpy.empty((blockCount, dctWidth))
#
#    bassCutOffFreq = 100  # anything below bassCutOffFreq requires specialised techniques
#    bassCutOffBand = int(bassCutOffFreq*2*dctWidth/sampleRate)
#
#    if verbose:
#        print('Creating bins for noise reduction')
#
#    rmsTab = numpy.empty(blockCount)
#    for index in range(blockCount):
#        blockIndex = index*stride
#        block = dataPad[blockIndex:blockIndex+dctWidth]*window
#        dct = scipy.fftpack.dct(block)
#
#        mask = numpy.ones_like(dct)
#
#        mask[0:bassCutOffBand] *= 0
#        rmsTab[index] = rms(dct*mask)
#
#        for band in range(dctWidth):
#            if abs(dct[band]) < tolerance[band]:
#                mask[band] *= 0.0
#
#        maskCon = 10*numpy.convolve(mask, numpy.ones(8)/8)[4:-3]
#
#        maskBin = numpy.where(maskCon > 0.1, 0, 1)
#        spectrogramTrimmed[index] = maskBin
#
#    resultPad = numpy.zeros_like(dataPad)
#
#    if verbose:
#        print('noise floor..')
#    rmsCutoff = numpy.median(rmsTab)
#
#    if verbose:
#        print('Reconstruction...')
#
#    for index in range(1, blockCount-1):
#        blockIndex = index*stride
#        block = dataPad[blockIndex:blockIndex+dctWidth]*window
#        dct = scipy.fftpack.dct(block)
#
#        trim3 = spectrogramTrimmed[index-1] * \
#            spectrogramTrimmed[index]*spectrogramTrimmed[index+1]
#        dct *= (1-trim3)
#
#        if rms(dct) < rmsCutoff:
#            continue  # too soft
#        if rms_nonzero(dct)*4 > max(dct):
#            continue  # white noise
#
#        rt = scipy.fftpack.idct(dct)/(dctWidth*2)
#        resultPad[blockIndex+trimWidth*1:blockIndex+trimWidth *
#                  2] += rt[trimWidth*1:trimWidth*2]*numpy.linspace(0, 1, trimWidth)
#        resultPad[blockIndex+trimWidth*2:blockIndex+trimWidth *
#                  6] = rt[trimWidth*2:trimWidth*6]  # *numpy.linspace(1,1,stride8*4)
#        resultPad[blockIndex+trimWidth*6:blockIndex+trimWidth *
#                  7] = rt[trimWidth*6:trimWidth*7]*numpy.linspace(1, 0, trimWidth)
#
#    result = resultPad[stride:stride+originalSampleCount]
#
#    if verbose:
#        stereoPad = numpy.zeros((dataPad.shape[0], 2))
#        stereoPad[:, 0] = dataPad
#        stereoPad[:, 1] = resultPad
#        wavio.write('temp/stereoPad.wav', stereoPad,
#                    sampleRate, (-1, 1), sampwidth=2)
#
#        stereo = numpy.zeros((originalSampleCount, 2))
#        stereo[:, 0] = data
#        stereo[:, 1] = result
#        wavio.write('temp/stereoCompare.wav', stereo,
#                    sampleRate, (-1, 1), sampwidth=2)
#
#    tempOut = 'temp/noiseReduce.wav'
#    if verbose:
#        print('Write to %s' % 'temp/noiseReduce.wav')
#        wavio.write(tempOut, result, sampleRate, (-1, 1), sampwidth=2)
#
#        print('Convert to MP3 (requires libmp3lame)')
#        cmd = '%s -y -i %s -codec:a libmp3lame -qscale:a 2 noiseReduce.mp3' % (
#            ffmpegEXE, 'temp/noiseReduce.wav')
#        print(cmd)
#        sys.stdout.flush()
#        os.system(cmd)
#
#    return result

def NoiseReduction(data, sampleRate, verbose):
    originalSampleCount = data.shape[0]

    dctWidth = 2048
    window = TukeyWindow(dctWidth)
    trimWidth = int(dctWidth/8)
    stride = dctWidth-trimWidth*3

    blockCount = int((originalSampleCount+stride-1)/stride)
    dataPad = numpy.pad(data, (stride, stride*2), 'reflect')
    spectrogram = numpy.empty((blockCount, dctWidth))

    if verbose:
        print('Building spectrogram')

    for index in range(blockCount):
        blockIndex = index*stride
        block = dataPad[blockIndex:blockIndex+dctWidth]*window
        dct = scipy.fftpack.dct(block)
        spectrogram[index] = dct

    # build the tolerance
    binMedians = numpy.median(abs(spectrogram), axis=0)
    tolerance = 4*numpy.convolve(binMedians, numpy.ones(8)/8)[4:-3]

    spectrogramTrimmed = numpy.empty((blockCount, dctWidth))

    bassCutOffFreq = 500  # anything below bassCutOffFreq requires specialised techniques
    bassCutOffBand = int(bassCutOffFreq*2*dctWidth/sampleRate)

    trebleCutOffFreq = 1000
    trebleCutOffBand = int(trebleCutOffFreq*2*dctWidth/sampleRate)

    if verbose:
        print('Creating bins for noise reduction')

    rmsTab = numpy.empty(blockCount)
    for index in range(blockCount):
        blockIndex = index*stride
        block = dataPad[blockIndex:blockIndex+dctWidth]*window
        dct = scipy.fftpack.dct(block)

        mask = numpy.ones_like(dct)

        mask[:bassCutOffBand] *= 0
        mask[trebleCutOffBand:] *= 0
        rmsTab[index] = rms(dct*mask)

        for band in range(dctWidth):
            if abs(dct[band]) < tolerance[band]:
                mask[band] *= 0.0

        maskCon = 10*numpy.convolve(mask, numpy.ones(8)/8)[4:-3]

        maskBin = numpy.where(maskCon > 0.1, 0, 1)
        spectrogramTrimmed[index] = maskBin

    resultPad = numpy.zeros_like(dataPad)

    if verbose:
        print('noise floor..')
    rmsCutoff = numpy.median(rmsTab)

    if verbose:
        print('Reconstruction...')

    for index in range(1, blockCount-1):
        blockIndex = index*stride
        block = dataPad[blockIndex:blockIndex+dctWidth]*window
        dct = scipy.fftpack.dct(block)

        trim3 = spectrogramTrimmed[index-1] * \
            spectrogramTrimmed[index]*spectrogramTrimmed[index+1]
        dct *= (1-trim3)

        if rms(dct) < rmsCutoff:
            continue  # too soft
# if rms_nonzero(dct)*4>max(dct):
# continue #white noise

        rt = scipy.fftpack.idct(dct)/(dctWidth*2)
        resultPad[blockIndex+trimWidth*1:blockIndex+trimWidth *
                  2] += rt[trimWidth*1:trimWidth*2]*numpy.linspace(0, 1, trimWidth)
        resultPad[blockIndex+trimWidth*2:blockIndex+trimWidth *
                  6] = rt[trimWidth*2:trimWidth*6]  # *numpy.linspace(1,1,stride8*4)
        resultPad[blockIndex+trimWidth*6:blockIndex+trimWidth *
                  7] = rt[trimWidth*6:trimWidth*7]*numpy.linspace(1, 0, trimWidth)

    result = resultPad[stride:stride+originalSampleCount]

    if verbose:
        stereoPad = numpy.zeros((dataPad.shape[0], 2))
        stereoPad[:, 0] = dataPad
        stereoPad[:, 1] = resultPad
        wavio.write('temp/stereoPad.wav', stereoPad,
                    sampleRate, (-1, 1), sampwidth=2)

        stereo = numpy.zeros((originalSampleCount, 2))
        stereo[:, 0] = data
        stereo[:, 1] = result
        wavio.write('temp/stereoCompare.wav', stereo,
                    sampleRate, (-1, 1), sampwidth=2)

    tempOut = 'temp/noiseReduce.wav'
    if verbose:
        print('Write to %s' % 'temp/noiseReduce.wav')
        wavio.write(tempOut, result, sampleRate, (-1, 1), sampwidth=2)

        print('Convert to MP3 (requires libmp3lame)')
        cmd = '%s -y -i %s -codec:a libmp3lame -qscale:a 2 noiseReduce.mp3' % (
            ffmpegEXE, 'temp/noiseReduce.wav')
        print(cmd)
        sys.stdout.flush()
        os.system(cmd)

    return result

def FindSquawks(source, sampleRate):
    result = []
    source = source / max(source)
    startIndex = None
    stopIndex = None
    smallTime = int(sampleRate*0.1)
    tolerance = 0.2
    for index in range(source.shape[0]):
        if not startIndex:
            if abs(source[index]) > tolerance:
                startIndex = index
                stopIndex = index
            continue
        if abs(source[index]) > tolerance:
            stopIndex = index
        elif index > stopIndex+smallTime:
            duration = (stopIndex-startIndex)/sampleRate
            if duration > 0.05:
                squawk = {'start': startIndex,
                          'stop': stopIndex, 'duration': duration}
                squawk['rms'] = rms(source[startIndex:stopIndex])
                result.append(squawk)
            startIndex = None
    return result


def ExtractSquawkData(source, sampleRate, squawk):
    startIndex = squawk['start']
    stopIndex = squawk['stop']
    width = int(0.05*sampleRate)
    t0 = max(0, startIndex-width)
    t1 = min(source.shape[0], stopIndex+width)
    result = source[t0:t1]
    result[:startIndex-t0] *= numpy.linspace(0, 1, startIndex-t0)
    result[stopIndex-t0:t1-t0] *= numpy.linspace(1, 0, t1-stopIndex)
    result *= 0.125/squawk['rms']
    return result


def Main():
    verbose = True
    audio_in_path = './test_samples/153036.m4a'
    (data, sampleRate) = ExtractCompressedAudioNTS(audio_in_path)

    rescale = 1/(rms(data)+1e-8)/16
    data *= rescale

    if verbose:
        wavio.write('temp/loadcheck.wav', data,
                    sampleRate, (-1, 1), sampwidth=2)

    noiseReduceData = NoiseReduction(data, sampleRate, verbose)

    squawks = FindSquawks(noiseReduceData, sampleRate)

    os.system('mkdir -p squawk')
    index = 0
    for s in sorted(squawks, key=lambda squawk: squawk['duration']):
        sub = ExtractSquawkData(noiseReduceData, sampleRate, s)
        print(json.dumps(s))
        fileName = 'squawk/squawk%04d.wav' % index
        wavio.write(fileName, sub, sampleRate, (-1, 1), sampwidth=2)
        fileName = 'squawk/squawk%04d.json' % index
        with open(fileName, 'w') as f:
            f.write(json.dumps(s, sort_keys=True, indent=4))
        index = index+1


def ExtractSquawks(dirName, fileName, meta):
    
    global GSquawkIndex
    GSquawkIndex=0
    verbose = True

    (data, sampleRate) = ExtractCompressedAudioNTS(dirName+'/'+fileName)

    rescale = 1/(rms(data)+1e-8)/16
    data *= rescale

    if verbose:
        wavio.write('temp/loadcheck.wav', data,
                    sampleRate, (-1, 1), sampwidth=2)

    noiseReduceData = NoiseReduction(data, sampleRate, verbose)

    squawks = FindSquawks(noiseReduceData, sampleRate)

    print('Squawk count : %d\n' % len(squawks))

    os.system('mkdir -p squawk')
    for s in sorted(squawks, key=lambda squawk: squawk['duration']):
        s['origin'] = fileName
        index = GSquawkIndex
        GSquawkIndex = GSquawkIndex+1
        sub = ExtractSquawkData(noiseReduceData, sampleRate, s)
        print(json.dumps(s))
        wavName = 'squawk/squawk%04d.wav' % index
        wavio.write(wavName, sub, sampleRate, (-1, 1), sampwidth=2)
        jsonName = 'squawk/squawk%04d.json' % index
        s.update(meta)
        with open(jsonName, 'w') as f:
            f.write(json.dumps(s, sort_keys=True, indent=4))
    
    
#Main()
            
ExtractSquawks('./test_samples/', '153036.m4a', meta={'test':'yes'})

