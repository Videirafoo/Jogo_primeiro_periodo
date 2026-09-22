import math
import random

import pygame

from weapon_art import draw_viking_axe


ARENA = pygame.Rect(70, 270, 1140, 300)
INK = (236, 242, 248)
MUTED = (160, 174, 190)
PANEL = (12, 20, 31)
PANEL_2 = (24, 36, 54)
GOLD = (231, 190, 93)
GREEN = (90, 210, 142)
RED = (235, 94, 105)
CYAN = (74, 222, 232)


CHAPTER_CHALLENGES = {
    0: ("dodge", "Desvie do machado viking"),
    1: ("rune", "Rastreie as runas antes que o caminho desapareça"),
    2: ("timing", "Sincronize o Pulso de Código com o portão"),
    3: ("timing", "Bloqueie os golpes no momento certo"),
    4: ("rune", "Encontre as marcas verdadeiras no bosque"),
    5: ("dodge", "Desvie dos lobos de ferro e dos machados"),
    6: ("timing", "Sincronize fogo, sombra e código"),
    7: ("rune", "Estabilize a última porta de Valdrak"),
}


class Challenge:
    def __init__(self, chapter_number):
        self.chapter_number = chapter_number
        self.kind, self.title = CHAPTER_CHALLENGES.get(
            chapter_number,
            ("timing", "Supere o desafio de Valdrak"),
        )
        self.rng = random.Random(3000 + chapter_number)
        self.elapsed = 0.0
        self.finished = False
        self.success = False
        self.events = []

        self.cursor = pygame.Vector2(ARENA.centerx, ARENA.centery)
        self.cursor_speed = 310
        self.target = self._new_target()
        self.collected = 0
        self.rune_goal = 3 + chapter_number // 3

        self.marker = 0.0
        self.marker_dir = 1.0
        self.timing_hits = 0
        self.timing_misses = 0
        self.target_center = 0.62 if chapter_number % 2 else 0.38
        self.target_width = max(0.11, 0.19 - chapter_number * 0.009)

        self.player_x = float(ARENA.centerx)
        self.hazards = []
        self.spawn_timer = 0.25
        self.spawn_count = 0
        self.lives = 3
        self.survive_for = 7.5 + chapter_number * 0.45

        self.time_limit = 13.0 if self.kind != "dodge" else self.survive_for
        self.result_text = ""

    def _new_target(self):
        margin = 55
        return pygame.Vector2(
            self.rng.randint(ARENA.left + margin, ARENA.right - margin),
            self.rng.randint(ARENA.top + margin, ARENA.bottom - margin),
        )

    def pop_events(self):
        events = list(self.events)
        self.events.clear()
        return events

    def handle_key(self, event):
        if self.finished:
            return

        if self.kind == "timing" and event.key in (
            pygame.K_SPACE,
            pygame.K_RETURN,
        ):
            self._timing_press()

    def handle_click(self, pos):
        if self.finished:
            return

        if self.kind == "timing":
            self._timing_press()
        elif self.kind == "rune":
            self.cursor.update(pos)

    def update(self, dt, keys):
        if self.finished:
            return

        self.elapsed += dt

        if self.kind == "rune":
            self._update_rune(dt, keys)
        elif self.kind == "timing":
            self._update_timing(dt)
        else:
            self._update_dodge(dt, keys)

        if not self.finished and self.elapsed >= self.time_limit:
            if self.kind == "dodge" and self.lives > 0:
                self._finish(True, "Você sobreviveu à investida.")
            else:
                self._finish(False, "O tempo acabou.")

    def _update_rune(self, dt, keys):
        direction = pygame.Vector2()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            direction.y += 1

        if direction.length_squared():
            direction = direction.normalize()
            self.cursor += direction * self.cursor_speed * dt

        self.cursor.x = max(ARENA.left + 18, min(ARENA.right - 18, self.cursor.x))
        self.cursor.y = max(ARENA.top + 18, min(ARENA.bottom - 18, self.cursor.y))

        if self.cursor.distance_to(self.target) <= 34:
            self.collected += 1
            event_name = {
                1: "scanner",
                4: "crow",
                7: "portal",
            }.get(self.chapter_number, "rune")
            self.events.append(event_name)
            self.target = self._new_target()
            if self.collected >= self.rune_goal:
                self._finish(True, "Runas sincronizadas.")

    def _update_timing(self, dt):
        speed = 0.78 + self.chapter_number * 0.045
        self.marker += self.marker_dir * speed * dt
        if self.marker >= 1.0:
            self.marker = 1.0
            self.marker_dir = -1.0
        elif self.marker <= 0.0:
            self.marker = 0.0
            self.marker_dir = 1.0

    def _timing_press(self):
        half = self.target_width / 2
        if abs(self.marker - self.target_center) <= half:
            self.timing_hits += 1
            event_name = {
                2: "gate",
                3: "shield",
                6: "rune",
            }.get(self.chapter_number, "tech")
            self.events.append(event_name)
            self.target_center = self.rng.uniform(0.22, 0.78)
            if self.timing_hits >= 3:
                self._finish(True, "Sincronização perfeita.")
        else:
            self.timing_misses += 1
            self.events.append("error")
            if self.timing_misses >= 3:
                self._finish(False, "A sincronização se perdeu.")

    def _update_dodge(self, dt, keys):
        direction = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction += 1

        self.player_x += direction * 420 * dt
        self.player_x = max(ARENA.left + 28, min(ARENA.right - 28, self.player_x))

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = max(0.28, 0.64 - self.chapter_number * 0.035)
            self.spawn_count += 1
            hazard_kind = (
                "axe"
                if self.chapter_number == 0 or self.spawn_count % 2 == 0
                else "wolf"
            )
            self.hazards.append(
                {
                    "x": self.rng.randint(ARENA.left + 20, ARENA.right - 20),
                    "y": ARENA.top - 20,
                    "speed": self.rng.randint(210, 330),
                    "size": self.rng.randint(16, 26),
                    "kind": hazard_kind,
                    "spin": self.rng.uniform(0, 360),
                    "spin_speed": self.rng.choice(
                        [-760, -620, 620, 760]
                    ),
                }
            )

            if self.spawn_count % 3 == 1:
                self.events.append(
                    "axe_whoosh" if hazard_kind == "axe" else "wolf"
                )

        player = pygame.Rect(int(self.player_x) - 24, ARENA.bottom - 55, 48, 48)
        remaining = []

        for hazard in self.hazards:
            hazard["y"] += hazard["speed"] * dt
            hazard["spin"] = (
                hazard.get("spin", 0.0)
                + hazard.get("spin_speed", 0.0) * dt
            ) % 360
            rect = pygame.Rect(
                int(hazard["x"] - hazard["size"]),
                int(hazard["y"] - hazard["size"]),
                hazard["size"] * 2,
                hazard["size"] * 2,
            )

            if rect.colliderect(player):
                self.lives -= 1
                self.events.append(
                    "axe_hit" if hazard.get("kind") == "axe" else "wolf"
                )
                if self.lives <= 0:
                    self._finish(False, "Os lobos cercaram o caminho.")
                    return
                continue

            if hazard["y"] < ARENA.bottom + 40:
                remaining.append(hazard)

        self.hazards = remaining

    def _finish(self, success, text):
        self.finished = True
        self.success = success
        self.result_text = text
        self.events.append("victory" if success else "error")

    def draw(self, surface, fonts, accent):
        pygame.draw.rect(surface, PANEL, ARENA, border_radius=22)
        pygame.draw.rect(surface, accent, ARENA, 1, border_radius=22)

        title = fonts["heading"].render(self.title, True, INK)
        surface.blit(title, (ARENA.x + 28, ARENA.y + 22))

        if self.kind == "rune":
            self._draw_rune(surface, fonts, accent)
        elif self.kind == "timing":
            self._draw_timing(surface, fonts, accent)
        else:
            self._draw_dodge(surface, fonts, accent)

        if self.finished:
            self._draw_result(surface, fonts, accent)

    def _draw_rune(self, surface, fonts, accent):
        tx, ty = int(self.target.x), int(self.target.y)
        pygame.draw.circle(surface, accent, (tx, ty), 29, 2)
        pygame.draw.circle(surface, accent, (tx, ty), 21, 1)
        pygame.draw.line(surface, accent, (tx, ty - 15), (tx, ty + 16), 3)
        pygame.draw.line(surface, accent, (tx, ty - 8), (tx + 12, ty), 3)
        pygame.draw.line(surface, accent, (tx, ty + 3), (tx - 12, ty + 13), 3)

        cx, cy = int(self.cursor.x), int(self.cursor.y)
        pygame.draw.circle(surface, INK, (cx, cy), 19, 2)
        pygame.draw.circle(surface, accent, (cx, cy), 5)
        pygame.draw.line(surface, INK, (cx - 30, cy), (cx - 13, cy), 2)
        pygame.draw.line(surface, INK, (cx + 13, cy), (cx + 30, cy), 2)
        pygame.draw.line(surface, INK, (cx, cy - 30), (cx, cy - 13), 2)
        pygame.draw.line(surface, INK, (cx, cy + 13), (cx, cy + 30), 2)

        info = f"Runas {self.collected}/{self.rune_goal}  •  WASD/setas para mover"
        surface.blit(fonts["small"].render(info, True, MUTED), (ARENA.x + 28, ARENA.bottom - 42))

    def _draw_timing(self, surface, fonts, accent):
        bar = pygame.Rect(ARENA.x + 100, ARENA.centery - 15, ARENA.width - 200, 30)
        pygame.draw.rect(surface, PANEL_2, bar, border_radius=15)

        target_w = int(bar.width * self.target_width)
        target_x = int(bar.x + bar.width * self.target_center - target_w / 2)
        target_rect = pygame.Rect(target_x, bar.y, target_w, bar.height)
        pygame.draw.rect(surface, GREEN, target_rect, border_radius=15)

        marker_x = int(bar.x + bar.width * self.marker)
        pygame.draw.line(surface, INK, (marker_x, bar.y - 16), (marker_x, bar.bottom + 16), 5)

        info = f"Acertos {self.timing_hits}/3  •  Erros {self.timing_misses}/3  •  ESPAÇO/clique"
        surface.blit(fonts["small"].render(info, True, MUTED), (ARENA.x + 28, ARENA.bottom - 42))

    def _draw_dodge(self, surface, fonts, accent):
        px = int(self.player_x)
        py = ARENA.bottom - 32
        shield = [
            (px, py - 28),
            (px + 23, py - 15),
            (px + 17, py + 16),
            (px, py + 29),
            (px - 17, py + 16),
            (px - 23, py - 15),
        ]
        pygame.draw.polygon(surface, accent, shield)
        pygame.draw.polygon(surface, INK, shield, 2)
        pygame.draw.circle(surface, PANEL, (px, py), 9)
        pygame.draw.circle(surface, INK, (px, py), 9, 2)

        for hazard in self.hazards:
            x = int(hazard["x"])
            y = int(hazard["y"])
            size = hazard["size"]

            if hazard.get("kind") == "axe":
                draw_viking_axe(
                    surface,
                    (x, y),
                    angle=hazard.get("spin", 0.0),
                    scale=max(0.38, size / 46),
                    rune_color=accent,
                    motion=1.0,
                )
            else:
                pygame.draw.ellipse(
                    surface,
                    (76, 86, 98),
                    (x - size, y - size // 2, size * 2, size),
                )
                pygame.draw.circle(surface, (88, 98, 110), (x, y - size // 2), size // 2)
                pygame.draw.polygon(
                    surface,
                    (88, 98, 110),
                    [(x - 12, y - size), (x - 4, y - size // 2), (x - 18, y - size // 2)],
                )
                pygame.draw.polygon(
                    surface,
                    (88, 98, 110),
                    [(x + 12, y - size), (x + 4, y - size // 2), (x + 18, y - size // 2)],
                )
                pygame.draw.circle(surface, RED, (x - 6, y - size // 2), 2)
                pygame.draw.circle(surface, RED, (x + 6, y - size // 2), 2)

        left = max(0.0, self.survive_for - self.elapsed)
        info = f"Vidas {self.lives}  •  Sobreviva {left:0.1f}s  •  A/D ou setas"
        surface.blit(fonts["small"].render(info, True, MUTED), (ARENA.x + 28, ARENA.bottom - 42))

    def _draw_result(self, surface, fonts, accent):
        overlay = pygame.Surface(ARENA.size, pygame.SRCALPHA)
        overlay.fill((3, 7, 13, 185))
        surface.blit(overlay, ARENA.topleft)

        color = GREEN if self.success else RED
        headline = "DESAFIO SUPERADO" if self.success else "DESAFIO FALHOU"
        h = fonts["heading"].render(headline, True, color)
        surface.blit(h, h.get_rect(center=(ARENA.centerx, ARENA.centery - 28)))

        body = fonts["body"].render(self.result_text, True, INK)
        surface.blit(body, body.get_rect(center=(ARENA.centerx, ARENA.centery + 18)))

        hint = fonts["small"].render("Pressione Enter para continuar", True, MUTED)
        surface.blit(hint, hint.get_rect(center=(ARENA.centerx, ARENA.centery + 58)))
