import math
import random

import pygame

from character_visuals import ALLY_STYLES, draw_ally, draw_dialogue_box
from rpg_entities import EnemyActor, Loot, NPC
from world_art import WorldArt
from sprite_animator import draw_actor
from hud import RPGHUD
from map_loader import MapScene
from character_art import draw_protagonist
from adventure_system import build_chests
from boss_v24 import BossCombatController
from living_valdrak import LivingValdrak
from combat_v25 import CombatV25
from combat_v27 import CombatPresentationV27
from quest_v27 import QuestSystemII
from world_v27 import WorldQualityIII
from adventure_v28 import AdventureDepthV28
from combat_v28 import CombatCoreV28
from companion_v28 import CompanionSystemV28
from dungeon_v28 import DungeonSystemIII
from production_art_v28 import (
    draw_final_ui_frame,
    draw_player_equipment_v28,
)
from rpg_depth_v28 import RPGDepthII, total_stats
from meta_v25 import (
    RECIPES,
    TALENTS,
    balance,
    buy_item,
    craft,
    cycle_difficulty,
    ensure_meta,
    grant_materials,
    quest_step,
    talent_bonus,
    toggle_accessibility,
    unlock_talent,
    upgrade_equipped,
    vendor_stock,
)
from visual_v25 import VisualRPGPass
from art_v26 import WorldArtII
from cinematic_v26 import CinematicDirector
from world_v26 import WorldQuestDirector

from progression_v24 import (
    add_and_auto_equip,
    codex_lines,
    ensure_progression_profile,
    equipment_stats,
    quest_lines,
    roll_equipment,
    unlock_codex,
    world_map_lines,
)
from world_expansion import (
    build_region_places,
    interact_with_place,
    region_progress,
    region_quest_name,
)


