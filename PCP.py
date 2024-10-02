
from __future__ import division
from scipy.signal.windows import hamming, bartlett
from scipy.fftpack import fft
import numpy as np
import matplotlib.pyplot as plt
from librosa import cqt, display, amplitude_to_db
import CQTransform


def compute_PCP(x, fs, bins = 12, fmin = 96, fmax = 4000):

    nOctave = np.int32(np.ceil(np.log2(fmax / fmin)))
    #print("Number of octaves: " + str(nOctave))
    pcp = np.zeros(bins)

    #using librosas cqt for speed
    cqt_fast = cqt(x, sr = fs, fmin = fmin, bins_per_octave = bins, window = bartlett)


    #librosa function to plot the resulting spectrogram
    #uncomment to use
    """fig, ax = plt.subplots()
    display.specshow(amplitude_to_db(np.abs(cqt_fast), ref = np.max),  sr=fs, x_axis='time', y_axis='cqt_note', ax=ax)
    plt.show()"""

    pcp = CQTransform.HPCP(np.absolute(cqt_fast), bins, nOctave)
    """plt.stem(range(len(CH)), CH)
    plt.show()"""
    return pcp
