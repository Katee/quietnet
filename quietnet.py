import numpy as np
import struct
import math

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def unpack(buffer):
    return unpack_buffer(list(chunks(buffer, 2)))

def unpack_buffer(buffer):
    return [struct.unpack('h', frame)[0] for frame in buffer]

def pack_buffer(buffer):
    return [struct.pack('h', frame) for frame in buffer]

def fft(signal):
    return np.abs(np.fft.rfft(signal))

def get_peak(hertz, rate, chunk):
    return int(round((float(hertz) / rate) * chunk))

def has_freq(fft_sample, freq_in_hertz, rate, chunk):
    offset = 2
    peak = get_peak(freq_in_hertz, rate, chunk)
    mid = fft_sample[peak]
    threshold = 10000 # this should be based on the sample size
    return mid > threshold and mid > fft_sample[peak - offset] and mid > fft_sample[peak + offset]

def get_signal(buffer):
    unpacked_buffer = unpack_buffer(list(chunks(buffer, 2)))
    return np.array(unpacked_buffer, dtype=float)

def raw_has_freq(buffer, freq_in_hertz, rate, chunk):
    fft_sample = fft(get_signal(buffer))
    return has_freq(fft_sample, freq_in_hertz, rate, chunk)

def tone(freq=400, datasize=4096, rate=44100):
    amp=8000.0
    sine_list=[]
    for x in range(datasize):
        samp = math.sin(2*math.pi*freq*(x/float(rate)))
        sine_list.append(int(samp*amp/2))
    return sine_list
