import math
import random

import pygame


REGIONS = {
    1: {
        "ground": (17, 31, 30),
        "earth": (43, 52, 45),
        "detail": (28, 61, 52),
        "accent": (70, 224, 235),
        "weather": "rain",
        "landmark": "bridge",
    },
    2: {
        "ground": (35, 37, 39),
        "earth": (66, 61, 52),
        "detail": (87, 82, 70),
        "accent": (221, 205, 163),
        "weather": "fog",
        "landmark": "gate",
    },
    3: {
        "ground": (48, 37, 31),
        "earth": (91, 65, 46),
        "detail": (122, 80, 50),
        "accent": (225, 82, 92),
        "weather": "embers",
        "landmark": "arena",
    },
    4: {
        "ground": (14, 30, 25),
        "earth": (31, 49, 38),
        "detail": (22, 65, 46),
        "accent": (84, 210, 139),
        "weather": "ravens",
        "landmark": "totems",
    },
    5: {
        "ground": (49, 61, 67),
        "earth": (86, 96, 101),
        "detail": (184, 203, 214),
        "accent": (190, 218, 231),
        "weather": "snow",
        "landmark": "ruins",
    },
    6: {
        "ground": (39, 27, 24),
        "earth": (70, 43, 34),
        "detail": (119, 52, 31),
        "accent": (245, 137, 69),
        "weather": "ash",
        "landmark": "forge",
    },
    7: {
        "ground": (22, 18, 39),
        "earth": (47, 35, 65),
        "detail": (86, 55, 118),
        "accent": (158, 116, 255),
        "weather": "portal",
        "landmark": "portal",
    },
}


