import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from engine import StoryEngine
from map_loader import MapScene
from rpg_world import RPGWorld
from story_data import GAME


class Keys:
    def __init__(self, *pressed):
        self.pressed = set(pressed)

    def __getitem__(self, key):
        return key in self.pressed


def fresh_profile(level=1):
    return {
        "level": level,
        "xp": 0,
        "xp_next": 4,
        "max_health": 160,
        "health": 160,
        "max_energy": 140,
        "energy": 140,
        "kills": 0,
    }


class V281MovementHotfixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def make_world(self, chapter_index):
        engine = StoryEngine(GAME)
        engine.chapter_index = chapter_index
        engine.allies = list(GAME["allies"].keys())[
            : min(6, chapter_index + 1)
        ]
        chapter = GAME["chapters"][chapter_index]
        return RPGWorld(
            chapter,
            engine,
            fresh_profile(chapter_index + 1),
        )

    def test_spawn_is_walkable_in_all_regions(self):
        for index in range(7):
            world = self.make_world(index)
            player_rect = world.player.rect_at()
            self.assertFalse(
                any(
                    player_rect.colliderect(obstacle)
                    for obstacle in world.obstacles
                ),
                f"region {index + 1} spawn blocked",
            )

    def test_player_moves_four_directions_from_spawn(self):
        controls = (
            (pygame.K_d, "right"),
            (pygame.K_a, "left"),
            (pygame.K_w, "up"),
            (pygame.K_s, "down"),
        )
        for index in range(7):
            world = self.make_world(index)
            origin = world.player.pos.copy()
            for key, label in controls:
                world.player.pos.update(origin)
                before = world.player.pos.copy()
                for _ in range(8):
                    world.update(
                        1 / 60,
                        Keys(key),
                    )
                moved = world.player.pos.distance_to(
                    before
                )
                self.assertGreater(
                    moved,
                    5,
                    f"region {index + 1} cannot move {label}",
                )

    def test_internal_map_seams_are_open(self):
        for chapter in range(1, 8):
            scene = MapScene(chapter)
            self.assertEqual(
                len(scene.collision_rects),
                8,
            )
            for point in (
                (1824, 552),
                (912, 1104),
                (1824, 1104),
            ):
                hits = [
                    rect
                    for rect in scene.collision_rects
                    if rect.collidepoint(*point)
                ]
                self.assertEqual(
                    hits,
                    [],
                    (
                        f"chapter {chapter} internal seam "
                        f"blocked at {point}"
                    ),
                )

    def test_interactables_are_relocated_to_walkable_ground(self):
        for index in range(7):
            world = self.make_world(index)
            groups = [
                [world.npc],
                world.shrines,
                world.places,
                world.chests,
                world.enemies,
                world.v26.villagers,
                world.v26.secrets,
                [world.v26.encounter],
                world.adventure_v28.sites,
            ]
            for group in groups:
                for obj in group:
                    rect = pygame.Rect(
                        int(obj.pos.x - 18),
                        int(obj.pos.y - 18),
                        36,
                        36,
                    )
                    self.assertFalse(
                        any(
                            rect.colliderect(obstacle)
                            for obstacle
                            in world.obstacles
                        ),
                        (
                            f"region {index + 1} "
                            f"{type(obj).__name__} blocked "
                            f"at {tuple(obj.pos)}"
                        ),
                    )

    def test_villager_routines_do_not_clip_buildings(self):
        world = self.make_world(0)
        for _ in range(600):
            world.v26.update(1 / 60, world)

        for npc in world.v26.villagers:
            rect = pygame.Rect(
                int(npc.pos.x - 13),
                int(npc.pos.y - 16),
                26,
                38,
            )
            self.assertFalse(
                any(
                    rect.colliderect(obstacle)
                    for obstacle in world.obstacles
                ),
                f"{npc.name} clipped into a building",
            )


if __name__ == "__main__":
    unittest.main()
