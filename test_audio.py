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

    def test_volume_pode_ser_reduzido(self):
        audio = Audio()
        before = audio.master_volume
        after = audio.adjust_volume(-0.10)

        self.assertLess(after, before)
        self.assertGreaterEqual(after, 0.15)

    def test_volume_tem_limite_superior(self):
        audio = Audio()
        for _ in range(20):
            audio.adjust_volume(0.10)

        self.assertEqual(audio.master_volume, 1.0)


if __name__ == "__main__":
    unittest.main()
