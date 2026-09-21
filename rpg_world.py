import math
import random

import pygame

from rpg_entities import EnemyActor, Loot, NPC


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

        walk_wave = math.sin(self.anim_time * 11)
        bob = int(walk_wave * 3) if self.state == "walk" else 0
        lean = 6 if self.state == "dash" else 0

        body_color = {
            "hurt": (164, 180, 198),
            "pulse": (49, 111, 134),
            "dash": (49, 90, 126),
        }.get(self.state, (52, 87, 118))

        shadow_w = 26 if self.state == "dash" else 22
        pygame.draw.ellipse(
            surface,
            (18, 23, 30),
            (x - shadow_w, y + 16, shadow_w * 2, 14),
        )

        leg_offset = int(walk_wave * 5) if self.state == "walk" else 0
        pygame.draw.line(
            surface,
            (31, 44, 58),
            (x - 7, y + 18),
            (x - 8 - leg_offset, y + 35),
            5,
        )
        pygame.draw.line(
            surface,
            (31, 44, 58),
            (x + 7, y + 18),
            (x + 8 + leg_offset, y + 35),
            5,
        )

        pygame.draw.rect(
            surface,
            body_color,
            (x - 16 + lean, y - 12 + bob, 32, 39),
            border_radius=10,
        )
        pygame.draw.circle(
            surface,
            (208, 173, 145),
            (x + lean, y - 22 + bob),
            14,
        )

        hood = [
            (x - 16 + lean, y - 26 + bob),
            (x + lean, y - 43 + bob),
            (x + 16 + lean, y - 26 + bob),
        ]
        pygame.draw.polygon(surface, (35, 57, 78), hood)

        end = pygame.Vector2(x + lean, y) + self.facing * 31
        pygame.draw.line(
            surface,
            accent,
            (x + lean, y + 2),
            end,
            4,
        )

        if self.state == "attack":
            pygame.draw.arc(
                surface,
                GOLD,
                pygame.Rect(x - 62, y - 62, 124, 124),
                -0.95,
                0.95,
                7,
            )
            pygame.draw.arc(
                surface,
                INK,
                pygame.Rect(x - 49, y - 49, 98, 98),
                -0.85,
                0.85,
                2,
            )

        if self.state == "pulse":
            radius = int(50 + (0.8 - self.pulse_timer) * 185)
            pygame.draw.circle(
                surface,
                CYAN,
                (x, y),
                max(10, radius),
                4,
            )
            for index in range(8):
                angle = self.anim_time * 5 + index * math.tau / 8
                px = x + math.cos(angle) * 34
                py = y + math.sin(angle) * 34
                pygame.draw.circle(
                    surface,
                    CYAN,
                    (int(px), int(py)),
                    3,
                )

        if self.state == "dash":
            for index in range(3):
                trail = pygame.Vector2(x, y) - self.facing * (22 + index * 16)
                pygame.draw.circle(
                    surface,
                    (*accent,),
                    (int(trail.x), int(trail.y)),
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

        self.obstacles = self._build_obstacles()
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
        if event.key == pygame.K_e:
            if (
                self.npc
                and self.player.pos.distance_to(self.npc.pos) <= 100
            ):
                self.notice = f"{self.npc.name}: {self.npc.talk()}"
                self.notice_timer = 4.2
                self.events.append("rune")

                flag = f"npc_gift_{self.chapter['number']}"
                if not self.profile["npc_flags"].get(flag):
                    self.profile["npc_flags"][flag] = True
                    self.profile["inventory"]["essencia"] += 1
                    self.notice += " • recebeu 1 Essência"
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
        world_point = pygame.Vector2(point) + self.camera
        self.player.auto_target = world_point

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

    def update(self, dt, keys):
        self.notice_timer = max(0.0, self.notice_timer - dt)
        self.player.update(dt, keys, self.obstacles)
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
        surface.fill(theme["ground"])

        self._draw_ground(surface, theme, seconds)
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
                self._draw_ally(
                    surface,
                    item[0],
                    item[1],
                    item[2],
                    theme["accent"],
                )

        for loot in self.loots:
            loot.draw(surface, self.camera, seconds)

        for particle in self.particles:
            particle.draw(surface, self.camera)

        self._draw_hud(surface, fonts, theme)

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
        screen = rect.move(
            -int(self.camera.x),
            -int(self.camera.y),
        )
        if not screen.colliderect(
            pygame.Rect(0, 0, 1280, 720)
        ):
            return

        pygame.draw.rect(
            surface,
            (23, 30, 35),
            screen,
            border_radius=10,
        )
        pygame.draw.rect(
            surface,
            (47, 55, 58),
            screen,
            2,
            border_radius=10,
        )

        for x in range(
            screen.left + 12,
            screen.right - 6,
            25,
        ):
            pygame.draw.line(
                surface,
                (55, 64, 65),
                (x, screen.top + 7),
                (x - 7, screen.bottom - 7),
                2,
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
    def _draw_hud(self, surface, fonts, theme):
        accent = theme["accent"]
        panel = pygame.Rect(18, 16, 1244, 92)
        pygame.draw.rect(
            surface,
            (7, 12, 19),
            panel,
            border_radius=16,
        )
        pygame.draw.rect(
            surface,
            (55, 70, 84),
            panel,
            1,
            border_radius=16,
        )

        title = fonts["heading"].render(
            theme["name"],
            True,
            INK,
        )
        surface.blit(title, (38, 29))

        level_text = (
            f"NÍVEL {self.profile['level']}  •  "
            f"EXP {self.profile['xp']}/{self.profile['xp_next']}  •  "
            f"ABATES {self.profile['kills']}"
        )
        surface.blit(
            fonts["small"].render(
                level_text,
                True,
                MUTED,
            ),
            (39, 63),
        )

        self._bar(
            surface,
            fonts["small"],
            pygame.Rect(540, 31, 250, 15),
            self.player.health,
            self.profile["max_health"],
            RED,
            "VIDA",
        )
        self._bar(
            surface,
            fonts["small"],
            pygame.Rect(540, 68, 250, 15),
            self.player.energy,
            self.profile["max_energy"],
            CYAN,
            "ENERGIA",
        )

        nearest = self.nearest_shrine()
        hint = (
            "WASD mover • ESPAÇO atacar • Q Pulso • "
            "SHIFT dash • E interagir"
        )

        if (
            self.npc
            and self.player.pos.distance_to(self.npc.pos) <= 100
        ):
            hint = f"E — falar com {self.npc.name}"
        elif (
            nearest
            and self.player.pos.distance_to(nearest.pos) <= 95
        ):
            if self.boss_alive():
                hint = "Derrote o Guardião para liberar os caminhos"
            elif nearest.available:
                hint = (
                    f"E — escolher Caminho "
                    f"{nearest.index + 1}"
                )
            else:
                hint = f"Bloqueado: {nearest.reason}"

        hint_surf = fonts["small"].render(
            hint,
            True,
            accent,
        )
        surface.blit(
            hint_surf,
            hint_surf.get_rect(topright=(1235, 35)),
        )

        inventory = self.profile["inventory"]
        item_text = (
            f"[1] Poção {inventory['pocao']}  •  "
            f"[2] Essência {inventory['essencia']}  •  "
            f"Fragmentos {inventory['fragmento']}"
        )
        surface.blit(
            fonts["small"].render(
                item_text,
                True,
                MUTED,
            ),
            (820, 82),
        )

        boss = self.boss()
        if boss and not boss.dead:
            ratio = max(0, boss.hp) / boss.max_hp
            boss_rect = pygame.Rect(390, 116, 500, 12)
            pygame.draw.rect(
                surface,
                (37, 29, 29),
                boss_rect,
                border_radius=6,
            )
            pygame.draw.rect(
                surface,
                GOLD,
                (
                    boss_rect.x,
                    boss_rect.y,
                    int(boss_rect.width * ratio),
                    boss_rect.height,
                ),
                border_radius=6,
            )
            boss_label = fonts["small"].render(
                f"GUARDIÃO — {boss.name}",
                True,
                GOLD,
            )
            surface.blit(
                boss_label,
                boss_label.get_rect(
                    center=(640, 106)
                ),
            )

        if self.notice_timer > 0 and self.notice:
            notice = fonts["small"].render(
                self.notice,
                True,
                GOLD,
            )
            surface.blit(
                notice,
                notice.get_rect(topright=(1235, 69)),
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
