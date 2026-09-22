import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from combat_v27 import CombatPresentationV27
from quest_v27 import FACTIONS, QuestSystemII
from sprite_v25 import (
    BOSS_STATES,
    CHAR_STATES,
    ENEMY_STATES,
    FRAMES,
    ROOT,
    build_all,
)
from world_v27 import WorldQualityIII


class DummyPlayer:
    def __init__(self):
        self.pos = pygame.Vector2(400, 400)
        self.facing = pygame.Vector2(1, 0)


class V27QualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))
        build_all()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_animacao_seis_frames(self):
        self.assertEqual(FRAMES, 6)
        for state in (
            "parry",
            "dodge",
            "knockdown",
            "execute",
        ):
            self.assertIn(
                state,
                CHAR_STATES,
            )
        self.assertIn(
            "knockdown",
            ENEMY_STATES,
        )
        self.assertIn(
            "phase2",
            BOSS_STATES,
        )
        self.assertTrue(
            (ROOT / "protagonist_v25.png").exists()
        )

    def test_combate_tem_fases_visuais(self):
        presentation = CombatPresentationV27()
        player = DummyPlayer()
        presentation.on_attack("heavy")
        self.assertEqual(
            presentation.attack_phase(),
            "anticipation",
        )
        presentation.update(
            0.2,
            player,
        )
        self.assertIn(
            presentation.attack_phase(),
            {"active", "recovery"},
        )

    def test_world_weather_afeta_movimento(self):
        snow = WorldQualityIII(
            5,
            {},
        )
        self.assertLess(
            snow.movement_multiplier(),
            1.0,
        )
        self.assertGreater(
            snow.stamina_drain(),
            0,
        )

    def test_faccoes_e_final_dependem_do_mundo(self):
        profile = {
            "v26_consequences": {
                str(i): "proteger"
                for i in range(1, 7)
            },
        }
        quest = QuestSystemII(
            7,
            profile,
        )
        for _ in range(3):
            quest.on_choice("proteger")
        self.assertEqual(
            len(FACTIONS),
            3,
        )
        self.assertIn(
            quest.ending(),
            {
                "O Guardião de Valdrak",
                "A Segunda Valdrak",
                "A Era dos Clãs Livres",
                "O Caminho Entre Mundos",
            },
        )


if __name__ == "__main__":
    unittest.main()
