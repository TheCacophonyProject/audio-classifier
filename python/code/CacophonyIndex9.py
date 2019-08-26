
import math
import numpy
import scipy.signal
import wavio


def GetSourceResampled(sampleRate=16000):
    source = wavio.read('source.wav')
    lengthResampled = int(source.data.shape[0]*sampleRate/source.rate)
    result = scipy.signal.resample(source.data, lengthResampled).flatten()
    return result


def GetBins(sourceTrim, sampleRate):
    windowSize = sourceTrim.shape[0]  # e.g. 2048
    window = numpy.hanning(windowSize)
    signal = window*sourceTrim
    dct = scipy.fftpack.dct(signal)
    bassCutOffFreq = 100
    bassCutOffBand = int(bassCutOffFreq*2*windowSize/sampleRate)

    edges = numpy.logspace(math.log10(bassCutOffBand),
                           math.log10(windowSize), num=11, dtype=int)
    binsRaw = numpy.split(dct, edges[:-1])
    return numpy.array([sum(x*x) for x in binsRaw[1:]])


def ScoreFromPoints(points):
    pointsSorted = sorted(points)
    k0 = int(len(points)*0.75)
    k1 = int(len(points)*0.95)
    return 10*numpy.mean(pointsSorted[k0:k1])


def Main():
    sampleRate = 16000
    windowSize = 2048
    source = GetSourceResampled(sampleRate)

    halfWS = int(windowSize/2)
    previousBins = None
    points = []
    for offset in range(halfWS, source.shape[0]-halfWS*3, halfWS):
        bins = GetBins(source[offset:offset+windowSize], sampleRate)
        if not previousBins is None:
            scorePlus = (sum(bins*2 < previousBins))
            scoreMinus = (sum(bins > previousBins*2))
            points.append(scorePlus+scoreMinus)
        previousBins = bins

    bin20Width = 312  # ~20 seconds
    for q in range(0, len(points)-bin20Width, bin20Width):
        score = ScoreFromPoints(points[q:q+bin20Width])
        t0 = int(q*halfWS/sampleRate+0.5)
        t1 = int((q+bin20Width)*halfWS/sampleRate+0.5)
        print('Score ( %ds .. %ds ) = %0.1f%%' % (t0, t1, score))


Main()
