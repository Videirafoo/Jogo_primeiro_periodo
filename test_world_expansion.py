import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from world_expansion import (
    REGION_EXPANSION,
    build_region_places,
    interact_with_place,
    region_progress,
)


class FakePlayer:
    def __init__(self, profile):
        self.pos = pygame.Vector2(900, 540)
        self.health = profile["health"]
        self.energy = profile["energy"]


class FakeWorld:
    def __init__(self, chapter_number=1):
        self.chapter = {"number": chapter_number}
        self.profile = {
            "level": 1,
            "xp": 0,
            "xp_next": 4,
            "max_health": 100,
            "health": 70,
            "max_energy": 100,
            "energy": 60,
            "kills": 0,
            "inventory": {
                "pocao": 1,
                "essencia": 1,
                "fragmento": 0,
                "reliquia": 0,
                "chave": 0,
            },
            "discoveries": [],
            "completed_region_quests": [],
        }
        self.player = FakePlayer(self.profile)
        self.camera = pygame.Vector2()


class WorldExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_sete_regioes_e_vinte_oito_lugares(self):
        self.assertEqual(set(REGION_EXPANSION), set(range(1, 8)))

        places = [
            place
            for region in REGION_EXPANSION.values()
            for place in region["places"]
        ]

        self.assertEqual(len(places), 28)
        self.assertEqual(
            sum(place["type"] == "passage" for place in places),
            7,
        )

        for place in places:
            self.assertGreater(len(place["story"]), 80)

    def test_descoberta_de_lore_entrega_reliquia(self):
        world = FakeWorld(1)
        places = build_region_places(1, world.profile)
        lore = next(place for place in places if place.kind == "lore")

        result = interact_with_place(lore, world)

        self.assertTrue(result["ok"])
        self.assertIn(lore.id, world.profile["discoveries"])
        self.assertEqual(world.profile["inventory"]["reliquia"], 1)
        self.assertEqual(world.profile["xp"], 1)

    def test_ruina_entrega_fragmento(self):
        world = FakeWorld(1)
        places = build_region_places(1, world.profile)
        ruin = next(place for place in places if place.kind == "ruin")

        interact_with_place(ruin, world)

        self.assertEqual(world.profile["inventory"]["fragmento"], 1)

    def test_tres_descobertas_concluem_missao_regional(self):
        world = FakeWorld(1)
        places = build_region_places(1, world.profile)
        normal_places = [
            place
            for place in places
            if place.kind != "passage"
        ]

        for place in normal_places[:3]:
            interact_with_place(place, world)

        found, total = region_progress(1, world.profile)

        self.assertEqual(found, 3)
        self.assertEqual(total, 4)
        self.assertIn(1, world.profile["completed_region_quests"])
        self.assertEqual(world.profile["inventory"]["chave"], 1)

    def test_passagem_bloqueada_nao_conta_descoberta(self):
        world = FakeWorld(1)
        places = build_region_places(1, world.profile)
        passage = next(
            place
            for place in places
            if place.kind == "passage"
        )

        result = interact_with_place(passage, world)

        self.assertFalse(result["ok"])
        self.assertNotIn(
            passage.id,
            world.profile["discoveries"],
        )

    def test_passagem_pode_teleportar(self):
        world = FakeWorld(1)
        places = build_region_places(1, world.profile)

        for place in [
            item
            for item in places
            if item.kind != "passage"
        ][:2]:
            interact_with_place(place, world)

        passage = next(
            place
            for place in places
            if place.kind == "passage"
        )

        result = interact_with_place(passage, world)

        self.assertTrue(result["ok"])
        self.assertEqual(
            tuple(int(value) for value in world.player.pos),
            tuple(passage.target),
        )


if __name__ == "__main__":
    unittest.main()
