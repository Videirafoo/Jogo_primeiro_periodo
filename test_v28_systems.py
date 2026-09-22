import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from adventure_v28 import AdventureDepthV28
from combat_v28 import CombatCoreV28
from companion_v28 import CompanionSystemV28
from dungeon_v28 import DungeonSystemIII
from eternos import GameApp
from map_loader import MapScene
from progression_v24 import ensure_progression_profile
from rpg_depth_v28 import RPGDepthII, total_stats
from savegame import load_game, save_game


class DummyPlayer:
    def __init__(self):
        self.pos = pygame.Vector2(800, 600)
        self.facing = pygame.Vector2(1, 0)
        self.attack_timer = 0.0


class DummyEngine:
    def __init__(self):
        self.state = {}
        self.allies = ["Thorvald", "Aurel"]
        self.history = []
        self.chapter_index = 0
        self.current_chapter = {"number": 1}


class V28SystemsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_map_quadruples_traversable_area(self):
        scene = MapScene(1)
        self.assertTrue(scene.available)
        self.assertEqual(scene.width, 3648)
        self.assertEqual(scene.height, 2208)
        self.assertGreaterEqual(
            max(rect.right for rect in scene.collision_rects),
            1824,
        )

    def test_adventure_depth_spans_expanded_map(self):
        profile = {"inventory": {"chave": 1, "reliquia": 2}}
        adventure = AdventureDepthV28(1, profile)
        self.assertEqual(len(adventure.sites), 8)
        self.assertTrue(any(site.pos.x > 2432 for site in adventure.sites))
        self.assertTrue(any(site.pos.y > 1104 for site in adventure.sites))
        self.assertEqual(
            adventure.update_position(pygame.Vector2(3200, 400)),
            "Costa de Skarn",
        )

    def test_dungeon_iii_generates_deep_run(self):
        profile = {}
        dungeon = DungeonSystemIII(3, profile, seed=7)
        dungeon.start_from_site("catacomb")
        self.assertTrue(dungeon.active)
        self.assertEqual(dungeon.rooms[0], "entrada")
        self.assertEqual(dungeon.rooms[-1], "cofre")
        self.assertIn("mini_boss", dungeon.rooms)
        self.assertEqual(len(dungeon.puzzle_target), 4)

    def test_combat_iii_hitbox_changes_by_frame_phase(self):
        combat = CombatCoreV28({})
        player = DummyPlayer()
        active = combat.attack_hitbox(
            player,
            heavy=False,
            frame_phase="active",
        )
        anticipation = combat.attack_hitbox(
            player,
            heavy=False,
            frame_phase="anticipation",
        )
        self.assertGreater(active.width, anticipation.width)
        self.assertGreater(active.height, anticipation.height)

    def test_parry_timing_is_enemy_specific(self):
        combat = CombatCoreV28({})
        self.assertGreater(
            combat.parry_window("archer"),
            combat.parry_window("boss"),
        )
        self.assertGreater(
            combat.stamina_cost("heavy", "Saga"),
            combat.stamina_cost("heavy", "Explorador"),
        )

    def test_rpg_depth_build_changes_total_stats(self):
        profile = {}
        ensure_progression_profile(profile)
        rpg = RPGDepthII(profile)
        first = total_stats(profile)
        rpg.cycle_build()
        second = total_stats(profile)
        self.assertNotEqual(first, second)

    def test_companion_system_limits_active_party_to_two(self):
        profile = {}
        companions = CompanionSystemV28(profile)
        available = [
            "Thorvald",
            "Aurel",
            "Kaion",
            "Brenor",
            "Eiran",
            "Noctar",
        ]
        companions.sync(available)
        self.assertEqual(len(companions.active), 2)
        self.assertEqual(len(set(companions.active)), 2)

    def test_friendship_unlocks_personal_quest(self):
        profile = {}
        companions = CompanionSystemV28(profile)
        companions.sync(["Thorvald", "Aurel"])
        message = None
        for _ in range(4):
            message = companions.friendship_gain("Thorvald", 1)
        self.assertIn("Quest pessoal disponível", message)
        self.assertEqual(
            profile["v28_personal_quests"]["Thorvald"]["stage"],
            1,
        )

    def test_v28_profile_survives_save_load(self):
        engine = DummyEngine()
        profile = {
            "v28_sites": {"site": {"discovered": True}},
            "v28_active_allies": ["Thorvald", "Aurel"],
            "v28_build": "Caçador do Vazio",
        }
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "save.json"
            self.assertTrue(
                save_game(
                    engine,
                    profile,
                    "explore",
                    0,
                    0,
                    path=path,
                )
            )
            loaded = load_game(path=path)
        self.assertEqual(
            loaded["rpg_profile"]["v28_build"],
            "Caçador do Vazio",
        )
        self.assertEqual(
            loaded["rpg_profile"]["v28_active_allies"],
            ["Thorvald", "Aurel"],
        )

    def test_game_world_integrates_all_v28_systems(self):
        app = GameApp(headless=True)
        world = app.world
        self.assertIsNotNone(world.adventure_v28)
        self.assertIsNotNone(world.dungeon_v28)
        self.assertIsNotNone(world.combat_v28)
        self.assertIsNotNone(world.rpg_v28)
        self.assertIsNotNone(world.companion_v28)
        self.assertLessEqual(
            len(world.companion_v28.active),
            2,
        )

    def test_authored_audio_ii_bank_exists(self):
        root = Path(__file__).with_name("assets") / "audio" / "music_v28"
        tracks = list(root.glob("*.wav"))
        self.assertGreaterEqual(len(tracks), 34)
        for region in range(1, 8):
            self.assertTrue(
                (root / f"music_region_{region}.wav").exists()
            )
            self.assertTrue(
                (root / f"music_boss_{region}.wav").exists()
            )


if __name__ == "__main__":
    unittest.main()
