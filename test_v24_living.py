import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from boss_v24 import BOSS_MOVESETS, BossCombatController
from living_valdrak import LivingValdrak
from progression_v24 import (
    add_and_auto_equip,
    ensure_progression_profile,
    equipment_stats,
    roll_equipment,
)
from rpg_entities import ARCHETYPES


class DummyPlayer:
    def __init__(self):
        self.pos = pygame.Vector2(900, 540)
        self.health = 100
        self.energy = 100

    def damage(self, amount):
        self.health -= amount
        return True


class DummyWorld:
    def __init__(self):
        self.profile = {
            "max_health": 100,
            "max_energy": 100,
            "inventory": {
                "pocao": 1,
                "essencia": 1,
                "fragmento": 0,
                "reliquia": 0,
                "chave": 0,
            },
        }
        ensure_progression_profile(self.profile)
        self.player = DummyPlayer()


class V24LivingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_oito_arquetipos_de_inimigos(self):
        expected = {
            "wolf",
            "alpha_wolf",
            "raider",
            "berserker",
            "archer",
            "rune_mage",
            "raven",
            "elite_raider",
        }
        self.assertTrue(expected <= set(ARCHETYPES))

    def test_sete_guardioes_tem_tres_moves(self):
        self.assertEqual(set(BOSS_MOVESETS), set(range(1, 8)))
        self.assertTrue(
            all(len(moves) == 3 for moves in BOSS_MOVESETS.values())
        )

    def test_living_valdrak_tem_seis_sites(self):
        world = DummyWorld()
        living = LivingValdrak(1, world.profile)
        self.assertEqual(len(living.sites), 6)

    def test_loot_tem_raridade_e_slot(self):
        world = DummyWorld()
        item = roll_equipment(4, random.Random(7), elite=True)
        self.assertIn(item["slot"], {"weapon", "armor", "amulet", "rune"})
        self.assertIn(item["rarity"], {"Comum", "Raro", "Épico", "Lendário"})
        add_and_auto_equip(world.profile, item)
        stats = equipment_stats(world.profile)
        self.assertIn("attack", stats)

    def test_boss_tem_stagger(self):
        controller = BossCombatController(3)
        self.assertFalse(controller.add_stagger(80))
        self.assertTrue(controller.add_stagger(25))
        self.assertGreater(controller.stunned, 0)


if __name__ == "__main__":
    unittest.main()
