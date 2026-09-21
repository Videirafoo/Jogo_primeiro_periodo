from array import array
import math
import random

import pygame


class Audio:
    def __init__(self):
        self.enabled = True
        self.cache = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1)
        except pygame.error:
            self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled

    def play(self, name, volume=0.35):
        if not self.enabled or not pygame.mixer.get_init():
            return

        sound = self.cache.get(name)
        if sound is None:
            sound = self._create_sound(name)
            self.cache[name] = sound

        sound.set_volume(volume)
        sound.play()

    def _create_sound(self, name):
        profiles = {
            "intro": (220, 0.38, "tone"),
            "dream_fall": (120, 0.50, "sweep"),
            "rain": (160, 0.45, "noise"),
            "wind": (95, 0.50, "noise"),
            "horse": (90, 0.28, "pulse"),
            "sword": (920, 0.18, "metal"),
            "axe_whoosh": (180, 0.22, "sweep"),
            "axe_hit": (75, 0.22, "pulse"),
            "crow": (620, 0.22, "pulse"),
            "thunder": (58, 0.55, "noise"),
            "lightning": (1100, 0.18, "metal"),
            "gate": (70, 0.35, "pulse"),
            "tech": (520, 0.30, "sweep"),
            "scanner": (760, 0.28, "pulse"),
            "rune": (360, 0.38, "tone"),
            "runes": (360, 0.38, "tone"),
            "portal": (260, 0.48, "sweep"),
            "shield": (680, 0.18, "metal"),
            "forge": (130, 0.38, "noise"),
            "fire": (180, 0.35, "noise"),
            "heal": (440, 0.45, "tone"),
            "shadow": (105, 0.40, "sweep"),
            "wolf": (145, 0.36, "pulse"),
            "chain": (760, 0.18, "metal"),
            "wake": (880, 0.28, "pulse"),
            "choice": (500, 0.13, "tone"),
            "error": (145, 0.18, "pulse"),
            "ending_good": (660, 0.48, "tone"),
            "victory": (660, 0.48, "tone"),
        }

        frequency, duration, kind = profiles.get(
            name,
            (330, 0.20, "tone"),
        )
        samples = self._samples(frequency, duration, kind)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _samples(self, frequency, duration, kind):
        sample_rate = 44100
        count = max(1, int(sample_rate * duration))
        data = array("h")
        rng = random.Random(f"{frequency}-{duration}-{kind}")

        for index in range(count):
            t = index / sample_rate
            envelope = max(0.0, 1.0 - index / count)

            if kind == "noise":
                value = rng.uniform(-1.0, 1.0) * 0.45
                value += math.sin(2 * math.pi * frequency * t) * 0.16
            elif kind == "pulse":
                wave = math.sin(2 * math.pi * frequency * t)
                value = (0.55 if wave >= 0 else -0.55)
            elif kind == "metal":
                value = (
                    math.sin(2 * math.pi * frequency * t) * 0.42
                    + math.sin(2 * math.pi * frequency * 1.83 * t) * 0.25
                )
            elif kind == "sweep":
                swept = frequency * (1.0 + t * 2.4)
                value = math.sin(2 * math.pi * swept * t) * 0.55
            else:
                value = (
                    math.sin(2 * math.pi * frequency * t) * 0.52
                    + math.sin(2 * math.pi * frequency * 0.5 * t) * 0.16
                )

            sample = int(max(-1.0, min(1.0, value)) * envelope * 32767)
            data.append(sample)

        return data
