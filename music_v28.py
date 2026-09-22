import math
from pathlib import Path
import wave


ROOT = Path(__file__).with_name("assets") / "audio" / "music_v28"
RATE = 22050

REGION_ROOTS = (55.0, 58.27, 65.41, 49.0, 73.42, 41.20, 46.25)
ALLY_ROOTS = {
    "thorvald": 73.42,
    "aurel": 82.41,
    "kaion": 98.00,
    "brenor": 55.00,
    "eiran": 87.31,
    "noctar": 46.25,
}


def _write(name, duration, root, tempo, mode=1.5, intensity=1.0):
    ROOT.mkdir(parents=True, exist_ok=True)
    path = ROOT / f"{name}.wav"
    count = int(RATE * duration)
    frames = bytearray()

    for i in range(count):
        t = i / RATE
        beat = (t * tempo / 60.0) % 1.0
        pulse = max(0.0, 1.0 - beat * 5.5)
        bar = int(t * tempo / 60.0) % 8
        note_mult = (1.0, mode, 2.0, 1.333)[bar % 4]

        drone = (
            math.sin(2 * math.pi * root * t)
            + 0.42 * math.sin(2 * math.pi * root * mode * t)
            + 0.22 * math.sin(2 * math.pi * root * 2 * t)
        ) * 0.22

        melody = (
            math.sin(2 * math.pi * root * note_mult * t)
            * 0.11
            * (0.55 + 0.45 * math.sin(2 * math.pi * 0.18 * t) ** 2)
        )

        drum = (
            math.sin(2 * math.pi * (42 + intensity * 9) * t)
            * (pulse ** 6)
            * 0.14
            * intensity
        )

        shimmer = (
            math.sin(2 * math.pi * root * 4.02 * t)
            * 0.025
            * math.sin(2 * math.pi * 0.31 * t)
        )

        value = (drone + melody + drum + shimmer) * 0.72
        value = max(-1.0, min(1.0, value))
        sample = int(value * 32767)
        frames += int(sample).to_bytes(2, "little", signed=True)

    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(frames)
    return path


def build_all():
    built = []
    for region, root in enumerate(REGION_ROOTS, 1):
        mode = 1.5 if region in {1, 4, 7} else 1.333
        built.append(_write(f"music_region_{region}", 12.0, root, 74 + region * 2, mode, 0.55))
        built.append(_write(f"music_danger_{region}", 10.0, root, 104 + region * 3, mode, 0.85))
        built.append(_write(f"music_boss_{region}", 10.0, root / 2, 126 + region * 4, mode, 1.25))
        built.append(_write(f"music_interior_{region}", 9.0, root, 58 + region, mode, 0.35))

    for ally, root in ALLY_ROOTS.items():
        built.append(_write(f"theme_{ally}", 5.0, root, 96, 1.5, 0.75))

    return built


if __name__ == "__main__":
    files = build_all()
    print(f"MUSIC_V28_BUILT={len(files)}")
