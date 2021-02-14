import numpy as np

def trim_silence(signal, threshold=100, hz=44100):
    indexes = np.nonzero(np.abs(signal) > 100)[0]
    i, j = indexes[0], indexes[-1]
    print(f'Trimming {i/hz:.2f}s left, {(len(signal)-j)/hz:.2f}s right')
    return signal[i:j+1]
