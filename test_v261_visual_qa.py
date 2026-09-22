import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from eternos import GameApp
from world_v27 import WorldQualityIII


class V261VisualQATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_aliados_nao_ficam_empilhados(self):
        app = GameApp(headless=True)
        world = app.world
        positions = [
            world._ally_pos(index)
            for index in range(6)
        ]
        for i, first in enumerate(positions):
            for second in positions[i + 1:]:
                self.assertGreater(
                    first.distance_to(second),
                    55,
                )

    def test_predios_tem_portas_fora_da_colisao(self):
        system = WorldQualityIII(1, {})
        collisions = system.collision_rects()
        self.assertEqual(len(collisions), 5)
        for building, collision in zip(
            system.buildings,
            collisions,
        ):
            self.assertFalse(
                collision.collidepoint(
                    building.door
                )
            )

    def test_todas_regioes_tem_cinco_interiores(self):
        for region in range(1, 8):
            system = WorldQualityIII(
                region,
                {},
            )
            self.assertEqual(
                len(system.buildings),
                5,
            )


if __name__ == "__main__":
    unittest.main()
