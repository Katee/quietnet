import numpy as np
import struct
import math

# let us use input in python 2.x.
try: input = raw_input
except NameError: pass

# split something into chunks
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

def weighted_values_around_peak(in_data, peak_index, offset):
    period = math.pi / (offset * 2)

    out_data = []
    for i in range(len(in_data)):
        if i >= peak_index - offset and i <= peak_index + offset:
            out_data.append(in_data[i] * np.abs(math.sin((period * (i - peak_index + offset)) + (math.pi / 2.0))))
        else:
            out_data.append(0)
    return out_data

def has_freq(fft_sample, freq_in_hertz, rate, chunk, offset=3):
    peak_index = get_peak(freq_in_hertz, rate, chunk)
    top = max(fft_sample[peak_index-1:peak_index+2])

    avg_around_peak = np.average(weighted_values_around_peak(fft_sample, peak_index, offset))

    if top > avg_around_peak:
        return fft_sample[peak_index]
    else:
        return 0

def get_signal(buffer):
    unpacked_buffer = unpack_buffer(list(chunks(buffer, 2)))
    return np.array(unpacked_buffer, dtype=float)

def raw_has_freq(buffer, freq_in_hertz, rate, chunk):
    fft_sample = fft(get_signal(buffer))
    return has_freq(fft_sample, freq_in_hertz, rate, chunk)

def get_freq_over_time(ffts, search_freq, chunk=1024, rate=44100):
    return [has_freq(fft, search_freq, rate, chunk) for fft in ffts]

def get_points(freq_samples, frame_length, threshold=None, last_point=0):
    if threshold == None:
        threshold = np.median(freq_samples)
    points = []
    for i in range(len(freq_samples)):
        freq_value = freq_samples[i]
        point = 0
        if freq_value > threshold:
            # ignore big changes in frequency when they aren't near the frame transition
            if last_point == 1 or (i % frame_length) <= 2:
                point = 1
            else:
                point = 0
        points.append(point)
        last_point = point
    return points

def get_bits(points, frame_length):
    return [int(round(sum(c) / float(frame_length))) for c in list(chunks(points, frame_length)) if len(c) == frame_length]

def get_bit(points, frame_length):
    return int(round(sum(points) / float(frame_length)))

def get_bytes(bits, sigil):
    i = 0
    # scan for the first occurance of the sigil
    while i < len(bits) - len(sigil):
        if bits[i:i+len(sigil)] == sigil:
            i += len(sigil)
            break
        i += 1
    return [l for l in list(chunks(bits[i:], 8)) if len(l) == 8]

def decode_byte(l):
    byte_string = ''.join([str(bit) for bit in l])
    return chr(int(byte_string, base=2))

def decode(bytes):
    string = ""
    for byte in bytes:
        byte = ''.join([str(bit) for bit in byte])
        string += chr(int(byte, base=2))
    return string

def tone(freq=400, datasize=4096, rate=44100, amp=12000.0, offset=0):
    sine_list=[]
    for x in range(datasize):
        samp = math.sin(2*math.pi*freq*((x + offset)/float(rate)))
        sine_list.append(int(samp*amp))
    return sine_list

def envelope(in_data, left=True, right=True, rate=44100):
    half = float(len(in_data)) / 2
    freq = math.pi / (len(in_data) / 2)
    out_data = []

    for x in range(len(in_data)):
        samp = in_data[x]
        if (x < half and left) or (right and x >= half):
            samp = samp * (1 + math.sin(freq*x - (math.pi / 2))) / 2
        out_data.append(int(samp))

    return out_data
