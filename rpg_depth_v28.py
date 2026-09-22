import pygame

from progression_v24 import RARITIES, equipment_stats, item_score


BUILD_ARCHETYPES = {
    "Berserker Rúnico": {
        "attack": 8,
        "defense": 2,
        "crit": 0.02,
        "energy": 0,
    },
    "Guardião de Ferro": {
        "attack": 2,
        "defense": 9,
        "crit": 0.0,
        "energy": 8,
    },
    "Caçador do Vazio": {
        "attack": 4,
        "defense": 2,
        "crit": 0.07,
        "energy": 10,
    },
}

ALLY_TREES = {
    "Thorvald": ("Raio Encadeado", "Tempestade de Guerra", "Olho de Torv"),
    "Aurel": ("Luz Cortante", "Escudo Solar", "Marca da Aurora"),
    "Kaion": ("Duas Lâminas", "Passo Fantasma", "Dança do Código"),
    "Brenor": ("Martelo Ígneo", "Pele de Cinzas", "Forja Viva"),
    "Eiran": ("Cura Rúnica", "Vínculo Vital", "Renascimento"),
    "Noctar": ("Sombra Longa", "Marca do Vazio", "Eclipse"),
}

SYNERGY_BONUSES = {
    frozenset(("Thorvald", "Aurel")): ("Tempestade Solar", "attack", 4),
    frozenset(("Kaion", "Noctar")): ("Lâmina do Eclipse", "crit", 0.05),
    frozenset(("Brenor", "Eiran")): ("Forja Vital", "defense", 4),
    frozenset(("Thorvald", "Brenor")): ("Martelo do Trovão", "attack", 5),
    frozenset(("Aurel", "Eiran")): ("Pacto da Aurora", "energy", 12),
    frozenset(("Kaion", "Eiran")): ("Passo Restaurador", "defense", 3),
}


def ensure_rpg_v28(profile):
    profile.setdefault("v28_build", "Berserker Rúnico")
    profile.setdefault("v28_ally_skills", {})
    profile.setdefault("v28_compare_index", 0)
    for ally in ALLY_TREES:
        profile["v28_ally_skills"].setdefault(ally, 0)


def total_stats(profile):
    ensure_rpg_v28(profile)
    stats = equipment_stats(profile)
    build = BUILD_ARCHETYPES[profile["v28_build"]]
    total = {
        key: stats.get(key, 0) + build.get(key, 0)
        for key in ("attack", "defense", "crit", "energy")
    }
    return total


def synergy_for(allies):
    if len(allies) < 2:
        return None
    return SYNERGY_BONUSES.get(frozenset(allies[:2]))


class RPGDepthII:
    def __init__(self, profile):
        self.profile = profile
        ensure_rpg_v28(profile)

    def cycle_build(self):
        names = list(BUILD_ARCHETYPES)
        current = names.index(self.profile["v28_build"])
        self.profile["v28_build"] = names[(current + 1) % len(names)]
        return self.profile["v28_build"]

    def comparison(self):
        bag = self.profile.get("gear_bag", [])
        if not bag:
            return None, None
        index = self.profile["v28_compare_index"] % len(bag)
        candidate = bag[index]
        equipped = self.profile.get("equipped", {}).get(candidate["slot"])
        return candidate, equipped

    def cycle_compare(self, direction=1):
        bag = self.profile.get("gear_bag", [])
        if not bag:
            return
        self.profile["v28_compare_index"] = (
            self.profile["v28_compare_index"] + direction
        ) % len(bag)

    def equip_comparison(self):
        candidate, equipped = self.comparison()
        if not candidate:
            return "Nenhum item disponível."
        self.profile["equipped"][candidate["slot"]] = candidate
        return f"Equipado: {candidate['rarity']} {candidate['name']}"

    def unlock_ally_skill(self, ally, points):
        level = self.profile["v28_ally_skills"].get(ally, 0)
        if level >= len(ALLY_TREES.get(ally, ())):
            return False, "Árvore deste Eterno já está completa."
        if points <= 0:
            return False, "Sem pontos de talento."
        self.profile["v28_ally_skills"][ally] = level + 1
        skill = ALLY_TREES[ally][level]
        return True, f"{ally}: {skill} desbloqueado"

    def draw_inventory(self, surface, fonts, accent, active_allies):
        veil = pygame.Surface((1280, 720), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 226))
        surface.blit(veil, (0, 0))
        panel = pygame.Rect(80, 55, 1120, 610)
        pygame.draw.rect(surface, (7, 12, 19), panel, border_radius=24)
        pygame.draw.rect(surface, accent, panel, 2, border_radius=24)

        surface.blit(fonts["title"].render("RPG DEPTH II — INVENTÁRIO & BUILD", True, (239, 244, 248)), (125, 92))
        stats = total_stats(self.profile)
        build = self.profile["v28_build"]
        surface.blit(fonts["heading"].render(f"BUILD: {build}", True, accent), (125, 145))
        surface.blit(
            fonts["body"].render(
                f"ATQ {stats['attack']}  DEF {stats['defense']}  CRIT {int(stats['crit'] * 100)}%  ENERGIA {stats['energy']}",
                True,
                (220, 228, 234),
            ),
            (125, 185),
        )

        candidate, equipped = self.comparison()
        y = 250
        if candidate:
            surface.blit(fonts["heading"].render("COMPARAÇÃO DE ITEM", True, (231, 190, 93)), (125, y))
            y += 42
            left = f"NOVO: {candidate['rarity']} {candidate['name']} +{candidate['value']} {candidate['stat']}"
            current = (
                f"ATUAL: {equipped['rarity']} {equipped['name']} +{equipped['value']} {equipped['stat']}"
                if equipped
                else "ATUAL: vazio"
            )
            delta = item_score(candidate) - item_score(equipped)
            surface.blit(fonts["body"].render(left, True, (230, 235, 240)), (125, y))
            surface.blit(fonts["body"].render(current, True, (180, 191, 202)), (125, y + 38))
            surface.blit(
                fonts["body"].render(f"Score relativo: {delta:+.1f}", True, (83, 212, 139) if delta >= 0 else (225, 82, 92)),
                (125, y + 76),
            )
        else:
            surface.blit(fonts["body"].render("Nenhum equipamento na bolsa.", True, (180, 191, 202)), (125, y))

        synergy = synergy_for(active_allies)
        if synergy:
            name, stat, value = synergy
            text = f"SINERGIA ATIVA: {name} • +{value} {stat}"
        else:
            text = "SINERGIA: selecione dois Eternos compatíveis"
        surface.blit(fonts["heading"].render(text, True, accent), (125, 440))

        surface.blit(fonts["small"].render(
            "←/→ item • Espaço equipa • B troca build • Y/Esc fecha • skill trees no painel Companheiros",
            True,
            (150, 164, 178),
        ), (125, 615))
