import sounddevice as sd
import soundfile as sf
import time
from playsound import playsound
# from pygame import Sound


filename = '/home/mathdudeman/Music/Alvin & the Chipmunks/The Chipmunks Greatest Christmas Hits/01 The Chipmunk Song (Christmas Don\'t Be Late).mp3'
# Extract data and sampling rate from file

playsound(filename, block = False)
time.sleep(3)
playsound(filename, block = False)


# data, fs = sf.read(filename, dtype='float32')  
# sd.play(data, fs)

# time.sleep(3)

# data, fs = sf.read(filename, dtype='float32')  
# sd.play(data, fs)
# status = sd.wait()  # Wait until file is done playing