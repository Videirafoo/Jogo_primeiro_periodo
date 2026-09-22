from array import array
import math
from pathlib import Path
import random

import pygame



ASSET_ROOT = Path(__file__).with_name("assets") / "audio" / "cc0"
KENNEY_AUDIO = (
    Path(__file__).with_name("assets")
    / "kenney"
    / "audio"
)
VALDRAK_AUDIO = (
    Path(__file__).with_name("assets")
    / "audio"
    / "valdrak"
)
VOICE_ROOT = (
    Path(__file__).with_name("assets")
    / "audio"
    / "voices"
)

VALDRAK_SFX = {
    "footstep": [
        "footstep_grass_1.wav",
        "footstep_grass_2.wav",
        "footstep_grass_3.wav",
        "footstep_grass_4.wav",
    ],
    "sword": [
        "sword_slash_1.wav",
        "sword_slash_2.wav",
        "sword_slash_3.wav",
    ],
    "blade_hit": [
        "blade_hit_1.wav",
        "blade_hit_2.wav",
    ],
    "axe_whoosh": [
        "axe_whoosh_1.wav",
        "axe_whoosh_2.wav",
        "axe_whoosh_3.wav",
    ],
    "axe_hit": [
        "axe_hit_1.wav",
        "axe_hit_2.wav",
        "axe_hit_3.wav",
    ],
    "shield": [
        "shield_hit_1.wav",
        "shield_hit_2.wav",
    ],
    "rune": ["rune_pulse_1.wav"],
    "runes": ["rune_pulse_1.wav"],
    "boss_defeat": ["boss_defeat_1.wav"],
}

KENNEY_SFX = {
    "footstep": "footstep07.ogg",
    "sword": "knifeSlice.ogg",
    "shield": "metalLatch.ogg",
    "pickup": "handleCoins.ogg",
    "gate": "doorOpen_1.ogg",
    "choice": "metalClick.ogg",
    "boss_defeat": "chop.ogg",
    "inventory": "creak2.ogg",
}

EXTERNAL_SFX = {
    "sword": "steel1.wav",
    "shield": "metal1.wav",
    "axe_hit": "metal1.wav",
    "gate": "switch1.wav",
    "thunder": "cracker1.wav",
    "lightning": "cracker1.wav",
    "choice": "switch1.wav",
}

AMBIENCE_BY_EVENT = {
    "rain": "rain",
    "dream_fall": "wind",
    "wind": "wind",
    "horse": "wind",
    "sword": "wind",
    "axe_whoosh": "wind",
    "axe_hit": "wind",
    "crow": "forest",
    "thunder": "rain",
    "lightning": "rain",
    "gate": "wind",
    "tech": "techhum",
    "scanner": "techhum",
    "rune": "techhum",
    "runes": "techhum",
    "portal": "portalhum",
    "forge": "fire",
    "fire": "fire",
    "heal": "wind",
    "shadow": "forest",
    "wolf": "wind",
    "chain": "wind",
    "wake": None,
    "ending_good": "wind",
}


