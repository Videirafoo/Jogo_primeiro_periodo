import os
import unittest

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from audio import Audio


class AudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_chuva_cria_ambiente_continuo(self):
        audio = Audio()
        audio.set_ambience("rain")
        self.assertEqual(audio.current_ambience, "rain")
        self.assertIn("rain", audio.ambience_cache)

    def test_eventos_geram_sons_distintos(self):
        audio = Audio()
        thunder = audio._create_sound("thunder")
        sword = audio._create_sound("sword")
        horse = audio._create_sound("horse")

        self.assertGreater(len(thunder.get_raw()), len(sword.get_raw()))
        self.assertNotEqual(sword.get_raw(), horse.get_raw())

    def test_toggle_desliga_e_religa_audio(self):
        audio = Audio()
        audio.set_ambience("rain")
        self.assertTrue(audio.enabled)

        audio.toggle()
        self.assertFalse(audio.enabled)

        audio.toggle()
        self.assertTrue(audio.enabled)
        self.assertEqual(audio.current_ambience, "rain")


if __name__ == "__main__":
    unittest.main()
