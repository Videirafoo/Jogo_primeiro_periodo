import random

BOSS_MOVESETS = {
    1: [
        {"name": "Carga da Tempestade", "range": 165, "damage": 16, "sfx": "thunder"},
        {"name": "Machado Arremessado", "range": 250, "damage": 13, "sfx": "axe_whoosh"},
        {"name": "Chuva de Runas", "range": 210, "damage": 15, "sfx": "rune"},
    ],
    2: [
        {"name": "Esmagamento de Ossos", "range": 150, "damage": 18, "sfx": "axe_hit"},
        {"name": "Onda do Ossário", "range": 225, "damage": 14, "sfx": "wind"},
        {"name": "Muralha de Crânios", "range": 175, "damage": 16, "sfx": "shield"},
    ],
    3: [
        {"name": "Giro de Dois Machados", "range": 175, "damage": 20, "sfx": "axe_whoosh"},
        {"name": "Lançamento Duplo", "range": 270, "damage": 16, "sfx": "axe_whoosh"},
        {"name": "Fúria da Arena", "range": 205, "damage": 19, "sfx": "axe_hit"},
    ],
    4: [
        {"name": "Nuvem de Corvos", "range": 235, "damage": 15, "sfx": "crow"},
        {"name": "Passo Sombrio", "range": 170, "damage": 19, "sfx": "shadow"},
        {"name": "Garras do Eclipse", "range": 195, "damage": 18, "sfx": "shadow"},
    ],
    5: [
        {"name": "Salto do Alfa", "range": 180, "damage": 21, "sfx": "wolf"},
        {"name": "Chamado da Matilha", "range": 240, "damage": 16, "sfx": "wolf"},
        {"name": "Fúria de Ferro", "range": 165, "damage": 23, "sfx": "metal"},
    ],
    6: [
        {"name": "Martelo da Forja", "range": 160, "damage": 24, "sfx": "axe_hit"},
        {"name": "Rio de Lava", "range": 235, "damage": 18, "sfx": "fire"},
        {"name": "Explosão da Forja", "range": 210, "damage": 22, "sfx": "fire"},
    ],
    7: [
        {"name": "Espada do Vazio", "range": 185, "damage": 24, "sfx": "shadow"},
        {"name": "Portal Partido", "range": 260, "damage": 20, "sfx": "portal"},
        {"name": "Segunda Realidade", "range": 220, "damage": 26, "sfx": "portal"},
    ],
}


class BossCombatController:
    def __init__(self, chapter):
        self.chapter = chapter
        self.moves = BOSS_MOVESETS[chapter]
        self.rng = random.Random(9400 + chapter)
        self.cooldown = 2.2
        self.telegraph = 0.0
        self.pending = None
        self.phase = 1
        self.stagger = 0.0
        self.stunned = 0.0

    def add_stagger(self, amount):
        if self.stunned > 0:
            return False
        self.stagger += amount
        if self.stagger >= 100:
            self.stagger = 0
            self.stunned = 2.1
            return True
        return False

    def update(self, dt, boss, player):
        if boss is None or boss.dead:
            return None

        if boss.hp <= boss.max_hp * 0.48:
            self.phase = 2

        self.stunned = max(0.0, self.stunned - dt)
        if self.stunned > 0:
            boss.attack_cd = max(boss.attack_cd, self.stunned)
            return None

        if self.pending:
            self.telegraph -= dt
            if self.telegraph <= 0:
                move = self.pending
                self.pending = None
                self.cooldown = 1.45 if self.phase == 2 else 2.25
                return {
                    "kind": "resolve",
                    "move": move,
                    "hit": boss.pos.distance_to(player.pos) <= move["range"],
                }
            return {
                "kind": "telegraph",
                "move": self.pending,
                "progress": max(0.0, self.telegraph),
            }

        self.cooldown -= dt
        if self.cooldown <= 0:
            self.pending = self.rng.choice(self.moves)
            self.telegraph = 0.72 if self.phase == 1 else 0.48
            return {
                "kind": "telegraph_start",
                "move": self.pending,
            }
        return None
