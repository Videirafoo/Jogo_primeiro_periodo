import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from ending_gallery import EndingGallery
from map_loader import MapScene
from sprite_animator import LIBRARY
from story_data import GAME


class GraphicOverhaulTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_sete_mapas_tmx(self):
        for chapter in range(1, 8):
            scene = MapScene(chapter)
            self.assertTrue(scene.available)
            self.assertIsNotNone(scene.surface)
            self.assertGreaterEqual(
                len(scene.collision_rects),
                4,
            )

    def test_sprite_sheet_carrega(self):
        self.assertIsNotNone(
            LIBRARY.tile(0)
        )

    def test_galeria_tem_cinco_finais(self):
        gallery = EndingGallery(
            GAME["endings"]
        )
        self.assertEqual(
            len(gallery.entries()),
            5,
        )


if __name__ == "__main__":
    unittest.main()
