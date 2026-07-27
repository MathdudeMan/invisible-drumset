import pygame.mixer
import pytest

from image_processor.audio_device import AudioDevice


class FakeSound:
    def __init__(self, audio_file):
        self.audio_file = audio_file
        self.play_count = 0

    def play(self):
        self.play_count += 1


@pytest.fixture()
def fake_mixer(monkeypatch):
    calls = {"init": [], "channels": [], "sounds": []}
    sounds = {}

    monkeypatch.setattr(pygame.mixer, "get_init", lambda: None)
    monkeypatch.setattr(
        pygame.mixer, "init", lambda **kwargs: calls["init"].append(kwargs)
    )
    monkeypatch.setattr(
        pygame.mixer,
        "set_num_channels",
        lambda channels: calls["channels"].append(channels),
    )

    def create_sound(audio_file):
        sound = FakeSound(audio_file)
        sounds[audio_file] = sound
        calls["sounds"].append(audio_file)
        return sound

    monkeypatch.setattr(pygame.mixer, "Sound", create_sound)
    return calls, sounds


def test_preloads_samples_and_reuses_them_for_playback(fake_mixer):
    calls, sounds = fake_mixer

    device = AudioDevice(["kick.wav", "snare.wav"])
    device.play_audiofile("kick.wav")

    assert calls["init"] == [
        {"frequency": 44100, "size": -16, "channels": 2, "buffer": 256}
    ]
    assert calls["channels"] == [16]
    assert calls["sounds"] == ["kick.wav", "snare.wav"]
    assert sounds["kick.wav"].play_count == 1
    assert sounds["snare.wav"].play_count == 0


def test_reuses_an_initialized_mixer(monkeypatch):
    init_calls = []
    monkeypatch.setattr(pygame.mixer, "get_init", lambda: (44100, -16, 2))
    monkeypatch.setattr(
        pygame.mixer, "init", lambda **kwargs: init_calls.append(kwargs)
    )
    monkeypatch.setattr(pygame.mixer, "set_num_channels", lambda channels: None)

    AudioDevice([])

    assert init_calls == []
