import Queue
import threading
import time
import pyaudio
import numpy as np
import quietnet
import options
import sys
import psk

FORMAT = pyaudio.paInt16
frame_length = options.frame_length
chunk = options.chunk
search_freq = options.freq
rate = options.rate
sigil = [int(x) for x in options.sigil]
frames_per_buffer = chunk * 10

in_length = 4000
# raw audio frames
in_frames = Queue.Queue(in_length)
# the value of the fft at the frequency we care about
points = Queue.Queue(in_length)
bits = Queue.Queue(in_length / frame_length)

wait_for_sample_timeout = 0.1
wait_for_frames_timeout = 0.1
wait_for_point_timeout = 0.1
wait_for_byte_timeout = 0.1

# yeeeep this is just hard coded
bottom_threshold = 8000

def process_frames():
    while True:
        try:
            frame = in_frames.get(False)
            fft = quietnet.fft(frame)
            point = quietnet.has_freq(fft, search_freq, rate, chunk)
            points.put(point)
        except Queue.Empty:
            time.sleep(wait_for_frames_timeout)

def process_points():
    while True:
        cur_points = []
        while len(cur_points) < frame_length:
            try:
                cur_points.append(points.get(False))
            except Queue.Empty:
                time.sleep(wait_for_point_timeout)

        while True:
            while np.average(cur_points) > bottom_threshold:
                try:
                    cur_points.append(points.get(False))
                    cur_points = cur_points[1:]
                except Queue.Empty:
                    time.sleep(wait_for_point_timeout)
            next_point = None
            while next_point == None:
                try:
                    next_point = points.get(False)
                except Queue.Empty:
                    time.sleep(wait_for_point_timeout)
            if next_point > bottom_threshold:
                bits.put(0)
                bits.put(0)
                cur_points = [cur_points[-1]]
                break
        print("")

        last_bits = []
        while True:
            if len(cur_points) == frame_length:
                bit = int(quietnet.get_bit(cur_points, frame_length) > bottom_threshold)
                cur_points = []
                bits.put(bit)
                last_bits.append(bit)
            # if we've only seen low bits for a while assume the next message might not be on the same bit boundary
            if len(last_bits) > 3:
                if sum(last_bits) == 0:
                    break
                last_bits = last_bits[1:]
            try:
                cur_points.append(points.get(False))
            except Queue.Empty:
                time.sleep(wait_for_point_timeout)

def process_bits():
    while True:
        cur_bits = []
        # while the last two characters are not the sigil
        while len(cur_bits) < 2 or cur_bits[-len(sigil):len(cur_bits)] != sigil:
            try:
                cur_bits.append(bits.get(False))
            except Queue.Empty:
                time.sleep(wait_for_byte_timeout)
        sys.stdout.write(psk.decode(cur_bits[:-len(sigil)]))
        sys.stdout.flush()

# start the queue processing threads
processes = [process_frames, process_points, process_bits]
threads = []

for process in processes:
    thread = threading.Thread(target=process)
    thread.daemon = True
    thread.start()

def callback(in_data, frame_count, time_info, status):
    frames = list(quietnet.chunks(quietnet.unpack(in_data), chunk))
    for frame in frames:
        if not in_frames.full():
            in_frames.put(frame, False)
    return (in_data, pyaudio.paContinue)

def start_analysing_stream():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=options.channels, rate=options.rate,
        input=True, frames_per_buffer=frames_per_buffer, stream_callback=callback)
    stream.start_stream()
    while stream.is_active():
        time.sleep(wait_for_sample_timeout)

sys.stdout.write("Quietnet listening at %sHz" % search_freq)
sys.stdout.flush()
start_analysing_stream()
