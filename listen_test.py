import pyaudio
import sys
import time
import Queue
import threading
import quietnet

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 44

FRAME_LENGTH = 8
search_freq = 19043

samples_to_process = 4000
sigil = ([0] * 3) + ([1] * 10) + ([0] * 3)

def process_samples(samples, chunk, rate, frame_length):
    buffers = [quietnet.unpack(b) for b in samples]
    ffts = [quietnet.fft(b) for b in buffers]
    freq_values = quietnet.get_freq_over_time(ffts, search_freq, chunk, rate)
    points = quietnet.get_points(freq_values)
    bits = quietnet.get_bits(points, frame_length)
    bytes = quietnet.get_bytes(bits, sigil)
    return quietnet.decode(bytes)

def process():
    samples = []
    while True:
        try:
            samples.append(q.get(False))
        except Queue.Empty:
            break
    decoded = process_samples(samples, CHUNK, RATE, FRAME_LENGTH)
    sys.stdout.write(decoded)
    sys.stdout.flush()

q = Queue.Queue(samples_to_process)
commandQueue = Queue.Queue(50)

def callback(in_data, frame_count, time_info, status):
    if not q.full():
        q.put(in_data, False)
    return (in_data, pyaudio.paContinue)

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)
stream.start_stream()

print "Quietnet listen test started, listening at %sHz" % search_freq

while True:
    time.sleep(1.5)
    t = threading.Thread(target=process)
    t.daemon = True
    t.start()

stream.stop_stream()
stream.close()
p.terminate()

