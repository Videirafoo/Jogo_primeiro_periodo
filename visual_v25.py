import math
import random

import pygame


class VisualRPGPass:
    def __init__(self, chapter, world_size=(1800, 1080)):
        self.chapter = chapter
        self.world_w, self.world_h = world_size
        rng = random.Random(25000 + chapter)
        self.grass = [
            (
                rng.randint(50, self.world_w - 50),
                rng.randint(70, self.world_h - 40),
                rng.uniform(0.7, 1.4),
            )
            for _ in range(48)
        ]
        self.water = [
            (
                rng.randint(120, self.world_w - 120),
                rng.randint(150, self.world_h - 100),
                rng.randint(34, 70),
            )
            for _ in range(7)
        ]
        self.fireflies = [
            (
                rng.randint(40, self.world_w - 40),
                rng.randint(60, self.world_h - 60),
                rng.uniform(0, math.tau),
            )
            for _ in range(24)
        ]

    def draw_environment(self, surface, camera, seconds, accent):
        # Water receives moving highlights instead of static ovals.
        for wx, wy, radius in self.water:
            x = int(wx - camera.x)
            y = int(wy - camera.y)
            if -100 < x < 1380 and -80 < y < 800:
                pygame.draw.ellipse(
                    surface,
                    (23, 47, 57),
                    (x - radius, y - radius // 4, radius * 2, radius // 2),
                )
                for index in range(3):
                    offset = math.sin(seconds * 1.8 + index + wx * 0.01) * radius * 0.35
                    pygame.draw.arc(
                        surface,
                        (58, 114, 132),
                        (
                            int(x - radius * 0.65 + offset),
                            y - 5 + index * 4,
                            int(radius * 1.3),
                            12,
                        ),
                        0.2,
                        2.8,
                        1,
                    )

        # Vegetation sways instead of being rigid.
        for index, (wx, wy, scale) in enumerate(self.grass):
            x = int(wx - camera.x)
            y = int(wy - camera.y)
            if -30 < x < 1310 and -30 < y < 750:
                sway = math.sin(seconds * 2.2 + index * 0.67) * 4 * scale
                color = (
                    max(24, 52 - self.chapter * 2),
                    min(120, 77 + self.chapter * 3),
                    max(40, 61 + (4 - self.chapter) * 3),
                )
                for dx in (-5, 0, 5):
                    pygame.draw.line(
                        surface,
                        color,
                        (x + dx, y),
                        (int(x + dx + sway), int(y - 13 * scale)),
                        max(1, int(2 * scale)),
                    )

        # Fireflies / embers / rune motes.
        for index, (wx, wy, phase) in enumerate(self.fireflies):
            x = int(wx - camera.x + math.sin(seconds * 0.7 + phase) * 11)
            y = int(wy - camera.y + math.cos(seconds * 0.9 + phase) * 7)
            if 0 < x < 1280 and 0 < y < 720:
                alpha = int(90 + (math.sin(seconds * 3 + phase) + 1) * 55)
                glow = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*accent, alpha // 3), (8, 8), 7)
                pygame.draw.circle(glow, (*accent, alpha), (8, 8), 2)
                surface.blit(glow, (x - 8, y - 8))

    def draw_lighting(self, surface, world, seconds):
        accessibility = world.profile.get("accessibility", {})
        high_contrast = accessibility.get("high_contrast", False)
        darkness = 38 if high_contrast else {
            1: 54,
            2: 62,
            3: 50,
            4: 72,
            5: 46,
            6: 68,
            7: 78,
        }.get(self.chapter, 58)

        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((4, 7, 12, darkness))

        lights = [
            (world.player.pos, 125),
        ]
        for index, _name in enumerate(world.engine.ally_names()):
            lights.append((world._ally_pos(index), 82))
        boss = world.boss()
        if boss and not boss.dead:
            lights.append((boss.pos, 105))

        for site in getattr(world.living, "sites", []):
            if site.kind in {"altar", "temple"}:
                lights.append((site.pos, 72))

        for pos, radius in lights:
            x = int(pos.x - world.camera.x)
            y = int(pos.y - world.camera.y)
            if -radius < x < 1280 + radius and -radius < y < 720 + radius:
                for ring in range(5, 0, -1):
                    r = int(radius * ring / 5)
                    alpha = int(darkness * (ring - 1) / 5)
                    pygame.draw.circle(
                        overlay,
                        (0, 0, 0, alpha),
                        (x, y),
                        r,
                    )

        surface.blit(overlay, (0, 0))

        # Subtle cinematic grade, region-dependent.
        tint = {
            1: (12, 34, 38, 18),
            2: (40, 38, 32, 18),
            3: (55, 22, 16, 18),
            4: (9, 38, 24, 24),
            5: (31, 48, 58, 16),
            6: (65, 24, 10, 24),
            7: (42, 20, 68, 26),
        }.get(self.chapter, (0, 0, 0, 0))
        grade = pygame.Surface((1280, 720), pygame.SRCALPHA)
        grade.fill(tint)
        surface.blit(grade, (0, 0))

        # Soft letterbox only during boss proximity for cinematic framing.
        if boss and not boss.dead and boss.pos.distance_to(world.player.pos) < 430:
            bar = max(0, int(9 + math.sin(seconds * 1.5) * 2))
            pygame.draw.rect(surface, (0, 0, 0), (0, 0, 1280, bar))
            pygame.draw.rect(surface, (0, 0, 0), (0, 720 - bar, 1280, bar))
