
import numpy as np
import pyaudio
import sys
from contextlib import contextmanager
from numpy import arange, array, pi, sin, sqrt
from threading import Thread
from time import sleep, time

tau = 2.0 * pi

volume = 0.5     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer

def say(*items):
    sys.stdout.write(' '.join(str(item) for item in items) + '\n')

def launch(function, *args):
    thread = Thread(target=function, args=args)
    thread.start()
    return thread

def find_device(pa, name):
    names = [pa.get_device_info_by_index(i)['name']
             for i in range(pa.get_device_count())]
    try:
        index = names.index(name)
    except ValueError as e:
        raise ValueError(
            'cannot find device {!r} among these devices:\n{}'
            .format(name, '\n'.join(names))
        ) from None
    return index

def play_tone(pa, output_index, frequency, seconds):
    # for paFloat32 sample values must be in range [-1.0, 1.0]
    t = arange(fs * seconds) / fs
    waveform = volume * sin(frequency * t * tau)
    samples = waveform.astype(np.float32).tostring()

    stream = pa.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=fs,
        output=True,
        output_device_index=output_index,
    )

    stream.write(samples)

    stream.stop_stream()
    stream.close()

def record(pa, input_index, seconds):
    stream = pa.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=fs + 11,
        input=True,
        input_device_index=input_index,
    )

    say('Recording for {} seconds...'.format(seconds))
    t0 = time()
    data = stream.read(int(fs * seconds))
    dt = time() - t0
    say('Recorded for {} seconds'.format(dt))
    stream.close()

    result = np.fromstring(data, np.float32)
    say('Recorded {:,} samples'.format(len(result)))
    return result

    # t = np.linspace(0, seconds, fs * seconds, endpoint=False)
    # return t

def scan(frequencies):
    pa = pyaudio.PyAudio()
    try:
        input_index = find_device(pa, 'Scarlett Solo USB: Audio (hw:1,0)')
        output_index = find_device(pa, 'HDA Intel PCH: ALC293 Analog (hw:0,0)')
        #output_index = find_device(pa, 'HDA Intel PCH: HDMI 0 (hw:0,3)')
        response = []
        waveforms = []

        for frequency in frequencies:
            thread = launch(play_tone, pa, output_index, frequency, 2.0)
            #play_tone(pa, output_index, frequency, 1.0)
            waveform = record(pa, input_index, 1.0)
            say(len(waveform))
            thread.join()
            rms = sqrt((waveform * waveform).mean())
            say(frequency, rms)
            response.append(rms)
            waveforms.append(waveform)
        return array(response), waveforms
    finally:
        pa.terminate()


def sine_cycle(frequency):
    samples_per_period = fs // frequency
    theta = np.linspace(0, tau, samples_per_period, endpoint=False)
    return volume * sin(theta)

def play_repeating(pa, output_index, waveform, seconds):
    #print(waveform[0:5], waveform[-5:])
    assert abs(waveform[-1] - waveform[0]) < 0.05, (waveform[0], waveform[-1])
    repeats = int(fs * seconds) // len(waveform)

    data = waveform.astype(np.float32).tostring() * repeats

    stream = pa.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=fs,
        output=True,
        output_device_index=output_index,
    )

    say('Playing for {} seconds...'.format(seconds))
    t0 = time()
    stream.write(data)
    dt = time() - t0
    say('Played for {} seconds'.format(dt))

    stream.stop_stream()
    stream.close()
    say('Played {:,} samples'.format(len(waveform) * repeats))

@contextmanager
def pyaudio_instance():
    pa = pyaudio.PyAudio()
    try:
        yield pa
    finally:
        pa.terminate()

def yeah():
    seconds = 10.0
    with pyaudio_instance() as pa:
        input_index = find_device(pa, 'Scarlett Solo USB: Audio (hw:1,0)')
        output_index = find_device(pa, 'HDA Intel PCH: ALC293 Analog (hw:0,0)')
        waveform = sine_cycle(440.0)
        #waveform = sine_cycle(20.0)
        thread = launch(play_repeating, pa, output_index, waveform, seconds)
        result = record(pa, input_index, seconds)
        thread.join()
    return waveform, result
