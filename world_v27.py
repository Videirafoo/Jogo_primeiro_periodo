import math
import random

import pygame

from npc_art_v27 import draw_interior_resident


BUILDING_TYPES = (
    "taverna",
    "ferreiro",
    "loja",
    "casa",
    "salão",
)

BUILDING_NAMES = {
    "taverna": "Taverna do Corvo",
    "ferreiro": "Forja da Vila",
    "loja": "Mercado Rúnico",
    "casa": "Casa dos Despertos",
    "salão": "Salão do Jarl",
}

INTERIOR_ROLES = {
    "taverna": "viajante",
    "ferreiro": "ferreiro",
    "loja": "mercador",
    "casa": "curandeira",
    "salão": "guarda",
}

WEATHER = {
    1: "rain",
    2: "fog",
    3: "wind",
    4: "rain",
    5: "snow",
    6: "ash",
    7: "void",
}

SURFACE_FOOTSTEP = {
    1: "footstep_grass",
    2: "footstep_stone",
    3: "footstep_wood",
    4: "footstep_grass",
    5: "footstep_snow",
    6: "footstep_stone",
    7: "footstep_stone",
}


class TownBuilding:
    def __init__(self, region, kind, center, index):
        self.region = region
        self.kind = kind
        self.name = BUILDING_NAMES[kind]
        self.index = index
        self.center = pygame.Vector2(center)
        self.rect = pygame.Rect(0, 0, 150, 102)
        self.rect.center = (int(center[0]), int(center[1]))
        self.door = pygame.Vector2(self.rect.centerx, self.rect.bottom + 18)
        self.color = {
            "taverna": (112, 69, 43),
            "ferreiro": (91, 54, 39),
            "loja": (119, 87, 48),
            "casa": (87, 67, 53),
            "salão": (72, 75, 83),
        }[kind]