WORLD_W = 3648
WORLD_H = 2208
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
        self.attack_combo = 0
        self.heavy_timer = 0.0
        self.death_timer = 0.0
        self.parry_timer = 0.0
        self.dodge_anim_timer = 0.0
        self.execute_timer = 0.0
        self.knockdown_timer = 0.0

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
        self.profile.setdefault("discoveries", [])
        self.profile.setdefault("completed_region_quests", [])
        self.profile["inventory"].setdefault("reliquia", 0)
        self.profile["inventory"].setdefault("chave", 0)

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
        self.heavy_timer = max(0.0, self.heavy_timer - dt)
        self.death_timer = max(0.0, self.death_timer - dt)
        self.parry_timer = max(0.0, self.parry_timer - dt)
        self.dodge_anim_timer = max(0.0, self.dodge_anim_timer - dt)
        self.execute_timer = max(0.0, self.execute_timer - dt)
        self.knockdown_timer = max(0.0, self.knockdown_timer - dt)

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

        if (
            direction.length_squared() == 0
            and pygame.joystick.get_init()
            and pygame.joystick.get_count() > 0
        ):
            try:
                joystick = pygame.joystick.Joystick(0)
                if not joystick.get_init():
                    joystick.init()
                axis_x = joystick.get_axis(0)
                axis_y = joystick.get_axis(1)
                if abs(axis_x) > 0.18 or abs(axis_y) > 0.18:
                    direction.update(axis_x, axis_y)
            except pygame.error:
                pass

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

        if self.death_timer > 0:
            self.state = "death"
        elif self.knockdown_timer > 0:
            self.state = "knockdown"
        elif self.execute_timer > 0:
            self.state = "execute"
        elif self.parry_timer > 0:
            self.state = "parry"
        elif self.dodge_anim_timer > 0:
            self.state = "dodge"
        elif self.invulnerable > 0:
            self.state = "hurt"
        elif self.heavy_timer > 0:
            self.state = "heavy"
        elif self.pulse_timer > 0:
            self.state = "power"
        elif self.attack_timer > 0:
            self.state = "attack1" if self.attack_combo % 2 else "attack2"
        elif self.dash_timer > 0.35:
            self.state = "dash"
        elif self.is_moving:
            self.state = "run" if self.energy > 75 else "walk"
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

        stats = equipment_stats(self.profile)
        reduction = min(0.45, stats["defense"] * 0.012)
        amount = max(1, int(round(amount * (1 - reduction))))
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

        rendered = draw_protagonist(
            surface,
            (x, y),
            self.facing,
            self.state,
            seconds,
            accent,
        )

        if not rendered:
            rendered = draw_actor(
                surface,
                "player",
                (x, y),
                state=self.state,
                facing=self.facing,
                seconds=seconds,
                tint=accent,
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
        ensure_progression_profile(self.profile)
        ensure_meta(self.profile)
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
        self.places = build_region_places(
            chapter["number"],
            self.profile,
        )
        self.loots = []
        self.chests = build_chests(
            chapter["number"],
            self.profile,
        )
        self.npc = NPC(
            chapter["number"],
            (WORLD_W / 2 + 185, WORLD_H / 2 - 105),
        )

        self.chapter_kills_start = profile.get("kills", 0)

        self.profile.setdefault("tutorial_complete", False)
        self.profile.setdefault("tutorial_stage", 0)
        self.tutorial_active = (
            chapter["number"] == 1
            and not self.profile["tutorial_complete"]
        )
        self.tutorial_stage = int(
            self.profile.get("tutorial_stage", 0)
        )
        self.tutorial_origin = self.player.pos.copy()
        self.story_echoes = list(chapter.get("scene", []))
        self.story_echo_index = 0

        if chapter["number"] not in self.profile["visited_regions"]:
            self.profile["visited_regions"].append(chapter["number"])

        self.living = LivingValdrak(chapter["number"], self.profile)
        self.boss_combat = BossCombatController(chapter["number"])
        self.combat_v25 = CombatV25(self.profile)
        self.visual_v25 = VisualRPGPass(
            chapter["number"],
            (WORLD_W, WORLD_H),
        )
        self.art_v26 = WorldArtII(
            chapter["number"],
            self.profile,
            (WORLD_W, WORLD_H),
        )
        self.v26 = WorldQuestDirector(
            chapter["number"],
            self.profile,
            seed=chapter["number"] * 101,
        )
        self.cinematic_v26 = CinematicDirector(
            chapter["number"],
            self.profile,
        )
        self.combat_v27 = CombatPresentationV27()
        self.world_v27 = WorldQualityIII(
            chapter["number"],
            self.profile,
        )
        self.quest_v27 = QuestSystemII(
            chapter["number"],
            self.profile,
        )
        self.obstacles.extend(
            self.world_v27.collision_rects()
        )
        self.v27_boss_phase2 = False

        self.adventure_v28 = AdventureDepthV28(
            chapter["number"],
            self.profile,
        )
        self.dungeon_v28 = DungeonSystemIII(
            chapter["number"],
            self.profile,
            seed=chapter["number"] * 281,
        )
        self.combat_v28 = CombatCoreV28(
            self.profile,
        )
        self.rpg_v28 = RPGDepthII(
            self.profile,
        )
        self.companion_v28 = CompanionSystemV28(
            self.profile,
        )
        self.companion_v28.sync(
            self.engine.ally_names()
        )

        self.vendor_items = vendor_stock(
            chapter["number"],
            self.rng,
        )
        self.overlay_screen = None
        self.map_selection = chapter["number"]
        self.requested_travel_chapter = None
        self.music_state = "music_explore"
        self.last_music_state = None

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
        count = 3 + chapter_number // 2
        enemies = []
        archetypes = [
            "wolf",
            "raider",
            "raven",
            "berserker",
            "archer",
            "rune_mage",
            "alpha_wolf",
            "elite_raider",
        ]

        for index in range(count):
            for _attempt in range(30):
                pos = pygame.Vector2(
                    self.rng.randint(180, WORLD_W - 180),
                    self.rng.randint(180, WORLD_H - 180),
                )
                if pos.distance_to(self.player.pos) > 280:
                    pool_end = min(
                        len(archetypes),
                        3 + chapter_number,
                    )
                    archetype = archetypes[
                        (index + chapter_number) % pool_end
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

        boss_types = {
            1: "raider",
            2: "elite_raider",
            3: "berserker",
            4: "raven",
            5: "alpha_wolf",
            6: "elite_raider",
            7: "rune_mage",
        }
        boss_archetype = boss_types[chapter_number]
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

    def _spawn_living_enemy(self, archetype=None):
        choices = [
            "raider",
            "berserker",
            "archer",
            "rune_mage",
            "alpha_wolf",
        ]
        archetype = archetype or self.rng.choice(choices)
        angle = self.rng.uniform(0, math.tau)
        pos = self.player.pos + pygame.Vector2(
            math.cos(angle) * self.rng.randint(170, 250),
            math.sin(angle) * self.rng.randint(170, 250),
        )
        pos.x = clamp(pos.x, 90, WORLD_W - 90)
        pos.y = clamp(pos.y, 90, WORLD_H - 90)
        self.enemies.append(
            EnemyActor(
                pos,
                self.chapter["number"],
                self.rng,
                archetype=archetype,
            )
        )

    def _update_music_state(self):
        chapter = self.chapter["number"]
        if self.living.interior or self.world_v27.interior:
            self.music_state = f"music_interior_{chapter}"
            return
        boss = self.boss()
        if (
            boss
            and not boss.dead
            and boss.pos.distance_to(self.player.pos) < 520
        ):
            self.music_state = f"music_boss_{chapter}"
            return
        danger = any(
            not enemy.dead
            and enemy.pos.distance_to(self.player.pos) < 280
            for enemy in self.enemies
        )
        self.music_state = (
            f"music_danger_{chapter}"
            if danger
            else f"music_region_{chapter}"
        )

    def _damage_player(self, amount):
        difficulty = balance(self.profile)
        amount = max(
            1,
            int(round(amount * difficulty["enemy_damage"])),
        )
        resolved, label = self.combat_v25.incoming(amount)
        if label:
            if "PARRY" in label:
                self.combat_v27.on_parry()
                self.profile["v28_perfect_parries"] = (
                    self.profile.get(
                        "v28_perfect_parries",
                        0,
                    )
                    + 1
                )
            else:
                self.combat_v27.on_dodge()
            self.notice = label
            self.notice_timer = 1.2
            self.events.append(
                "shield" if "PARRY" in label else "wind"
            )
            self.impact_feedback(
                strength=5,
                stop=0.045,
                flash=0.05,
            )
            return False
        damaged = self.player.damage(resolved)
        if damaged:
            heavy = resolved >= 18
            self.combat_v27.on_hit(heavy=heavy)
            if resolved >= 24:
                self.player.knockdown_timer = 0.48
                self.combat_v27.on_knockdown()
        return damaged

    def _status_from_rune(self):
        rune = self.profile.get("equipped", {}).get("rune")
        if not rune:
            return None
        name = rune.get("name", "")
        if "Trovão" in name:
            return "bleed"
        if "Pedra" in name:
            return "frost"
        if "Código" in name:
            return "burn"
        return None

    def parry(self):
        difficulty = self.profile.get(
            "difficulty",
            "Normal",
        )
        cost = self.combat_v28.stamina_cost(
            "parry",
            difficulty,
        )
        if self.combat_v25.stamina < cost:
            self.notice = "Stamina insuficiente"
            self.notice_timer = 1.0
            return

        nearby = [
            enemy
            for enemy in self.enemies
            if (
                not enemy.dead
                and enemy.pos.distance_to(
                    self.player.pos
                )
                <= 180
            )
        ]
        target = (
            min(
                nearby,
                key=lambda enemy: enemy.pos.distance_to(
                    self.player.pos
                ),
            )
            if nearby
            else None
        )
        archetype = (
            "boss"
            if target and target.boss
            else target.archetype
            if target
            else "raider"
        )
        window = self.combat_v28.parry_window(
            archetype
        )
        self.combat_v25.stamina -= cost
        self.combat_v25.parry_window = window
        self.player.parry_timer = window + 0.08
        self.combat_v27.on_parry()
        self.notice = (
            f"PARRY • janela {int(window * 1000)}ms"
        )
        self.notice_timer = 0.8
        self.events.append("shield")

    def execute_boss(self):
        finishable = [
            enemy
            for enemy in self.enemies
            if self.combat_v28.finisher_available(
                enemy,
                self.player,
            )
        ]
        if finishable:
            target = min(
                finishable,
                key=lambda enemy: enemy.pos.distance_to(
                    self.player.pos
                ),
            )
            cost = self.combat_v28.stamina_cost(
                "finisher",
                self.profile.get(
                    "difficulty",
                    "Normal",
                ),
            )
            if self.combat_v25.stamina < cost:
                self.notice = "Stamina insuficiente"
                self.notice_timer = 1.0
                return
            self.combat_v25.stamina -= cost
            damage = self.combat_v28.finisher(
                target
            )
            self.player.execute_timer = 0.95
            self.combat_v27.on_execution()
            died = target.hit(damage)
            self.notice = (
                f"FINISHER • {target.archetype} • "
                f"{damage} dano"
            )
            self.notice_timer = 1.8
            self.events.extend(
                ["blade_hit", "rune"]
            )
            self.impact_feedback(
                strength=17,
                stop=0.13,
                flash=0.16,
            )
            if died:
                self._enemy_defeated(target)
            return

        boss = self.boss()
        if not boss or boss.dead:
            return
        if not self.combat_v25.execution_available(
            self.boss_combat,
            boss.pos.distance_to(self.player.pos),
        ):
            self.notice = "Execução indisponível"
            self.notice_timer = 1.0
            return
        self.combat_v25.execute()
        self.player.execute_timer = 0.95
        self.combat_v27.on_execution()
        damage = int(boss.max_hp * 0.22)
        died = boss.hit(damage)
        self.notice = f"EXECUÇÃO RÚNICA • {damage} dano"
        self.notice_timer = 1.8
        self.events.extend(["blade_hit", "rune"])
        self.impact_feedback(
            strength=16,
            stop=0.12,
            flash=0.16,
        )
        if died:
            self._enemy_defeated(boss)

    def heavy_attack(self):
        if self.player.heavy_timer > 0:
            return
        heavy_cost = self.combat_v28.stamina_cost(
            "heavy",
            self.profile.get(
                "difficulty",
                "Normal",
            ),
        )
        if self.combat_v25.stamina < heavy_cost:
            self.notice = "Stamina insuficiente"
            self.notice_timer = 1.0
            return
        self.combat_v25.stamina -= heavy_cost
        if self.player.energy < 20:
            self.notice = "Energia insuficiente"
            self.notice_timer = 1.0
            return
        self.player.energy -= 20
        self.player.heavy_timer = 0.72
        self.player.attack_timer = 0.52
        self.combat_v27.on_attack("heavy")
        self.events.append("axe_whoosh")
        attack_center = self.player.pos + self.player.facing * 68
        hitbox = self.combat_v28.attack_hitbox(
            self.player,
            heavy=True,
            frame_phase="active",
        )
        stats = total_stats(self.profile)
        difficulty = balance(self.profile)
        damage = int(
            (
                42
                + self.profile["level"] * 4
                + stats["attack"]
                + talent_bonus(
                    self.profile,
                    "attack_bonus",
                )
            )
            * difficulty["player_damage"]
        )
        for enemy in self.enemies:
            if enemy.dead:
                continue
            enemy_box = pygame.Rect(
                0,
                0,
                enemy.radius * 2,
                enemy.radius * 2,
            )
            enemy_box.center = (
                int(enemy.pos.x),
                int(enemy.pos.y),
            )
            if hitbox.colliderect(enemy_box):
                died = enemy.hit(damage)
                self.combat_v28.open_cancel_window(
                    0.18
                )
                self._burst(enemy.pos, GOLD, 16)
                self.impact_feedback(
                    strength=14 if enemy.boss else 9,
                    stop=0.10,
                    flash=0.14,
                )
                if enemy.boss:
                    if self.boss_combat.add_stagger(24):
                        self.notice = "GUARDIÃO ATORDOADO"
                        self.notice_timer = 2.0
                elif not died:
                    delta = enemy.pos - self.player.pos
                    if delta.length_squared():
                        enemy.pos += delta.normalize() * 34
                    status = self._status_from_rune()
                    if status:
                        self.combat_v25.apply_status(
                            enemy,
                            status,
                            duration=4.0,
                        )
                if died:
                    self._enemy_defeated(enemy)

    def handle_key(self, event):
        if self.dungeon_v28.active:
            result = self.dungeon_v28.handle_key(
                event.key,
                self,
            )
            if result:
                message, sfx = result
                self.notice = message
                self.notice_timer = 2.6
                if sfx:
                    self.events.append(sfx)
            return

        if self.adventure_v28.current_site:
            result = self.adventure_v28.handle_key(
                event.key,
                self,
            )
            if result:
                message, sfx = result
                if message == "__open_dungeon_v28__":
                    self.notice = "Masmorra profunda aberta"
                    self.notice_timer = 2.2
                else:
                    self.notice = message
                    self.notice_timer = 2.6
                if sfx:
                    self.events.append(sfx)
            return

        if self.world_v27.interior:
            result = self.world_v27.handle_key(
                event.key,
                self,
            )
            if result:
                message, sfx = result
                if message == "__upgrade_weapon__":
                    ok, message = upgrade_equipped(
                        self.profile,
                        "weapon",
                    )
                    sfx = "blacksmith" if ok else "error"
                self.notice = message
                self.notice_timer = 2.4
                self.events.append(sfx)
            return

        if self.v26.pending_choice:
            choice_keys = {
                pygame.K_1: 1,
                pygame.K_2: 2,
                pygame.K_KP1: 1,
                pygame.K_KP2: 2,
            }
            if event.key in choice_keys:
                message = self.v26.choose_quest(
                    choice_keys[event.key]
                )
                if message:
                    consequence = self.profile[
                        "v26_consequences"
                    ].get(str(self.chapter["number"]))
                    if consequence:
                        self.quest_v27.on_choice(
                            consequence
                        )
                    self.notice = message
                    self.dialogue = (
                        "ESCOLHA DE VALDRAK",
                        message,
                    )
                    self.notice_timer = 5.0
                    self.events.extend(
                        ["choice", "quest_complete"]
                    )
                    self.cinematic_v26.start(
                        "VALDRAK MUDOU",
                        message,
                        duration=3.1,
                        kind="choice",
                    )
                return

        if self.inventory_open and event.key == pygame.K_ESCAPE:
            self.inventory_open = False
            return

        if self.living.interior:
            result = self.living.handle_interior_key(
                event.key,
                self,
            )
            if result:
                self.notice, sfx = result
                self.notice_timer = 3.0
                self.events.append(sfx)
            return

        if self.overlay_screen:
            if self.overlay_screen == "rpg_v28":
                if event.key in {
                    pygame.K_ESCAPE,
                    pygame.K_y,
                }:
                    self.overlay_screen = None
                    return
                if event.key in {
                    pygame.K_LEFT,
                    pygame.K_a,
                }:
                    self.rpg_v28.cycle_compare(-1)
                elif event.key in {
                    pygame.K_RIGHT,
                    pygame.K_d,
                }:
                    self.rpg_v28.cycle_compare(1)
                elif event.key == pygame.K_SPACE:
                    self.notice = (
                        self.rpg_v28.equip_comparison()
                    )
                    self.notice_timer = 2.0
                    self.events.append("inventory")
                elif event.key == pygame.K_b:
                    build = self.rpg_v28.cycle_build()
                    self.notice = f"Build: {build}"
                    self.notice_timer = 1.8
                    self.events.append("rune")
                return

            if self.overlay_screen == "companions":
                available = self.engine.ally_names()
                self.companion_v28.sync(available)
                if event.key in {
                    pygame.K_ESCAPE,
                    pygame.K_z,
                }:
                    self.overlay_screen = None
                    return
                if event.key in {
                    pygame.K_UP,
                    pygame.K_w,
                }:
                    self.companion_v28.cycle_selected(-1)
                elif event.key in {
                    pygame.K_DOWN,
                    pygame.K_s,
                }:
                    self.companion_v28.cycle_selected(1)
                elif event.key == pygame.K_SPACE:
                    self.notice = (
                        self.companion_v28.swap_selected(
                            available
                        )
                    )
                    self.notice_timer = 1.8
                    if self.companion_v28.active:
                        ally = self.companion_v28.active[
                            self.companion_v28.selected
                            % len(self.companion_v28.active)
                        ]
                        self.events.append(
                            f"theme_{ally.lower()}"
                        )
                elif event.key == pygame.K_c:
                    mode = self.companion_v28.cycle_mode()
                    self.notice = (
                        f"Comando dos Eternos: {mode}"
                    )
                    self.notice_timer = 1.8
                elif event.key == pygame.K_t:
                    active = self.companion_v28.active
                    if active:
                        ally = active[
                            self.companion_v28.selected
                            % len(active)
                        ]
                        points = self.profile.get(
                            "skill_points",
                            0,
                        )
                        ok, message = (
                            self.rpg_v28.unlock_ally_skill(
                                ally,
                                points,
                            )
                        )
                        if ok:
                            self.profile["skill_points"] -= 1
                        self.notice = message
                        self.notice_timer = 2.0
                        self.events.append(
                            "rune" if ok else "error"
                        )
                return

            close_keys = {
                pygame.K_ESCAPE,
                pygame.K_m,
                pygame.K_j,
                pygame.K_c,
                pygame.K_g,
                pygame.K_k,
                pygame.K_t,
                pygame.K_o,
                pygame.K_h,
                pygame.K_l,
            }
            if event.key in close_keys:
                self.overlay_screen = None
                return

            number_map = {
                pygame.K_1: 0,
                pygame.K_2: 1,
                pygame.K_3: 2,
                pygame.K_KP1: 0,
                pygame.K_KP2: 1,
                pygame.K_KP3: 2,
            }
            if self.overlay_screen == "craft" and event.key in number_map:
                ok, message = craft(
                    self.profile,
                    number_map[event.key],
                    self.chapter["number"],
                    self.rng,
                )
                self.notice = message
                self.notice_timer = 2.0
                self.events.append("pickup" if ok else "error")
                return

            if self.overlay_screen == "talents" and event.key in number_map:
                ok, message = unlock_talent(
                    self.profile,
                    number_map[event.key],
                )
                self.notice = message
                self.notice_timer = 2.0
                self.events.append("rune" if ok else "error")
                return

            if self.overlay_screen == "vendor" and event.key in number_map:
                item = self.vendor_items[number_map[event.key]]
                ok, message = buy_item(self.profile, item)
                self.notice = message
                self.notice_timer = 2.0
                self.events.append("pickup" if ok else "error")
                return

            if self.overlay_screen == "accessibility":
                access_map = {
                    pygame.K_1: "high_contrast",
                    pygame.K_2: "reduce_flash",
                    pygame.K_3: "screen_shake",
                    pygame.K_4: "large_ui",
                }
                if event.key in access_map:
                    key = access_map[event.key]
                    value = toggle_accessibility(
                        self.profile,
                        key,
                    )
                    self.notice = (
                        f"{key}: {'ON' if value else 'OFF'}"
                    )
                    self.notice_timer = 1.4
                    return
                if event.key == pygame.K_5:
                    mode = cycle_difficulty(self.profile)
                    self.notice = f"Dificuldade: {mode}"
                    self.notice_timer = 1.4
                    return
            if self.overlay_screen == "factions":
                if event.key in number_map:
                    message = self.quest_v27.accept_optional(
                        number_map[event.key]
                    )
                    self.notice = message
                    self.notice_timer = 2.2
                    self.events.append("quest_complete")
                return

            if self.overlay_screen == "contracts":
                if event.key in number_map:
                    message = self.v26.accept_contract(
                        number_map[event.key]
                    )
                    self.notice = message
                    self.notice_timer = 2.2
                    self.events.append("contract")
                return

            if self.overlay_screen == "map":
                if event.key in {pygame.K_UP, pygame.K_w}:
                    self.map_selection = max(1, self.map_selection - 1)
                elif event.key in {pygame.K_DOWN, pygame.K_s}:
                    self.map_selection = min(7, self.map_selection + 1)
                elif event.key in {pygame.K_RETURN, pygame.K_SPACE}:
                    if self.map_selection in self.profile["fast_travel_regions"]:
                        self.requested_travel_chapter = self.map_selection
                        self.overlay_screen = None
                        self.events.append("portal")
                    else:
                        self.notice = "Ative o altar desta região para usar Fast Travel"
                        self.notice_timer = 2.3
                return
            return

        if event.key == pygame.K_y:
            self.overlay_screen = "rpg_v28"
            self.events.append("inventory")
            return

        if event.key == pygame.K_z:
            self.overlay_screen = "companions"
            self.events.append("rune")
            return

        if event.key == pygame.K_p:
            self.parry()
            return

        if event.key == pygame.K_x:
            self.execute_boss()
            return

        if event.key == pygame.K_k:
            self.overlay_screen = "craft"
            self.events.append("inventory")
            return

        if event.key == pygame.K_t:
            self.overlay_screen = "talents"
            self.events.append("rune")
            return

        if event.key == pygame.K_u:
            ok, message = upgrade_equipped(
                self.profile,
                "weapon",
            )
            self.notice = message
            self.notice_timer = 2.0
            self.events.append("forge" if ok else "error")
            return

        if event.key == pygame.K_o:
            self.overlay_screen = "accessibility"
            self.events.append("choice")
            return

        if event.key == pygame.K_l:
            self.overlay_screen = "factions"
            self.events.append("quest_complete")
            return

        if event.key == pygame.K_h:
            self.overlay_screen = "contracts"
            self.events.append("contract")
            return

        if event.key == pygame.K_m:
            self.overlay_screen = "map"
            self.map_selection = self.chapter["number"]
            self.events.append("rune")
            return

        if event.key == pygame.K_j:
            self.overlay_screen = "quests"
            self.events.append("choice")
            return

        if event.key == pygame.K_c:
            self.overlay_screen = "codex"
            self.events.append("choice")
            return

        if event.key == pygame.K_g:
            self.overlay_screen = "gear"
            self.events.append("inventory")
            return

        if event.key == pygame.K_f:
            self.heavy_attack()
            return

        if event.key == pygame.K_r:
            self._ally_assist()
            self.ally_cooldown = 2.4
            return

        if event.key in (pygame.K_i, pygame.K_TAB):
            self.inventory_open = not self.inventory_open
            self.events.append("choice")
            return

        if event.key == pygame.K_e:
            site = self.adventure_v28.nearest_site(
                self.player.pos
            )
            if site:
                message = self.adventure_v28.enter(
                    site
                )
                self.notice = message
                self.dialogue = (
                    site.name,
                    message,
                )
                self.notice_timer = 3.5
                self.events.append("rune")
                return

            building = self.world_v27.nearest_door(
                self.player.pos
            )
            if building:
                result = self.world_v27.enter(
                    building,
                    self.player.pos,
                )
                self.notice = result["text"]
                self.notice_timer = 2.2
                self.events.append(result["sfx"])
                return

            v26_result = self.v26.interact(self)
            if v26_result:
                self.notice = (
                    f"{v26_result['speaker']}: "
                    f"{v26_result['text']}"
                )
                self.dialogue = (
                    v26_result["speaker"],
                    v26_result["text"],
                )
                self.notice_timer = 5.0
                self.events.append(
                    v26_result.get("sfx", "voice_low")
                )
                if self.tutorial_active:
                    self._tutorial_advance(
                        4,
                        "Vila encontrada • tutorial concluído",
                    )
                return

            if (
                self.npc
                and self.player.pos.distance_to(self.npc.pos) <= 100
            ):
                line = self.npc.talk()
                quest_line = quest_step(
                    self.profile,
                    self.npc.name,
                )
                if quest_line:
                    line = f"{line}  {quest_line}"
                self.notice = f"{self.npc.name}: {line}"
                self.dialogue = (self.npc.name, line)
                self.notice_timer = 4.2
                self.events.append("rune")
                self._tutorial_advance(
                    4,
                    "Edda reconheceu você • tutorial concluído",
                )
                if not self.tutorial_active:
                    self.advance_story_echo()

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

            living_obj = self.living.nearest(self.player.pos)
            if living_obj is not None:
                text, sfx = self.living.interact(
                    living_obj,
                    self,
                )
                self.notice = living_obj.name
                self.dialogue = (
                    living_obj.name,
                    text,
                )
                self.notice_timer = 5.0
                self.events.append(sfx)
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

            place = self.nearest_place()
            if (
                place
                and self.player.pos.distance_to(place.pos) <= 86
            ):
                result = interact_with_place(
                    place,
                    self,
                )
                self.notice = result["title"]
                self.dialogue = (
                    result["title"],
                    result["text"],
                )
                self.notice_timer = 5.2
                self.events.append(result["sfx"])
                self.advance_story_echo()
                return

            chest = self.nearest_chest()
            if (
                chest
                and self.player.pos.distance_to(chest.pos) <= 78
            ):
                result = chest.open(self)
                self.notice = result["title"]
                self.dialogue = (
                    result["title"],
                    result["text"],
                )
                self.notice_timer = 5.0
                self.events.append(result["sfx"])
                return

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
        accessibility = self.profile.get(
            "accessibility",
            {},
        )
        if accessibility.get("screen_shake", True):
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
        if not accessibility.get("reduce_flash", False):
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
        if (
            self.player.attack_timer > 0
            and not self.combat_v28.can_cancel(
                self.player
            )
        ):
            return

        cost = self.combat_v28.stamina_cost(
            "attack",
            self.profile.get(
                "difficulty",
                "Normal",
            ),
        )
        if self.combat_v25.stamina < cost:
            self.notice = "Stamina insuficiente"
            self.notice_timer = 0.8
            return
        self.combat_v25.stamina -= cost

        self.player.attack_combo = (
            self.player.attack_combo + 1
        ) % 2
        self.player.attack_timer = 0.42
        self.combat_v27.on_attack("normal")
        self.events.append("sword")
        self._tutorial_advance(
            1,
            "Ataque dominado • use Q para o Pulso de Código",
        )
        attack_center = self.player.pos + self.player.facing * 55
        hitbox = self.combat_v28.attack_hitbox(
            self.player,
            heavy=False,
            frame_phase="active",
        )

        hit_any = False
        for enemy in self.enemies:
            if enemy.dead:
                continue
            enemy_box = pygame.Rect(
                0,
                0,
                enemy.radius * 2,
                enemy.radius * 2,
            )
            enemy_box.center = (
                int(enemy.pos.x),
                int(enemy.pos.y),
            )
            if hitbox.colliderect(enemy_box):
                hit_any = True
                stats = total_stats(self.profile)
                self.combat_v28.open_cancel_window(
                    0.14
                )
                crit = self.rng.random() < (
                    0.06 + stats["crit"]
                )
                combo_mult = self.combat_v25.next_combo()
                difficulty = balance(self.profile)
                damage = int(
                    (
                        22
                        + self.profile["level"] * 2
                        + stats["attack"]
                        + talent_bonus(
                            self.profile,
                            "attack_bonus",
                        )
                    )
                    * combo_mult
                    * difficulty["player_damage"]
                )
                if crit:
                    damage = int(damage * 1.7)
                    self.notice = "ACERTO CRÍTICO"
                    self.notice_timer = 0.9
                died = enemy.hit(damage)
                if not died:
                    delta = enemy.pos - self.player.pos
                    if delta.length_squared():
                        enemy.pos += delta.normalize() * 18
                    status = self._status_from_rune()
                    if status and self.rng.random() < 0.34:
                        self.combat_v25.apply_status(
                            enemy,
                            status,
                        )
                self._burst(enemy.pos, GOLD, 10)
                self._burst(
                    enemy.pos,
                    RED,
                    4 if not enemy.boss else 7,
                )
                self.impact_feedback(
                    strength=11 if enemy.boss else 6,
                    stop=0.075 if enemy.boss else 0.045,
                    flash=0.11,
                )
                if died:
                    self._enemy_defeated(enemy)

        if hit_any:
            self.events.append("blade_hit")

    def tech_pulse(self):
        if self.player.pulse_timer > 0 or self.player.energy < 24:
            if self.player.energy < 24:
                self.notice = "Energia insuficiente"
                self.notice_timer = 1.4
                self.events.append("error")
            return
        self.player.energy -= 24
        self.player.pulse_timer = 0.80
        self.combat_v27.on_attack("power")
        self._tutorial_advance(
            2,
            "Pulso dominado • experimente SHIFT",
        )
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
                if enemy.boss:
                    if self.boss_combat.add_stagger(18):
                        self.notice = "GUARDIÃO ATORDOADO"
                        self.notice_timer = 2.0
                if died:
                    self._enemy_defeated(enemy)

    def dash(self):
        if self.combat_v28.grab_timer > 0:
            if self.combat_v28.break_grab():
                self.notice = "AGARRE QUEBRADO"
                self.notice_timer = 1.0
                self.events.append("shield")
            return

        if self.player.dash_timer > 0 or self.player.energy < 15:
            return

        dodge_cost = self.combat_v28.stamina_cost(
            "dodge",
            self.profile.get(
                "difficulty",
                "Normal",
            ),
        )
        if self.combat_v25.stamina < dodge_cost:
            self.notice = "Stamina insuficiente"
            self.notice_timer = 0.8
            return
        self.player.energy -= 15
        self.combat_v25.stamina -= dodge_cost
        self.combat_v25.dodge_window = 0.24
        self.player.dodge_anim_timer = 0.30
        self.combat_v27.on_dodge()
        self.player.dash_timer = 0.7
        self._tutorial_advance(
            3,
            "Dash dominado • encontre Edda e pressione E",
        )
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
        elite = (
            enemy.boss
            or enemy.archetype
            in {"elite_raider", "berserker", "alpha_wolf"}
        )
        grant_materials(
            self.profile,
            self.rng,
            elite=elite,
        )
        if self.profile["kills"] % 8 == 0:
            self.profile["skill_points"] += 1
        for message in self.quest_v27.on_kill(
            enemy.archetype
        ):
            self.notice = message
            self.notice_timer = 3.0
            self.events.append("quest_complete")

        for message in self.v26.on_enemy_defeated(
            enemy.archetype
        ):
            self.notice = message
            self.notice_timer = 3.0
            self.events.append("contract")

        for ally in self.companion_v28.active:
            message = (
                self.companion_v28.friendship_gain(
                    ally,
                    1,
                )
            )
            if message:
                self.notice = message
                self.notice_timer = 2.4
                self.events.append("quest_complete")

        if self.profile["kills"] % 2 == 0:
            self.advance_story_echo()
        xp_gain = 3 if enemy.boss else 1
        leveled = self.player.gain_xp(xp_gain)
        self.events.append("victory")
        self._burst(
            enemy.pos,
            GOLD if enemy.boss else self.theme["accent"],
            30 if enemy.boss else 18,
        )

        if enemy.boss:
            if self.chapter["number"] == 7:
                ending = self.quest_v27.finalize_ending()
                self.dialogue = (
                    "DESTINO DE VALDRAK",
                    ending,
                )
                self.events.append("ending_good")
            self.cinematic_v26.start(
                "GUARDIÃO DERROTADO",
                f"{enemy.name} caiu. A região reage à vitória.",
                duration=3.4,
                kind="boss_defeat",
            )
            self.events.append("boss_defeat")
            unlock_codex(self.profile, "guardioes")
            item = roll_equipment(
                self.chapter["number"],
                self.rng,
                boss=True,
            )
            equipped = add_and_auto_equip(
                self.profile,
                item,
            )
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
            self.notice += (
                f" • {item['rarity']} {item['name']}"
                + (" equipado" if equipped else "")
            )
        else:
            if self.rng.random() < 0.24:
                gear = roll_equipment(
                    self.chapter["number"],
                    self.rng,
                    elite=enemy.archetype
                    in {"elite_raider", "berserker", "alpha_wolf"},
                )
                auto = add_and_auto_equip(
                    self.profile,
                    gear,
                )
                self.notice = (
                    f"Loot: {gear['rarity']} {gear['name']}"
                    + (" • equipado" if auto else "")
                )
                self.notice_timer = 2.3

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

    def nearest_chest(self):
        if not self.chests:
            return None
        return min(
            self.chests,
            key=lambda chest: self.player.pos.distance_to(chest.pos),
        )

    def active_objective(self):
        if self.tutorial_active:
            objectives = [
                "TUTORIAL — mova-se com WASD ou setas",
                "TUTORIAL — ataque com ESPAÇO",
                "TUTORIAL — use o Pulso de Código com Q",
                "TUTORIAL — faça um dash com SHIFT",
                "TUTORIAL — encontre Edda e fale com E",
            ]
            return objectives[
                min(self.tutorial_stage, len(objectives) - 1)
            ]
        return self.exploration_quest_name()

    def _tutorial_advance(self, expected, message):
        if not self.tutorial_active or self.tutorial_stage != expected:
            return

        self.tutorial_stage += 1
        self.profile["tutorial_stage"] = self.tutorial_stage
        self.notice = message
        self.notice_timer = 2.6
        self.events.append("rune")

        if self.tutorial_stage >= 5:
            self.tutorial_active = False
            self.profile["tutorial_complete"] = True
            self.notice = "Prólogo jogável concluído • Valdrak está aberto"
            self.notice_timer = 4.0
            self.player.gain_xp(2)
            self.events.append("victory")

    def start_story_echo(self, speaker=None, text=None):
        if text:
            self.dialogue = (speaker or self.chapter["title"], text)
            self.notice_timer = 6.0
            return

        if not self.story_echoes:
            return

        item = self.story_echoes[0]
        self.dialogue = (
            self.chapter["title"],
            item.get("text", ""),
        )
        self.notice_timer = 5.2
        self.events.append(item.get("sfx", "rune"))
        self.story_echo_index = 1

    def advance_story_echo(self):
        if self.story_echo_index >= len(self.story_echoes):
            return

        item = self.story_echoes[self.story_echo_index]
        self.story_echo_index += 1
        self.dialogue = (
            self.chapter["title"],
            item.get("text", ""),
        )
        self.notice_timer = 5.2
        self.events.append(item.get("sfx", "rune"))

    def nearest_place(self):
        if not self.places:
            return None
        return min(
            self.places,
            key=lambda place: self.player.pos.distance_to(place.pos),
        )

    def exploration_progress(self):
        return region_progress(
            self.chapter["number"],
            self.profile,
        )

    def exploration_quest_name(self):
        return region_quest_name(
            self.chapter["number"]
        )

    def _ally_assist(self):
        allies = self.engine.ally_names()
        self.companion_v28.sync(allies)
        result = self.companion_v28.assist(
            self
        )
        if not result:
            return
        message, sfx = result
        self.notice = message
        self.notice_timer = 1.4
        if sfx:
            self.events.append(sfx)
        self.impact_feedback(
            strength=7,
            stop=0.04,
            flash=0.06,
        )

    def update(self, dt, keys):
        self.notice_timer = max(0.0, self.notice_timer - dt)
        self.cinematic_v26.update(dt)
        self.combat_v27.update(
            dt,
            self.player,
        )
        self.combat_v25.update(
            dt,
            moving=self.player.is_moving,
        )
        self.combat_v28.update(
            dt,
            self,
        )
        self.dungeon_v28.update(dt)
        for defeated in self.combat_v25.update_statuses(dt):
            if defeated.dead:
                self._enemy_defeated(defeated)

        if self.living.interior:
            self._update_music_state()
            return
        self.shake_timer = max(0.0, self.shake_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)

        if self.hit_stop > 0:
            self.hit_stop = max(0.0, self.hit_stop - dt)
            for particle in self.particles:
                particle.update(dt * 0.18)
            return

        if self.inventory_open:
            return

        ambient_event = self.world_v27.update(
            dt,
            self.v26.hour,
        )
        if ambient_event:
            self.events.append(ambient_event)

        self.player.speed = (
            250
            * self.world_v27.movement_multiplier()
        )
        drain = self.world_v27.stamina_drain()
        if drain:
            self.combat_v25.stamina -= drain * dt

        if self.combat_v28.grab_timer <= 0:
            self.player.update(
                dt,
                keys,
                self.obstacles,
            )
        else:
            self.player.is_moving = False

        self.adventure_v28.update_position(
            self.player.pos
        )

        self.step_timer = max(
            0.0,
            self.step_timer - dt,
        )
        if (
            self.player.is_moving
            and self.step_timer <= 0
        ):
            self.events.append(
                self.world_v27.footstep_event()
            )
            self.step_timer = 0.34

        self.ally_cooldown = max(
            0.0,
            self.ally_cooldown - dt,
        )

        if (
            self.tutorial_active
            and self.tutorial_stage == 0
            and self.player.pos.distance_to(self.tutorial_origin) >= 85
        ):
            self._tutorial_advance(
                0,
                "Movimento dominado • agora ataque com ESPAÇO",
            )

        if self.ally_cooldown <= 0:
            self._ally_assist()
            self.ally_cooldown = 2.4

        living_event = self.living.update(dt, self)
        if living_event:
            if living_event["kind"] == "ambush":
                for _ in range(living_event["count"]):
                    self._spawn_living_enemy()
                self.notice = living_event["text"]
                self.notice_timer = 3.0
                self.events.append("shield")
            else:
                self.notice = living_event["text"]
                self.notice_timer = 2.8
                self.events.append(living_event.get("sfx", "wind"))

        v26_event = self.v26.update(dt, self)
        if v26_event:
            self.notice = (
                f"{v26_event['title']}: "
                f"{v26_event['text']}"
            )
            self.dialogue = (
                v26_event["title"],
                v26_event["text"],
            )
            self.notice_timer = 5.0
            self.events.append(
                v26_event.get("sfx", "rare_event")
            )
            self.cinematic_v26.start(
                v26_event["title"],
                v26_event["text"],
                duration=3.0,
                kind="rare",
            )

        boss = self.boss()
        boss_cinematic_id = (
            f"boss_intro_{self.chapter['number']}"
        )
        if (
            boss
            and not boss.dead
            and boss.pos.distance_to(self.player.pos) < 460
            and boss_cinematic_id
            not in self.profile["v26_cinematics"]
        ):
            self.profile["v26_cinematics"].append(
                boss_cinematic_id
            )
            self.cinematic_v26.start(
                f"GUARDIÃO — {boss.name}",
                "Observe o telegraph, preserve stamina e procure a janela de stagger.",
                duration=3.2,
                kind="boss",
            )
            self.events.append("voice_warrior")

        if (
            boss
            and not boss.dead
            and not self.v27_boss_phase2
            and boss.hp <= boss.max_hp * 0.5
        ):
            self.v27_boss_phase2 = True
            self.combat_v27.on_boss_phase(
                boss.name,
                2,
            )
            self.cinematic_v26.start(
                f"{boss.name} — FASE 2",
                "O Guardião muda o ritmo. Novos ataques e menos janelas seguras.",
                duration=3.0,
                kind="boss_phase",
            )
            self.events.extend(
                ["voice_warrior", "thunder"]
            )

        boss_event = self.boss_combat.update(
            dt,
            self.boss(),
            self.player,
        )
        if boss_event:
            move = boss_event["move"]
            if boss_event["kind"] == "telegraph_start":
                self.notice = f"GUARDIÃO: {move['name']}"
                self.notice_timer = 1.1
                self.events.append("rune")
            elif boss_event["kind"] == "resolve":
                self.events.append(move["sfx"])
                if boss_event["hit"]:
                    self._damage_player(move["damage"])
                    self._burst(
                        self.player.pos,
                        RED,
                        12,
                    )
                    self.impact_feedback(
                        strength=11,
                        stop=0.06,
                        flash=0.11,
                    )

        self._update_music_state()

        for enemy in self.enemies:
            enemy.update(dt, self.player.pos)
            if enemy.dead:
                continue

            distance = enemy.pos.distance_to(
                self.player.pos
            )
            phase = (
                2
                if enemy.boss
                and self.v27_boss_phase2
                else 1
            )
            combo = self.combat_v28.enemy_combo(
                enemy.archetype,
                phase=phase,
            )
            combo_index = getattr(
                enemy,
                "v28_combo_index",
                0,
            )
            action = combo[
                combo_index % len(combo)
            ]

            if (
                enemy.archetype
                in {"archer", "rune_mage", "raven"}
                and 95 <= distance <= 380
                and enemy.attack_cd <= 0
            ):
                self.combat_v28.spawn_enemy_projectile(
                    enemy,
                    self.player,
                )
                enemy.v28_combo_index = (
                    combo_index + 1
                ) % len(combo)
                enemy.attack_cd = (
                    1.15
                    if action == "projectile"
                    else 0.9
                )
                self.events.append(
                    "sword"
                    if enemy.archetype == "archer"
                    else "rune"
                )
                continue

            if (
                distance <= enemy.radius + 29
                and enemy.attack_cd <= 0
            ):
                if (
                    action in {"heavy", "lunge"}
                    and self.rng.random() < 0.22
                    and self.combat_v28.try_grab(
                        enemy,
                        self.player,
                    )
                ):
                    self.notice = (
                        "AGARRADO • SHIFT para escapar"
                    )
                    self.notice_timer = 1.2
                    self.events.append("shield")
                    enemy.attack_cd = 1.25
                    continue

                multiplier = {
                    "heavy": 1.45,
                    "bite": 1.20,
                    "lunge": 1.28,
                    "burst": 1.35,
                }.get(action, 1.0)
                damage = max(
                    1,
                    int(enemy.damage * multiplier),
                )
                if self._damage_player(damage):
                    enemy.v28_combo_index = (
                        combo_index + 1
                    ) % len(combo)
                    enemy.attack_cd = (
                        0.68
                        if len(combo) >= 3
                        else 0.88
                    )
                    self.events.append("wolf")
                    self._burst(
                        self.player.pos,
                        RED,
                        9,
                    )
                    self.impact_feedback(
                        strength=(
                            12 if enemy.boss else 7
                        ),
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

        if self.dungeon_v28.active:
            self.dungeon_v28.draw(
                surface,
                fonts,
                theme["accent"],
            )
            return

        if self.adventure_v28.current_site:
            self.adventure_v28.draw_site(
                surface,
                fonts,
                theme["accent"],
                seconds,
            )
            return

        if self.world_v27.interior:
            self.world_v27.draw_interior(
                surface,
                fonts,
                seconds,
            )
            return

        if self.living.interior:
            self.living.draw_interior(
                surface,
                fonts,
                theme["accent"],
            )
            return

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
        self.art_v26.draw_world(
            surface,
            self.camera,
            seconds,
        )
        self.visual_v25.draw_environment(
            surface,
            self.camera,
            seconds,
            theme["accent"],
        )
        self.world_v27.draw_exterior(
            surface,
            self.camera,
            fonts,
            seconds,
            self.v26.hour,
            self.player.pos,
        )
        self.adventure_v28.draw_exterior(
            surface,
            self.camera,
            fonts,
            seconds,
            self.player.pos,
        )

        items = []

        if not self.map_scene.available:
            for rect in self.obstacles[4:]:
                items.append(
                    (rect.bottom, "obstacle", rect)
                )

        for shrine in self.shrines:
            items.append(
                (shrine.pos.y, "shrine", shrine)
            )

        for place in self.places:
            items.append(
                (place.pos.y, "place", place)
            )
        for chest in self.chests:
            items.append(
                (chest.pos.y, "chest", chest)
            )
        if self.npc:
            items.append((self.npc.pos.y, "npc", self.npc))
        for enemy in self.enemies:
            if not enemy.dead:
                items.append((enemy.pos.y, "enemy", enemy))
        items.append((self.player.pos.y, "player", self.player))

        available_allies = self.engine.ally_names()
        self.companion_v28.sync(
            available_allies
        )
        ally_names = self.companion_v28.active
        for index, ally_name in enumerate(
            ally_names[:2]
        ):
            pos = self._ally_pos(index)
            items.append((pos.y, "ally", (ally_name, pos, index)))

        for villager in self.v26.villagers:
            items.append(
                (villager.pos.y, "v26_npc", villager)
            )

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
            elif kind == "place":
                near_place = (
                    self.player.pos.distance_to(item.pos) <= 100
                )
                item.draw(
                    surface,
                    self.camera,
                    fonts["small"],
                    seconds,
                    near=near_place,
                )
            elif kind == "chest":
                near_chest = (
                    self.player.pos.distance_to(item.pos) <= 95
                )
                item.draw(
                    surface,
                    self.camera,
                    fonts["small"],
                    theme["accent"],
                    seconds,
                    near=near_chest,
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
            elif kind == "v26_npc":
                item.draw(
                    surface,
                    self.camera,
                    fonts,
                    seconds,
                    near=(
                        self.player.pos.distance_to(item.pos)
                        <= 95
                    ),
                )
            elif kind == "enemy":
                item.draw(surface, self.camera)
            elif kind == "player":
                item.draw(
                    surface,
                    self.camera,
                    theme["accent"],
                )
                draw_player_equipment_v28(
                    surface,
                    (
                        int(
                            self.player.pos.x
                            - self.camera.x
                        ),
                        int(
                            self.player.pos.y
                            - self.camera.y
                        ),
                    ),
                    self.profile,
                    self.player.facing,
                )
            else:
                draw_ally(
                    surface,
                    item[0],
                    item[1],
                    self.camera,
                    seconds,
                    item[2],
                )

        self.living.draw(
            surface,
            self.camera,
            fonts,
            seconds,
            self.player.pos,
        )
        self.v26.draw(
            surface,
            self.camera,
            fonts,
            seconds,
            self.player.pos,
        )
        self.quest_v27.draw_markers(
            surface,
            self.camera,
            fonts,
            self.v26,
            self.enemies,
        )

        for loot in self.loots:
            loot.draw(surface, self.camera, seconds)

        for particle in self.particles:
            particle.draw(surface, self.camera)

        self.combat_v28.draw(
            surface,
            self.camera,
            fonts,
        )

        self.visual_v25.draw_lighting(
            surface,
            self,
            seconds,
        )
        self.art_v26.draw_foreground(
            surface,
            self,
            seconds,
        )
        self.combat_v27.draw_world_fx(
            surface,
            self.camera,
            self.player,
            theme["accent"],
        )
        self.world_v27.draw_day_night(
            surface,
            self.v26.hour,
        )
        self.world_v27.draw_weather(
            surface,
            seconds,
        )
        self._draw_boss_telegraph(
            surface,
            theme,
        )

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
        self._draw_v25_stamina(
            surface,
            fonts,
            theme,
        )

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

        if self.overlay_screen:
            if self.overlay_screen == "rpg_v28":
                self.rpg_v28.draw_inventory(
                    surface,
                    fonts,
                    theme["accent"],
                    self.companion_v28.active,
                )
            elif self.overlay_screen == "companions":
                self.companion_v28.draw(
                    surface,
                    fonts,
                    theme["accent"],
                    self.engine.ally_names(),
                    self.rpg_v28,
                )
            elif self.overlay_screen == "factions":
                self.quest_v27.draw_overlay(
                    surface,
                    fonts,
                    theme["accent"],
                )
            elif self.overlay_screen == "contracts":
                self.v26.draw_contracts(
                    surface,
                    fonts,
                    theme["accent"],
                )
            elif self.overlay_screen in {
                "craft",
                "talents",
                "vendor",
                "accessibility",
            }:
                self._draw_v25_meta_overlay(
                    surface,
                    fonts,
                    theme,
                )
            else:
                self._draw_v24_overlay(
                    surface,
                    fonts,
                    theme,
                )

        self.combat_v27.draw_screen_fx(
            surface,
            fonts,
            theme["accent"],
        )
        self.cinematic_v26.draw(
            surface,
            fonts,
            theme["accent"],
        )

        draw_final_ui_frame(
            surface,
            theme["accent"],
        )

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
        # Two-row formation behind the player prevents six allies
        # from occupying the same visual space.
        formations = [
            (-88, 58),
            (88, 58),
            (-135, 105),
            (135, 105),
            (-56, 128),
            (56, 128),
        ]
        if index < len(formations):
            ox, oy = formations[index]
        else:
            angle = math.pi * 0.25 + index * 0.72
            ox = math.cos(angle) * 145
            oy = 105 + math.sin(angle) * 55
        return self.player.pos + pygame.Vector2(ox, oy)

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
        site = self.adventure_v28.nearest_site(
            self.player.pos
        )
        if site:
            return f"E — explorar: {site.name}"

        building = self.world_v27.nearest_door(
            self.player.pos
        )
        if building:
            return f"E — entrar: {building.name}"

        v26_nearest = self.v26.nearest(
            self.player.pos
        )
        if v26_nearest:
            kind, obj = v26_nearest
            if kind == "npc":
                return f"E — falar com {obj.name}"
            if kind == "secret":
                return "E — investigar segredo"
            return f"E — encontro: {obj.name}"

        nearest = self.nearest_shrine()
        place = self.nearest_place()
        chest = self.nearest_chest()

        living_obj = self.living.nearest(self.player.pos)
        if living_obj is not None:
            return f"E — interagir: {living_obj.name}"

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

        if (
            place
            and self.player.pos.distance_to(
                place.pos
            )
            <= 86
        ):
            status = (
                "revisitar"
                if place.discovered
                else "descobrir"
            )
            return f"E — {status}: {place.name}"

        if (
            chest
            and self.player.pos.distance_to(chest.pos) <= 78
        ):
            action = "examinar" if chest.opened else "abrir"
            return f"E — {action}: {chest.name}"

        return ""

    def _draw_hud(self, surface, fonts, theme):
        self.hud.draw(
            surface,
            fonts,
            self,
            theme,
        )

    def _draw_boss_telegraph(self, surface, theme):
        boss = self.boss()
        move = self.boss_combat.pending
        if not boss or boss.dead or not move:
            return

        x = int(boss.pos.x - self.camera.x)
        y = int(boss.pos.y - self.camera.y)
        radius = min(250, int(move["range"]))
        warning = pygame.Surface(
            (radius * 2 + 8, radius * 2 + 8),
            pygame.SRCALPHA,
        )
        pygame.draw.circle(
            warning,
            (225, 82, 92, 42),
            (radius + 4, radius + 4),
            radius,
        )
        pygame.draw.circle(
            warning,
            (255, 118, 92, 205),
            (radius + 4, radius + 4),
            radius,
            3,
        )
        surface.blit(
            warning,
            (x - radius - 4, y - radius - 4),
        )

    def _draw_v25_stamina(self, surface, fonts, theme):
        value = self.combat_v25.stamina
        maximum = self.profile["max_stamina"]
        ratio = value / max(1, maximum)
        rect = pygame.Rect(485, 646, 310, 10)
        pygame.draw.rect(
            surface,
            (23, 30, 39),
            rect,
            border_radius=5,
        )
        pygame.draw.rect(
            surface,
            GOLD,
            (
                rect.x,
                rect.y,
                int(rect.width * ratio),
                rect.height,
            ),
            border_radius=5,
        )
        label = fonts["small"].render(
            f"STAMINA {int(value)}/{maximum}",
            True,
            (205, 213, 221),
        )
        surface.blit(
            label,
            label.get_rect(midbottom=(640, 644)),
        )

    def _draw_v25_meta_overlay(
        self,
        surface,
        fonts,
        theme,
    ):
        veil = pygame.Surface(
            (1280, 720),
            pygame.SRCALPHA,
        )
        veil.fill((0, 0, 0, 215))
        surface.blit(veil, (0, 0))

        panel = pygame.Rect(180, 82, 920, 560)
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

        titles = {
            "craft": "FORJA & CRAFTING",
            "talents": "ÁRVORE DE TALENTOS",
            "vendor": "MERCADOR DE VALDRAK",
            "accessibility": "ACESSIBILIDADE & BALANCEAMENTO",
        }
        surface.blit(
            fonts["title"].render(
                titles[self.overlay_screen],
                True,
                INK,
            ),
            (225, 120),
        )
        y = 190

        if self.overlay_screen == "craft":
            mats = self.profile["materials"]
            summary = "  ".join(
                f"{k.upper()} {v}"
                for k, v in mats.items()
            )
            surface.blit(
                fonts["small"].render(
                    summary,
                    True,
                    theme["accent"],
                ),
                (225, y),
            )
            y += 50
            for index, recipe in enumerate(RECIPES, 1):
                cost = ", ".join(
                    f"{key}:{value}"
                    for key, value in recipe["cost"].items()
                )
                line = f"{index}. {recipe['name']} — {cost}"
                surface.blit(
                    fonts["body"].render(
                        line,
                        True,
                        INK,
                    ),
                    (225, y),
                )
                y += 58
            hint = "1/2/3 cria • U melhora arma • K/Esc fecha"

        elif self.overlay_screen == "talents":
            surface.blit(
                fonts["heading"].render(
                    f"PONTOS: {self.profile['skill_points']}",
                    True,
                    GOLD,
                ),
                (225, y),
            )
            y += 52
            for index, (
                name,
                key,
                value,
            ) in enumerate(TALENTS[:3], 1):
                unlocked = key in self.profile["talents"]
                suffix = (
                    "DESBLOQUEADO"
                    if unlocked
                    else f"+{value} {key}"
                )
                surface.blit(
                    fonts["body"].render(
                        f"{index}. {name} — {suffix}",
                        True,
                        theme["accent"]
                        if unlocked
                        else INK,
                    ),
                    (225, y),
                )
                y += 62
            hint = "1/2/3 desbloqueia • T/Esc fecha"

        elif self.overlay_screen == "vendor":
            surface.blit(
                fonts["heading"].render(
                    f"MOEDAS: {self.profile['coins']}",
                    True,
                    GOLD,
                ),
                (225, y),
            )
            y += 54
            prices = {
                "Comum": 25,
                "Raro": 48,
                "Épico": 85,
                "Lendário": 140,
            }
            for index, item in enumerate(
                self.vendor_items,
                1,
            ):
                line = (
                    f"{index}. {item['rarity']} {item['name']} "
                    f"+{item['value']} {item['stat']} "
                    f"— {prices[item['rarity']]} moedas"
                )
                surface.blit(
                    fonts["body"].render(
                        line,
                        True,
                        INK,
                    ),
                    (225, y),
                )
                y += 62
            hint = "1/2/3 compra • Esc fecha"

        else:
            settings = self.profile["accessibility"]
            labels = [
                ("Alto contraste", "high_contrast"),
                ("Reduzir flashes", "reduce_flash"),
                ("Screen shake", "screen_shake"),
                ("UI ampliada", "large_ui"),
            ]
            for index, (label, key) in enumerate(
                labels,
                1,
            ):
                state = "ON" if settings[key] else "OFF"
                surface.blit(
                    fonts["body"].render(
                        f"{index}. {label}: {state}",
                        True,
                        INK,
                    ),
                    (225, y),
                )
                y += 58

            surface.blit(
                fonts["body"].render(
                    f"5. Dificuldade: {self.profile['difficulty']}",
                    True,
                    GOLD,
                ),
                (225, y),
            )
            hint = "1-4 alterna • 5 dificuldade • O/Esc fecha"

        surface.blit(
            fonts["small"].render(
                hint,
                True,
                (155, 170, 185),
            ),
            (225, 602),
        )

    def _draw_v24_overlay(self, surface, fonts, theme):
        veil = pygame.Surface(
            (1280, 720),
            pygame.SRCALPHA,
        )
        veil.fill((0, 0, 0, 205))
        surface.blit(veil, (0, 0))

        panel = pygame.Rect(185, 78, 910, 570)
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

        titles = {
            "map": "MAPA MUNDIAL DE VALDRAK",
            "quests": "QUEST LOG",
            "codex": "CODEX DE VALDRAK",
            "gear": "EQUIPAMENTOS",
        }
        surface.blit(
            fonts["title"].render(
                titles[self.overlay_screen],
                True,
                INK,
            ),
            (225, 112),
        )

        y = 180
        if self.overlay_screen == "map":
            for number, name, status in world_map_lines(
                self.profile,
                self.chapter["number"],
            ):
                selected = number == self.map_selection
                color = (
                    theme["accent"]
                    if selected
                    else (155, 170, 185)
                )
                line = (
                    f"{'▶' if selected else ' '} "
                    f"{number}. {name} — {status}"
                )
                surface.blit(
                    fonts["body"].render(
                        line,
                        True,
                        color,
                    ),
                    (240, y),
                )
                y += 48
            hint = (
                "↑/↓ seleciona • Enter viaja "
                "quando o Altar da região estiver ativo"
            )
        elif self.overlay_screen == "quests":
            for line in quest_lines(
                self.profile,
                self.chapter["number"],
                self.boss_alive(),
            ):
                surface.blit(
                    fonts["body"].render(
                        line,
                        True,
                        INK,
                    ),
                    (240, y),
                )
                y += 58
            y += 10
            for line in self.v26.journal_lines():
                surface.blit(
                    fonts["small"].render(
                        line,
                        True,
                        theme["accent"],
                    ),
                    (240, y),
                )
                y += 28
            hint = "J ou Esc fecha o Quest Log • H contratos"
        elif self.overlay_screen == "codex":
            for title, body in codex_lines(self.profile)[:7]:
                surface.blit(
                    fonts["heading"].render(
                        title,
                        True,
                        GOLD,
                    ),
                    (240, y),
                )
                surface.blit(
                    fonts["small"].render(
                        body[:92],
                        True,
                        (155, 170, 185),
                    ),
                    (240, y + 28),
                )
                y += 65
            hint = "C ou Esc fecha o Codex"
        else:
            stats = equipment_stats(self.profile)
            for slot in ("weapon", "armor", "amulet", "rune"):
                item = self.profile["equipped"].get(slot)
                if item:
                    line = (
                        f"{slot.upper()}: "
                        f"{item['rarity']} {item['name']} "
                        f"(+{item['value']} {item['stat']})"
                    )
                else:
                    line = f"{slot.upper()}: vazio"
                surface.blit(
                    fonts["body"].render(
                        line,
                        True,
                        INK,
                    ),
                    (240, y),
                )
                y += 52
            y += 12
            summary = (
                f"ATQ +{stats['attack']}  DEF +{stats['defense']}  "
                f"CRIT +{int(stats['crit'] * 100)}%  ENERGIA +{stats['energy']}"
            )
            surface.blit(
                fonts["body"].render(
                    summary,
                    True,
                    theme["accent"],
                ),
                (240, y),
            )
            hint = "G ou Esc fecha Equipamentos"

        surface.blit(
            fonts["small"].render(
                hint,
                True,
                (155, 170, 185),
            ),
            (240, 605),
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
                "Fragmento antigo",
            ),
            (
                "Relíquia de Memória",
                inventory.get("reliquia", 0),
                VIOLET,
                "Microconto descoberto",
            ),
            (
                "Chave Rúnica",
                inventory.get("chave", 0),
                GREEN,
                "Recompensa de exploração",
            ),
        ]

        for index, (name, count, color, effect) in enumerate(cards):
            rect = pygame.Rect(
                292,
                244 + index * 58,
                690,
                50,
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
                (rect.x + 62, rect.y + 6),
            )
            surface.blit(
                fonts["small"].render(
                    effect,
                    True,
                    MUTED,
                ),
                (rect.x + 62, rect.y + 27),
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
            (294, 548),
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
            (294, 574),
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
