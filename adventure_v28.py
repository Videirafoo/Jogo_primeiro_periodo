import math
import random

import pygame


SITE_TYPES = (
    "camp",
    "fortress",
    "cave",
    "ruins",
    "catacomb",
    "coast",
    "ship",
    "island",
)

SITE_LABELS = {
    "camp": "Acampamento",
    "fortress": "Fortaleza",
    "cave": "Caverna Profunda",
    "ruins": "Ruínas",
    "catacomb": "Catacumbas",
    "coast": "Costa de Valdrak",
    "ship": "Navio Naufragado",
    "island": "Ilha Secreta",
}

SUBREGIONS = {
    1: ("Campos da Chuva", "Desfiladeiro Azul", "Costa de Skarn"),
    2: ("Muralha Exterior", "Vale dos Ossos", "Falésias do Norte"),
    3: ("Bairro dos Despertos", "Campos da Arena", "Porto Antigo"),
    4: ("Bosque Interior", "Pântano dos Corvos", "Cachoeiras Velhas"),
    5: ("Planície Congelada", "Passo dos Lobos", "Costa de Gelo"),
    6: ("Distrito da Forja", "Canais de Lava", "Escarpas Negras"),
    7: ("Vale do Vazio", "Escadas da Última Porta", "Costa do Segundo Céu"),
}

REGION_ROUTES = {
    1: ((180, 540), (520, 450), (860, 610), (1220, 500), (1620, 650)),
    2: ((160, 650), (500, 560), (860, 480), (1240, 570), (1660, 420)),
    3: ((160, 460), (480, 500), (850, 430), (1260, 470), (1660, 560)),
    4: ((180, 680), (500, 520), (860, 600), (1220, 420), (1620, 510)),
    5: ((170, 500), (530, 650), (870, 520), (1230, 600), (1640, 430)),
    6: ((180, 420), (520, 590), (850, 460), (1220, 640), (1640, 520)),
    7: ((180, 620), (520, 470), (860, 560), (1240, 430), (1640, 610)),
}


class AdventureSite:
    def __init__(self, region, kind, pos, index):
        self.region = region
        self.kind = kind
        self.pos = pygame.Vector2(pos)
        self.index = index
        self.id = f"v28_site_{region}_{kind}"
        self.name = f"{SITE_LABELS[kind]} — {SUBREGIONS[region][index % 3]}"
        self.discovered = False
        self.completed = False


