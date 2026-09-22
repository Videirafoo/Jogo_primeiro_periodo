import math
import random

import pygame

from progression_v24 import add_and_auto_equip


ROOM_TYPES = (
    "entrada",
    "armadilha",
    "puzzle",
    "atalho",
    "chave",
    "mini_boss",
    "santuário",
    "cofre",
)

EXCLUSIVE_LOOT = {
    1: ("Machado da Tempestade Antiga", "weapon", "attack", 18),
    2: ("Cota do Portão Quebrado", "armor", "defense", 16),
    3: ("Olho do Campeão Sem Sombra", "amulet", "crit", 0.13),
    4: ("Runa das Sete Penas", "rune", "energy", 22),
    5: ("Machado do Alfa Branco", "weapon", "attack", 23),
    6: ("Martelo da Memória Negra", "weapon", "attack", 27),
    7: ("Marca da Última Porta", "amulet", "crit", 0.18),
}


class DungeonSystemIII:
    def __init__(self, chapter, profile, seed=0):
        self.chapter = chapter
        self.profile = profile
        self.rng = random.Random(88000 + chapter + seed)
        self.active = False
        self.source_kind = None
        self.rooms = []
        self.room = 0
        self.puzzle = []
        self.puzzle_target = []
        self.key_found = False
        self.shortcut_open = False
        self.miniboss_hp = 0
        self.trap_phase = 0.0
        self.rewarded = False
        self.profile.setdefault("v28_dungeons", {})
        self.profile.setdefault("v28_special_keys", [])

    def start_from_site(self, source_kind="cave"):
        self.active = True
        self.source_kind = source_kind
        self.room = 0
        middle = list(ROOM_TYPES[1:-1])
        self.rng.shuffle(middle)
        self.rooms = ["entrada"] + middle + ["cofre"]
        self.puzzle = []
        self.puzzle_target = [
            self.rng.randint(1, 4)
            for _ in range(4)
        ]
        self.key_found = False
        self.shortcut_open = False
        self.miniboss_hp = 110 + self.chapter * 24
        self.trap_phase = 0.0
        self.rewarded = False

    @property
    def room_type(self):
        if not self.rooms:
            return "entrada"
        return self.rooms[self.room]

    def update(self, dt):
        if self.active:
            self.trap_phase = (self.trap_phase + dt * 1.8) % 6.283

    def handle_key(self, key, world):
        if not self.active:
            return None

        if key in {pygame.K_ESCAPE, pygame.K_e} and self.room == 0:
            self.active = False
            return "Você deixou a masmorra procedural.", "gate"

        if key in {pygame.K_LEFT, pygame.K_a}:
            if self.room > 0:
                self.room -= 1
                return f"Você retornou à sala {self.room + 1}.", "footstep_stone"
            return "A saída está atrás de você. E para sair.", "wind"

        if self.room_type == "puzzle" and key in {
            pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
            pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4,
        }:
            mapping = {
                pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4,
                pygame.K_KP1: 1, pygame.K_KP2: 2, pygame.K_KP3: 3, pygame.K_KP4: 4,
            }
            self.puzzle.append(mapping[key])
            if len(self.puzzle) == 4:
                if self.puzzle == self.puzzle_target:
                    self.key_found = True
                    self.profile.setdefault("puzzles_solved", []).append(
                        f"v28_{self.chapter}_{self.source_kind}"
                    )
                    self.puzzle = []
                    return "Puzzle maior resolvido • Chave Especial encontrada.", "quest_complete"
                self.puzzle = []
                return "Sequência incorreta. As runas reiniciam.", "error"
            return "Runas: " + "-".join(map(str, self.puzzle)), "rune"

        if self.room_type == "mini_boss" and key == pygame.K_SPACE:
            damage = 24 + world.profile["level"] * 3
            self.miniboss_hp = max(0, self.miniboss_hp - damage)
            if self.miniboss_hp <= 0:
                return "Mini-Boss único derrotado. A rota profunda foi aberta.", "boss_defeat"
            return f"Mini-Boss: -{damage} • HP {self.miniboss_hp}", "blade_hit"

        if key in {pygame.K_RIGHT, pygame.K_d, pygame.K_SPACE}:
            return self._forward(world)

        if self.room_type == "atalho" and key == pygame.K_s:
            self.shortcut_open = True
            self.room = max(0, len(self.rooms) - 3)
            return "Atalho aberto. Você contornou duas salas.", "gate"

        return "", ""

    def _forward(self, world):
        kind = self.room_type
        if kind == "armadilha":
            damage = 9 + self.chapter
            world._damage_player(damage)
            self.room = min(len(self.rooms) - 1, self.room + 1)
            return f"Armadilha móvel atingiu você por {damage}.", "axe_hit"

        if kind == "puzzle" and not self.key_found:
            target = "-".join(map(str, self.puzzle_target))
            return f"Puzzle selado. Descubra a sequência 1-4. Pista rúnica: {target[0]}...{target[-1]}", "rune"

        if kind == "mini_boss" and self.miniboss_hp > 0:
            return "O Mini-Boss bloqueia a passagem. Espaço ataca.", "error"

        if kind == "chave":
            key_id = f"special_{self.chapter}_{self.source_kind}"
            if key_id not in self.profile["v28_special_keys"]:
                self.profile["v28_special_keys"].append(key_id)
                self.key_found = True

        if kind == "cofre":
            if self.rewarded:
                return "O cofre exclusivo já foi aberto.", "inventory"
            if not self.key_found:
                return "O cofre exige uma Chave Especial.", "error"
            self.rewarded = True
            name, slot, stat, value = EXCLUSIVE_LOOT[self.chapter]
            item = {
                "id": f"v28-exclusive-{self.chapter}-{self.source_kind}",
                "name": name,
                "slot": slot,
                "rarity": "Lendário",
                "stat": stat,
                "value": value,
                "chapter": self.chapter,
                "exclusive": True,
            }
            equipped = add_and_auto_equip(self.profile, item)
            self.profile["coins"] = self.profile.get("coins", 0) + 120
            return (
                f"LOOT EXCLUSIVO: {name} • +120 moedas"
                + (" • equipado" if equipped else ""),
                "victory",
            )

        if self.room < len(self.rooms) - 1:
            self.room += 1
            return f"Você avançou para {self.room_type.replace('_', ' ').title()}.", "footstep_stone"
        return "Fim da masmorra.", "rune"

    def draw(self, surface, fonts, accent):
        surface.fill((5, 8, 12))
        panel = pygame.Rect(60, 48, 1160, 620)
        pygame.draw.rect(surface, (14, 18, 25), panel, border_radius=24)
        pygame.draw.rect(surface, accent, panel, 2, border_radius=24)
        surface.blit(
            fonts["title"].render("DUNGEON SYSTEM III", True, (239, 244, 248)),
            (105, 88),
        )
        surface.blit(
            fonts["body"].render(
                f"{self.source_kind.upper()} • sala {self.room + 1}/{len(self.rooms)} • {self.room_type.replace('_', ' ').upper()}",
                True,
                accent,
            ),
            (108, 138),
        )

        # Procedural room graph / mini-map.
        for index, room in enumerate(self.rooms):
            col = index % 4
            row = index // 4
            x = 185 + col * 255
            y = 235 + row * 170
            current = index == self.room
            color = accent if current else (75, 85, 96)
            rect = pygame.Rect(x - 70, y - 42, 140, 84)
            pygame.draw.rect(surface, (20, 27, 35), rect, border_radius=12)
            pygame.draw.rect(surface, color, rect, 3 if current else 1, border_radius=12)
            label = fonts["small"].render(room.replace("_", " ").upper(), True, color)
            surface.blit(label, label.get_rect(center=rect.center))
            if index < len(self.rooms) - 1 and col < 3:
                pygame.draw.line(surface, (75, 85, 96), (rect.right, rect.centery), (rect.right + 110, rect.centery), 3)

        if self.room_type == "armadilha":
            y = 570 + int(math.sin(self.trap_phase) * 18)
            pygame.draw.line(surface, (225, 82, 92), (300, y), (980, y), 7)
        elif self.room_type == "mini_boss":
            pygame.draw.circle(surface, (145, 52, 58), (640, 545), 48)
            hp = fonts["heading"].render(f"MINI-BOSS HP {self.miniboss_hp}", True, (239, 244, 248))
            surface.blit(hp, hp.get_rect(center=(640, 615)))

        hint = "A/D navega • S abre atalho • 1-4 puzzle • Espaço combate • E sai na entrada"
        surface.blit(fonts["small"].render(hint, True, (150, 164, 178)), (105, 636))
