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

def has_freq(fft_sample, freq_in_hertz, rate, chunk, offset=3):
    peak = get_peak(freq_in_hertz, rate, chunk)
    top = max(fft_sample[peak-1:peak+2])
    if top < np.average([fft_sample[peak-offset], fft_sample[peak+offset]]):
        return 0
    return fft_sample[peak]

def get_signal(buffer):
    unpacked_buffer = unpack_buffer(list(chunks(buffer, 2)))
    return np.array(unpacked_buffer, dtype=float)

def raw_has_freq(buffer, freq_in_hertz, rate, chunk):
    fft_sample = fft(get_signal(buffer))
    return has_freq(fft_sample, freq_in_hertz, rate, chunk)

def get_freq_over_time(ffts, search_freq, chunk=1024, rate=44100):
    return [has_freq(fft, search_freq, rate, chunk) for fft in ffts]

def get_points(freq_values, threshold=None):
    if threshold == None:
        max = np.max(freq_values)
        threshold = (np.max(freq_values) + np.min(freq_values)) / 2
    points = []
    for point in freq_values:
        if point < threshold:
            points.append(0)
        else:
            points.append(1)

    # TODO is this a hack for framing?
    i = 0
    while i < len(points):
        if points[i] != points[i+1]:
            points = points[i:]
            break
        i += 1
    return points

def get_bits(points, frame_length):
    return [int(round(sum(c) / float(frame_length))) for c in list(chunks(points, frame_length)) if len(c) == frame_length]

def get_bytes(bits, sigil):
    i = 0
    # scan for the first occurance of the sigil
    while i < len(bits) - len(sigil):
        if bits[i:i+len(sigil)] == sigil:
            i += len(sigil)
            break
        i += 1
    return [l for l in list(chunks(bits[i:], 8)) if len(l) == 8]

def decode(bytes):
    string = ""
    for byte in bytes:
        byte = ''.join([str(bit) for bit in byte])
        string += chr(int(byte, base=2))
    return string

def tone(freq=400, datasize=4096, rate=44100):
    amp=8000.0
    sine_list=[]
    for x in range(datasize):
        samp = math.sin(2*math.pi*freq*(x/float(rate)))
        sine_list.append(int(samp*amp/2))
    return sine_list

def envelope(in_data, rate=44100):
    freq = math.pi / len(in_data)
    amp=8000.0
    sine_list=[]
    for x in range(len(in_data)):
        samp = math.sin(freq*x) * in_data[x]
        sine_list.append(int(samp))
    return sine_list

def lenvelope(in_data, rate=44100):
    half = float(len(in_data)) / 2
    freq = math.pi / len(in_data)
    out_data=[]
    for x in range(len(in_data)):
        samp = in_data[x]
        if x < half:
            samp = samp * math.sin(freq*x)
        out_data.append(int(samp))
    return out_data

def renvelope(in_data, rate=44100):
    half = int(float(len(in_data)) / 2)
    freq = math.pi / len(in_data)
    out_data=[]
    for x in range(len(in_data)):
        samp = in_data[x]
        if x > half:
            samp = samp * math.sin(freq*x)
        out_data.append(int(samp))
    return out_data

