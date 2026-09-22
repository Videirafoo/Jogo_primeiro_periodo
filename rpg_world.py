import math
import random

import pygame

from character_visuals import ALLY_STYLES, draw_ally, draw_dialogue_box
from rpg_entities import EnemyActor, Loot, NPC
from world_art import WorldArt
from sprite_animator import draw_actor
from hud import RPGHUD
from map_loader import MapScene


WORLD_W = 1800
WORLD_H = 1080
PLAYER_SIZE = 42

INK = (236, 242, 248)
MUTED = (158, 174, 190)
DARK = (7, 12, 19)
PANEL = (12, 20, 31)
GREEN = (84, 210, 139)
RED = (225, 82, 92)
CYAN = (70, 224, 235)
GOLD = (231, 190, 93)
VIOLET = (158, 116, 255)


THEMES = {
    1: {
        "ground": (18, 33, 39),
        "path": (42, 56, 54),
        "accent": CYAN,
        "name": "Estrada de Valdrak",
        "ambience": "rain",
    },
    2: {
        "ground": (27, 32, 39),
        "path": (60, 57, 50),
        "accent": GOLD,
        "name": "Portão dos Ossos",
        "ambience": "wind",
    },
    3: {
        "ground": (36, 27, 27),
        "path": (70, 48, 39),
        "accent": RED,
        "name": "Arena Viking",
        "ambience": "fire",
    },
    4: {
        "ground": (18, 35, 31),
        "path": (38, 59, 45),
        "accent": GREEN,
        "name": "Bosque dos Corvos",
        "ambience": "forest",
    },
    5: {
        "ground": (28, 33, 38),
        "path": (53, 58, 61),
        "accent": (182, 202, 218),
        "name": "Caçada dos Lobos de Ferro",
        "ambience": "wind",
    },
    6: {
        "ground": (45, 26, 25),
        "path": (74, 46, 38),
        "accent": (255, 139, 72),
        "name": "Forja dos Eternos",
        "ambience": "fire",
    },
    7: {
        "ground": (26, 20, 43),
        "path": (48, 38, 67),
        "accent": VIOLET,
        "name": "Última Porta",
        "ambience": "portalhum",
    },
}


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def wrap(font, value, max_width):
    words = str(value).split()
    lines = []
    current = ""

    for word in words:
        candidate = word if not current else f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


class Particle:
    def __init__(self, pos, color, rng, speed=150, life=0.55):
        angle = rng.uniform(0, math.tau)
        magnitude = rng.uniform(speed * 0.45, speed)
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(
            math.cos(angle) * magnitude,
            math.sin(angle) * magnitude,
        )
        self.color = color
        self.life = life
        self.max_life = life
        self.radius = rng.randint(2, 5)

    def update(self, dt):
        self.life -= dt
        self.pos += self.vel * dt
        self.vel *= 0.92

    def draw(self, surface, offset):
        if self.life <= 0:
            return
        alpha = int(255 * self.life / self.max_life)
        layer = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(
            layer,
            (*self.color, alpha),
            (6, 6),
            self.radius,
        )
        surface.blit(layer, self.pos - offset - pygame.Vector2(6, 6))


class Enemy:
    def __init__(self, pos, chapter, rng):
        self.pos = pygame.Vector2(pos)
        self.chapter = chapter
        self.radius = 24
        self.max_hp = 35 + chapter * 6
        self.hp = self.max_hp
        self.speed = 62 + chapter * 7
        self.damage = 8 + chapter
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
            if distance < 390:
                direction = delta.normalize()
                self.pos += direction * self.speed * dt
            else:
                self.wander_angle += dt * 0.7
                direction = pygame.Vector2(
                    math.cos(self.wander_angle),
                    math.sin(self.wander_angle),
                )
                self.pos += direction * self.speed * 0.18 * dt

        self.pos.x = clamp(self.pos.x, 45, WORLD_W - 45)
        self.pos.y = clamp(self.pos.y, 45, WORLD_H - 45)

    def hit(self, damage):
        if self.dead:
            return False

        self.hp -= damage
        self.hit_flash = 0.12

        if self.hp <= 0:
            self.dead = True
            return True

        return False

    def draw(self, surface, offset):
        x = int(self.pos.x - offset.x)
        y = int(self.pos.y - offset.y)
        color = INK if self.hit_flash > 0 else (83, 94, 106)

        body = pygame.Rect(x - 25, y - 12, 50, 28)
        pygame.draw.ellipse(surface, color, body)
        pygame.draw.circle(surface, color, (x + 18, y - 13), 15)

        pygame.draw.polygon(
            surface,
            color,
            [(x + 8, y - 29), (x + 13, y - 15), (x + 1, y - 17)],
        )
        pygame.draw.polygon(
            surface,
            color,
            [(x + 28, y - 29), (x + 22, y - 15), (x + 35, y - 17)],
        )
        pygame.draw.circle(surface, RED, (x + 13, y - 13), 2)
        pygame.draw.circle(surface, RED, (x + 23, y - 13), 2)

        ratio = max(0, self.hp) / self.max_hp
        pygame.draw.rect(surface, (35, 42, 50), (x - 24, y - 38, 48, 5), border_radius=2)
        pygame.draw.rect(surface, RED, (x - 24, y - 38, int(48 * ratio), 5), border_radius=2)


