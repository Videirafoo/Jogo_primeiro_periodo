import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from character_visuals import ALLY_STYLES, draw_dialogue_box
from engine import StoryEngine
from rpg_world import RPGWorld
from story_data import GAME
import ui


class VisualRPGTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.surface = pygame.Surface((1280, 720))
        cls.fonts = ui.fonts()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def make_world(self):
        engine = StoryEngine(GAME)
        profile = {
            "level": 2,
            "xp": 1,
            "xp_next": 7,
            "max_health": 108,
            "health": 80,
            "max_energy": 106,
            "energy": 75,
            "kills": 1,
        }
        return RPGWorld(
            engine.current_chapter,
            engine,
            profile,
        )

    def test_seis_eternos_tem_identidade_visual(self):
        expected = {
            "Thorvald",
            "Aurel",
            "Kaion",
            "Brenor",
            "Eiran",
            "Noctar",
        }
        self.assertEqual(
            set(ALLY_STYLES),
            expected,
        )

        for data in ALLY_STYLES.values():
            self.assertIn("color", data)
            self.assertIn("power", data)
            self.assertIn("symbol", data)

    def test_inventario_abre_e_fecha(self):
        world = self.make_world()
        event = pygame.event.Event(
            pygame.KEYDOWN,
            key=pygame.K_i,
        )

        world.handle_key(event)
        self.assertTrue(world.inventory_open)

        world.handle_key(event)
        self.assertFalse(world.inventory_open)

    def test_dialogo_cria_retrato_e_caixa(self):
        draw_dialogue_box(
            self.surface,
            self.fonts,
            "Edda, a Vidente",
            "Valdrak observa seus passos.",
            (70, 224, 235),
        )

        self.assertNotEqual(
            self.surface.get_at((640, 500))[:3],
            (0, 0, 0),
        )

    def test_hit_feedback_ativa_shake_stop_flash(self):
        world = self.make_world()
        world.impact_feedback(
            strength=9,
            stop=0.08,
            flash=0.12,
        )

        self.assertGreater(
            world.shake_timer,
            0,
        )
        self.assertGreater(
            world.hit_stop,
            0,
        )
        self.assertGreater(
            world.flash_timer,
            0,
        )

    def test_aliado_pode_atacar(self):
        world = self.make_world()
        world.engine.allies.append("thorvald")
        target = world.enemies[0]
        target.pos.update(
            world.player.pos + pygame.Vector2(80, 0)
        )
        before = target.hp

        world._ally_assist()

        self.assertLess(
            target.hp,
            before,
        )
        self.assertIn(
            "Thorvald",
            world.notice,
        )

    def test_render_com_boss_npc_inventario(self):
        world = self.make_world()
        world.engine.allies.append("thorvald")
        world.inventory_open = True

        world.draw(
            self.surface,
            self.fonts,
        )

        self.assertTrue(world.boss_alive())


if __name__ == "__main__":
    unittest.main()
