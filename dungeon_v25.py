import random

import pygame

from progression_v24 import add_and_auto_equip, roll_equipment


class DungeonRun:
    ROOMS = (
        "Entrada",
        "Corredor de Armadilhas",
        "Câmara das Runas",
        "Sala do Mini-Boss",
        "Cofre Final",
    )

    def __init__(self, chapter, profile, seed=0):
        self.chapter = chapter
        self.profile = profile
        self.room = 0
        self.key_found = False
        self.trap_triggered = False
        self.puzzle = []
        self.puzzle_solved = False
        self.miniboss_hp = 90 + chapter * 18
        self.rewarded = False
        self.rng = random.Random(53000 + chapter + seed)

    @property
    def name(self):
        return f"Masmorra de Valdrak — {self.ROOMS[self.room]}"

    def handle_key(self, key, world):
        if key in {pygame.K_ESCAPE, pygame.K_e} and self.room == 0:
            return "exit", "Você deixou a masmorra.", "gate"

        if key in {pygame.K_RIGHT, pygame.K_d}:
            return self._forward(world)
        if key in {pygame.K_LEFT, pygame.K_a}:
            if self.room > 0:
                self.room -= 1
                return "stay", f"Retornou para {self.ROOMS[self.room]}.", "wind"
            return "stay", "A saída está atrás de você. Pressione E.", "wind"

        if self.room == 2 and key in {
            pygame.K_1,
            pygame.K_2,
            pygame.K_3,
            pygame.K_KP1,
            pygame.K_KP2,
            pygame.K_KP3,
        }:
            value = {
                pygame.K_1: 1,
                pygame.K_2: 2,
                pygame.K_3: 3,
                pygame.K_KP1: 1,
                pygame.K_KP2: 2,
                pygame.K_KP3: 3,
            }[key]
            self.puzzle.append(value)
            if len(self.puzzle) == 3:
                target = [((self.chapter + i + 1) % 3) + 1 for i in range(3)]
                if self.puzzle == target:
                    self.puzzle_solved = True
                    self.key_found = True
                    self.puzzle = []
                    return "stay", "Puzzle resolvido. Você recebeu a Chave da Masmorra.", "victory"
                self.puzzle = []
                return "stay", "As runas rejeitam a sequência.", "error"
            return "stay", "Sequência: " + "-".join(map(str, self.puzzle)), "rune"

        if self.room == 3 and key == pygame.K_SPACE:
            damage = 18 + world.profile["level"] * 3
            self.miniboss_hp = max(0, self.miniboss_hp - damage)
            if self.miniboss_hp <= 0:
                return "stay", "Mini-Boss derrotado. O cofre final foi liberado.", "boss_defeat"
            return "stay", f"Mini-Boss sofreu {damage}. HP restante: {self.miniboss_hp}", "blade_hit"

        return "stay", "", ""

    def _forward(self, world):
        if self.room == 0:
            self.room = 1
            return "stay", "Você entrou no corredor de armadilhas.", "gate"

        if self.room == 1:
            if not self.trap_triggered:
                self.trap_triggered = True
                damage = 8 + self.chapter
                world.player.damage(damage)
                self.room = 2
                return "stay", f"Armadilhas causaram {damage} de dano. A Câmara das Runas está adiante.", "axe_hit"
            self.room = 2
            return "stay", "A Câmara das Runas está adiante.", "rune"

        if self.room == 2:
            if not self.puzzle_solved:
                return "stay", "A porta está selada. Resolva a sequência 1/2/3.", "error"
            self.room = 3
            return "stay", "A chave abriu a Sala do Mini-Boss.", "gate"

        if self.room == 3:
            if self.miniboss_hp > 0:
                return "stay", "O Mini-Boss bloqueia a passagem. Ataque com Espaço.", "error"
            self.room = 4
            if not self.rewarded:
                self.rewarded = True
                item = roll_equipment(
                    self.chapter,
                    self.rng,
                    boss=True,
                    elite=True,
                )
                add_and_auto_equip(self.profile, item)
                self.profile["coins"] = self.profile.get("coins", 0) + 65
                return "stay", f"Cofre final: {item['rarity']} {item['name']} e 65 moedas.", "victory"
            return "stay", "O cofre final já foi saqueado.", "inventory"

        return "stay", "Você chegou ao fim da masmorra.", "rune"

    def draw(self, surface, fonts, accent):
        surface.fill((6, 8, 12))
        panel = pygame.Rect(70, 62, 1140, 590)
        pygame.draw.rect(surface, (16, 20, 28), panel, border_radius=24)
        pygame.draw.rect(surface, accent, panel, 2, border_radius=24)

        title = fonts["title"].render(self.name, True, (238, 243, 248))
        surface.blit(title, (110, 96))

        # Mini-map of rooms.
        for index, name in enumerate(self.ROOMS):
            x = 155 + index * 220
            active = index == self.room
            color = accent if active else (70, 80, 92)
            pygame.draw.circle(surface, color, (x, 205), 28, 3)
            if index < len(self.ROOMS) - 1:
                pygame.draw.line(surface, (70, 80, 92), (x + 30, 205), (x + 190, 205), 4)
            label = fonts["small"].render(str(index + 1), True, color)
            surface.blit(label, label.get_rect(center=(x, 205)))

        room_name = fonts["heading"].render(self.ROOMS[self.room], True, accent)
        surface.blit(room_name, (115, 270))

        message = ""
        if self.room == 0:
            message = "D para avançar. E ou Esc para sair."
        elif self.room == 1:
            message = "Armadilhas antigas cobrem o piso. D para atravessar."
        elif self.room == 2:
            seq = "-".join(map(str, self.puzzle)) or "..."
            message = f"Puzzle rúnico. Pressione 1/2/3. Sequência atual: {seq}"
        elif self.room == 3:
            message = f"Mini-Boss da Masmorra — HP {self.miniboss_hp}. Espaço ataca."
            pygame.draw.circle(surface, (145, 55, 55), (640, 430), 74)
            pygame.draw.circle(surface, accent, (640, 430), 84, 3)
        else:
            message = "Cofre final encontrado. A/D navega entre salas."

        body = fonts["body"].render(message, True, (185, 196, 207))
        surface.blit(body, (115, 540))

        hint = fonts["small"].render("A/D navega • Espaço combate • 1/2/3 puzzle • E sai na entrada", True, (145, 158, 172))
        surface.blit(hint, (115, 610))
