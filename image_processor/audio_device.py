from collections.abc import Iterable

import pygame.mixer


class AudioDevice:
    """Preloads samples and plays them through one shared low-latency mixer."""

    def __init__(self, audio_files: Iterable[str]):
        if pygame.mixer.get_init() is None:
            pygame.mixer.init(
                frequency=44100,
                size=-16,
                channels=2,
                buffer=256,
            )
        pygame.mixer.set_num_channels(16)
        self.sounds = {
            audio_file: pygame.mixer.Sound(audio_file) for audio_file in audio_files
        }

    def play_audiofile(self, audio_file: str) -> None:
        self.sounds[audio_file].play()
