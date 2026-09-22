import math
import random
import pygame

from progression_v24 import (
    add_and_auto_equip,
    ensure_progression_profile,
    roll_equipment,
    unlock_codex,
)

INK = (238, 243, 248)
MUTED = (156, 170, 185)
GOLD = (231, 190, 93)
CYAN = (70, 224, 235)
GREEN = (84, 210, 139)
RED = (225, 82, 92)
VIOLET = (158, 116, 255)
DARK = (7, 11, 17)

ACTOR_TYPES = {
    "traveler": ("Viajante Perdido", GOLD),
    "patrol": ("Patrulha Viking", RED),
    "animal": ("Cervo de Valdrak", GREEN),
    "caravan": ("Caravana Nórdica", CYAN),
}

SITE_TYPES = (
    "altar",
    "camp",
    "cave",
    "house",
    "temple",
    "dungeon",
)

SITE_LABELS = {
    "altar": "Altar Escondido",
    "camp": "Acampamento Inimigo",
    "cave": "Caverna Rúnica",
    "house": "Casa Abandonada",
    "temple": "Templo Antigo",
    "dungeon": "Masmorra de Valdrak",
}

SITE_COLORS = {
    "altar": VIOLET,
    "camp": RED,
    "cave": (119, 128, 137),
    "house": GOLD,
    "temple": CYAN,
    "dungeon": (182, 88, 88),
}


class LivingActor:
    def __init__(self, kind, pos, seed):
        self.kind = kind
        self.name, self.color = ACTOR_TYPES[kind]
        self.pos = pygame.Vector2(pos)
        self.seed = seed
        self.life = 42.0
        self.angle = random.Random(seed).uniform(0, math.tau)

    def update(self, dt):
        self.life -= dt
        self.angle += dt * 0.45
        if self.kind in {"traveler", "animal", "caravan"}:
            speed = {"traveler": 18, "animal": 34, "caravan": 12}[self.kind]
            self.pos.x += math.cos(self.angle) * speed * dt
            self.pos.y += math.sin(self.angle) * speed * dt

    def draw(self, surface, camera, font, near=False):
        x = int(self.pos.x - camera.x)
        y = int(self.pos.y - camera.y)
        if not (-60 < x < 1340 and -60 < y < 780):
            return
        pygame.draw.ellipse(surface, (0, 0, 0, 90), (x - 20, y + 13, 40, 12))
        if self.kind == "animal":
            pygame.draw.ellipse(surface, self.color, (x - 18, y - 8, 36, 24))
            pygame.draw.circle(surface, self.color, (x + 17, y - 9), 9)
            pygame.draw.line(surface, self.color, (x + 20, y - 16), (x + 26, y - 27), 2)
            pygame.draw.line(surface, self.color, (x + 15, y - 16), (x + 10, y - 27), 2)
        else:
            pygame.draw.circle(surface, (205, 171, 141), (x, y - 19), 9)
            pygame.draw.rect(surface, self.color, (x - 11, y - 10, 22, 30), border_radius=6)
            if self.kind == "patrol":
                pygame.draw.line(surface, GOLD, (x + 11, y), (x + 26, y - 22), 4)
            elif self.kind == "caravan":
                pygame.draw.rect(surface, (102, 70, 43), (x - 31, y + 8, 62, 18), border_radius=4)
        if near:
            label = font.render(f"E — {self.name}", True, INK)
            box = label.get_rect(center=(x, y - 43)).inflate(14, 7)
            pygame.draw.rect(surface, DARK, box, border_radius=7)
            pygame.draw.rect(surface, self.color, box, 1, border_radius=7)
            surface.blit(label, label.get_rect(center=box.center))


