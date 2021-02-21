import numpy as np
from math import tau as 𝜏
from scipy.io import wavfile

def write(filename, hz, left, right):
    stereo = np.array([left, right]).astype(np.int16).T
    print('Saving', len(stereo) / hz, 'seconds of audio to sample.wav')
    print('Maximum excursion:', max(stereo.flatten()))
    wavfile.write('sample.wav', hz, stereo)

def fuzz(a):
    amplitude = abs(a).max() / 1000.0
    r = np.random.random(size=len(a))
    return a + r * amplitude

def twenties(t):
    frequencies = 20, 63, 200, 630, 2000, 6300
    a = 0.0
    for frequency in frequencies:
        a += np.sin(𝜏 * t * frequency)
    return a / len(frequencies)

def sine_stack(t, low, high, logstep, verbose=True):
    T = t[-1] + t[1]
    print('Creating stacked sine sample', T, 'seconds long')
    low = np.log10(low)
    high = np.log10(high)
    frequencies = np.arange(low, high + logstep/100.0, logstep)
    indices = (10.0 ** frequencies * T).round().astype(int)
    frequencies = indices.astype(np.float64) / T
    if verbose:
        print('Stacking', len(frequencies), 'frequencies:')
        print(frequencies)
    a = 0.0
    for frequency in frequencies:
        a += np.sin(𝜏 * t * frequency)
    return indices, a

def normalize(a, verbose=True):
    factor = max(abs(a))
    if verbose:
        print('Dividing amplitude by:', factor)
    return a / factor

def trim_silence(T, hz, signal):
    """Return the `T` seconds of `signal` that are the least silent."""
    N = T * hz
    extra = len(signal) - N
    c = np.abs(signal).cumsum()
    c = c[-extra:] - c[:extra]
    i = np.argmax(c)
    print(f'Keeping {T:.2g} of {len(signal)/hz:.2g} seconds'
          f' starting at +{i/hz:.2f} seconds')
    return signal[i:i+N]
