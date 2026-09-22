import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from art_v26 import REGION_FEATURES, WorldArtII
from cinematic_v26 import CinematicDirector
from world_v26 import (
    CONTRACT_TARGETS,
    QUESTS,
    REGION_MINI_STORIES,
    VILLAGER_NAMES,
    WorldQuestDirector,
)


class V26WorldQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_sete_regioes_tem_vilas_populadas(self):
        self.assertEqual(
            set(VILLAGER_NAMES),
            set(range(1, 8)),
        )
        self.assertTrue(
            all(
                len(names) == 7
                for names in VILLAGER_NAMES.values()
            )
        )

    def test_quests_multietapa_em_sete_regioes(self):
        self.assertEqual(
            set(QUESTS),
            set(range(1, 8)),
        )
        for quest in QUESTS.values():
            self.assertGreaterEqual(
                quest["need"],
                2,
            )
            self.assertEqual(
                len(quest["choices"]),
                2,
            )

    def test_tres_contratos_por_regiao(self):
        self.assertEqual(
            set(CONTRACT_TARGETS),
            set(range(1, 8)),
        )
        self.assertTrue(
            all(
                len(targets) == 3
                for targets in CONTRACT_TARGETS.values()
            )
        )

    def test_duas_historias_secretas_por_regiao(self):
        self.assertTrue(
            all(
                len(stories) == 2
                for stories in REGION_MINI_STORIES.values()
            )
        )

    def test_escolha_gera_consequencia(self):
        profile = {}
        director = WorldQuestDirector(
            1,
            profile,
        )
        director.quest_state["stage"] = 2
        director.pending_choice = True
        message = director.choose_quest(1)
        self.assertIn(
            "Decisão registrada",
            message,
        )
        self.assertEqual(
            profile["v26_consequences"]["1"],
            "proteger",
        )
        self.assertEqual(
            director.quest_state["stage"],
            3,
        )

    def test_kills_avancam_quest(self):
        profile = {}
        director = WorldQuestDirector(
            1,
            profile,
        )
        director.quest_state["stage"] = 1
        target = QUESTS[1]["target"]
        for _ in range(QUESTS[1]["need"]):
            director.on_enemy_defeated(
                target
            )
        self.assertEqual(
            director.quest_state["stage"],
            2,
        )

    def test_art_world_ii_sete_regioes(self):
        self.assertEqual(
            set(REGION_FEATURES),
            set(range(1, 8)),
        )
        art = WorldArtII(6, {})
        self.assertEqual(
            art.region,
            6,
        )

    def test_cinematica_inicial_uma_vez(self):
        profile = {}
        first = CinematicDirector(
            1,
            profile,
        )
        self.assertTrue(first.active)
        second = CinematicDirector(
            1,
            profile,
        )
        self.assertFalse(second.active)


if __name__ == "__main__":
    unittest.main()
