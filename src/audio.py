from playsound import playsound

# Alternative sound playback libraries
# import pygame.mixer as pg
# import sounddevice as sd
# import soundfile as sf


class AudioDevice:

    def __init__(self):
        pass

    def play_audiofile(self, audio_file: str):

        playsound(audio_file, block=False)