class Player:
    def __init__(self, profile):
        self.profile = profile
        self.pos = pygame.Vector2(WORLD_W / 2, WORLD_H / 2)
        self.facing = pygame.Vector2(0, 1)
        self.speed = 250
        self.attack_timer = 0.0
        self.pulse_timer = 0.0
        self.dash_timer = 0.0
        self.invulnerable = 0.0
        self.anim_time = 0.0
        self.auto_target = None
        self.state = "idle"
        self.is_moving = False

        self.profile.setdefault("level", 1)
        self.profile.setdefault("xp", 0)
        self.profile.setdefault("xp_next", 4)
        self.profile.setdefault("max_health", 100)
        self.profile.setdefault("health", self.profile["max_health"])
        self.profile.setdefault("max_energy", 100)
        self.profile.setdefault("energy", self.profile["max_energy"])
        self.profile.setdefault("kills", 0)
        self.profile.setdefault(
            "inventory",
            {
                "pocao": 1,
                "essencia": 1,
                "fragmento": 0,
            },
        )
        self.profile.setdefault("npc_flags", {})

    @property
    def health(self):
        return self.profile["health"]

    @health.setter
    def health(self, value):
        self.profile["health"] = value

    @property
    def energy(self):
        return self.profile["energy"]

    @energy.setter
    def energy(self, value):
        self.profile["energy"] = value

    def rect_at(self, pos=None):
        pos = pos or self.pos
        return pygame.Rect(
            int(pos.x - PLAYER_SIZE / 2),
            int(pos.y - PLAYER_SIZE / 2),
            PLAYER_SIZE,
            PLAYER_SIZE,
        )

    def update(self, dt, keys, obstacles):
        self.anim_time += dt
        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.pulse_timer = max(0.0, self.pulse_timer - dt)
        self.dash_timer = max(0.0, self.dash_timer - dt)
        self.invulnerable = max(0.0, self.invulnerable - dt)

        self.energy = min(
            self.profile["max_energy"],
            self.energy + 13 * dt,
        )

        direction = pygame.Vector2()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1

        if direction.length_squared() == 0 and self.auto_target is not None:
            delta = self.auto_target - self.pos
            if delta.length() > 8:
                direction = delta.normalize()
            else:
                self.auto_target = None

        self.is_moving = bool(direction.length_squared())

        if direction.length_squared():
            direction = direction.normalize()
            self.facing = direction
            self._move(direction * self.speed * dt, obstacles)
        else:
            self.auto_target = (
                None
                if (
                    self.auto_target
                    and self.pos.distance_to(self.auto_target) < 8
                )
                else self.auto_target
            )

        if self.invulnerable > 0:
            self.state = "hurt"
        elif self.pulse_timer > 0:
            self.state = "pulse"
        elif self.attack_timer > 0:
            self.state = "attack"
        elif self.dash_timer > 0.35:
            self.state = "dash"
        elif self.is_moving:
            self.state = "walk"
        else:
            self.state = "idle"

    def _move(self, delta, obstacles):
        test = self.pos.copy()
        test.x += delta.x
        rect = self.rect_at(test)
        if not any(rect.colliderect(obstacle) for obstacle in obstacles):
            self.pos.x = test.x

        test = self.pos.copy()
        test.y += delta.y
        rect = self.rect_at(test)
        if not any(rect.colliderect(obstacle) for obstacle in obstacles):
            self.pos.y = test.y

        self.pos.x = clamp(self.pos.x, 35, WORLD_W - 35)
        self.pos.y = clamp(self.pos.y, 35, WORLD_H - 35)

    def damage(self, amount):
        if self.invulnerable > 0:
            return False

        self.health = max(0, self.health - amount)
        self.invulnerable = 0.7
        return True

    def gain_xp(self, amount=1):
        self.profile["xp"] += amount
        leveled = False

        while self.profile["xp"] >= self.profile["xp_next"]:
            self.profile["xp"] -= self.profile["xp_next"]
            self.profile["level"] += 1
            self.profile["xp_next"] += 3
            self.profile["max_health"] += 8
            self.profile["max_energy"] += 6
            self.health = self.profile["max_health"]
            self.energy = self.profile["max_energy"]
            leveled = True

        return leveled

    def draw(self, surface, offset, accent):
        x = int(self.pos.x - offset.x)
        y = int(self.pos.y - offset.y)
        seconds = pygame.time.get_ticks() / 1000

        rendered = draw_actor(
            surface,
            "player",
            (x, y),
            state=self.state,
            facing=self.facing,
            seconds=seconds,
            tint=accent,
        )

        if not rendered:
            pygame.draw.circle(
                surface,
                accent,
                (x, y),
                22,
            )

        if self.state == "attack":
            pygame.draw.arc(
                surface,
                GOLD,
                pygame.Rect(
                    x - 62,
                    y - 62,
                    124,
                    124,
                ),
                -0.95,
                0.95,
                7,
            )

        if self.state == "pulse":
            radius = int(
                50
                + (0.8 - self.pulse_timer)
                * 185
            )
            pygame.draw.circle(
                surface,
                CYAN,
                (x, y),
                max(10, radius),
                4,
            )

        if self.state == "dash":
            for index in range(3):
                trail = (
                    pygame.Vector2(x, y)
                    - self.facing
                    * (22 + index * 16)
                )
                pygame.draw.circle(
                    surface,
                    accent,
                    (
                        int(trail.x),
                        int(trail.y),
                    ),
                    8 - index * 2,
                    2,
                )


