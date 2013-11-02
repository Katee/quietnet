import pyaudio
import quietnet

WIDTH = 2
CHANNELS = 1
RATE = 44100

FREQ_OFF = 0
FREQ = 17000
FREQ2 = 17500

DATASIZE = 4096

p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                output=True)

freqs = [FREQ_OFF, FREQ, FREQ2];
samples = {i - 1 : quietnet.pack_buffer(quietnet.tone(freqs[i], DATASIZE)) for i in range(len(freqs))}

while True:
#    for frame in samples[0]:
#        stream.write(frame)
    input = raw_input()
    for l in input:
        i = bin(ord(l))
        for bit in str(i)[2:]:
            sample = samples[int(bit)]
            for frame in sample:
                stream.write(frame)
            # have quiet between bits
            sample = samples[-1]
            for frame in sample:
                stream.write(frame)

stream.stop_stream()
stream.close()
p.terminate()

p = pyaudio.PyAudio()
