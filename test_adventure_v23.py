import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from adventure_system import build_chests
from engine import StoryEngine
from rpg_world import RPGWorld
from story_data import GAME


class AdventureV23Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def make_world(self):
        engine = StoryEngine(GAME)
        profile = {
            "level": 1,
            "xp": 0,
            "xp_next": 4,
            "max_health": 100,
            "health": 100,
            "max_energy": 100,
            "energy": 100,
            "kills": 0,
        }
        return RPGWorld(engine.current_chapter, engine, profile)

    def test_primeiro_capitulo_tem_tutorial_jogavel(self):
        world = self.make_world()
        self.assertTrue(world.tutorial_active)
        self.assertIn("mova-se", world.active_objective())

    def test_tutorial_avanca_com_movimento_e_combate(self):
        world = self.make_world()
        world.player.pos += pygame.Vector2(100, 0)
        world.update(0.016, pygame.key.get_pressed())
        self.assertEqual(world.tutorial_stage, 1)

        world.attack()
        self.assertEqual(world.tutorial_stage, 2)

        world.player.pulse_timer = 0
        world.tech_pulse()
        self.assertEqual(world.tutorial_stage, 3)

        world.player.dash_timer = 0
        world.dash()
        self.assertEqual(world.tutorial_stage, 4)

    def test_tres_baus_por_regiao(self):
        profile = {"opened_chests": []}
        for chapter in range(1, 8):
            self.assertEqual(len(build_chests(chapter, profile)), 3)

    def test_bau_recompensa_uma_so_vez(self):
        world = self.make_world()
        chest = world.chests[0]
        before = world.profile["inventory"]["pocao"]
        chest.open(world)
        after_first = world.profile["inventory"]["pocao"]
        second = chest.open(world)
        after_second = world.profile["inventory"]["pocao"]

        self.assertEqual(after_first, before + 1)
        self.assertEqual(after_second, after_first)
        self.assertIn("já foi aberto", second["text"])


if __name__ == "__main__":
    unittest.main()