class Audio:
    def __init__(self):
        self.enabled = True
        self.cache = {}
        self.ambience_cache = {}
        self.variant_index = {}
        self.current_ambience = None
        self.master_volume = 0.72
        self.ambience_mix = 0.72

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=1,
                    buffer=512,
                )
            pygame.mixer.set_num_channels(8)
            pygame.mixer.set_reserved(1)
            self.ambience_channel = pygame.mixer.Channel(0)
            self.event_channel = pygame.mixer.Channel(1)
        except pygame.error:
            self.enabled = False
            self.ambience_channel = None
            self.event_channel = None

    def toggle(self):
        self.enabled = not self.enabled

        if not self.enabled:
            if self.ambience_channel:
                self.ambience_channel.stop()
            pygame.mixer.stop()
        elif self.current_ambience:
            name = self.current_ambience
            self.current_ambience = None
            self.set_ambience(name, direct=True)

        return self.enabled

    def adjust_volume(self, delta):
        self.master_volume = max(
            0.15,
            min(1.0, self.master_volume + delta),
        )

        if self.ambience_channel and self.current_ambience:
            base = {
                "rain": 0.34,
                "wind": 0.23,
                "forest": 0.24,
                "fire": 0.28,
                "techhum": 0.18,
                "portalhum": 0.22,
                "music_explore": 0.24,
                "music_danger": 0.29,
                "music_boss": 0.34,
                "music_interior": 0.22,
            }.get(self.current_ambience, 0.20)
            if self.current_ambience.startswith("music_boss_"):
                base = 0.34
            elif self.current_ambience.startswith("music_danger_"):
                base = 0.29
            elif self.current_ambience.startswith("music_region_"):
                base = 0.25
            elif self.current_ambience.startswith("music_interior_"):
                base = 0.22
            self.ambience_channel.set_volume(
                base * self.ambience_mix * self.master_volume
            )

        return self.master_volume

    def set_ambience(self, event_name, direct=False):
        ambience = event_name if direct else AMBIENCE_BY_EVENT.get(event_name)

        if ambience == self.current_ambience:
            return

        self.current_ambience = ambience

        if not self.enabled or not self.ambience_channel:
            return

        self.ambience_channel.fadeout(180)

        if not ambience:
            return

        sound = self.ambience_cache.get(ambience)
        if sound is None:
            sound = self._create_ambience(ambience)
            self.ambience_cache[ambience] = sound

        volume = {
            "rain": 0.34,
            "wind": 0.23,
            "forest": 0.24,
            "fire": 0.28,
            "techhum": 0.18,
            "portalhum": 0.22,
            "music_explore": 0.24,
            "music_danger": 0.29,
            "music_boss": 0.34,
            "music_interior": 0.22,
        }.get(ambience, 0.20)

        if ambience.startswith("music_boss_"):
            volume = 0.34
        elif ambience.startswith("music_danger_"):
            volume = 0.29
        elif ambience.startswith("music_region_"):
            volume = 0.25
        elif ambience.startswith("music_interior_"):
            volume = 0.22
        self.ambience_channel.set_volume(
            volume * self.ambience_mix * self.master_volume
        )
        self.ambience_channel.play(sound, loops=-1, fade_ms=220)

    def play(self, name, volume=0.52):
        if not self.enabled or not pygame.mixer.get_init():
            return

        variants = VALDRAK_SFX.get(name)
        cache_key = name
        variant = 0
        if variants:
            variant = self.variant_index.get(name, 0) % len(variants)
            self.variant_index[name] = variant + 1
            cache_key = f"{name}:{variant}"

        sound = self.cache.get(cache_key)
        if sound is None:
            sound = self._create_sound(name, variant=variant)
            self.cache[cache_key] = sound

        channel = pygame.mixer.find_channel(True)
        if channel is None:
            channel = self.event_channel

        if channel:
            channel.set_volume(volume * self.master_volume)
            channel.play(sound)

    def stop(self):
        if pygame.mixer.get_init():
            pygame.mixer.stop()
        self.current_ambience = None

    def _create_sound(self, name, variant=0):
        variants = VALDRAK_SFX.get(name)
        if variants:
            filename = variants[variant % len(variants)]
            path = VALDRAK_AUDIO / filename
            if path.exists():
                try:
                    return pygame.mixer.Sound(str(path))
                except pygame.error:
                    pass

        kenney = KENNEY_SFX.get(name)
        if kenney:
            path = KENNEY_AUDIO / kenney
            if path.exists():
                try:
                    return pygame.mixer.Sound(
                        str(path)
                    )
                except pygame.error:
                    pass

        external = EXTERNAL_SFX.get(name)
        if external:
            path = ASSET_ROOT / external
            if path.exists():
                try:
                    return pygame.mixer.Sound(str(path))
                except pygame.error:
                    pass

        if name.startswith("voice_"):
            voice_path = VOICE_ROOT / f"{name}.wav"
            if voice_path.exists():
                try:
                    return pygame.mixer.Sound(
                        str(voice_path)
                    )
                except pygame.error:
                    pass

        profiles = {
            "intro": (220, 0.45, "tone"),
            "dream_fall": (120, 0.70, "sweep"),
            "rain": (180, 0.22, "rain_hit"),
            "wind": (95, 0.42, "whoosh"),
            "horse": (88, 0.62, "horse"),
            "sword": (1180, 0.24, "metal"),
            "axe_whoosh": (150, 0.34, "whoosh"),
            "axe_hit": (62, 0.34, "impact"),
            "crow": (730, 0.42, "crow"),
            "thunder": (48, 1.15, "thunder"),
            "lightning": (1450, 0.24, "metal"),
            "gate": (54, 0.72, "impact"),
            "tech": (520, 0.40, "sweep"),
            "scanner": (840, 0.34, "scanner"),
            "rune": (360, 0.55, "tone"),
            "runes": (360, 0.55, "tone"),
            "portal": (240, 0.78, "portal"),
            "shield": (720, 0.30, "metal"),
            "forge": (135, 0.48, "impact"),
            "fire": (190, 0.34, "crackle"),
            "heal": (440, 0.68, "tone"),
            "shadow": (105, 0.58, "sweep"),
            "wolf": (135, 0.62, "wolf"),
            "chain": (840, 0.30, "metal"),
            "wake": (980, 0.38, "pulse"),
            "choice": (530, 0.18, "tone"),
            "error": (145, 0.22, "pulse"),
            "ending_good": (660, 0.72, "tone"),
            "victory": (760, 0.64, "victory"),
            "voice_low": (132, 0.42, "voice"),
            "voice_mystic": (186, 0.52, "voice"),
            "voice_warrior": (108, 0.44, "voice"),
            "secret": (610, 0.48, "scanner"),
            "rare_event": (248, 0.62, "sweep"),
            "contract": (430, 0.32, "tone"),
            "quest_complete": (820, 0.72, "victory"),
            "footstep_grass": (115, 0.11, "footstep_soft"),
            "footstep_stone": (210, 0.10, "footstep_hard"),
            "footstep_wood": (165, 0.12, "footstep_wood"),
            "footstep_snow": (92, 0.13, "footstep_snow"),
            "footstep_water": (260, 0.14, "rain_hit"),
            "village": (350, 0.32, "village"),
            "village_night": (220, 0.34, "village_night"),
            "tavern": (180, 0.38, "tavern"),
            "blacksmith": (96, 0.34, "blacksmith"),
            "door_wood": (72, 0.28, "door_wood"),
            "creature_raven": (720, 0.35, "crow"),
            "creature_wolf": (128, 0.50, "wolf"),
        }

        frequency, duration, kind = profiles.get(
            name,
            (330, 0.24, "tone"),
        )
        data = self._event_samples(frequency, duration, kind)
        return pygame.mixer.Sound(buffer=data.tobytes())

    def _create_ambience(self, name):
        sample_rate = 44100
        duration = (
            6.0
            if name.startswith("music_")
            else 3.0
        )
        count = int(sample_rate * duration)
        data = array("h")
        rng = random.Random(f"ambience-{name}")

        music_kind = None
        music_region = 1
        for prefix, kind in (
            ("music_region_", "region"),
            ("music_danger_", "danger"),
            ("music_boss_", "boss"),
            ("music_interior_", "interior"),
        ):
            if name.startswith(prefix):
                music_kind = kind
                try:
                    music_region = max(
                        1,
                        min(
                            7,
                            int(name[len(prefix):]),
                        ),
                    )
                except ValueError:
                    music_region = 1
                break

        rain_signal = None
        if name == "rain":
            rain_signal = [0.0] * count
            for _ in range(85):
                start = rng.randrange(0, count - 700)
                strength = rng.uniform(0.35, 0.9)
                tone = 1250 + strength * 900

                for delta in range(520):
                    pos = start + delta
                    t_drop = delta / sample_rate
                    rain_signal[pos] += (
                        math.exp(-delta / 110)
                        * math.sin(2 * math.pi * tone * t_drop)
                        * 0.20
                        * strength
                    )

        for index in range(count):
            t = index / sample_rate
            value = 0.0

            if name == "rain":
                value = rng.uniform(-1, 1) * 0.16
                value += rain_signal[index]
            elif name == "wind":
                slow = math.sin(2 * math.pi * 0.22 * t)
                value = rng.uniform(-1, 1) * (0.06 + 0.05 * (slow + 1))
                value += math.sin(2 * math.pi * 82 * t) * 0.035
            elif name == "forest":
                value = rng.uniform(-1, 1) * 0.05
                value += math.sin(2 * math.pi * 58 * t) * 0.035
                value += math.sin(2 * math.pi * 117 * t) * 0.018
            elif name == "fire":
                value = rng.uniform(-1, 1) * 0.07
                if rng.random() < 0.0026:
                    value += rng.uniform(-0.7, 0.7)
                value += math.sin(2 * math.pi * 72 * t) * 0.025
            elif name == "techhum":
                value = (
                    math.sin(2 * math.pi * 92 * t) * 0.055
                    + math.sin(2 * math.pi * 184 * t) * 0.025
                    + math.sin(2 * math.pi * 0.7 * t) * 0.018
                )
            elif name == "portalhum":
                mod = 1 + 0.18 * math.sin(2 * math.pi * 0.3 * t)
                value = (
                    math.sin(2 * math.pi * 68 * mod * t) * 0.065
                    + math.sin(2 * math.pi * 136 * t) * 0.025
                )
            elif music_kind:
                roots = (
                    55.0,
                    58.3,
                    65.4,
                    49.0,
                    73.4,
                    41.2,
                    46.2,
                )
                root_note = roots[music_region - 1]
                if music_kind == "boss":
                    beat = 3.6 + music_region * 0.11
                    gain = 0.078
                elif music_kind == "danger":
                    beat = 2.0 + music_region * 0.07
                    gain = 0.056
                elif music_kind == "interior":
                    beat = 0.48 + music_region * 0.03
                    gain = 0.032
                else:
                    beat = 0.72 + music_region * 0.04
                    gain = 0.039

                mode = (
                    1.5
                    if music_region in {1, 4, 7}
                    else 1.333
                )
                chord = (
                    math.sin(
                        2 * math.pi * root_note * t
                    )
                    + 0.50
                    * math.sin(
                        2
                        * math.pi
                        * root_note
                        * mode
                        * t
                    )
                    + 0.30
                    * math.sin(
                        2
                        * math.pi
                        * root_note
                        * 2.0
                        * t
                    )
                )
                pulse = max(
                    0.0,
                    math.sin(
                        2 * math.pi * beat * t
                    ),
                )
                drum = 0.0
                if music_kind in {"danger", "boss"}:
                    drum = (
                        math.sin(
                            2
                            * math.pi
                            * (39 + music_region)
                            * t
                        )
                        * (pulse ** 8)
                        * 0.38
                    )
                texture = 0.0
                if music_region in {4, 7}:
                    texture = (
                        math.sin(
                            2
                            * math.pi
                            * root_note
                            * 2.5
                            * t
                        )
                        * 0.012
                    )
                elif music_region == 6:
                    texture = (
                        rng.uniform(-1, 1)
                        * 0.012
                    )

                value = (
                    chord
                    * gain
                    * (0.52 + pulse * 0.48)
                    + drum * gain
                    + texture
                )

            elif name in {
                "music_explore",
                "music_danger",
                "music_boss",
                "music_interior",
            }:
                config = {
                    "music_explore": (55, 0.9, 0.035),
                    "music_danger": (65, 2.2, 0.055),
                    "music_boss": (46, 3.8, 0.075),
                    "music_interior": (73, 0.55, 0.030),
                }[name]
                root_note, beat, gain = config
                chord = (
                    math.sin(2 * math.pi * root_note * t)
                    + 0.55 * math.sin(2 * math.pi * root_note * 1.5 * t)
                    + 0.32 * math.sin(2 * math.pi * root_note * 2.0 * t)
                )
                pulse = max(
                    0.0,
                    math.sin(2 * math.pi * beat * t),
                )
                drum = 0.0
                if name in {"music_danger", "music_boss"}:
                    drum = (
                        math.sin(2 * math.pi * 42 * t)
                        * (pulse ** 8)
                        * 0.35
                    )
                value = chord * gain * (0.55 + pulse * 0.45) + drum * gain

            data.append(self._to_sample(value))

        return pygame.mixer.Sound(buffer=data.tobytes())

    def _event_samples(self, frequency, duration, kind):
        sample_rate = 44100
        count = max(1, int(sample_rate * duration))
        data = array("h")
        rng = random.Random(f"{frequency}-{duration}-{kind}")

        for index in range(count):
            t = index / sample_rate
            progress = index / count
            envelope = max(0.0, 1.0 - progress)
            value = 0.0

            if kind == "footstep_soft":
                value = (
                    rng.uniform(-1, 1)
                    * 0.18
                    * math.exp(-t * 24)
                )
                value += (
                    math.sin(
                        2 * math.pi * frequency * t
                    )
                    * 0.08
                    * math.exp(-t * 18)
                )

            elif kind == "footstep_hard":
                value = (
                    math.sin(
                        2 * math.pi * frequency * t
                    )
                    * 0.22
                    * math.exp(-t * 28)
                )
                value += (
                    rng.uniform(-1, 1)
                    * 0.08
                    * math.exp(-t * 30)
                )

            elif kind == "footstep_wood":
                value = (
                    math.sin(
                        2 * math.pi * frequency * t
                    )
                    * 0.16
                    * math.exp(-t * 18)
                )
                value += (
                    math.sin(
                        2 * math.pi * frequency * 2.2 * t
                    )
                    * 0.07
                    * math.exp(-t * 20)
                )

            elif kind == "footstep_snow":
                value = (
                    rng.uniform(-1, 1)
                    * 0.14
                    * math.exp(-t * 13)
                )

            elif kind in {
                "village",
                "village_night",
                "tavern",
                "blacksmith",
                "door_wood",
            }:
                base = (
                    math.sin(
                        2 * math.pi * frequency * t
                    )
                    * 0.08
                )
                noise = rng.uniform(-1, 1) * 0.04
                if kind == "blacksmith":
                    base += (
                        math.sin(
                            2 * math.pi * 880 * t
                        )
                        * 0.13
                        * math.exp(
                            -((t % 0.18) * 18)
                        )
                    )
                elif kind == "tavern":
                    base += (
                        math.sin(
                            2 * math.pi * 260 * t
                        )
                        * 0.04
                    )
                elif kind == "door_wood":
                    base *= math.exp(-t * 9)
                    noise *= math.exp(-t * 11)
                value = base + noise

            elif kind == "voice":
                formant = (
                    math.sin(
                        2 * math.pi * frequency * t
                    )
                    + 0.42
                    * math.sin(
                        2
                        * math.pi
                        * frequency
                        * 2.02
                        * t
                    )
                    + 0.18
                    * math.sin(
                        2
                        * math.pi
                        * frequency
                        * 3.10
                        * t
                    )
                )
                vibrato = (
                    0.88
                    + 0.12
                    * math.sin(
                        2 * math.pi * 4.6 * t
                    )
                )
                value = (
                    formant
                    * 0.34
                    * vibrato
                )

            elif kind == "thunder":
                rumble = (
                    math.sin(2 * math.pi * frequency * t) * 0.34
                    + math.sin(2 * math.pi * frequency * 0.53 * t) * 0.25
                )
                value = rumble + rng.uniform(-1, 1) * 0.30 * envelope
                envelope = max(0.0, 1.0 - progress * 0.75)
            elif kind == "horse":
                beat = (math.sin(2 * math.pi * 6.6 * t) > 0.72)
                value = (-0.62 if beat else 0.0) + rng.uniform(-0.08, 0.08)
            elif kind == "crow":
                chirp = frequency + 220 * math.sin(2 * math.pi * 5 * t)
                value = math.sin(2 * math.pi * chirp * t) * 0.48
            elif kind == "wolf":
                growl = frequency + 40 * math.sin(2 * math.pi * 3.2 * t)
                value = math.sin(2 * math.pi * growl * t) * 0.50
            elif kind == "scanner":
                step = 1 if int(t * 14) % 2 == 0 else 1.45
                value = math.sin(2 * math.pi * frequency * step * t) * 0.52
            elif kind == "crackle":
                value = rng.uniform(-1, 1) * 0.36
                if rng.random() < 0.008:
                    value += rng.uniform(-0.8, 0.8)
            elif kind == "rain_hit":
                value = rng.uniform(-1, 1) * 0.30
            elif kind == "impact":
                value = (
                    math.sin(2 * math.pi * frequency * t) * 0.58
                    + rng.uniform(-1, 1) * 0.22
                )
            elif kind == "metal":
                value = (
                    math.sin(2 * math.pi * frequency * t) * 0.45
                    + math.sin(2 * math.pi * frequency * 1.91 * t) * 0.28
                    + math.sin(2 * math.pi * frequency * 2.73 * t) * 0.13
                )
            elif kind in {"sweep", "whoosh", "portal"}:
                factor = 1.0 + progress * (3.2 if kind == "portal" else 2.2)
                value = math.sin(2 * math.pi * frequency * factor * t) * 0.53
                if kind == "whoosh":
                    value += rng.uniform(-1, 1) * 0.16
            elif kind == "pulse":
                wave = math.sin(2 * math.pi * frequency * t)
                value = 0.55 if wave >= 0 else -0.55
            elif kind == "victory":
                value = (
                    math.sin(2 * math.pi * frequency * t) * 0.38
                    + math.sin(2 * math.pi * frequency * 1.25 * t) * 0.28
                )
            else:
                value = (
                    math.sin(2 * math.pi * frequency * t) * 0.52
                    + math.sin(2 * math.pi * frequency * 0.5 * t) * 0.16
                )

            data.append(self._to_sample(value * envelope))

        return data

    @staticmethod
    def _to_sample(value):
        value = max(-1.0, min(1.0, value))
        return int(value * 32767)
