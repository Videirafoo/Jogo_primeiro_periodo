import math
import random
import pygame

INK = (238, 243, 248)
GOLD = (231, 190, 93)
GREEN = (84, 210, 139)
DARK = (8, 13, 20)

CHEST_NAMES = (
    "Baú do Saqueador",
    "Cofre Rúnico",
    "Baú Amaldiçoado",
)

CHEST_POSITIONS = {
    1: [(600, 325), (1215, 760), (1540, 520)],
    2: [(410, 690), (1020, 310), (1490, 760)],
    3: [(540, 280), (1260, 740), (1590, 420)],
    4: [(360, 620), (990, 300), (1460, 760)],
    5: [(520, 300), (1130, 740), (1510, 470)],
    6: [(390, 700), (1040, 320), (1530, 700)],
    7: [(470, 310), (1190, 760), (1580, 520)],
}


class AdventureChest:
    def __init__(self, chapter, index, pos, profile):
        self.chapter = chapter
        self.index = index
        self.id = f"chest_{chapter}_{index}"
        self.name = CHEST_NAMES[index % len(CHEST_NAMES)]
        self.pos = pygame.Vector2(pos)
        self.profile = profile

    @property
    def opened(self):
        return self.id in self.profile.get("opened_chests", [])

    def open(self, world):
        if self.opened:
            return {
                "title": self.name,
                "text": "O baú já foi aberto. Restam marcas de runas na madeira.",
                "sfx": "inventory",
            }

        self.profile.setdefault("opened_chests", []).append(self.id)
        inventory = self.profile["inventory"]
        rng = random.Random(f"{self.id}-valdrak")

        if self.index % 3 == 0:
            inventory["pocao"] += 1
            inventory["fragmento"] += 1
            world.player.gain_xp(1)
            text = (
                "Dentro havia uma Poção Nórdica e um Fragmento de Valdrak. "
                "As ferragens do baú ainda estavam quentes."
            )
            sfx = "pickup"
        elif self.index % 3 == 1:
            inventory["essencia"] += 2
            inventory["reliquia"] = inventory.get("reliquia", 0) + 1
            world.player.gain_xp(1)
            text = (
                "Duas Essências Rúnicas flutuaram para fora do cofre. "
                "Sob elas havia uma Relíquia de Memória."
            )
            sfx = "rune"
        else:
            damage = rng.randint(7, 13)
            world.player.health = max(1, world.player.health - damage)
            inventory["fragmento"] += 2
            world.player.gain_xp(2)
            text = (
                f"Uma armadilha rúnica causou {damage} de dano, "
                "mas o fundo falso escondia dois Fragmentos de Valdrak."
            )
            sfx = "axe_hit"

        return {"title": self.name, "text": text, "sfx": sfx}

    def draw(self, surface, camera, font, accent, seconds, near=False):
        x = int(self.pos.x - camera.x)
        y = int(self.pos.y - camera.y)
        if not (-80 < x < 1360 and -80 < y < 800):
            return

        y += int(math.sin(seconds * 2.4 + self.index) * 2)
        glow = GREEN if self.opened else GOLD

        pygame.draw.ellipse(surface, (0, 0, 0, 90), (x - 24, y + 16, 48, 14))
        pygame.draw.rect(surface, (73, 44, 29), (x - 22, y - 7, 44, 28), border_radius=5)
        pygame.draw.rect(surface, (112, 70, 38), (x - 22, y - 17, 44, 18), border_radius=6)
        pygame.draw.line(surface, (183, 131, 64), (x - 22, y - 1), (x + 22, y - 1), 4)
        pygame.draw.rect(surface, glow, (x - 5, y - 3, 10, 13), border_radius=2)

        if not self.opened:
            pulse = 31 + int((math.sin(seconds * 3 + self.index) + 1) * 3)
            pygame.draw.circle(surface, accent, (x, y), pulse, 1)

        if near:
            label = font.render(
                ("ABERTO — " if self.opened else "E — ") + self.name,
                True,
                INK,
            )
            box = label.get_rect(center=(x, y - 43)).inflate(16, 8)
            pygame.draw.rect(surface, DARK, box, border_radius=7)
            pygame.draw.rect(surface, glow, box, 1, border_radius=7)
            surface.blit(label, label.get_rect(center=box.center))


def build_chests(chapter, profile):
    profile.setdefault("opened_chests", [])
    return [
        AdventureChest(chapter, index, pos, profile)
        for index, pos in enumerate(CHEST_POSITIONS.get(chapter, []))
    ]
