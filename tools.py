import numpy as np
from math import tau as 𝜏

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

def sine_stack(t, low, high, logstep):
    low = np.log10(low)
    high = np.log10(high)
    frequencies = np.arange(low, high + logstep/100.0, logstep)
    frequencies = (10.0 ** frequencies).round()
    print('Frequencies:', frequencies)
    a = 0.0
    for frequency in frequencies:
        a += np.sin(𝜏 * t * frequency)
    return a / len(frequencies)

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