class Shrine:
    def __init__(self, index, pos, choice, available, reason):
        self.index = index
        self.pos = pygame.Vector2(pos)
        self.choice = choice
        self.available = available
        self.reason = reason

    def draw(self, surface, offset, font, small, accent, seconds, near):
        x = int(self.pos.x - offset.x)
        y = int(self.pos.y - offset.y)

        color = accent if self.available else (78, 83, 92)
        pulse = 8 + int((math.sin(seconds * 3 + self.index) + 1) * 4)

        pygame.draw.circle(surface, color, (x, y), 42 + pulse, 2)
        pygame.draw.circle(surface, color, (x, y), 26, 3)
        pygame.draw.line(surface, color, (x, y - 18), (x, y + 18), 3)
        pygame.draw.line(surface, color, (x, y - 5), (x + 14, y + 5), 3)
        pygame.draw.line(surface, color, (x, y + 6), (x - 13, y + 17), 3)

        label = font.render(f"CAMINHO {self.index + 1}", True, color)
        surface.blit(label, label.get_rect(center=(x, y + 67)))

        if near:
            box = pygame.Rect(x - 190, y - 145, 380, 76)
            pygame.draw.rect(surface, (8, 14, 22), box, border_radius=12)
            pygame.draw.rect(surface, color, box, 1, border_radius=12)
            lines = wrap(small, self.choice["text"], 340)
            for line_index, line in enumerate(lines[:2]):
                rendered = small.render(line, True, INK)
                surface.blit(rendered, (box.x + 18, box.y + 13 + line_index * 20))