class AdventureDepthV28:
    def __init__(self, region, profile):
        self.region = region
        self.profile = profile
        self.profile.setdefault("v28_sites", {})
        self.profile.setdefault("v28_discoveries", [])
        self.profile.setdefault("v28_secret_islands", [])
        self.profile.setdefault("v28_subregions", {})
        self.profile["v28_subregions"].setdefault(str(region), 0)
        self.current_site = None
        self.site_stage = 0
        self.site_progress = 0
        self.rng = random.Random(82800 + region)
        points = (
            (225, 300),
            (480, 820),
            (710, 250),
            (940, 820),
            (1175, 260),
            (1410, 780),
            (1600, 350),
            (1650, 900),
        )
        self.sites = [
            AdventureSite(region, kind, points[index], index)
            for index, kind in enumerate(SITE_TYPES)
        ]
        for site in self.sites:
            state = self.profile["v28_sites"].setdefault(
                site.id,
                {"discovered": False, "completed": False},
            )
            site.discovered = state["discovered"]
            site.completed = state["completed"]

    @property
    def subregion_index(self):
        return self.profile["v28_subregions"][str(self.region)]

    @property
    def subregion_name(self):
        return SUBREGIONS[self.region][self.subregion_index % 3]

    def cycle_subregion(self, direction=1):
        value = (self.subregion_index + direction) % 3
        self.profile["v28_subregions"][str(self.region)] = value
        return SUBREGIONS[self.region][value]

    def nearest_site(self, player_pos):
        candidates = [
            (player_pos.distance_to(site.pos), site)
            for site in self.sites
            if self._site_available(site)
        ]
        if not candidates:
            return None
        distance, site = min(candidates, key=lambda row: row[0])
        return site if distance <= 88 else None

    def _site_available(self, site):
        if site.kind != "island":
            return True
        inventory = self.profile.get("inventory", {})
        return (
            inventory.get("chave", 0) >= 1
            or inventory.get("reliquia", 0) >= 2
            or site.id in self.profile["v28_secret_islands"]
        )

    def enter(self, site):
        self.current_site = site
        self.site_stage = 0
        self.site_progress = 0
        site.discovered = True
        self.profile["v28_sites"][site.id]["discovered"] = True
        if site.id not in self.profile["v28_discoveries"]:
            self.profile["v28_discoveries"].append(site.id)
        if site.kind == "island" and site.id not in self.profile["v28_secret_islands"]:
            self.profile["v28_secret_islands"].append(site.id)
        return f"Você entrou em {site.name}."

    def exit(self):
        name = self.current_site.name if self.current_site else "local"
        self.current_site = None
        self.site_stage = 0
        self.site_progress = 0
        return f"Você deixou {name}."

    def complete_site(self):
        if not self.current_site:
            return ""
        site = self.current_site
        site.completed = True
        self.profile["v28_sites"][site.id]["completed"] = True
        reward = 28 + self.region * 7 + site.index * 3
        self.profile["coins"] = self.profile.get("coins", 0) + reward
        return f"{site.name} concluído • +{reward} moedas"

    def handle_key(self, key, world):
        if not self.current_site:
            return None

        if key in {pygame.K_ESCAPE, pygame.K_e}:
            return self.exit(), "wind"

        site = self.current_site
        if key in {pygame.K_RIGHT, pygame.K_d, pygame.K_SPACE}:
            self.site_progress += 1
            if site.kind in {"cave", "catacomb", "fortress"}:
                if self.site_progress >= 2:
                    world.dungeon_v28.start_from_site(site.kind)
                    return "__open_dungeon_v28__", "gate"
                return f"{site.name}: você avança para uma seção mais profunda.", "footstep_stone"

            if site.kind == "camp":
                if self.site_progress == 1:
                    return "Você encontra patrulheiros reunidos ao redor da fogueira.", "fire"
                if self.site_progress >= 2:
                    return self.complete_site(), "victory"

            if site.kind == "ruins":
                if self.site_progress == 1:
                    return "Uma parede rúnica revela uma inscrição esquecida.", "rune"
                if self.site_progress >= 2:
                    world.profile["inventory"]["reliquia"] = (
                        world.profile["inventory"].get("reliquia", 0) + 1
                    )
                    return self.complete_site() + " • +1 Relíquia", "secret"

            if site.kind == "coast":
                if self.site_progress == 1:
                    return "A maré recua e revela uma passagem entre as pedras.", "water"
                if self.site_progress >= 2:
                    return self.complete_site(), "victory"

            if site.kind == "ship":
                if self.site_progress == 1:
                    return "O convés range. Há marcas de combate e um porão fechado.", "door_wood"
                if self.site_progress >= 2:
                    world.profile["inventory"]["chave"] = (
                        world.profile["inventory"].get("chave", 0) + 1
                    )
                    return self.complete_site() + " • +1 Chave Rúnica", "pickup"

            if site.kind == "island":
                if self.site_progress == 1:
                    return "A ilha não aparece no horizonte quando você olha para trás.", "portal"
                if self.site_progress >= 2:
                    world.profile["skill_points"] = world.profile.get("skill_points", 0) + 1
                    return self.complete_site() + " • +1 ponto de talento", "quest_complete"

        return "", ""

    def draw_exterior(self, surface, camera, fonts, seconds, player_pos):
        # Roads connecting settlements and adventure sites.
        route = REGION_ROUTES[self.region]
        points = [
            (int(x - camera.x), int(y - camera.y))
            for x, y in route
        ]
        pygame.draw.lines(surface, (94, 76, 55), False, points, 20)
        pygame.draw.lines(surface, (132, 104, 70), False, points, 3)

        colors = {
            "camp": (231, 151, 67),
            "fortress": (171, 176, 186),
            "cave": (103, 113, 124),
            "ruins": (142, 126, 100),
            "catacomb": (114, 90, 130),
            "coast": (73, 151, 180),
            "ship": (121, 83, 53),
            "island": (78, 221, 184),
        }
        symbols = {
            "camp": "A",
            "fortress": "F",
            "cave": "C",
            "ruins": "R",
            "catacomb": "K",
            "coast": "~",
            "ship": "N",
            "island": "I",
        }

        for site in self.sites:
            if not self._site_available(site):
                continue
            x = int(site.pos.x - camera.x)
            y = int(site.pos.y - camera.y)
            if not (-80 < x < 1360 and -80 < y < 800):
                continue
            color = colors[site.kind]
            pulse = 17 + int((math.sin(seconds * 2.5 + site.index) + 1) * 3)
            pygame.draw.circle(surface, (7, 11, 15), (x, y), pulse + 6)
            pygame.draw.circle(surface, color, (x, y), pulse, 2)
            glyph = fonts["small"].render(symbols[site.kind], True, color)
            surface.blit(glyph, glyph.get_rect(center=(x, y)))
            if site.completed:
                pygame.draw.circle(surface, (83, 212, 139), (x + 16, y - 16), 5)
            if player_pos.distance_to(site.pos) <= 88:
                label = fonts["small"].render(f"E — {site.name}", True, (238, 243, 248))
                box = label.get_rect(center=(x, y - 45)).inflate(16, 8)
                pygame.draw.rect(surface, (5, 9, 15), box, border_radius=8)
                pygame.draw.rect(surface, color, box, 1, border_radius=8)
                surface.blit(label, label.get_rect(center=box.center))

    def draw_site(self, surface, fonts, accent, seconds):
        if not self.current_site:
            return
        site = self.current_site
        surface.fill((7, 10, 14))
        panel = pygame.Rect(70, 58, 1140, 600)
        pygame.draw.rect(surface, (15, 20, 28), panel, border_radius=22)
        pygame.draw.rect(surface, accent, panel, 2, border_radius=22)

        title = fonts["title"].render(site.name, True, (239, 244, 248))
        surface.blit(title, (110, 96))
        subtitle = fonts["body"].render(
            f"Sub-região: {self.subregion_name} • exploração {self.site_progress}/2",
            True,
            accent,
        )
        surface.blit(subtitle, (112, 142))

        descriptions = {
            "camp": "Fogueiras, tendas, vigias e rastros de uma patrulha inimiga.",
            "fortress": "Muros, torres e corredores levam a uma masmorra ocupada.",
            "cave": "O ar fica frio. O som vem de túneis abaixo da região.",
            "ruins": "Pedras antigas guardam inscrições que reagem às runas.",
            "catacomb": "Escadas levam a câmaras funerárias e portas especiais.",
            "coast": "Ondas, rochedos e cavernas costeiras cercam a trilha.",
            "ship": "Um navio preso às pedras ainda guarda o porão e o diário da tripulação.",
            "island": "Uma ilha secreta existe fora das rotas normais de Valdrak.",
        }
        y = 220
        for line in wrap_text(fonts["body"], descriptions[site.kind], 900):
            surface.blit(fonts["body"].render(line, True, (190, 201, 211)), (110, y))
            y += 32

        # Minimal scene art by site.
        cx, cy = 640, 425
        if site.kind == "camp":
            pygame.draw.polygon(surface, (112, 76, 48), [(cx - 120, cy + 60), (cx - 50, cy - 55), (cx + 20, cy + 60)])
            pygame.draw.circle(surface, (245, 123, 48), (cx + 95, cy + 45), 16)
        elif site.kind in {"fortress", "ruins", "catacomb"}:
            pygame.draw.rect(surface, (75, 79, 84), (cx - 150, cy - 80, 300, 160))
            pygame.draw.rect(surface, (15, 19, 24), (cx - 34, cy + 5, 68, 75), border_radius=22)
        elif site.kind == "cave":
            pygame.draw.ellipse(surface, (53, 60, 67), (cx - 180, cy - 100, 360, 220))
            pygame.draw.ellipse(surface, (4, 7, 10), (cx - 90, cy - 65, 180, 160))
        elif site.kind in {"coast", "ship", "island"}:
            pygame.draw.rect(surface, (24, 77, 101), (cx - 300, cy + 35, 600, 95))
            if site.kind == "ship":
                pygame.draw.polygon(surface, (106, 70, 42), [(cx - 120, cy + 35), (cx + 120, cy + 35), (cx + 80, cy + 95), (cx - 80, cy + 95)])
                pygame.draw.line(surface, (136, 100, 63), (cx, cy + 20), (cx, cy - 120), 7)
            elif site.kind == "island":
                pygame.draw.ellipse(surface, (73, 108, 65), (cx - 145, cy - 5, 290, 105))

        surface.blit(
            fonts["small"].render("D/Espaço explora • E/Esc sai", True, (150, 164, 178)),
            (110, 610),
        )


def wrap_text(font, text, width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if font.size(candidate)[0] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
