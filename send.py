import pyaudio
import quietnet
import options
import psk

FORMAT = pyaudio.paInt16
CHANNELS = options.channels
RATE = options.rate
FREQ = options.freq
FREQ_OFF = 0
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

def play_buffer(buffer):
    for sample in buffer:
        stream.write(sample)

print "Use ctrl-c to exit"
while True:
    print ">",
    pattern = psk.encode(raw_input())
    buffer = make_buffer_from_bit_pattern(pattern)
    play_buffer(buffer)

# never actually reached, right now you exit with ctrl-c
stream.stop_stream()
stream.close()
p.terminate()