class WorldQualityIII:
    def __init__(self, region, profile):
        self.region = region
        self.profile = profile
        self.weather = WEATHER[region]
        self.interior = None
        self.entry_pos = None
        self.interior_notice = ""
        self.ambient_timer = 1.0
        positions = (
            (350, 330),
            (615, 330),
            (1185, 330),
            (1420, 350),
            (920, 600),
        )
        self.buildings = [
            TownBuilding(region, kind, positions[index], index)
            for index, kind in enumerate(BUILDING_TYPES)
        ]

    def collision_rects(self):
        # Door gaps remain passable; collision boxes stop at the threshold.
        rects = []
        for building in self.buildings:
            rect = building.rect.copy()
            rect.height -= 17
            rects.append(rect)
        return rects

    def nearest_door(self, player_pos):
        nearest = min(
            self.buildings,
            key=lambda building: player_pos.distance_to(building.door),
        )
        if player_pos.distance_to(nearest.door) <= 76:
            return nearest
        return None

    def enter(self, building, player_pos):
        self.interior = building
        self.entry_pos = player_pos.copy()
        return {
            "text": f"Entrou em {building.name}.",
            "sfx": {
                "taverna": "tavern",
                "ferreiro": "blacksmith",
                "loja": "village",
                "casa": "door_wood",
                "salão": "door_wood",
            }[building.kind],
        }

    def exit(self):
        building = self.interior
        self.interior = None
        if building:
            return building.door + pygame.Vector2(0, 36)
        return self.entry_pos

    def handle_key(self, key, world):
        if not self.interior:
            return None

        if key in {pygame.K_ESCAPE, pygame.K_e}:
            position = self.exit()
            if position is not None:
                world.player.pos.update(position)
            return "Saiu para a vila.", "door_wood"

        kind = self.interior.kind
        if kind == "taverna" and key == pygame.K_1:
            if world.profile.get("coins", 0) < 8:
                return "Você precisa de 8 moedas para descansar.", "error"
            world.profile["coins"] -= 8
            world.player.health = world.profile["max_health"]
            world.player.energy = world.profile["max_energy"]
            world.combat_v25.stamina = world.profile["max_stamina"]
            return "Você descansou. Vida, energia e stamina recuperadas.", "tavern"

        if kind == "ferreiro" and key == pygame.K_u:
            return "__upgrade_weapon__", "blacksmith"

        if kind == "loja" and key == pygame.K_1:
            if world.profile.get("coins", 0) < 12:
                return "Você precisa de 12 moedas.", "error"
            world.profile["coins"] -= 12
            world.profile["inventory"]["pocao"] += 1
            return "Comprou uma Poção Nórdica por 12 moedas.", "village"

        if kind == "casa" and key == pygame.K_1:
            world.profile["coins"] = world.profile.get("coins", 0) + 3
            return "Um morador compartilha um rumor e 3 moedas antigas.", "voice_low"

        if kind == "salão" and key == pygame.K_1:
            return "O mapa do Jarl marca objetivos importantes da região.", "quest_complete"

        return None

    def movement_multiplier(self):
        return {
            "rain": 0.96,
            "fog": 0.98,
            "wind": 0.98,
            "snow": 0.90,
            "ash": 0.94,
            "void": 0.93,
        }.get(self.weather, 1.0)

    def stamina_drain(self):
        return {
            "snow": 1.8,
            "ash": 1.4,
            "void": 1.0,
        }.get(self.weather, 0.0)

    def footstep_event(self):
        return SURFACE_FOOTSTEP[self.region]

    def update(self, dt, hour):
        self.ambient_timer = max(0.0, self.ambient_timer - dt)
        if self.ambient_timer <= 0:
            self.ambient_timer = 3.7
            if 6 <= hour < 20:
                return "village"
            return "village_night"
        return None

    def draw_exterior(self, surface, camera, fonts, seconds, hour, player_pos):
        night = hour >= 19.5 or hour < 5.5
        for building in self.buildings:
            rect = building.rect.move(-int(camera.x), -int(camera.y))
            if rect.right < -30 or rect.left > 1310 or rect.bottom < -30 or rect.top > 750:
                continue

            pygame.draw.rect(surface, building.color, rect, border_radius=7)
            roof_color = tuple(max(0, c - 30) for c in building.color)
            pygame.draw.polygon(
                surface,
                roof_color,
                [
                    (rect.left - 10, rect.top + 4),
                    (rect.centerx, rect.top - 55),
                    (rect.right + 10, rect.top + 4),
                ],
            )

            door = pygame.Rect(0, 0, 26, 42)
            door.midbottom = (rect.centerx, rect.bottom + 1)
            pygame.draw.rect(surface, (50, 35, 28), door, border_radius=4)
            pygame.draw.circle(surface, (213, 167, 76), (door.right - 6, door.centery), 2)

            window_color = (241, 173, 72) if night else (109, 160, 181)
            for dx in (-42, 42):
                window = pygame.Rect(rect.centerx + dx - 10, rect.centery - 14, 20, 18)
                pygame.draw.rect(surface, window_color, window, border_radius=3)
                pygame.draw.line(surface, (57, 50, 45), window.midtop, window.midbottom, 1)
                pygame.draw.line(surface, (57, 50, 45), window.midleft, window.midright, 1)

            icon = {
                "taverna": "T",
                "ferreiro": "F",
                "loja": "$",
                "casa": "C",
                "salão": "J",
            }[building.kind]
            label = fonts["small"].render(icon, True, (241, 238, 226))
            surface.blit(label, label.get_rect(center=(rect.centerx, rect.top + 18)))

            near = player_pos.distance_to(building.door) <= 76
            if near:
                prompt = fonts["small"].render(
                    f"E — entrar: {building.name}",
                    True,
                    (239, 244, 247),
                )
                box = prompt.get_rect(center=(rect.centerx, rect.bottom + 32)).inflate(16, 8)
                pygame.draw.rect(surface, (6, 10, 16), box, border_radius=8)
                pygame.draw.rect(surface, (231, 190, 93), box, 1, border_radius=8)
                surface.blit(prompt, prompt.get_rect(center=box.center))

            if night:
                for side in (-1, 1):
                    tx = rect.centerx + side * 62
                    ty = rect.bottom + 6
                    flame = 6 + int(math.sin(seconds * 8 + side) * 2)
                    pygame.draw.line(surface, (105, 70, 40), (tx, ty + 14), (tx, ty - 3), 3)
                    pygame.draw.circle(surface, (245, 137, 62), (tx, ty - 8), flame)

    def draw_day_night(self, surface, hour):
        # Smooth dusk/night curve.
        if 6 <= hour <= 18:
            darkness = 0
        elif 18 < hour < 21:
            darkness = int((hour - 18) / 3 * 105)
        elif 4 < hour < 6:
            darkness = int((6 - hour) / 2 * 105)
        else:
            darkness = 105

        if darkness:
            layer = pygame.Surface((1280, 720), pygame.SRCALPHA)
            layer.fill((8, 17, 35, darkness))
            surface.blit(layer, (0, 0))

    def draw_weather(self, surface, seconds):
        rng = random.Random(self.region * 1000 + int(seconds * 7))
        if self.weather == "snow":
            for _ in range(46):
                x = rng.randrange(0, 1280)
                y = rng.randrange(0, 720)
                pygame.draw.circle(surface, (222, 235, 244), (x, y), rng.randint(1, 3))
        elif self.weather == "ash":
            for _ in range(38):
                x = rng.randrange(0, 1280)
                y = rng.randrange(0, 720)
                pygame.draw.circle(surface, (118, 102, 92), (x, y), 2)
        elif self.weather == "fog":
            layer = pygame.Surface((1280, 720), pygame.SRCALPHA)
            for index in range(5):
                y = 80 + index * 130 + int(math.sin(seconds * 0.3 + index) * 30)
                pygame.draw.ellipse(layer, (180, 190, 196, 18), (-120, y, 1520, 170))
            surface.blit(layer, (0, 0))
        elif self.weather == "void":
            for index in range(16):
                x = int((index * 97 + seconds * 18) % 1280)
                y = int((index * 173 + math.sin(seconds + index) * 80) % 720)
                pygame.draw.circle(surface, (151, 91, 218), (x, y), 2)

    def draw_interior(self, surface, fonts, seconds):
        if not self.interior:
            return
        kind = self.interior.kind
        surface.fill((16, 13, 12))
        pygame.draw.rect(surface, (44, 34, 28), (55, 55, 1170, 610), border_radius=20)
        pygame.draw.rect(surface, (116, 82, 54), (55, 55, 1170, 610), 3, border_radius=20)

        title = fonts["title"].render(self.interior.name, True, (239, 235, 222))
        surface.blit(title, (95, 88))

        # Floorboards.
        for y in range(160, 640, 42):
            pygame.draw.line(surface, (72, 53, 41), (80, y), (1200, y), 2)
        for x in range(110, 1200, 110):
            pygame.draw.line(surface, (55, 42, 35), (x, 150), (x, 640), 1)

        if kind == "taverna":
            for x in (300, 640, 980):
                pygame.draw.rect(surface, (92, 61, 40), (x - 70, 340, 140, 52), border_radius=8)
            hint = "1 — descansar por 8 moedas • E/Esc sair"
        elif kind == "ferreiro":
            pygame.draw.rect(surface, (69, 69, 72), (770, 310, 190, 95), border_radius=8)
            pygame.draw.circle(surface, (245, 101, 53), (865, 355), 36)
            hint = "U — melhorar arma • E/Esc sair"
        elif kind == "loja":
            pygame.draw.rect(surface, (96, 64, 41), (300, 310, 680, 72), border_radius=8)
            for x in range(360, 920, 90):
                pygame.draw.circle(surface, (231, 190, 93), (x, 345), 12)
            hint = "1 — comprar Poção por 12 moedas • E/Esc sair"
        elif kind == "casa":
            pygame.draw.rect(surface, (91, 65, 45), (730, 360, 230, 130), border_radius=12)
            hint = "1 — conversar com morador • E/Esc sair"
        else:
            pygame.draw.rect(surface, (79, 59, 43), (520, 280, 260, 180), border_radius=14)
            hint = "1 — consultar mapa do Jarl • E/Esc sair"

        role = INTERIOR_ROLES[kind]
        draw_interior_resident(
            surface,
            (430, 420),
            role,
            seconds,
            {
                "taverna": "Astrid",
                "ferreiro": "Torsten",
                "loja": "Kari",
                "casa": "Liv",
                "salão": "Sten",
            }[kind],
            fonts,
        )
        surface.blit(
            fonts["body"].render(hint, True, (219, 224, 228)),
            (95, 585),
        )
