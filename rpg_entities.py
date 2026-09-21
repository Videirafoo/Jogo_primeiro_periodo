import math
import random

import pygame

from character_visuals import draw_boss_aura


INK = (236, 242, 248)
MUTED = (158, 174, 190)
RED = (225, 82, 92)
GOLD = (231, 190, 93)
CYAN = (70, 224, 235)
GREEN = (84, 210, 139)
VIOLET = (158, 116, 255)


ARCHETYPES = {
    "wolf": {
        "name": "Lobo de Ferro",
        "hp": 1.0,
        "speed": 1.15,
        "damage": 1.0,
        "color": (82, 94, 108),
    },
    "raider": {
        "name": "Saqueador de Valdrak",
        "hp": 1.35,
        "speed": 0.82,
        "damage": 1.35,
        "color": (120, 78, 67),
    },
    "raven": {
        "name": "Corvo Sombrio",
        "hp": 0.75,
        "speed": 1.42,
        "damage": 0.82,
        "color": (73, 62, 94),
    },
}


BOSSES = {
    1: "Ulfgar, o Caçador da Chuva",
    2: "Mork, Guardião dos Ossos",
    3: "Hroth, Campeão do Machado",
    4: "Veyra, Senhora dos Corvos",
    5: "Fenrik, Alfa de Ferro",
    6: "Surtan, Mestre da Forja",
    7: "Nidh, Sentinela da Última Porta",
}


NPCS = {
    1: (
        "Edda, a Vidente",
        [
            "Valdrak não recompensa pressa. Observe as runas e escute a chuva.",
            "Os três caminhos são reais. O que você escolhe muda quem caminhará com você.",
        ],
    ),
    2: (
        "Orm, o Ossário",
        [
            "O portão responde a coragem, mas também a inteligência.",
            "Um guardião protege as runas. Derrube-o antes de decidir seu destino.",
        ],
    ),
    3: (
        "Sigrun, Escudeira",
        [
            "Na arena, sobreviver não basta. Aprenda quando atacar e quando recuar.",
            "Seu Pulso de Código atravessa armaduras que espada nenhuma entende.",
        ],
    ),
    4: (
        "Hilda dos Corvos",
        [
            "Nem todo som no bosque pertence a um animal.",
            "Os corvos veem escolhas que nós ainda não fizemos.",
        ],
    ),
    5: (
        "Torsten, Ferreiro Errante",
        [
            "Lobos de ferro caçam em grupo. Quebre a formação deles com seu pulso.",
            "Fragmentos de Valdrak podem fortalecer sua jornada.",
        ],
    ),
    6: (
        "Yrsa da Forja",
        [
            "Fogo e tecnologia não são opostos. Ambos transformam matéria.",
            "Guarde energia para o mestre da forja.",
        ],
    ),
    7: (
        "A Voz da Porta",
        [
            "Você chegou longe demais para ser apenas um sonhador.",
            "O último guardião protege a escolha que definirá o que Valdrak significa.",
        ],
    ),
}


