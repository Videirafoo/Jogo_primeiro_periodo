import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from combat_v25 import CombatV25
from dungeon_v25 import DungeonRun
from eternos import GameApp
from meta_v25 import craft, ensure_meta, unlock_talent
from savegame import slot_path
from sprite_v25 import (
    ACTORS,
    CHAR_STATES,
    DIRECTIONS_8,
    ENEMIES,
    ROOT,
    build_all,
)


class DummyPlayer:
    def __init__(self):
        self.health = 100
        self.energy = 100

    def damage(self, value):
        self.health -= value
        return True


class DummyWorld:
    def __init__(self):
        self.profile = {
            "level": 3,
            "inventory": {
                "pocao": 1,
                "essencia": 1,
                "fragmento": 0,
                "reliquia": 0,
                "chave": 0,
            },
        }
        ensure_meta(self.profile)
        self.player = DummyPlayer()


class V25SystemsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))
        build_all()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_sprite_sheets_autorais_existem(self):
        self.assertEqual(len(DIRECTIONS_8), 8)
        self.assertIn("heavy", CHAR_STATES)
        self.assertIn("power", CHAR_STATES)
        self.assertEqual(len(ACTORS), 7)
        self.assertEqual(len(ENEMIES), 8)
        self.assertTrue(
            (ROOT / "protagonist_v25.png").exists()
        )
        for chapter in range(1, 8):
            self.assertTrue(
                (ROOT / f"boss_{chapter}_v25.png").exists()
            )

    def test_parry_e_esquiva_perfeita(self):
        profile = {}
        combat = CombatV25(profile)
        self.assertTrue(combat.activate_parry())
        damage, label = combat.incoming(20)
        self.assertEqual(damage, 0)
        self.assertIn("PARRY", label)

        combat.stamina = 100
        self.assertTrue(combat.activate_dodge())
        damage, label = combat.incoming(20)
        self.assertEqual(damage, 0)
        self.assertIn("ESQUIVA", label)

    def test_crafting_e_talentos(self):
        world = DummyWorld()
        ok, _ = craft(world.profile, 0, 1)
        self.assertTrue(ok)
        world.profile["skill_points"] = 1
        ok, _ = unlock_talent(world.profile, 0)
        self.assertTrue(ok)

    def test_dungeon_tem_cinco_salas(self):
        world = DummyWorld()
        dungeon = DungeonRun(1, world.profile)
        self.assertEqual(len(dungeon.ROOMS), 5)
        self.assertEqual(dungeon.room, 0)

    def test_save_slots_sao_distintos(self):
        self.assertNotEqual(slot_path(1), slot_path(2))
        self.assertNotEqual(slot_path(2), slot_path(3))

    def test_p_aciona_parry_sem_pausar(self):
        app = GameApp(headless=True)
        app.handle_key(
            pygame.event.Event(
                pygame.KEYDOWN,
                key=pygame.K_p,
            )
        )
        self.assertFalse(app.paused)
        self.assertGreater(
            app.world.combat_v25.parry_window,
            0,
        )

    def test_escape_fecha_overlay_antes_de_pausar(self):
        app = GameApp(headless=True)
        app.world.overlay_screen = "map"
        app.handle_key(
            pygame.event.Event(
                pygame.KEYDOWN,
                key=pygame.K_ESCAPE,
            )
        )
        self.assertFalse(app.paused)
        self.assertIsNone(app.world.overlay_screen)


if __name__ == "__main__":
    unittest.main()
