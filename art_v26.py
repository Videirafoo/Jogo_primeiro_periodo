import math
import random

import pygame


REGION_FEATURES = {
    1: ("Rio de Vidro", "Vila da Estrada"),
    2: ("Montanhas do Portão", "Fortaleza de Ossos"),
    3: ("Cidade dos Despertos", "Arena de Hroth"),
    4: ("Cachoeira dos Corvos", "Templo Móvel"),
    5: ("Rio Congelado", "Castelo dos Lobos"),
    6: ("Rios de Lava Negra", "Grande Forja"),
    7: ("Montanhas do Vazio", "Templo da Última Porta"),
}


class WorldArtII:
    def __init__(self, region, profile, world_size=(1800, 1080)):
        self.region = region
        self.profile = profile
        self.world_w, self.world_h = world_size
        rng = random.Random(77000 + region)
        self.mountain_points = [
            (
                rng.randint(0, self.world_w),
                rng.randint(55, 145),
                rng.randint(80, 180),
            )
            for _ in range(13)
        ]
        self.braziers = [
            pygame.Vector2(455, 470),
            pygame.Vector2(1340, 470),
            pygame.Vector2(455, 700),
            pygame.Vector2(1340, 700),
        ]

    def draw_world(self, surface, camera, seconds):
        self._mountains(surface, camera)
        if self.region in {1, 4, 5, 6}:
            self._river(surface, camera, seconds)
        if self.region == 4:
            self._waterfall(surface, camera, seconds)
        if self.region == 6:
            self._lava(surface, camera, seconds)
        self._settlement(surface, camera, seconds)
        self._landmark(surface, camera, seconds)
        self._consequence(surface, camera, seconds)

    def _mountains(self, surface, camera):
        if self.region not in {2, 5, 7}:
            return
        palette = {
            2: ((50, 52, 55), (73, 72, 69)),
            5: ((79, 94, 103), (128, 145, 154)),
            7: ((40, 30, 62), (73, 50, 105)),
        }[self.region]
        for wx, wy, size in self.mountain_points:
            x = int(wx - camera.x)
            y = int(wy - camera.y)
            pygame.draw.polygon(
                surface,
                palette[0],
                [(x - size, y + size // 2), (x, y - size), (x + size, y + size // 2)],
            )
            pygame.draw.polygon(
                surface,
                palette[1],
                [(x - size // 3, y - size // 3), (x, y - size), (x + size // 4, y - size // 3)],
            )

    def _river(self, surface, camera, seconds):
        color = {
            1: (32, 77, 91),
            4: (25, 67, 62),
            5: (122, 161, 180),
            6: (34, 27, 29),
        }[self.region]
        points = []
        for i in range(15):
            wx = -100 + i * 145
            wy = 780 + math.sin(i * 0.72 + self.region) * 95
            points.append((int(wx - camera.x), int(wy - camera.y)))
        pygame.draw.lines(surface, color, False, points, 92)
        highlight = (73, 145, 166) if self.region != 6 else (86, 55, 46)
        shifted = [(x, y + int(math.sin(seconds * 1.8 + i) * 5)) for i, (x, y) in enumerate(points)]
        pygame.draw.lines(surface, highlight, False, shifted, 3)

    def _waterfall(self, surface, camera, seconds):
        x = int(260 - camera.x)
        y = int(210 - camera.y)
        rect = pygame.Rect(x - 55, y - 40, 110, 245)
        pygame.draw.rect(surface, (33, 79, 79), rect, border_radius=18)
        for i in range(7):
            px = x - 42 + i * 14 + int(math.sin(seconds * 3 + i) * 4)
            pygame.draw.line(surface, (95, 167, 165), (px, y - 25), (px, y + 180), 3)
        pygame.draw.ellipse(surface, (26, 68, 71), (x - 90, y + 165, 180, 48))

    def _lava(self, surface, camera, seconds):
        for index in range(3):
            y = int(250 + index * 245 - camera.y)
            x1 = int(130 - camera.x)
            x2 = int(1640 - camera.x)
            points = []
            for step in range(14):
                x = x1 + step * ((x2 - x1) / 13)
                wave = math.sin(seconds * 2.4 + step + index) * 17
                points.append((int(x), int(y + wave)))
            pygame.draw.lines(surface, (68, 22, 17), False, points, 44)
            pygame.draw.lines(surface, (221, 72, 28), False, points, 10)
            pygame.draw.lines(surface, (255, 153, 62), False, points, 3)

    def _house(self, surface, x, y, scale=1.0, color=(100, 67, 45)):
        w = int(72 * scale)
        h = int(46 * scale)
        pygame.draw.rect(surface, color, (x - w // 2, y - h // 2, w, h), border_radius=5)
        roof = tuple(max(0, c - 28) for c in color)
        pygame.draw.polygon(
            surface,
            roof,
            [(x - w // 2 - 8, y - h // 2), (x, y - h), (x + w // 2 + 8, y - h // 2)],
        )
        pygame.draw.rect(surface, (225, 173, 76), (x - 7, y - 9, 14, 18))
        pygame.draw.rect(surface, (53, 38, 29), (x + 19, y - 5, 10, 21))

    def _settlement(self, surface, camera, seconds):
        base_positions = [
            (420, 420),
            (590, 400),
            (755, 430),
            (1100, 410),
            (1270, 440),
            (515, 650),
            (700, 680),
            (1125, 660),
            (1320, 680),
        ]
        tint = {
            1: (99, 69, 45),
            2: (88, 80, 68),
            3: (119, 72, 49),
            4: (72, 67, 47),
            5: (89, 96, 99),
            6: (104, 56, 39),
            7: (78, 58, 104),
        }[self.region]
        for index, (wx, wy) in enumerate(base_positions):
            x = int(wx - camera.x)
            y = int(wy - camera.y)
            self._house(surface, x, y, 0.86 + (index % 3) * 0.08, tint)

    def _landmark(self, surface, camera, seconds):
        x = int(900 - camera.x)
        y = int(315 - camera.y)
        accent = {
            1: (70, 224, 235),
            2: (221, 205, 163),
            3: (225, 82, 92),
            4: (84, 210, 139),
            5: (190, 218, 231),
            6: (245, 137, 69),
            7: (158, 116, 255),
        }[self.region]

        if self.region == 1:
            # Timber longhouse / village hall.
            pygame.draw.rect(surface, (101, 68, 45), (x - 110, y - 40, 220, 100), border_radius=8)
            pygame.draw.polygon(surface, (61, 43, 34), [(x - 130, y - 40), (x, y - 118), (x + 130, y - 40)])
        elif self.region == 2:
            # Castle.
            pygame.draw.rect(surface, (83, 83, 80), (x - 140, y - 90, 280, 170))
            for dx in (-125, -65, 65, 125):
                pygame.draw.rect(surface, (108, 105, 96), (x + dx - 25, y - 125, 50, 205))
            pygame.draw.rect(surface, (25, 28, 30), (x - 33, y + 5, 66, 75), border_radius=18)
        elif self.region == 3:
            # City square + arena.
            pygame.draw.circle(surface, (102, 63, 45), (x, y), 145, 16)
            pygame.draw.circle(surface, accent, (x, y), 118, 3)
        elif self.region == 4:
            # Large temple.
            pygame.draw.rect(surface, (45, 69, 53), (x - 120, y - 55, 240, 120), border_radius=8)
            pygame.draw.polygon(surface, (30, 52, 40), [(x - 145, y - 55), (x, y - 145), (x + 145, y - 55)])
            for dx in (-70, 0, 70):
                pygame.draw.line(surface, accent, (x + dx, y - 45), (x + dx, y + 55), 6)
        elif self.region == 5:
            pygame.draw.rect(surface, (98, 109, 116), (x - 145, y - 80, 290, 150))
            pygame.draw.polygon(surface, (160, 180, 190), [(x - 150, y - 80), (x, y - 155), (x + 150, y - 80)])
        elif self.region == 6:
            pygame.draw.rect(surface, (74, 43, 33), (x - 160, y - 95, 320, 185), border_radius=18)
            for dx in (-100, 100):
                pygame.draw.rect(surface, (35, 29, 27), (x + dx - 28, y - 150, 56, 235))
            glow = 50 + int((math.sin(seconds * 5) + 1) * 20)
            pygame.draw.circle(surface, (245, 80 + glow, 42), (x, y + 10), 48)
        else:
            pygame.draw.polygon(surface, (51, 37, 72), [(x - 160, y + 90), (x - 90, y - 100), (x, y - 170), (x + 90, y - 100), (x + 160, y + 90)])
            pygame.draw.circle(surface, accent, (x, y - 20), 82, 7)
            pygame.draw.circle(surface, (22, 17, 36), (x, y - 20), 67)

    def _consequence(self, surface, camera, seconds):
        consequence = self.profile.get("v26_consequences", {}).get(str(self.region))
        if not consequence:
            return
        for pos in self.braziers:
            x = int(pos.x - camera.x)
            y = int(pos.y - camera.y)
            if consequence == "proteger":
                pygame.draw.line(surface, (82, 55, 34), (x, y), (x, y - 22), 4)
                flame = 7 + int(math.sin(seconds * 8 + x) * 2)
                pygame.draw.circle(surface, (245, 132, 55), (x, y - 28), flame)
                pygame.draw.line(surface, (120, 109, 92), (x - 22, y + 10), (x + 22, y + 10), 6)
            else:
                pygame.draw.circle(surface, (70, 224, 235), (x, y - 10), 13, 2)
                pygame.draw.line(surface, (70, 224, 235), (x - 10, y - 10), (x + 10, y - 10), 2)

    def draw_foreground(self, surface, world, seconds):
        # Power particles, cape/hair motion cues and stylized impact traces.
        for index, ally in enumerate(world.engine.ally_names()[:6]):
            pos = world._ally_pos(index)
            x = int(pos.x - world.camera.x)
            y = int(pos.y - world.camera.y)
            if not (-60 < x < 1340 and -80 < y < 800):
                continue
            color = {
                "Thorvald": (92, 184, 255),
                "Aurel": (245, 220, 115),
                "Kaion": (113, 224, 232),
                "Brenor": (245, 137, 69),
                "Eiran": (84, 210, 139),
                "Noctar": (158, 116, 255),
            }.get(ally, (70, 224, 235))
            for dot in range(3):
                angle = seconds * (0.9 + dot * 0.17) + index + dot * 2.1
                px = x + math.cos(angle) * (24 + dot * 6)
                py = y - 9 + math.sin(angle) * (17 + dot * 4)
                pygame.draw.circle(surface, color, (int(px), int(py)), 2)

        # Warm local lights from village windows.
        glow = pygame.Surface((1280, 720), pygame.SRCALPHA)
        for wx, wy in ((590, 400), (1100, 410), (700, 680), (1320, 680)):
            x = int(wx - world.camera.x)
            y = int(wy - world.camera.y)
            if 0 < x < 1280 and 0 < y < 720:
                pygame.draw.circle(glow, (244, 178, 84, 20), (x, y), 55)
        surface.blit(glow, (0, 0))
