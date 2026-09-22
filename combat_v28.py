import math

import pygame


class Projectile:
    def __init__(self, pos, velocity, damage, owner="enemy", color=(225, 82, 92)):
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity)
        self.damage = damage
        self.owner = owner
        self.color = color
        self.life = 3.0
        self.dead = False

    def update(self, dt):
        self.pos += self.velocity * dt
        self.life -= dt
        if self.life <= 0:
            self.dead = True

    def draw(self, surface, camera):
        x = int(self.pos.x - camera.x)
        y = int(self.pos.y - camera.y)
        pygame.draw.circle(surface, self.color, (x, y), 7)
        pygame.draw.circle(surface, (244, 239, 223), (x, y), 3)


class CombatCoreV28:
    def __init__(self, profile):
        self.profile = profile
        self.profile.setdefault("v28_finishers", 0)
        self.profile.setdefault("v28_perfect_parries", 0)
        self.profile.setdefault("v28_grab_breaks", 0)
        self.projectiles = []
        self.cancel_timer = 0.0
        self.enemy_combo_clock = 0.0
        self.grab_timer = 0.0
        self.grab_source = None
        self.finisher_timer = 0.0
        self.last_finisher = None

    def update(self, dt, world):
        self.cancel_timer = max(0.0, self.cancel_timer - dt)
        self.enemy_combo_clock += dt
        self.grab_timer = max(0.0, self.grab_timer - dt)
        self.finisher_timer = max(0.0, self.finisher_timer - dt)

        for projectile in list(self.projectiles):
            projectile.update(dt)
            if projectile.dead:
                continue
            if projectile.owner == "enemy":
                if projectile.pos.distance_to(world.player.pos) <= 24:
                    if world._damage_player(projectile.damage):
                        world.events.append("blade_hit")
                    projectile.dead = True
            else:
                for enemy in world.enemies:
                    if not enemy.dead and projectile.pos.distance_to(enemy.pos) <= 28:
                        died = enemy.hit(projectile.damage)
                        projectile.dead = True
                        if died:
                            world._enemy_defeated(enemy)
                        break
        self.projectiles = [p for p in self.projectiles if not p.dead]

    def attack_hitbox(self, player, heavy=False, frame_phase="active"):
        facing = player.facing if player.facing.length_squared() else pygame.Vector2(0, 1)
        center = player.pos + facing * (76 if heavy else 58)
        size = (128, 96) if heavy else (96, 74)
        rect = pygame.Rect(0, 0, *size)
        rect.center = (int(center.x), int(center.y))
        if frame_phase != "active":
            rect.inflate_ip(-44, -28)
        return rect

    def can_cancel(self, player):
        if player.attack_timer <= 0:
            return True
        return player.attack_timer <= 0.15 or self.cancel_timer > 0

    def open_cancel_window(self, duration=0.14):
        self.cancel_timer = max(self.cancel_timer, duration)

    def stamina_cost(self, action, difficulty="Normal"):
        base = {
            "attack": 3,
            "heavy": 22,
            "parry": 14,
            "dodge": 18,
            "finisher": 12,
        }.get(action, 0)
        multiplier = 0.9 if difficulty == "Explorador" else 1.12 if difficulty == "Saga" else 1.0
        return int(round(base * multiplier))

    def parry_window(self, archetype):
        return {
            "raider": 0.22,
            "berserker": 0.17,
            "archer": 0.25,
            "rune_mage": 0.20,
            "wolf": 0.19,
            "alpha_wolf": 0.15,
            "raven": 0.24,
            "elite_raider": 0.14,
            "boss": 0.12,
        }.get(archetype, 0.20)

    def enemy_combo(self, archetype, phase=1):
        patterns = {
            "raider": ("slash", "slash"),
            "berserker": ("slash", "heavy", "heavy"),
            "archer": ("projectile", "sidestep", "projectile"),
            "rune_mage": ("projectile", "projectile", "burst"),
            "wolf": ("lunge", "bite"),
            "alpha_wolf": ("lunge", "bite", "lunge"),
            "raven": ("dash", "projectile"),
            "elite_raider": ("slash", "parry", "heavy"),
        }
        combo = list(patterns.get(archetype, ("slash",)))
        if phase >= 2:
            combo.append("heavy")
        return tuple(combo)

    def spawn_enemy_projectile(self, enemy, player):
        delta = player.pos - enemy.pos
        if not delta.length_squared():
            return
        speed = 330 if enemy.archetype == "archer" else 250
        color = (225, 82, 92) if enemy.archetype == "archer" else (158, 116, 255)
        self.projectiles.append(
            Projectile(
                enemy.pos,
                delta.normalize() * speed,
                8 + max(0, getattr(enemy, "damage", 10) // 3),
                owner="enemy",
                color=color,
            )
        )

    def try_grab(self, enemy, player):
        if enemy.boss or enemy.archetype in {"berserker", "alpha_wolf", "elite_raider"}:
            if enemy.pos.distance_to(player.pos) <= 46 and self.grab_timer <= 0:
                self.grab_timer = 0.85
                self.grab_source = enemy
                return True
        return False

    def break_grab(self):
        if self.grab_timer > 0:
            self.grab_timer = 0
            self.grab_source = None
            self.profile["v28_grab_breaks"] += 1
            return True
        return False

    def finisher_available(self, enemy, player):
        if enemy.dead:
            return False
        ratio = enemy.hp / max(1, enemy.max_hp)
        return ratio <= 0.18 and enemy.pos.distance_to(player.pos) <= 96

    def finisher(self, enemy):
        damage = max(1, int(enemy.max_hp * 0.35))
        self.finisher_timer = 0.9
        self.last_finisher = enemy.archetype
        self.profile["v28_finishers"] += 1
        return damage

    def draw(self, surface, camera, fonts):
        for projectile in self.projectiles:
            projectile.draw(surface, camera)
        if self.grab_timer > 0:
            label = fonts["heading"].render("AGARRADO — pressione SHIFT para escapar", True, (245, 170, 88))
            surface.blit(label, label.get_rect(center=(640, 185)))
        if self.finisher_timer > 0:
            label = fonts["title"].render("FINISHER", True, (231, 190, 93))
            surface.blit(label, label.get_rect(center=(640, 205)))
