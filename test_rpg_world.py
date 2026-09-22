import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from engine import StoryEngine
from rpg_world import RPGWorld
from story_data import GAME


class RPGWorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def make_world(self, chapter_index=0):
        engine = StoryEngine(GAME)
        engine.chapter_index = chapter_index
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

    def test_mundo_tem_tres_caminhos_fisicos(self):
        world = self.make_world()
        self.assertEqual(len(world.shrines), 3)

    def test_ataque_derrota_inimigo_proximo(self):
        world = self.make_world()
        enemy = world.enemies[0]
        enemy.pos = world.player.pos + world.player.facing * 45
        enemy.hp = 1

        world.attack()

        self.assertTrue(enemy.dead)
        self.assertEqual(world.profile["kills"], 1)

    def test_pulso_de_codigo_gasta_energia(self):
        world = self.make_world()
        before = world.player.energy

        world.tech_pulse()

        self.assertLess(world.player.energy, before)

    def test_interacao_escolhe_santuario(self):
        world = self.make_world()
        boss = world.boss()
        boss.dead = True
        shrine = next(item for item in world.shrines if item.available)
        world.player.pos.update(shrine.pos)

        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        world.handle_key(event)

        self.assertEqual(world.selected_choice, shrine.index)

    def test_boss_bloqueia_caminhos(self):
        world = self.make_world()
        shrine = next(item for item in world.shrines if item.available)
        world.player.pos.update(shrine.pos)

        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        world.handle_key(event)

        self.assertIsNone(world.selected_choice)
        self.assertIn("Guardião", world.notice)

    def test_cada_capitulo_tem_boss(self):
        for chapter_index in range(7):
            world = self.make_world(chapter_index)
            boss = world.boss()
            self.assertIsNotNone(boss)
            self.assertTrue(boss.boss)
            self.assertFalse(boss.dead)

    def test_npc_entrega_presente_uma_vez(self):
        world = self.make_world()
        world.player.pos.update(world.npc.pos)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)

        before = world.profile["inventory"]["essencia"]
        world.handle_key(event)
        after_first = world.profile["inventory"]["essencia"]
        world.handle_key(event)
        after_second = world.profile["inventory"]["essencia"]

        self.assertEqual(after_first, before + 1)
        self.assertEqual(after_second, after_first)

    def test_pocao_recupera_vida(self):
        world = self.make_world()
        world.player.health = 40
        before = world.profile["inventory"]["pocao"]

        used = world.use_item("pocao")

        self.assertTrue(used)
        self.assertEqual(world.player.health, 75)
        self.assertEqual(
            world.profile["inventory"]["pocao"],
            before - 1,
        )

    def test_progressao_de_nivel_persiste_no_profile(self):
        world = self.make_world()
        world.profile["xp"] = world.profile["xp_next"] - 1

        leveled = world.player.gain_xp(1)

        self.assertTrue(leveled)
        self.assertEqual(world.profile["level"], 2)
        self.assertGreater(world.profile["max_health"], 100)

    def test_recompensa_por_combate_altera_historia(self):
        world = self.make_world()
        world.profile["kills"] += 2
        before = world.engine.state.get("coragem", 0)

        reward = world.apply_rewards()

        self.assertIn("Coragem", reward)
        self.assertEqual(
            world.engine.state["coragem"],
            before + 1,
        )


if __name__ == "__main__":
    unittest.main()