class RPGWorld:
    def __init__(self, chapter, engine, profile):
        self.chapter = chapter
        self.engine = engine
        self.profile = profile
        self.theme = THEMES.get(chapter["number"], THEMES[1])
        self.rng = random.Random(7000 + chapter["number"])

        self.player = Player(profile)
        self.camera = pygame.Vector2()
        self.particles = []
        self.events = []
        self.selected_choice = None
        self.notice = ""
        self.notice_timer = 0.0
        self.dialogue = None
        self.inventory_open = False
        self.shake_timer = 0.0
        self.shake_strength = 0.0
        self.hit_stop = 0.0
        self.flash_timer = 0.0
        self.ally_cooldown = 0.8
        self.world_art = WorldArt(
            chapter["number"],
            (WORLD_W, WORLD_H),
        )
        self.map_scene = MapScene(
            chapter["number"]
        )
        self.hud = RPGHUD()
        self.step_timer = 0.0

        map_collisions = (
            self.map_scene.collision_rects
            if self.map_scene.available
            else []
        )
        self.obstacles = (
            map_collisions
            or self._build_obstacles()
        )
        self.shrines = self._build_shrines()
        self.enemies = self._build_enemies()
        self.loots = []
        self.npc = NPC(
            chapter["number"],
            (WORLD_W / 2 + 185, WORLD_H / 2 - 105),
        )

        self.chapter_kills_start = profile.get("kills", 0)

    def _build_obstacles(self):
        obstacles = [
            pygame.Rect(0, 0, WORLD_W, 28),
            pygame.Rect(0, WORLD_H - 28, WORLD_W, 28),
            pygame.Rect(0, 0, 28, WORLD_H),
            pygame.Rect(WORLD_W - 28, 0, 28, WORLD_H),
        ]

        for _ in range(14):
            w = self.rng.randint(70, 150)
            h = self.rng.randint(55, 120)
            x = self.rng.randint(120, WORLD_W - 200)
            y = self.rng.randint(130, WORLD_H - 190)

            rect = pygame.Rect(x, y, w, h)
            if rect.collidepoint(WORLD_W / 2, WORLD_H / 2):
                continue
            obstacles.append(rect)

        return obstacles

    def _build_shrines(self):
        positions = [
            (250, 210),
            (WORLD_W - 250, 230),
            (WORLD_W / 2, WORLD_H - 190),
        ]
        shrines = []

        for index, choice in enumerate(self.chapter["choices"]):
            shrines.append(
                Shrine(
                    index,
                    positions[index],
                    choice,
                    self.engine.choice_available(choice),
                    self.engine.availability_reason(choice),
                )
            )

        return shrines

    def _build_enemies(self):
        chapter_number = self.chapter["number"]
        count = 2 + chapter_number // 2
        enemies = []
        archetypes = ["wolf", "raider", "raven"]

        for index in range(count):
            for _attempt in range(30):
                pos = pygame.Vector2(
                    self.rng.randint(180, WORLD_W - 180),
                    self.rng.randint(180, WORLD_H - 180),
                )
                if pos.distance_to(self.player.pos) > 280:
                    archetype = archetypes[
                        (index + chapter_number) % len(archetypes)
                    ]
                    enemies.append(
                        EnemyActor(
                            pos,
                            chapter_number,
                            self.rng,
                            archetype=archetype,
                        )
                    )
                    break

        boss_archetype = archetypes[(chapter_number - 1) % 3]
        boss_pos = pygame.Vector2(
            WORLD_W / 2,
            175 if chapter_number % 2 else WORLD_H - 175,
        )
        enemies.append(
            EnemyActor(
                boss_pos,
                chapter_number,
                self.rng,
                archetype=boss_archetype,
                boss=True,
            )
        )
        return enemies

    def boss(self):
        for enemy in self.enemies:
            if enemy.boss:
                return enemy
        return None

    def boss_alive(self):
        boss = self.boss()
        return bool(boss and not boss.dead)

    def pop_events(self):
        values = list(self.events)
        self.events.clear()
        return values

    def handle_key(self, event):
        if event.key == pygame.K_r:
            self._ally_assist()
            self.ally_cooldown = 2.4
            return

        if event.key in (pygame.K_i, pygame.K_TAB):
            self.inventory_open = not self.inventory_open
            self.events.append("choice")
            return

        if event.key == pygame.K_e:
            if (
                self.npc
                and self.player.pos.distance_to(self.npc.pos) <= 100
            ):
                line = self.npc.talk()
                self.notice = f"{self.npc.name}: {line}"
                self.dialogue = (self.npc.name, line)
                self.notice_timer = 4.2
                self.events.append("rune")

                flag = f"npc_gift_{self.chapter['number']}"
                if not self.profile["npc_flags"].get(flag):
                    self.profile["npc_flags"][flag] = True
                    self.profile["inventory"]["essencia"] += 1
                    self.notice += " • recebeu 1 Essência"
                    self.dialogue = (
                        self.npc.name,
                        line + " Receba também uma Essência Rúnica.",
                    )
                return

            shrine = self.nearest_shrine()
            if shrine and self.player.pos.distance_to(shrine.pos) <= 95:
                if self.boss_alive():
                    self.notice = (
                        "O Guardião de Valdrak ainda protege os caminhos"
                    )
                    self.notice_timer = 2.4
                    self.events.append("error")
                elif shrine.available:
                    self.selected_choice = shrine.index
                    self.events.append("rune")
                else:
                    self.notice = shrine.reason or "Caminho bloqueado"
                    self.notice_timer = 2.0
                    self.events.append("error")
            return

        if event.key == pygame.K_1:
            self.use_item("pocao")
            return

        if event.key == pygame.K_2:
            self.use_item("essencia")
            return

        if event.key == pygame.K_SPACE:
            self.attack()
            return

        if event.key == pygame.K_q:
            self.tech_pulse()
            return

        if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
            self.dash()
    def handle_click(self, point):
        if self.inventory_open:
            return
        world_point = pygame.Vector2(point) + self.camera
        self.player.auto_target = world_point

    def impact_feedback(
        self,
        strength=6.0,
        stop=0.045,
        flash=0.08,
    ):
        self.shake_strength = max(
            self.shake_strength,
            strength,
        )
        self.shake_timer = max(
            self.shake_timer,
            0.18,
        )
        self.hit_stop = max(
            self.hit_stop,
            stop,
        )
        self.flash_timer = max(
            self.flash_timer,
            flash,
        )

    def use_item(self, kind):
        inventory = self.profile["inventory"]
        if inventory.get(kind, 0) <= 0:
            self.notice = "Item indisponível"
            self.notice_timer = 1.4
            self.events.append("error")
            return False

        if kind == "pocao":
            if self.player.health >= self.profile["max_health"]:
                self.notice = "Vida já está cheia"
                self.notice_timer = 1.3
                return False
            inventory[kind] -= 1
            self.player.health = min(
                self.profile["max_health"],
                self.player.health + 35,
            )
            self.notice = "Poção Nórdica • +35 Vida"
            self.notice_timer = 1.8
            self.events.append("heal")
            return True

        if kind == "essencia":
            if self.player.energy >= self.profile["max_energy"]:
                self.notice = "Energia já está cheia"
                self.notice_timer = 1.3
                return False
            inventory[kind] -= 1
            self.player.energy = min(
                self.profile["max_energy"],
                self.player.energy + 45,
            )
            self.notice = "Essência Rúnica • +45 Energia"
            self.notice_timer = 1.8
            self.events.append("tech")
            return True

        return False

    def attack(self):
        if self.player.attack_timer > 0:
            return

        self.player.attack_timer = 0.42
        self.events.append("sword")
        attack_center = self.player.pos + self.player.facing * 55

        for enemy in self.enemies:
            if enemy.dead:
                continue
            if enemy.pos.distance_to(attack_center) <= 90:
                died = enemy.hit(22 + self.profile["level"] * 2)
                self._burst(enemy.pos, GOLD, 10)
                self.impact_feedback(
                    strength=11 if enemy.boss else 6,
                    stop=0.075 if enemy.boss else 0.045,
                    flash=0.11,
                )
                if died:
                    self._enemy_defeated(enemy)

    def tech_pulse(self):
        if self.player.pulse_timer > 0 or self.player.energy < 24:
            if self.player.energy < 24:
                self.notice = "Energia insuficiente"
                self.notice_timer = 1.4
                self.events.append("error")
            return
        self.player.energy -= 24
        self.player.pulse_timer = 0.80
        self.events.append("tech")
        self._burst(self.player.pos, CYAN, 20, speed=210)

        for enemy in self.enemies:
            if enemy.dead:
                continue
            if enemy.pos.distance_to(self.player.pos) <= 155:
                died = enemy.hit(30 + self.profile["level"] * 3)
                self._burst(enemy.pos, CYAN, 12)
                self.impact_feedback(
                    strength=13 if enemy.boss else 8,
                    stop=0.085 if enemy.boss else 0.055,
                    flash=0.13,
                )
                if died:
                    self._enemy_defeated(enemy)

    def dash(self):
        if self.player.dash_timer > 0 or self.player.energy < 15:
            return

        self.player.energy -= 15
        self.player.dash_timer = 0.7
        self.events.append("wind")
        start = self.player.pos.copy()

        for _ in range(5):
            self.player._move(self.player.facing * 24, self.obstacles)

        for step in range(8):
            pos = start.lerp(self.player.pos, step / 7)
            self.particles.append(
                Particle(pos, self.theme["accent"], self.rng, speed=35, life=0.35)
            )
    def _enemy_defeated(self, enemy):
        self.profile["kills"] += 1
        xp_gain = 3 if enemy.boss else 1
        leveled = self.player.gain_xp(xp_gain)
        self.events.append("victory")
        self._burst(
            enemy.pos,
            GOLD if enemy.boss else self.theme["accent"],
            30 if enemy.boss else 18,
        )

        if enemy.boss:
            self.notice = (
                f"{enemy.name} derrotado • caminhos liberados"
            )
            self.notice_timer = 3.2
            self.engine.state["coragem"] = (
                self.engine.state.get("coragem", 0) + 1
            )
            self.loots.append(
                Loot(enemy.pos + pygame.Vector2(25, 0), "fragmento")
            )
            self.loots.append(
                Loot(enemy.pos + pygame.Vector2(-25, 0), "pocao")
            )
            self.loots.append(
                Loot(enemy.pos + pygame.Vector2(0, 25), "essencia")
            )
            self.events.append("thunder")
        else:
            roll = self.rng.random()
            if roll < 0.28:
                kind = "pocao"
            elif roll < 0.58:
                kind = "essencia"
            else:
                kind = "fragmento"
            self.loots.append(Loot(enemy.pos, kind))

        if leveled:
            self.notice = f"Nível {self.profile['level']} alcançado"
            self.notice_timer = 2.2
            self.events.append("tech")

    def _burst(self, pos, color, count, speed=155):
        for _ in range(count):
            self.particles.append(
                Particle(pos, color, self.rng, speed=speed)
            )

    def nearest_shrine(self):
        if not self.shrines:
            return None
        return min(
            self.shrines,
            key=lambda shrine: self.player.pos.distance_to(shrine.pos),
        )

    def _ally_assist(self):
        allies = self.engine.ally_names()
        if not allies:
            return

        targets = [
            enemy
            for enemy in self.enemies
            if (
                not enemy.dead
                and enemy.pos.distance_to(self.player.pos) <= 300
            )
        ]
        if not targets:
            return

        target = min(
            targets,
            key=lambda enemy: enemy.pos.distance_to(self.player.pos),
        )
        ally_name = allies[
            self.profile["kills"] % len(allies)
        ]
        style = ALLY_STYLES.get(ally_name, {})
        power = style.get("power", "Poder Desperto")
        color = style.get("color", CYAN)

        damage = 10 + self.profile["level"] * 2
        died = target.hit(damage)
        self._burst(target.pos, color, 9)
        self.notice = f"{ally_name}: {power}"
        self.notice_timer = 1.0

        sfx = {
            "Thorvald": "thunder",
            "Aurel": "lightning",
            "Kaion": "sword",
            "Brenor": "fire",
            "Eiran": "heal",
            "Noctar": "shadow",
        }.get(ally_name, "rune")
        self.events.append(sfx)
        self.impact_feedback(
            strength=5 if not target.boss else 8,
            stop=0.035,
            flash=0.06,
        )

        if ally_name == "Eiran":
            self.player.health = min(
                self.profile["max_health"],
                self.player.health + 4,
            )

        if died:
            self._enemy_defeated(target)

    def update(self, dt, keys):
        self.notice_timer = max(0.0, self.notice_timer - dt)
        self.shake_timer = max(0.0, self.shake_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)

        if self.hit_stop > 0:
            self.hit_stop = max(0.0, self.hit_stop - dt)
            for particle in self.particles:
                particle.update(dt * 0.18)
            return

        if self.inventory_open:
            return

        self.player.update(
            dt,
            keys,
            self.obstacles,
        )

        self.step_timer = max(
            0.0,
            self.step_timer - dt,
        )
        if (
            self.player.is_moving
            and self.step_timer <= 0
        ):
            self.events.append("footstep")
            self.step_timer = 0.34

        self.ally_cooldown = max(
            0.0,
            self.ally_cooldown - dt,
        )
        if self.ally_cooldown <= 0:
            self._ally_assist()
            self.ally_cooldown = 2.4

        for enemy in self.enemies:
            enemy.update(dt, self.player.pos)
            if enemy.dead:
                continue

            distance = enemy.pos.distance_to(self.player.pos)
            if distance <= enemy.radius + 25 and enemy.attack_cd <= 0:
                if self.player.damage(enemy.damage):
                    enemy.attack_cd = 0.9
                    self.events.append("wolf")
                    self._burst(self.player.pos, RED, 9)
                    self.impact_feedback(
                        strength=12 if enemy.boss else 7,
                        stop=0.065,
                        flash=0.12,
                    )

        if self.player.health <= 0:
            self.engine.state["caos"] = self.engine.state.get("caos", 0) + 1
            self.player.health = self.profile["max_health"]
            self.player.energy = self.profile["max_energy"]
            self.player.pos.update(WORLD_W / 2, WORLD_H / 2)
            self.notice = "Você caiu e despertou no marco rúnico • +1 Caos"
            self.notice_timer = 2.8
            self.events.append("wake")

        for loot in self.loots:
            if loot.picked:
                continue
            if loot.pos.distance_to(self.player.pos) <= 36:
                loot.picked = True
                self.profile["inventory"][loot.kind] += 1
                label = {
                    "pocao": "Poção Nórdica",
                    "essencia": "Essência Rúnica",
                    "fragmento": "Fragmento de Valdrak",
                }[loot.kind]
                self.notice = f"Coletou: {label}"
                self.notice_timer = 1.8
                self.events.append("scanner")

        for particle in self.particles:
            particle.update(dt)
        self.particles = [
            particle for particle in self.particles
            if particle.life > 0
        ]
        target = self.player.pos - pygame.Vector2(640, 360)
        self.camera.x += (target.x - self.camera.x) * min(1.0, dt * 7)
        self.camera.y += (target.y - self.camera.y) * min(1.0, dt * 7)
        self.camera.x = clamp(self.camera.x, 0, WORLD_W - 1280)
        self.camera.y = clamp(self.camera.y, 0, WORLD_H - 720)

    def apply_rewards(self):
        chapter_kills = self.profile["kills"] - self.chapter_kills_start

        if chapter_kills >= 2:
            self.engine.state["coragem"] = (
                self.engine.state.get("coragem", 0) + 1
            )
            return "+1 Coragem por combate"

        if chapter_kills == 1:
            self.engine.state["tecnologia"] = (
                self.engine.state.get("tecnologia", 0) + 1
            )
            return "+1 Tecnologia por exploração"

        return ""

    def draw(self, surface, fonts):
        seconds = pygame.time.get_ticks() / 1000
        theme = self.theme

        if (
            self.map_scene
            and self.map_scene.draw(
                surface,
                self.camera,
            )
        ):
            self.world_art.draw_overlay(
                surface,
                self.camera,
                seconds,
            )
        else:
            self.world_art.draw(
                surface,
                self.camera,
                seconds,
            )
        items = []
        for rect in self.obstacles[4:]:
            items.append((rect.bottom, "obstacle", rect))
        for shrine in self.shrines:
            items.append((shrine.pos.y, "shrine", shrine))
        if self.npc:
            items.append((self.npc.pos.y, "npc", self.npc))
        for enemy in self.enemies:
            if not enemy.dead:
                items.append((enemy.pos.y, "enemy", enemy))
        items.append((self.player.pos.y, "player", self.player))

        ally_names = self.engine.ally_names()
        for index, ally_name in enumerate(ally_names[:4]):
            pos = self._ally_pos(index)
            items.append((pos.y, "ally", (ally_name, pos, index)))

        nearest = self.nearest_shrine()

        for _y, kind, item in sorted(items, key=lambda row: row[0]):
            if kind == "obstacle":
                self._draw_obstacle(surface, item)
            elif kind == "shrine":
                near = (
                    nearest is item
                    and self.player.pos.distance_to(item.pos) <= 125
                )
                item.draw(
                    surface,
                    self.camera,
                    fonts["small"],
                    fonts["small"],
                    theme["accent"],
                    seconds,
                    near,
                )
            elif kind == "npc":
                near_npc = (
                    self.player.pos.distance_to(item.pos) <= 100
                )
                item.draw(
                    surface,
                    self.camera,
                    theme["accent"],
                    near=near_npc,
                )
            elif kind == "enemy":
                item.draw(surface, self.camera)
            elif kind == "player":
                item.draw(surface, self.camera, theme["accent"])
            else:
                draw_ally(
                    surface,
                    item[0],
                    item[1],
                    self.camera,
                    seconds,
                    item[2],
                )

        for loot in self.loots:
            loot.draw(surface, self.camera, seconds)

        for particle in self.particles:
            particle.draw(surface, self.camera)

        if self.shake_timer > 0:
            power = self.shake_strength * (
                self.shake_timer / 0.18
            )
            dx = int(math.sin(seconds * 73) * power)
            dy = int(math.cos(seconds * 61) * power * 0.65)
            frame = surface.copy()
            surface.fill(theme["ground"])
            surface.blit(frame, (dx, dy))

        self._draw_hud(surface, fonts, theme)

        if self.dialogue and self.notice_timer > 0:
            speaker, body = self.dialogue
            draw_dialogue_box(
                surface,
                fonts,
                speaker,
                body,
                theme["accent"],
            )

        if self.inventory_open:
            self._draw_inventory(surface, fonts, theme)

        if self.flash_timer > 0:
            alpha = int(
                85 * min(1.0, self.flash_timer / 0.13)
            )
            flash = pygame.Surface(
                (1280, 720),
                pygame.SRCALPHA,
            )
            flash.fill((255, 255, 255, alpha))
            surface.blit(flash, (0, 0))

    def _draw_ground(self, surface, theme, seconds):
        offset_x = int(self.camera.x) % 64
        offset_y = int(self.camera.y) % 64
        for x in range(-offset_x, 1280, 64):
            pygame.draw.line(
                surface,
                theme["path"],
                (x, 0),
                (x, 720),
                1,
            )
        for y in range(-offset_y, 720, 64):
            pygame.draw.line(
                surface,
                theme["path"],
                (0, y),
                (1280, y),
                1,
            )

        for index in range(22):
            world_x = (
                index * 181 + self.chapter["number"] * 73
            ) % WORLD_W
            world_y = (
                index * 127 + self.chapter["number"] * 91
            ) % WORLD_H
            x = int(world_x - self.camera.x)
            y = int(world_y - self.camera.y)
            if -20 < x < 1300 and -20 < y < 740:
                radius = 2 + index % 3
                color = theme["accent"]
                glow = max(
                    40,
                    int(110 + math.sin(seconds * 2 + index) * 50),
                )
                layer = pygame.Surface((18, 18), pygame.SRCALPHA)
                pygame.draw.circle(
                    layer,
                    (*color, glow),
                    (9, 9),
                    radius + 3,
                )
                surface.blit(layer, (x - 9, y - 9))

    def _draw_obstacle(self, surface, rect):
        self.world_art.draw_obstacle(
            surface,
            rect,
            self.camera,
        )

    def _ally_pos(self, index):
        angle = math.pi + (index - 1.5) * 0.55
        distance = 62 + (index % 2) * 16
        return self.player.pos + pygame.Vector2(
            math.cos(angle) * distance,
            math.sin(angle) * distance,
        )
    def _draw_ally(self, surface, name, pos, index, accent):
        x = int(pos.x - self.camera.x)
        y = int(pos.y - self.camera.y)
        colors = [GOLD, CYAN, GREEN, VIOLET]
        color = colors[index % len(colors)]

        pygame.draw.circle(
            surface,
            (11, 17, 24),
            (x, y + 8),
            18,
        )
        pygame.draw.rect(
            surface,
            color,
            (x - 10, y - 8, 20, 28),
            border_radius=7,
        )
        pygame.draw.circle(
            surface,
            (202, 171, 145),
            (x, y - 17),
            9,
        )
        pygame.draw.circle(
            surface,
            accent,
            (x, y),
            24,
            1,
        )
    def interaction_hint(self):
        nearest = self.nearest_shrine()

        if (
            self.npc
            and self.player.pos.distance_to(
                self.npc.pos
            )
            <= 100
        ):
            return f"E — falar com {self.npc.name}"

        if (
            nearest
            and self.player.pos.distance_to(
                nearest.pos
            )
            <= 95
        ):
            if self.boss_alive():
                return (
                    "Derrote o Guardião "
                    "para liberar os caminhos"
                )

            if nearest.available:
                return (
                    f"E — escolher Caminho "
                    f"{nearest.index + 1}"
                )

            return f"Bloqueado: {nearest.reason}"

        return ""

    def _draw_hud(self, surface, fonts, theme):
        self.hud.draw(
            surface,
            fonts,
            self,
            theme,
        )

    def _draw_inventory(self, surface, fonts, theme):
        veil = pygame.Surface(
            (1280, 720),
            pygame.SRCALPHA,
        )
        veil.fill((0, 0, 0, 165))
        surface.blit(veil, (0, 0))

        panel = pygame.Rect(250, 130, 780, 470)
        pygame.draw.rect(
            surface,
            (8, 14, 22),
            panel,
            border_radius=24,
        )
        pygame.draw.rect(
            surface,
            theme["accent"],
            panel,
            2,
            border_radius=24,
        )

        surface.blit(
            fonts["title"].render(
                "INVENTÁRIO DE VALDRAK",
                True,
                INK,
            ),
            (292, 166),
        )
        surface.blit(
            fonts["small"].render(
                "I/TAB para fechar • 1 e 2 usam itens durante exploração",
                True,
                MUTED,
            ),
            (294, 208),
        )

        inventory = self.profile["inventory"]
        cards = [
            (
                "Poção Nórdica",
                inventory["pocao"],
                RED,
                "+35 Vida",
            ),
            (
                "Essência Rúnica",
                inventory["essencia"],
                CYAN,
                "+45 Energia",
            ),
            (
                "Fragmento de Valdrak",
                inventory["fragmento"],
                GOLD,
                "Relíquia rara",
            ),
        ]

        for index, (name, count, color, effect) in enumerate(cards):
            rect = pygame.Rect(
                292,
                254 + index * 82,
                690,
                66,
            )
            pygame.draw.rect(
                surface,
                (18, 28, 40),
                rect,
                border_radius=14,
            )
            pygame.draw.rect(
                surface,
                color,
                rect,
                1,
                border_radius=14,
            )
            pygame.draw.circle(
                surface,
                color,
                (rect.x + 34, rect.centery),
                13,
            )
            surface.blit(
                fonts["body"].render(
                    name,
                    True,
                    INK,
                ),
                (rect.x + 62, rect.y + 12),
            )
            surface.blit(
                fonts["small"].render(
                    effect,
                    True,
                    MUTED,
                ),
                (rect.x + 62, rect.y + 38),
            )
            count_text = fonts["heading"].render(
                str(count),
                True,
                color,
            )
            surface.blit(
                count_text,
                count_text.get_rect(
                    center=(rect.right - 42, rect.centery)
                ),
            )

        allies = self.engine.ally_names()
        ally_text = (
            " • ".join(allies)
            if allies
            else "Nenhum Eterno encontrado ainda"
        )
        surface.blit(
            fonts["small"].render(
                f"Eternos: {ally_text}",
                True,
                theme["accent"],
            ),
            (294, 518),
        )
        surface.blit(
            fonts["small"].render(
                (
                    f"Nível {self.profile['level']} • "
                    f"XP {self.profile['xp']}/{self.profile['xp_next']} • "
                    f"Abates {self.profile['kills']}"
                ),
                True,
                MUTED,
            ),
            (294, 548),
        )

    @staticmethod
    def _bar(
        surface,
        font,
        rect,
        value,
        maximum,
        color,
        label,
    ):
        ratio = (
            0
            if maximum <= 0
            else clamp(value / maximum, 0, 1)
        )
        pygame.draw.rect(
            surface,
            (31, 39, 49),
            rect,
            border_radius=7,
        )
        pygame.draw.rect(
            surface,
            color,
            (
                rect.x,
                rect.y,
                int(rect.width * ratio),
                rect.height,
            ),
            border_radius=7,
        )
        value_text = font.render(
            f"{label} {int(value)}/{int(maximum)}",
            True,
            INK,
        )
        surface.blit(
            value_text,
            (rect.x, rect.y - 18),
        )
