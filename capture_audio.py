import pyaudio

FORMAT = pyaudio.paInt16
CHANNELS = 1

def capture_buffers(num_buffers, chunk, rate, skip=None):
    if skip == None:
        skip = rate / 2

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=rate, input=True, frames_per_buffer=chunk)
    
    # ignore some data at the beginning as it is usually weird
    if skip > 0:
        data = stream.read(skip)
    
    buffers = [stream.read(chunk) for i in range(0, num_buffers)]  
    
    # close the audio stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    return buffers

def capture_seconds(num_seconds, chunksize, rate, width):
    num_buffers = int(float(num_seconds * rate) / chunksize)
    return capture_buffers(num_buffers, chunksize, rate, width)