class WorldArt:
    def __init__(self, chapter, world_size=(1800, 1080)):
        self.chapter = chapter
        self.config = REGIONS.get(chapter, REGIONS[1])
        self.world_w, self.world_h = world_size
        self.rng = random.Random(9100 + chapter)
        self.decor = self._build_decor()

    def _build_decor(self):
        items = []
        # Use authored clusters instead of a uniform random scatter. The
        # deterministic anchors keep roads/villages readable and make each
        # biome feel composed rather than procedurally noisy.
        kinds = {
            1: ["pine", "pine", "grass", "rock", "puddle"],
            2: ["dead_tree", "fogstone", "bone", "rock"],
            3: ["stake", "banner", "torch", "rock"],
            4: ["pine", "mushroom", "raven_post", "rock"],
            5: ["snow_pine", "snow_pine", "ice", "rock", "bones"],
            6: ["basalt", "ember_pit", "anvil", "rock"],
            7: ["obelisk", "crystal", "rune", "rock"],
        }[self.chapter]
        anchors = (
            (180, 210), (470, 185), (760, 250),
            (1080, 180), (1450, 250), (1710, 190),
            (220, 820), (520, 900), (820, 840),
            (1130, 910), (1480, 820), (1710, 930),
            (260, 1450), (600, 1510), (960, 1420),
            (1320, 1530), (1640, 1460),
            (330, 1900), (820, 1880), (1370, 1920),
        )
        for cluster, (ax, ay) in enumerate(anchors):
            for member in range(3):
                angle = (
                    cluster * 1.73
                    + member * 2.15
                    + self.chapter * 0.41
                )
                radius = 26 + member * 34 + (cluster % 3) * 9
                wx = int(ax + math.cos(angle) * radius)
                wy = int(ay + math.sin(angle) * radius)
                if 45 <= wx <= self.world_w - 45 and 80 <= wy <= self.world_h - 45:
                    items.append(
                        (
                            kinds[(cluster + member) % len(kinds)],
                            wx,
                            wy,
                            0.78 + ((cluster + member) % 5) * 0.11,
                        )
                    )
        return items

    def draw(self, surface, camera, seconds):
        cfg = self.config
        surface.fill(cfg["ground"])
        self._terrain_patches(surface, camera)
        self._path(surface, camera)
        self._landmark(surface, camera, seconds)

        for kind, wx, wy, scale in sorted(
            self.decor,
            key=lambda item: item[2],
        ):
            x = int(wx - camera.x)
            y = int(wy - camera.y)
            if -100 < x < 1380 and -120 < y < 820:
                self._decor(surface, kind, x, y, scale, seconds)

        self._weather(surface, seconds)
        self._vignette(surface)

    def draw_overlay(self, surface, camera, seconds):
        # Quando existe tilemap real, o procedural entra apenas como
        # camada cinematográfica. Isso evita árvores e pedras vetoriais
        # gigantes competindo com os tiles.
        self._travel_overlay(
            surface,
            camera,
            seconds,
        )
        self._landmark(
            surface,
            camera,
            seconds,
        )
        self._weather(
            surface,
            seconds,
        )
        self._vignette(
            surface
        )

    def draw_obstacle(self, surface, rect, camera):
        x = int(rect.centerx - camera.x)
        y = int(rect.centery - camera.y)
        w = max(28, int(rect.width * 0.46))
        h = max(24, int(rect.height * 0.40))
        cfg = self.config

        if self.chapter in (1, 4, 5):
            trunk = (67, 49, 35)
            pygame.draw.rect(
                surface,
                trunk,
                (x - 8, y - 8, 16, h + 12),
                border_radius=4,
            )
            leaf = (
                (34, 65, 48)
                if self.chapter != 5
                else (138, 158, 166)
            )
            pygame.draw.polygon(
                surface,
                leaf,
                [
                    (x, y - h),
                    (x - w, y + h // 3),
                    (x + w, y + h // 3),
                ],
            )
            pygame.draw.polygon(
                surface,
                leaf,
                [
                    (x, y - h // 2),
                    (x - int(w * 0.8), y + h // 2),
                    (x + int(w * 0.8), y + h // 2),
                ],
            )
            return

        stone = cfg["earth"]
        pygame.draw.ellipse(
            surface,
            (8, 12, 17),
            (x - w, y + h // 3, w * 2, h),
        )
        pygame.draw.polygon(
            surface,
            stone,
            [
                (x - w, y + h // 2),
                (x - int(w * 0.55), y - h // 2),
                (x, y - h),
                (x + int(w * 0.75), y - h // 3),
                (x + w, y + h // 2),
            ],
        )
        pygame.draw.line(
            surface,
            cfg["detail"],
            (x - w // 2, y),
            (x + w // 3, y - h // 3),
            2,
        )

    def _terrain_patches(self, surface, camera):
        cfg = self.config
        for index in range(26):
            wx = (index * 233 + self.chapter * 91) % self.world_w
            wy = (index * 157 + self.chapter * 67) % self.world_h
            x = int(wx - camera.x)
            y = int(wy - camera.y)
            rx = 90 + (index * 19) % 110
            ry = 45 + (index * 13) % 70
            pygame.draw.ellipse(
                surface,
                cfg["earth"],
                (x - rx, y - ry, rx * 2, ry * 2),
            )

    def _path(self, surface, camera):
        cfg = self.config
        points = [
            (-100 - camera.x, 610 - camera.y),
            (300 - camera.x, 540 - camera.y),
            (740 - camera.x, 590 - camera.y),
            (1180 - camera.x, 480 - camera.y),
            (1900 - camera.x, 520 - camera.y),
        ]
        pts = [(int(x), int(y)) for x, y in points]
        if len(pts) >= 2:
            pygame.draw.lines(
                surface,
                cfg["earth"],
                False,
                pts,
                115,
            )
            pygame.draw.lines(
                surface,
                cfg["detail"],
                False,
                pts,
                3,
            )

    def _travel_overlay(self, surface, camera, seconds):
        """Adds restrained authored travel cues over the TMX world."""
        cfg = self.config
        layer = pygame.Surface((1280, 720), pygame.SRCALPHA)

        # Main road: dark shoulder + warm compacted center.
        route = [
            (-80 - camera.x, 612 - camera.y),
            (300 - camera.x, 548 - camera.y),
            (740 - camera.x, 590 - camera.y),
            (1180 - camera.x, 486 - camera.y),
            (1900 - camera.x, 524 - camera.y),
        ]
        pts = [(int(x), int(y)) for x, y in route]
        pygame.draw.lines(
            layer,
            (*cfg["earth"], 42),
            False,
            pts,
            46,
        )
        pygame.draw.lines(
            layer,
            (*cfg["detail"], 58),
            False,
            pts,
            3,
        )

        # Region 1 gains a readable river and timber crossing without
        # covering gameplay objects. Other regions receive dry creek/rift.
        river_y = 392
        if self.chapter == 1:
            wave = int(math.sin(seconds * 1.8) * 3)
            water = [
                (0, river_y - int(camera.y)),
                (1280, river_y + 28 - int(camera.y)),
            ]
            pygame.draw.line(
                layer,
                (24, 82, 103, 62),
                water[0],
                water[1],
                54,
            )
            pygame.draw.line(
                layer,
                (83, 179, 196, 74),
                (0, water[0][1] - 10 + wave),
                (1280, water[1][1] - 10 + wave),
                2,
            )
            bx = int(900 - camera.x)
            by = int(river_y + 13 - camera.y)
            for step in range(-4, 5):
                plank = pygame.Rect(
                    bx + step * 22 - 9,
                    by - 34,
                    18,
                    68,
                )
                pygame.draw.rect(
                    layer,
                    (111, 76, 45, 220),
                    plank,
                    border_radius=3,
                )
                pygame.draw.line(
                    layer,
                    (171, 126, 70, 190),
                    plank.topleft,
                    plank.topright,
                    2,
                )
            for side in (-1, 1):
                rx = bx + side * 106
                pygame.draw.line(
                    layer,
                    (55, 39, 28, 230),
                    (rx, by - 36),
                    (rx, by + 38),
                    4,
                )
        elif self.chapter in {2, 5, 7}:
            rift_y = int(405 - camera.y)
            pygame.draw.line(
                layer,
                (*cfg["detail"], 32),
                (-20, rift_y),
                (1300, rift_y + 22),
                18,
            )
            pygame.draw.line(
                layer,
                (*cfg["accent"], 34),
                (-20, rift_y - 2),
                (1300, rift_y + 20),
                2,
            )

        surface.blit(layer, (0, 0))

    def _landmark(self, surface, camera, seconds):
        kind = self.config["landmark"]
        x = int(900 - camera.x)
        y = int(230 - camera.y)
        accent = self.config["accent"]

        # Every region gets a distinct silhouette and ground footprint so
        # landmarks work as navigation anchors, not generic decoration.
        shadow = pygame.Surface((360, 210), pygame.SRCALPHA)
        pygame.draw.ellipse(
            shadow,
            (0, 0, 0, 70),
            (10, 120, 340, 65),
        )
        surface.blit(
            shadow,
            (x - 180, y - 105),
        )

        if kind == "bridge":
            for step in range(8):
                rect = pygame.Rect(
                    x - 180 + step * 46,
                    y + step % 2 * 3,
                    39,
                    68,
                )
                pygame.draw.rect(surface, (93, 67, 44), rect, border_radius=5)
            pygame.draw.line(surface, (55, 41, 30), (x - 190, y), (x + 190, y), 5)
            return

        if kind == "gate":
            stone = (76, 71, 61)
            edge = (122, 113, 91)
            for side in (-1, 1):
                px = x + side * 102
                pygame.draw.rect(
                    surface,
                    (48, 46, 43),
                    (px - 25, y - 78, 50, 196),
                    border_radius=5,
                )
                for course in range(5):
                    block = pygame.Rect(
                        px - 21 + (course % 2) * 3,
                        y - 70 + course * 34,
                        42,
                        28,
                    )
                    pygame.draw.rect(
                        surface,
                        stone,
                        block,
                        border_radius=3,
                    )
                    pygame.draw.rect(
                        surface,
                        edge,
                        block,
                        1,
                        border_radius=3,
                    )
                pygame.draw.polygon(
                    surface,
                    stone,
                    [
                        (px - 34, y - 78),
                        (px, y - 112),
                        (px + 34, y - 78),
                    ],
                )
            pygame.draw.arc(
                surface,
                edge,
                (x - 105, y - 128, 210, 170),
                0,
                math.pi,
                12,
            )
            pygame.draw.circle(
                surface,
                accent,
                (x, y - 86),
                8 + int((math.sin(seconds * 2) + 1) * 2),
                2,
            )
            return

        if kind == "arena":
            pygame.draw.circle(surface, (112, 77, 51), (x, y), 145, 18)
            for a in range(0, 360, 30):
                ang = math.radians(a)
                px = x + math.cos(ang) * 160
                py = y + math.sin(ang) * 160
                pygame.draw.line(surface, (71, 51, 38), (px, py), (px, py - 48), 7)
            return

        if kind == "totems":
            for dx in (-90, 0, 90):
                pygame.draw.rect(surface, (70, 54, 41), (x + dx - 12, y - 75, 24, 130))
                pygame.draw.circle(surface, accent, (x + dx, y - 36), 7)
            return

        if kind == "ruins":
            pygame.draw.rect(surface, (104, 113, 117), (x - 125, y - 40, 250, 35))
            pygame.draw.rect(surface, (104, 113, 117), (x - 115, y - 40, 32, 120))
            pygame.draw.rect(surface, (104, 113, 117), (x + 83, y - 40, 32, 120))
            return

        if kind == "forge":
            pygame.draw.rect(surface, (71, 50, 40), (x - 120, y - 80, 240, 170), border_radius=18)
            pygame.draw.rect(surface, (24, 18, 16), (x - 55, y - 25, 110, 85), border_radius=12)
            glow = 30 + int((math.sin(seconds * 6) + 1) * 15)
            pygame.draw.circle(surface, (245, 94 + glow, 42), (x, y + 10), 38)
            return

        if kind == "portal":
            pulse = 92 + int(math.sin(seconds * 2.4) * 8)
            pygame.draw.circle(surface, accent, (x, y), pulse, 8)
            pygame.draw.circle(surface, (35, 21, 61), (x, y), pulse - 15)
            for i in range(10):
                a = seconds + i * math.tau / 10
                px = x + math.cos(a) * (pulse + 18)
                py = y + math.sin(a) * (pulse + 18)
                pygame.draw.circle(surface, accent, (int(px), int(py)), 4)

    def _decor(self, surface, kind, x, y, scale, seconds):
        cfg = self.config
        accent = cfg["accent"]
        s = scale

        if kind in ("pine", "snow_pine", "dead_tree"):
            trunk = (67, 49, 35)
            shadow_w = max(18, int(38 * s))
            pygame.draw.ellipse(
                surface,
                (7, 12, 12),
                (x - shadow_w // 2, y + 8, shadow_w, 10),
            )
            pygame.draw.rect(
                surface,
                trunk,
                (
                    x - max(3, int(4 * s)),
                    y - int(18 * s),
                    max(6, int(8 * s)),
                    int(36 * s),
                ),
                border_radius=2,
            )
            if kind == "dead_tree":
                pygame.draw.line(
                    surface,
                    trunk,
                    (x, y - int(10 * s)),
                    (x - int(18 * s), y - int(38 * s)),
                    max(3, int(4 * s)),
                )
                pygame.draw.line(
                    surface,
                    trunk,
                    (x, y - int(7 * s)),
                    (x + int(16 * s), y - int(31 * s)),
                    max(3, int(4 * s)),
                )
                pygame.draw.line(
                    surface,
                    (92, 69, 48),
                    (x - int(17 * s), y - int(37 * s)),
                    (x - int(24 * s), y - int(44 * s)),
                    2,
                )
            else:
                base = (
                    (34, 72, 50)
                    if kind == "pine"
                    else (176, 194, 201)
                )
                dark = tuple(max(0, c - 24) for c in base)
                light = tuple(min(255, c + 18) for c in base)
                for tier, width in ((0, 25), (13, 21), (25, 15)):
                    top = y - int((48 + tier) * s)
                    bottom = y - int((4 + tier) * s)
                    pygame.draw.polygon(
                        surface,
                        dark,
                        [
                            (x, top),
                            (x - int(width * s), bottom),
                            (x + int(width * s), bottom),
                        ],
                    )
                    pygame.draw.line(
                        surface,
                        light,
                        (x, top + int(5 * s)),
                        (x - int((width - 5) * s), bottom - int(3 * s)),
                        2,
                    )
            return

        if kind in ("rock", "basalt", "ice", "fogstone"):
            color = {
                "rock": cfg["earth"],
                "basalt": (55, 48, 47),
                "ice": (154, 186, 199),
                "fogstone": (91, 88, 79),
            }[kind]
            pygame.draw.polygon(
                surface,
                color,
                [(x - 14, y + 9), (x - 8, y - 10), (x + 4, y - 15), (x + 16, y + 8)],
            )
            return

        if kind in ("torch", "ember_pit"):
            pygame.draw.line(surface, (83, 58, 38), (x, y), (x, y - 24), 4)
            pygame.draw.circle(surface, (245, 117, 52), (x, y - 29), 6 + int(math.sin(seconds*8+x)*2))
            return

        if kind in ("rune", "obelisk", "bone", "bones", "stake", "anvil", "banner", "raven_post"):
            pygame.draw.line(surface, cfg["detail"], (x, y + 14), (x, y - 24), max(3, int(5*s)))
            pygame.draw.circle(surface, accent, (x, y - 15), 3)
            return

        if kind == "crystal":
            pygame.draw.polygon(surface, accent, [(x, y - 19), (x - 8, y + 9), (x + 8, y + 9)])
            return

        if kind == "puddle":
            pygame.draw.ellipse(surface, (29, 62, 70), (x - 22, y - 6, 44, 12))
            return

        if kind == "grass":
            for dx in (-7, 0, 7):
                pygame.draw.line(surface, (49, 83, 56), (x + dx, y), (x + dx - 3, y - 12), 2)
            return

        if kind == "mushroom":
            pygame.draw.line(surface, (210, 198, 169), (x, y), (x, y - 10), 2)
            pygame.draw.circle(surface, (128, 68, 83), (x, y - 12), 5)

    def _weather(self, surface, seconds):
        weather = self.config["weather"]
        accent = self.config["accent"]
        layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        if weather == "rain":
            for i in range(70):
                x = (i * 73 + int(seconds * 420)) % 1320 - 20
                y = (i * 137 + int(seconds * 610)) % 760 - 20
                pygame.draw.line(layer, (150, 205, 220, 85), (x, y), (x - 7, y + 20), 1)

        elif weather == "fog":
            for i in range(8):
                x = (i * 220 + int(seconds * 18)) % 1500 - 160
                pygame.draw.ellipse(layer, (190, 190, 180, 22), (x, 130 + (i%3)*150, 420, 130))

        elif weather in ("embers", "ash"):
            color = (250, 121, 53, 130) if weather == "embers" else (170, 156, 147, 80)
            for i in range(35):
                x = (i * 97 + int(seconds * 42)) % 1280
                y = 720 - ((i * 61 + int(seconds * 65)) % 760)
                pygame.draw.circle(layer, color, (x, y), 2)

        elif weather == "snow":
            for i in range(55):
                x = (i * 101 + int(seconds * 25)) % 1280
                y = (i * 67 + int(seconds * 42)) % 720
                pygame.draw.circle(layer, (235, 245, 250, 130), (x, y), 2 + i % 2)

        elif weather == "ravens":
            for i in range(7):
                x = (i * 190 + int(seconds * 55)) % 1450 - 90
                y = 120 + (i % 3) * 80
                pygame.draw.arc(layer, (15, 15, 20, 180), (x, y, 18, 10), 0, math.pi, 2)
                pygame.draw.arc(layer, (15, 15, 20, 180), (x + 16, y, 18, 10), 0, math.pi, 2)

        elif weather == "portal":
            for i in range(28):
                a = seconds * 0.8 + i * 1.73
                x = int(640 + math.cos(a) * (200 + i * 9))
                y = int(360 + math.sin(a * 1.3) * (100 + i * 4))
                pygame.draw.circle(layer, (*accent, 90), (x, y), 2)

        surface.blit(layer, (0, 0))

    @staticmethod
    def _vignette(surface):
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for index in range(8):
            alpha = 8 + index * 7
            rect = pygame.Rect(index * 18, index * 13, 1280 - index * 36, 720 - index * 26)
            pygame.draw.rect(overlay, (0, 0, 0, alpha), rect, width=18)
        surface.blit(overlay, (0, 0))
