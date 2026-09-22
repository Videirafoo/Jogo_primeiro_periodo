import math

import pygame


class CombatPresentationV27:
    def __init__(self):
        self.attack_kind = None
        self.attack_timer = 0.0
        self.attack_total = 0.0
        self.hit_timer = 0.0
        self.parry_timer = 0.0
        self.dodge_timer = 0.0
        self.execution_timer = 0.0
        self.knockdown_timer = 0.0
        self.camera_kick = 0.0
        self.phase_banner = None
        self.phase_timer = 0.0
        self.trail = []
        self.impact_bursts = []

    def update(self, dt, player):
        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.hit_timer = max(0.0, self.hit_timer - dt)
        self.parry_timer = max(0.0, self.parry_timer - dt)
        self.dodge_timer = max(0.0, self.dodge_timer - dt)
        self.execution_timer = max(0.0, self.execution_timer - dt)
        self.knockdown_timer = max(0.0, self.knockdown_timer - dt)
        self.camera_kick = max(0.0, self.camera_kick - dt * 5.5)
        self.phase_timer = max(0.0, self.phase_timer - dt)
        if self.phase_timer <= 0:
            self.phase_banner = None

        if self.attack_timer > 0 and self.attack_total > 0:
            progress = 1 - self.attack_timer / self.attack_total
            facing = player.facing if player.facing.length_squared() else pygame.Vector2(0, 1)
            normal = pygame.Vector2(-facing.y, facing.x)
            swing = math.sin(progress * math.pi) * 48
            point = player.pos + facing * (42 + swing * 0.55) + normal * math.cos(progress * math.pi) * 32
            self.trail.append((point.copy(), 0.18, self.attack_kind or "normal"))

        new_trail = []
        for point, life, kind in self.trail:
            life -= dt
            if life > 0:
                new_trail.append((point, life, kind))
        self.trail = new_trail[-18:]

        bursts = []
        for point, life, heavy in self.impact_bursts:
            life -= dt
            if life > 0:
                bursts.append((point, life, heavy))
        self.impact_bursts = bursts[-10:]

    def on_attack(self, kind="normal"):
        timings = {
            "normal": 0.36,
            "heavy": 0.62,
            "power": 0.52,
        }
        self.attack_kind = kind
        self.attack_total = timings.get(kind, 0.36)
        self.attack_timer = self.attack_total

    def on_hit(self, heavy=False, point=None):
        self.hit_timer = 0.22 if heavy else 0.14
        self.camera_kick = 1.0 if heavy else 0.62
        if point is not None:
            self.impact_bursts.append(
                (
                    pygame.Vector2(point),
                    0.24 if heavy else 0.18,
                    heavy,
                )
            )

    def on_parry(self):
        self.parry_timer = 0.34
        self.camera_kick = 0.72

    def on_dodge(self):
        self.dodge_timer = 0.30

    def on_knockdown(self):
        self.knockdown_timer = 0.55
        self.camera_kick = 0.9

    def on_execution(self):
        self.execution_timer = 0.95
        self.camera_kick = 1.0

    def on_boss_phase(self, name, phase):
        self.phase_banner = f"{name} — FASE {phase}"
        self.phase_timer = 2.7
        self.camera_kick = 1.0

    def attack_phase(self):
        if self.attack_timer <= 0 or self.attack_total <= 0:
            return "idle"
        progress = 1 - self.attack_timer / self.attack_total
        if progress < 0.24:
            return "anticipation"
        if progress < 0.60:
            return "active"
        return "recovery"

    def draw_world_fx(self, surface, camera, player, accent):
        for point, life, heavy in self.impact_bursts:
            x = int(point.x - camera.x)
            y = int(point.y - camera.y)
            total = 0.24 if heavy else 0.18
            progress = 1.0 - life / total
            radius = int((18 if heavy else 12) + progress * (42 if heavy else 28))
            alpha = int(230 * max(0.0, 1.0 - progress))
            color = (255, 190, 92) if heavy else (225, 240, 245)
            burst = pygame.Surface((120, 120), pygame.SRCALPHA)
            center = pygame.Vector2(60, 60)
            pygame.draw.circle(
                burst,
                (*color, alpha),
                (60, 60),
                radius,
                max(2, 5 if heavy else 3),
            )
            for i in range(8 if heavy else 6):
                angle = i * math.tau / (8 if heavy else 6)
                inner = center + pygame.Vector2(
                    math.cos(angle),
                    math.sin(angle),
                ) * (radius * 0.45)
                outer = center + pygame.Vector2(
                    math.cos(angle),
                    math.sin(angle),
                ) * (radius * 1.25)
                pygame.draw.line(
                    burst,
                    (*color, alpha),
                    inner,
                    outer,
                    3 if heavy else 2,
                )
            surface.blit(burst, (x - 60, y - 60))

        for point, life, kind in self.trail:
            x = int(point.x - camera.x)
            y = int(point.y - camera.y)
            alpha = int(220 * min(1.0, life / 0.18))
            color = (
                (245, 190, 90)
                if kind == "heavy"
                else (120, 225, 235)
            )
            glow = pygame.Surface((36, 36), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*color, alpha // 3), (18, 18), 15)
            pygame.draw.circle(glow, (*color, alpha), (18, 18), 5, 2)
            surface.blit(glow, (x - 18, y - 18))

        px = int(player.pos.x - camera.x)
        py = int(player.pos.y - camera.y)
        if self.parry_timer > 0:
            radius = 38 + int((self.parry_timer / 0.34) * 20)
            pygame.draw.arc(
                surface,
                (174, 224, 255),
                (px - radius, py - radius, radius * 2, radius * 2),
                -0.8,
                2.4,
                5,
            )
        if self.dodge_timer > 0:
            alpha = int(130 * (self.dodge_timer / 0.30))
            ghost = pygame.Surface((74, 44), pygame.SRCALPHA)
            pygame.draw.ellipse(ghost, (*accent, alpha), (5, 8, 64, 24), 3)
            surface.blit(ghost, (px - 37, py - 22))

    def draw_screen_fx(self, surface, fonts, accent):
        if self.hit_timer > 0:
            alpha = int(55 * min(1.0, self.hit_timer / 0.14))
            hit = pygame.Surface((1280, 720), pygame.SRCALPHA)
            hit.fill((120, 12, 18, alpha))
            surface.blit(hit, (0, 0))

        if self.execution_timer > 0:
            amount = int(28 * min(1.0, self.execution_timer / 0.4))
            pygame.draw.rect(surface, (0, 0, 0), (0, 0, 1280, amount))
            pygame.draw.rect(surface, (0, 0, 0), (0, 720 - amount, 1280, amount))
            label = fonts["heading"].render("EXECUÇÃO RÚNICA", True, (231, 190, 93))
            surface.blit(label, label.get_rect(center=(640, 84)))

        if self.phase_banner:
            panel = pygame.Surface((1280, 92), pygame.SRCALPHA)
            panel.fill((4, 7, 12, 210))
            surface.blit(panel, (0, 74))
            text = fonts["title"].render(self.phase_banner, True, accent)
            surface.blit(text, text.get_rect(center=(640, 120)))
