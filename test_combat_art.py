import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from audio import Audio, VALDRAK_SFX
from weapon_art import draw_viking_axe, draw_sword


class CombatArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_machado_autoral_renderiza(self):
        surface = pygame.Surface((220, 220), pygame.SRCALPHA)
        draw_viking_axe(
            surface,
            (110, 110),
            angle=37,
            scale=0.8,
            rune_color=(70, 224, 235),
            motion=1.0,
        )
        self.assertGreater(
            pygame.mask.from_surface(surface).count(),
            300,
        )

    def test_espada_autoral_renderiza(self):
        surface = pygame.Surface((220, 220), pygame.SRCALPHA)
        draw_sword(
            surface,
            (110, 110),
            angle=-25,
            scale=0.8,
            motion=1.0,
        )
        self.assertGreater(
            pygame.mask.from_surface(surface).count(),
            200,
        )

    def test_audio_valdrak_tem_variantes(self):
        self.assertGreaterEqual(len(VALDRAK_SFX["axe_whoosh"]), 3)
        self.assertGreaterEqual(len(VALDRAK_SFX["axe_hit"]), 3)
        self.assertGreaterEqual(len(VALDRAK_SFX["footstep"]), 4)

        audio = Audio()
        first = audio._create_sound("axe_whoosh", 0)
        second = audio._create_sound("axe_whoosh", 1)
        self.assertNotEqual(first.get_raw(), second.get_raw())


if __name__ == "__main__":
    unittest.main()
