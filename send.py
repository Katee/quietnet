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

def make_buffer_from_bit_pattern(pattern, on_freq, off_freq):
    """ Takes a pattern and returns an audio buffer that encodes that pattern """
    # the key's middle value is the bit's value and the left and right bits are the bits before and after
    # the buffers are enveloped to cleanly blend into each other

    last_bit = pattern[-1]
    output_buffer = []
    offset = 0

    for i in range(len(pattern)):
        bit = pattern[i]
        if i < len(pattern) - 1:
            next_bit = pattern[i+1]
        else:
            next_bit = pattern[0]

        freq = on_freq if bit == '1' else off_freq
        tone = quietnet.tone(freq, DATASIZE, offset=offset)
        output_buffer += quietnet.envelope(tone, left=last_bit=='0', right=next_bit=='0')
        offset += DATASIZE
        last_bit = bit

    return quietnet.pack_buffer(output_buffer)

def play_buffer(buffer):
    output = ''.join(buffer)
    stream.write(output)

if __name__ == "__main__":
    print("Welcome to quietnet. Use ctrl-c to exit")

    try:
        # get user input and play message
        while True:
            message = input("> ")
            try:
              pattern = psk.encode(message)
              buffer = make_buffer_from_bit_pattern(pattern, FREQ, FREQ_OFF)
              play_buffer(buffer)
            except KeyError:
              print("Messages may only contain printable ASCII characters.")
    except KeyboardInterrupt:
        # clean up our streams and exit
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("exited cleanly")
