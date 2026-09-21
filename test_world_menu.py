import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from audio import ASSET_ROOT, EXTERNAL_SFX
from pause_menu import PauseMenu
from world_art import REGIONS, WorldArt


class WorldMenuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.surface = pygame.Surface((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_sete_regioes_possuem_identidade(self):
        self.assertEqual(set(REGIONS), set(range(1, 8)))
        self.assertEqual(len({x["landmark"] for x in REGIONS.values()}), 7)

    def test_world_art_renderiza(self):
        art = WorldArt(6)
        art.draw(self.surface, pygame.Vector2(0, 0), 1.5)
        self.assertNotEqual(self.surface.get_at((640, 360))[:3], (0, 0, 0))

    def test_menu_tem_save_load(self):
        actions = {action for _label, action in PauseMenu.OPTIONS}
        self.assertTrue({"save", "load", "controls", "resume", "quit"} <= actions)

    def test_esc_menu_retorna_resume(self):
        menu = PauseMenu()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        self.assertEqual(menu.handle_key(event), "resume")

    def test_sons_cc0_existem(self):
        for filename in set(EXTERNAL_SFX.values()):
            self.assertTrue((ASSET_ROOT / filename).exists(), filename)


if __name__ == "__main__":
    unittest.main()
