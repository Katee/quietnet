import pyaudio
import time
import sys
import quietnet

class colors:
    RED = '\033[91m'
    ENDC = '\033[0m'

WIDTH = 2
CHANNELS = 1
RATE = 44100
CHUNK = 1024

FREQ = 17000

p = pyaudio.PyAudio()

buffers = []

def callback(in_data, frame_count, time_info, status):
    if quietnet.raw_has_freq(in_data, FREQ, RATE, CHUNK):
        sys.stdout.write(colors.RED + "O" + colors.ENDC)
    else:
        sys.stdout.write('.')
    sys.stdout.flush()
    return (in_data, pyaudio.paContinue)

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=False,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(.1)

stream.stop_stream()
stream.close()
p.terminate()
