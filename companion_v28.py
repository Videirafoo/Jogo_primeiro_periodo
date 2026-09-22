import pygame

from production_art_v28 import draw_portrait_v28
from rpg_depth_v28 import ALLY_TREES, synergy_for


POWER = {
    "Thorvald": ("Raio de Torv", "thunder", (92, 184, 255)),
    "Aurel": ("Lança Solar", "lightning", (245, 220, 115)),
    "Kaion": ("Corte Duplo", "sword", (113, 224, 232)),
    "Brenor": ("Martelo Ígneo", "fire", (245, 137, 69)),
    "Eiran": ("Vínculo de Cura", "heal", (84, 210, 139)),
    "Noctar": ("Marca do Eclipse", "shadow", (158, 116, 255)),
}


class CompanionSystemV28:
    def __init__(self, profile):
        self.profile = profile
        self.profile.setdefault("v28_active_allies", [])
        self.profile.setdefault("v28_friendship", {})
        self.profile.setdefault("v28_companion_mode", "aggressive")
        self.profile.setdefault("v28_personal_quests", {})
        self.profile.setdefault("v28_companion_combo", 0)
        self.selected = 0

    def sync(self, available):
        for ally in available:
            self.profile["v28_friendship"].setdefault(ally, 0)
            self.profile["v28_personal_quests"].setdefault(
                ally,
                {"stage": 0, "complete": False},
            )
        active = [
            ally
            for ally in self.profile["v28_active_allies"]
            if ally in available
        ]
        for ally in available:
            if ally not in active and len(active) < 2:
                active.append(ally)
        self.profile["v28_active_allies"] = active[:2]

    @property
    def active(self):
        return self.profile["v28_active_allies"][:2]

    def cycle_selected(self, direction=1):
        self.selected = (self.selected + direction) % 2

    def swap_selected(self, available):
        if not available:
            return "Nenhum Eterno disponível."
        self.sync(available)
        active = self.active
        slot = min(self.selected, len(active) - 1)
        current = active[slot]
        start = available.index(current) if current in available else -1
        for offset in range(1, len(available) + 1):
            candidate = available[(start + offset) % len(available)]
            if candidate not in active:
                active[slot] = candidate
                self.profile["v28_active_allies"] = active
                return f"Eterno ativo: {candidate}"
        return "Todos os Eternos disponíveis já estão ativos."

    def cycle_mode(self):
        modes = ("aggressive", "guard", "support")
        current = modes.index(self.profile["v28_companion_mode"])
        self.profile["v28_companion_mode"] = modes[(current + 1) % len(modes)]
        return self.profile["v28_companion_mode"]

    def friendship_gain(self, ally, amount=1):
        if ally not in self.profile["v28_friendship"]:
            self.profile["v28_friendship"][ally] = 0
        self.profile["v28_friendship"][ally] += amount
        state = self.profile["v28_personal_quests"].setdefault(
            ally,
            {"stage": 0, "complete": False},
        )
        friendship = self.profile["v28_friendship"][ally]
        if friendship >= 4 and state["stage"] == 0:
            state["stage"] = 1
            return f"Quest pessoal disponível: {ally}"
        if friendship >= 9 and state["stage"] == 1:
            state["stage"] = 2
            state["complete"] = True
            return f"Quest pessoal concluída: {ally} confia plenamente em você."
        return None

    def assist(self, world):
        available = world.engine.ally_names()
        self.sync(available)
        if not self.active:
            return None

        targets = [
            enemy
            for enemy in world.enemies
            if not enemy.dead
            and enemy.pos.distance_to(world.player.pos) <= 340
        ]
        if not targets:
            return "Nenhum inimigo próximo.", "rune"

        target = min(targets, key=lambda enemy: enemy.pos.distance_to(world.player.pos))
        mode = self.profile["v28_companion_mode"]
        total_damage = 0
        labels = []

        for ally in self.active:
            power, sfx, color = POWER.get(ally, ("Poder Desperto", "rune", (70, 224, 235)))
            friendship = self.profile["v28_friendship"].get(ally, 0)
            base = 8 + world.profile["level"] * 2 + friendship // 2
            if mode == "aggressive":
                base = int(base * 1.25)
            elif mode == "support":
                if ally == "Eiran":
                    world.player.health = min(world.profile["max_health"], world.player.health + 8)
                world.player.energy = min(world.profile["max_energy"], world.player.energy + 4)
            elif mode == "guard":
                world.combat_v25.stamina = min(world.profile["max_stamina"], world.combat_v25.stamina + 7)

            total_damage += base
            labels.append(f"{ally}: {power}")
            world._burst(target.pos, color, 7)
            world.events.append(sfx)
            self.friendship_gain(ally, 1)

        synergy = synergy_for(self.active)
        if synergy:
            name, stat, value = synergy
            bonus = 8 if stat == "attack" else 4
            total_damage += bonus + int(value if isinstance(value, int) else value * 100)
            labels.append(name)
            self.profile["v28_companion_combo"] += 1

        died = target.hit(total_damage)
        if died:
            world._enemy_defeated(target)
        return " + ".join(labels) + f" • {total_damage} dano", "rune"

    def draw(self, surface, fonts, accent, available, rpg_depth):
        self.sync(available)
        veil = pygame.Surface((1280, 720), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 226))
        surface.blit(veil, (0, 0))
        panel = pygame.Rect(100, 62, 1080, 600)
        pygame.draw.rect(surface, (7, 12, 19), panel, border_radius=24)
        pygame.draw.rect(surface, accent, panel, 2, border_radius=24)

        surface.blit(fonts["title"].render("COMPANION SYSTEM — ETERNOS", True, (239, 244, 248)), (145, 100))
        mode = self.profile["v28_companion_mode"].upper()
        surface.blit(fonts["heading"].render(f"MODO: {mode}", True, accent), (145, 152))

        y = 220
        for index in range(2):
            ally = self.active[index] if index < len(self.active) else "Vazio"
            selected = index == self.selected
            rect = pygame.Rect(145, y, 460, 145)
            pygame.draw.rect(surface, (15, 23, 32), rect, border_radius=16)
            pygame.draw.rect(surface, (231, 190, 93) if selected else (70, 83, 97), rect, 2, border_radius=16)
            if ally != "Vazio":
                draw_portrait_v28(
                    surface,
                    pygame.Rect(170, y + 14, 88, 112),
                    ally,
                    pygame.time.get_ticks() / 1000,
                )
                friendship = self.profile["v28_friendship"].get(ally, 0)
                level = self.profile.get("v28_ally_skills", {}).get(ally, 0)
                tree = ALLY_TREES.get(ally, ())
                unlocked = ", ".join(tree[:level]) or "nenhuma"
                surface.blit(fonts["heading"].render(ally, True, (239, 244, 248)), (280, y + 18))
                surface.blit(fonts["body"].render(f"Amizade: {friendship}", True, accent), (280, y + 56))
                surface.blit(fonts["small"].render(f"Skills: {unlocked}"[:48], True, (170, 184, 197)), (280, y + 92))
            y += 165

        synergy = synergy_for(self.active)
        if synergy:
            surface.blit(fonts["heading"].render(f"SINERGIA: {synergy[0]}", True, (231, 190, 93)), (650, 250))
        surface.blit(fonts["body"].render("Quests pessoais avançam com amizade e uso em combate.", True, (195, 204, 212)), (650, 305))
        surface.blit(fonts["small"].render(
            "↑/↓ slot • Espaço troca Eterno • C muda comando • T libera skill • V/Esc fecha",
            True,
            (150, 164, 178),
        ), (145, 620))
