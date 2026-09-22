import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from adventure_v28 import AdventureDepthV28, SITE_TYPES, SUBREGIONS
from combat_v28 import CombatCoreV28, Projectile
from companion_v28 import CompanionSystemV28
from dungeon_v28 import DungeonSystemIII, ROOM_TYPES
from rpg_depth_v28 import BUILD_ARCHETYPES, RPGDepthII, ensure_rpg_v28, synergy_for


def profile():
    return {
        "level": 5,
        "coins": 100,
        "skill_points": 2,
        "inventory": {
            "pocao": 1,
            "essencia": 1,
            "fragmento": 0,
            "reliquia": 2,
            "chave": 1,
        },
        "gear_bag": [],
        "equipped": {
            "weapon": None,
            "armor": None,
            "amulet": None,
            "rune": None,
        },
    }


class AdventureDepthTests(unittest.TestCase):
    def test_all_regions_have_three_subregions(self):
        self.assertEqual(set(SUBREGIONS), set(range(1, 8)))
        self.assertTrue(all(len(names) == 3 for names in SUBREGIONS.values()))

    def test_region_has_all_adventure_sites(self):
        data = profile()
        system = AdventureDepthV28(1, data)
        self.assertEqual({site.kind for site in system.sites}, set(SITE_TYPES))
        self.assertEqual(len(system.sites), 8)

    def test_discovery_persists(self):
        data = profile()
        system = AdventureDepthV28(2, data)
        site = system.sites[0]
        system.enter(site)
        restored = AdventureDepthV28(2, data)
        self.assertTrue(restored.sites[0].discovered)
        self.assertIn(site.id, data["v28_discoveries"])

    def test_subregion_tracks_world_position(self):
        data = profile()
        system = AdventureDepthV28(3, data)
        self.assertEqual(system.update_position(pygame.Vector2(3000, 500)), SUBREGIONS[3][2])


class DungeonV28Tests(unittest.TestCase):
    def test_dungeon_contains_required_room_types(self):
        data = profile()
        dungeon = DungeonSystemIII(4, data)
        dungeon.start_from_site("catacomb")
        self.assertEqual(dungeon.rooms[0], "entrada")
        self.assertEqual(dungeon.rooms[-1], "cofre")
        self.assertTrue(set(ROOM_TYPES).issubset(set(dungeon.rooms)))

    def test_dungeon_state_is_save_ready(self):
        data = profile()
        DungeonSystemIII(1, data)
        self.assertIn("v28_dungeons", data)
        self.assertIn("v28_special_keys", data)


class CombatV28Tests(unittest.TestCase):
    def test_parry_windows_change_by_enemy(self):
        core = CombatCoreV28(profile())
        self.assertGreater(core.parry_window("archer"), core.parry_window("boss"))

    def test_enemy_combos_have_phase_two_extension(self):
        core = CombatCoreV28(profile())
        p1 = core.enemy_combo("berserker", 1)
        p2 = core.enemy_combo("berserker", 2)
        self.assertGreater(len(p2), len(p1))

    def test_projectile_moves(self):
        projectile = Projectile((10, 10), (100, 0), 5)
        projectile.update(0.25)
        self.assertGreater(projectile.pos.x, 10)


class RPGDepthTests(unittest.TestCase):
    def test_builds_and_ally_trees_are_persistent(self):
        data = profile()
        ensure_rpg_v28(data)
        system = RPGDepthII(data)
        old = data["v28_build"]
        new = system.cycle_build()
        self.assertIn(new, BUILD_ARCHETYPES)
        self.assertNotEqual(old, new)
        self.assertIn("v28_ally_skills", data)

    def test_known_pair_has_synergy(self):
        synergy = synergy_for(["Thorvald", "Aurel"])
        self.assertIsNotNone(synergy)
        self.assertEqual(synergy[0], "Tempestade Solar")


class CompanionTests(unittest.TestCase):
    def test_two_active_companions_maximum(self):
        data = profile()
        companions = CompanionSystemV28(data)
        companions.sync(["Thorvald", "Aurel", "Kaion", "Brenor"])
        self.assertEqual(len(companions.active), 2)

    def test_friendship_unlocks_personal_quest(self):
        data = profile()
        companions = CompanionSystemV28(data)
        companions.sync(["Thorvald"])
        message = None
        for _ in range(4):
            message = companions.friendship_gain("Thorvald", 1)
        self.assertIn("Quest pessoal", message)


if __name__ == "__main__":
    unittest.main()