class EnemyActor:
    def __init__(
        self,
        pos,
        chapter,
        rng,
        archetype="wolf",
        boss=False,
    ):
        self.pos = pygame.Vector2(pos)
        self.chapter = chapter
        self.rng = rng
        self.archetype = archetype
        self.boss = boss

        data = ARCHETYPES[archetype]
        multiplier = 2.9 if boss else 1.0

        self.name = (
            BOSSES.get(chapter, "Guardião de Valdrak")
            if boss
            else data["name"]
        )
        self.radius = 35 if boss else 24
        self.max_hp = int(
            (35 + chapter * 7)
            * data["hp"]
            * multiplier
        )
        self.hp = self.max_hp
        self.speed = (
            (60 + chapter * 6)
            * data["speed"]
            * (0.88 if boss else 1.0)
        )
        self.damage = int(
            (8 + chapter)
            * data["damage"]
            * (1.35 if boss else 1.0)
        )
        self.color = data["color"]
        self.attack_cd = 0.0
        self.hit_flash = 0.0
        self.wander_angle = rng.uniform(0, math.tau)
        self.dead = False

    def update(self, dt, player_pos):
        if self.dead:
            return

        self.attack_cd = max(0.0, self.attack_cd - dt)
        self.hit_flash = max(0.0, self.hit_flash - dt)

        delta = player_pos - self.pos
        distance = delta.length()

        if distance > 1:
            if distance < (520 if self.boss else 390):
                direction = delta.normalize()
                self.pos += direction * self.speed * dt
            else:
                self.wander_angle += dt * 0.65
                direction = pygame.Vector2(
                    math.cos(self.wander_angle),
                    math.sin(self.wander_angle),
                )
                self.pos += direction * self.speed * 0.16 * dt

    def hit(self, damage):
        if self.dead:
            return False

        self.hp -= damage
        self.hit_flash = 0.13

        if self.hp <= 0:
            self.dead = True
            return True

        return False

    def draw(self, surface, offset):
        x = int(self.pos.x - offset.x)
        y = int(self.pos.y - offset.y)
        color = INK if self.hit_flash > 0 else self.color
        scale = 1.35 if self.boss else 1.0

        if self.boss:
            draw_boss_aura(
                surface,
                self.chapter,
                (x, y),
                pygame.time.get_ticks() / 1000,
                scale=1.0,
            )

        if self.archetype == "wolf":
            self._draw_wolf(surface, x, y, color, scale)
        elif self.archetype == "raider":
            self._draw_raider(surface, x, y, color, scale)
        else:
            self._draw_raven(surface, x, y, color, scale)

        width = 86 if self.boss else 48
        ratio = max(0, self.hp) / self.max_hp
        bar_x = x - width // 2
        bar_y = y - (66 if self.boss else 40)
        pygame.draw.rect(
            surface,
            (34, 40, 48),
            (bar_x, bar_y, width, 6),
            border_radius=3,
        )
        pygame.draw.rect(
            surface,
            RED if not self.boss else GOLD,
            (bar_x, bar_y, int(width * ratio), 6),
            border_radius=3,
        )

    @staticmethod
    def _draw_wolf(surface, x, y, color, scale):
        w = int(50 * scale)
        h = int(28 * scale)
        pygame.draw.ellipse(
            surface,
            color,
            (x - w // 2, y - h // 3, w, h),
        )
        head = int(15 * scale)
        pygame.draw.circle(
            surface,
            color,
            (x + w // 3, y - h // 2),
            head,
        )
        pygame.draw.circle(
            surface,
            RED,
            (x + w // 3 + 4, y - h // 2 - 2),
            max(2, int(2 * scale)),
        )

    @staticmethod
    def _draw_raider(surface, x, y, color, scale):
        body_w = int(28 * scale)
        body_h = int(42 * scale)
        pygame.draw.rect(
            surface,
            color,
            (x - body_w // 2, y - body_h // 2, body_w, body_h),
            border_radius=max(4, int(7 * scale)),
        )
        pygame.draw.circle(
            surface,
            (192, 159, 132),
            (x, y - int(30 * scale)),
            int(12 * scale),
        )
        pygame.draw.line(
            surface,
            GOLD,
            (x + int(13 * scale), y - int(8 * scale)),
            (x + int(32 * scale), y - int(34 * scale)),
            max(3, int(4 * scale)),
        )

    @staticmethod
    def _draw_raven(surface, x, y, color, scale):
        wing = int(29 * scale)
        pygame.draw.polygon(
            surface,
            color,
            [
                (x, y),
                (x - wing, y - int(13 * scale)),
                (x - int(11 * scale), y + int(14 * scale)),
            ],
        )
        pygame.draw.polygon(
            surface,
            color,
            [
                (x, y),
                (x + wing, y - int(13 * scale)),
                (x + int(11 * scale), y + int(14 * scale)),
            ],
        )
        pygame.draw.circle(
            surface,
            color,
            (x, y - int(8 * scale)),
            int(10 * scale),
        )
        pygame.draw.circle(
            surface,
            VIOLET,
            (x + int(4 * scale), y - int(10 * scale)),
            2,
        )


class NPC:
    def __init__(self, chapter, pos):
        self.chapter = chapter
        self.pos = pygame.Vector2(pos)
        self.name, self.lines = NPCS[chapter]
        self.dialog_index = 0
        self.gifted = False

    @property
    def current_line(self):
        return self.lines[self.dialog_index % len(self.lines)]

    def talk(self):
        line = self.current_line
        self.dialog_index = (
            self.dialog_index + 1
        ) % len(self.lines)
        return line

    def draw(self, surface, offset, accent, near=False):
        x = int(self.pos.x - offset.x)
        y = int(self.pos.y - offset.y)

        pygame.draw.circle(
            surface,
            (11, 17, 24),
            (x, y + 11),
            21,
        )
        pygame.draw.rect(
            surface,
            accent,
            (x - 13, y - 12, 26, 37),
            border_radius=8,
        )
        pygame.draw.circle(
            surface,
            (208, 174, 145),
            (x, y - 23),
            12,
        )
        pygame.draw.line(
            surface,
            GOLD,
            (x + 11, y - 3),
            (x + 27, y - 31),
            4,
        )

        if near:
            pygame.draw.circle(
                surface,
                accent,
                (x, y),
                34,
                2,
            )


class Loot:
    COLORS = {
        "pocao": RED,
        "essencia": CYAN,
        "fragmento": GOLD,
    }

    def __init__(self, pos, kind):
        self.pos = pygame.Vector2(pos)
        self.kind = kind
        self.picked = False
        self.time = random.random() * math.tau

    def draw(self, surface, offset, seconds):
        if self.picked:
            return

        x = int(self.pos.x - offset.x)
        y = int(
            self.pos.y
            - offset.y
            + math.sin(seconds * 3 + self.time) * 4
        )
        color = self.COLORS[self.kind]

        pygame.draw.circle(
            surface,
            (7, 12, 18),
            (x, y + 6),
            15,
        )
        pygame.draw.circle(
            surface,
            color,
            (x, y),
            10,
        )
        pygame.draw.circle(
            surface,
            INK,
            (x, y),
            10,
            1,
        )