class WorldSite:
    def __init__(self, chapter, kind, pos):
        self.chapter = chapter
        self.kind = kind
        self.id = f"site_{chapter}_{kind}"
        self.name = SITE_LABELS[kind]
        self.pos = pygame.Vector2(pos)
        self.color = SITE_COLORS[kind]

    def draw(self, surface, camera, font, seconds, active=False):
        x = int(self.pos.x - camera.x)
        y = int(self.pos.y - camera.y)
        if not (-80 < x < 1360 and -80 < y < 800):
            return
        pulse = 25 + int((math.sin(seconds * 2.6 + self.chapter) + 1) * 3)
        pygame.draw.circle(surface, (0, 0, 0), (x, y + 8), 19)
        if self.kind == "altar":
            pygame.draw.polygon(surface, self.color, [(x, y - 26), (x + 17, y + 16), (x - 17, y + 16)], 3)
        elif self.kind in {"cave", "dungeon"}:
            pygame.draw.arc(surface, self.color, (x - 28, y - 24, 56, 52), math.pi, math.tau, 6)
            pygame.draw.rect(surface, (20, 20, 24), (x - 22, y, 44, 25))
        elif self.kind == "house":
            pygame.draw.rect(surface, (98, 65, 41), (x - 24, y - 8, 48, 33))
            pygame.draw.polygon(surface, self.color, [(x - 31, y - 7), (x, y - 32), (x + 31, y - 7)])
        elif self.kind == "temple":
            pygame.draw.rect(surface, self.color, (x - 25, y - 14, 50, 38), 3)
            for dx in (-15, 0, 15):
                pygame.draw.line(surface, self.color, (x + dx, y - 12), (x + dx, y + 22), 3)
        else:
            pygame.draw.circle(surface, self.color, (x, y), 20, 3)
            pygame.draw.line(surface, self.color, (x - 20, y + 18), (x + 20, y - 18), 3)
        pygame.draw.circle(surface, self.color, (x, y), pulse, 1)
        if active:
            label = font.render(f"E — {self.name}", True, INK)
            box = label.get_rect(center=(x, y - 48)).inflate(14, 7)
            pygame.draw.rect(surface, DARK, box, border_radius=7)
            pygame.draw.rect(surface, self.color, box, 1, border_radius=7)
            surface.blit(label, label.get_rect(center=box.center))


