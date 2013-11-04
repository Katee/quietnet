import sys
import pyaudio
from datetime import datetime, timedelta
import quietnet
import options

FORMAT = pyaudio.paInt16
CHANNELS = options.channels
RATE = options.rate
FREQ = options.freq
FREQ_OFF = 0
SIGIL = options.sigil
FRAME_LENGTH = options.frame_length
DATASIZE = options.datasize

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)

buffers = {
    "000": quietnet.tone(FREQ_OFF, DATASIZE),
    "100": quietnet.lenvelope(quietnet.tone(FREQ_OFF, DATASIZE)),
    "001": quietnet.renvelope(quietnet.tone(FREQ_OFF, DATASIZE)),
    "101": quietnet.envelope(quietnet.tone(FREQ_OFF, DATASIZE)),
    "010": quietnet.envelope(quietnet.tone(FREQ, DATASIZE)),
    "011": quietnet.lenvelope(quietnet.tone(FREQ, DATASIZE)),
    "110": quietnet.renvelope(quietnet.tone(FREQ, DATASIZE)),
    "111": quietnet.tone(FREQ, DATASIZE)
}

def make_buffer_from_bit_pattern(pattern):
    last_bit = pattern[-1]
    output_buffer = []
    for i in range(len(pattern)):
        bit = pattern[i]
        if i < len(pattern) - 1:
            next_bit = pattern[i+1]
        else:
            next_bit = pattern[0]
        output_buffer = output_buffer + buffers[last_bit + bit + next_bit]
        last_bit = bit
    return quietnet.pack_buffer(output_buffer)

def repeat_buffer(buffer):
    while True:
        for sample in buffer:
            stream.write(sample)

def play_tone():
    buffer = quietnet.pack_buffer(quietnet.tone(FREQ, DATASIZE))
    repeat_buffer(buffer)

def fill(letter):
    n = ord(letter)
    b = str(bin(n))[2:]
    return b.zfill(8)

def make_bit_pattern_from_string(string, prefix):
    pattern = prefix
    for l in string:
        pattern += fill(l)
    return pattern

if len(sys.argv) > 1:
    pattern = sys.argv[1]
else:
    print "enter a string to repeat:",
    pattern = make_bit_pattern_from_string(raw_input(), SIGIL)

print "repeating %s" % pattern
print "Use ctrl-c to exit"
buffer = make_buffer_from_bit_pattern(pattern)

# keep playing the buffer until the program is terminated
repeat_buffer(buffer)

# never actually reached, right now you exit with ctrl-c
stream.stop_stream()
stream.close()
p.terminate()