class LivingValdrak:
    def __init__(self, chapter, profile):
        self.chapter = chapter
        self.profile = profile
        ensure_progression_profile(profile)
        self.rng = random.Random(12000 + chapter)
        self.actors = []
        self.event_timer = 8.0
        self.interior = None
        self.puzzle_input = []
        self.message = ""
        self.sites = self._build_sites()

    def _build_sites(self):
        positions = [
            (315, 365),
            (1510, 350),
            (330, 810),
            (1490, 810),
            (900, 240),
            (905, 890),
        ]
        return [
            WorldSite(self.chapter, kind, pos)
            for kind, pos in zip(SITE_TYPES, positions)
        ]

    def nearest(self, player_pos):
        choices = [(player_pos.distance_to(s.pos), s) for s in self.sites]
        choices += [(player_pos.distance_to(a.pos), a) for a in self.actors]
        if not choices:
            return None
        distance, obj = min(choices, key=lambda pair: pair[0])
        return obj if distance <= 88 else None

    def _spawn_actor(self, kind, player_pos):
        angle = self.rng.uniform(0, math.tau)
        distance = self.rng.randint(220, 390)
        pos = player_pos + pygame.Vector2(
            math.cos(angle) * distance,
            math.sin(angle) * distance,
        )
        pos.x = max(90, min(1710, pos.x))
        pos.y = max(90, min(990, pos.y))
        actor = LivingActor(kind, pos, self.rng.randrange(999999))
        self.actors.append(actor)
        return actor

    def update(self, dt, world):
        if self.interior:
            return None
        for actor in self.actors:
            actor.update(dt)
        self.actors = [a for a in self.actors if a.life > 0]

        self.event_timer -= dt
        if self.event_timer > 0:
            return None
        self.event_timer = self.rng.uniform(12.0, 21.0)
        event = self.rng.choice([
            "traveler",
            "patrol",
            "animal",
            "caravan",
            "ambush",
            "rune_storm",
        ])
        self.profile["living_events"] += 1
        if event == "ambush":
            return {
                "kind": "ambush",
                "text": "Emboscada! Guerreiros surgem entre as runas.",
                "count": 2 + self.chapter // 3,
            }
        if event == "rune_storm":
            unlock_codex(self.profile, "runas")
            return {
                "kind": "story",
                "text": "Uma tempestade de runas atravessa o mapa e revela símbolos esquecidos.",
                "sfx": "rune",
            }
        actor = self._spawn_actor(event, world.player.pos)
        return {
            "kind": "story",
            "text": f"{actor.name} apareceu na região.",
            "sfx": "horse" if event == "caravan" else "wind",
        }

    def interact(self, obj, world):
        if isinstance(obj, LivingActor):
            if obj.kind == "traveler":
                world.profile["inventory"]["essencia"] += 1
                unlock_codex(self.profile, "eternos")
                return "O viajante troca uma Essência por uma história sobre Os Eternos.", "rune"
            if obj.kind == "patrol":
                return "A patrulha exige passagem. O conflito parece inevitável.", "shield"
            if obj.kind == "animal":
                world.player.energy = min(world.profile["max_energy"], world.player.energy + 15)
                return "O cervo conduz você por uma trilha segura. +15 Energia.", "forest"
            world.profile["inventory"]["pocao"] += 1
            return "A caravana oferece suprimentos. Você recebe uma Poção Nórdica.", "horse"

        if obj.kind == "altar":
            regions = self.profile["fast_travel_regions"]
            if self.chapter not in regions:
                regions.append(self.chapter)
            unlock_codex(self.profile, "runas")
            return "Altar sincronizado. Esta região agora aceita Fast Travel.", "rune"

        if obj.kind == "camp":
            item = roll_equipment(self.chapter, self.rng, elite=True)
            equipped = add_and_auto_equip(self.profile, item)
            suffix = " e foi equipado automaticamente." if equipped else "."
            return f"Acampamento saqueado: {item['rarity']} {item['name']}{suffix}", "pickup"

        self.interior = obj
        self.puzzle_input = []
        return f"Você entrou em {obj.name}. Procure as runas e resolva o puzzle.", "gate"

    def handle_interior_key(self, key, world):
        if not self.interior:
            return None
        if key == pygame.K_ESCAPE or key == pygame.K_e:
            name = self.interior.name
            self.interior = None
            self.puzzle_input = []
            return f"Você saiu de {name}.", "gate"

        mapping = {
            pygame.K_1: 1,
            pygame.K_2: 2,
            pygame.K_3: 3,
            pygame.K_KP1: 1,
            pygame.K_KP2: 2,
            pygame.K_KP3: 3,
        }
        if key not in mapping:
            return None

        self.puzzle_input.append(mapping[key])
        target = [((self.chapter + i) % 3) + 1 for i in range(3)]
        if len(self.puzzle_input) < 3:
            return f"Runas: {'-'.join(map(str, self.puzzle_input))}", "rune"

        solved = self.puzzle_input == target
        self.puzzle_input = []
        if solved:
            puzzle_id = self.interior.id
            if puzzle_id not in self.profile["puzzles_solved"]:
                self.profile["puzzles_solved"].append(puzzle_id)
                item = roll_equipment(
                    self.chapter,
                    self.rng,
                    boss=self.interior.kind == "dungeon",
                    elite=True,
                )
                add_and_auto_equip(self.profile, item)
                unlock_codex(
                    self.profile,
                    "forja" if self.chapter >= 6 else "valdrak",
                )
                return f"Puzzle resolvido! Encontrou {item['rarity']} {item['name']}.", "victory"
            return "Este puzzle já foi resolvido.", "rune"
        return "Sequência incorreta. As runas se apagam.", "error"

    def draw(self, surface, camera, fonts, seconds, player_pos):
        font = fonts["small"]
        for site in self.sites:
            active = player_pos.distance_to(site.pos) <= 95
            site.draw(surface, camera, font, seconds, active)
        for actor in self.actors:
            actor.draw(
                surface,
                camera,
                font,
                near=player_pos.distance_to(actor.pos) <= 95,
            )

    def draw_interior(self, surface, fonts, accent):
        if not self.interior:
            return
        surface.fill((8, 10, 15))
        pygame.draw.rect(surface, (18, 24, 31), (80, 78, 1120, 560), border_radius=24)
        pygame.draw.rect(surface, accent, (80, 78, 1120, 560), 2, border_radius=24)
        title = fonts["title"].render(self.interior.name, True, INK)
        surface.blit(title, (125, 118))

        for i in range(7):
            x = 170 + i * 145
            pygame.draw.circle(surface, (34, 40, 49), (x, 350), 48)
            pygame.draw.circle(surface, accent, (x, 350), 48, 2)
            pygame.draw.line(surface, accent, (x - 18, 350), (x + 18, 350), 3)
            pygame.draw.line(surface, accent, (x, 332), (x, 368), 3)

        body = fonts["body"].render(
            "Puzzle rúnico: pressione 1, 2 e 3 na sequência correta. E ou Esc sai do interior.",
            True,
            MUTED,
        )
        surface.blit(body, (125, 545))
        current = "-".join(map(str, self.puzzle_input)) or "..."
        prompt = fonts["heading"].render(f"SEQUÊNCIA: {current}", True, GOLD)
        surface.blit(prompt, (125, 590))
