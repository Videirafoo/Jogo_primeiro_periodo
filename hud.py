from pathlib import Path
import pygame

ASSET_ROOT = Path(__file__).with_name("assets") / "kenney" / "ui"

INK = (245, 247, 250)
MUTED = (176, 186, 198)
RED = (224, 74, 83)
CYAN = (69, 215, 230)
GOLD = (230, 188, 91)


class RPGHUD:
    def __init__(self):
        self.images = {}
        for name in ["panel_blue.png", "panel_brown.png"]:
            path = ASSET_ROOT / name
            if not path.exists():
                continue
            try:
                self.images[name] = pygame.image.load(str(path)).convert_alpha()
            except pygame.error:
                pass

    def panel(self, surface, rect, brown=False):
        key = "panel_brown.png" if brown else "panel_blue.png"
        image = self.images.get(key)

        if image:
            surface.blit(
                pygame.transform.smoothscale(image, rect.size),
                rect,
            )
        else:
            pygame.draw.rect(
                surface,
                (10, 18, 28),
                rect,
                border_radius=16,
            )

    def draw(self, surface, fonts, world, theme):
        accent = theme["accent"]

        region = pygame.Rect(18, 16, 370, 92)
        self.panel(surface, region)
        surface.blit(
            fonts["heading"].render(theme["name"], True, INK),
            (42, 34),
        )

        meta = (
            f"NÍVEL {world.profile['level']} • "
            f"XP {world.profile['xp']}/{world.profile['xp_next']} • "
            f"ABATES {world.profile['kills']}"
        )
        surface.blit(
            fonts["small"].render(meta, True, MUTED),
            (43, 72),
        )

        vitals = pygame.Rect(405, 16, 420, 92)
        self.panel(surface, vitals)

        self._bar(
            surface,
            fonts["small"],
            pygame.Rect(438, 43, 350, 14),
            world.player.health,
            world.profile["max_health"],
            RED,
            "VIDA",
        )
        self._bar(
            surface,
            fonts["small"],
            pygame.Rect(438, 79, 350, 14),
            world.player.energy,
            world.profile["max_energy"],
            CYAN,
            "ENERGIA",
        )

        info = pygame.Rect(842, 16, 420, 92)
        self.panel(surface, info, brown=True)

        inventory = world.profile["inventory"]
        items = (
            f"POÇÃO {inventory['pocao']}   "
            f"ESSÊNCIA {inventory['essencia']}   "
            f"FRAGMENTOS {inventory['fragmento']}"
        )

        surface.blit(
            fonts["small"].render(items, True, INK),
            (865, 39),
        )
        surface.blit(
            fonts["small"].render(
                "ESC menu • I inventário • F5 salvar",
                True,
                MUTED,
            ),
            (865, 72),
        )

        boss = world.boss()
        if boss and not boss.dead:
            ratio = max(0, boss.hp) / boss.max_hp
            bar = pygame.Rect(350, 124, 580, 18)
            pygame.draw.rect(
                surface,
                (35, 25, 27),
                bar,
                border_radius=9,
            )
            pygame.draw.rect(
                surface,
                GOLD,
                (
                    bar.x,
                    bar.y,
                    int(bar.width * ratio),
                    bar.height,
                ),
                border_radius=9,
            )

            label = fonts["small"].render(
                f"GUARDIÃO — {boss.name}",
                True,
                GOLD,
            )
            surface.blit(
                label,
                label.get_rect(center=(640, 116)),
            )

        dock = pygame.Rect(408, 638, 464, 64)
        self.panel(surface, dock)

        abilities = [
            ("ESPAÇO", "ATAQUE"),
            ("Q", "PULSO"),
            ("SHIFT", "DASH"),
            ("R", "ETERNO"),
        ]

        for index, (key, label) in enumerate(abilities):
            x = 430 + index * 108
            cell = pygame.Rect(x, 650, 94, 40)
            pygame.draw.rect(
                surface,
                (25, 43, 61),
                cell,
                border_radius=10,
            )
            pygame.draw.rect(
                surface,
                accent,
                cell,
                1,
                border_radius=10,
            )
            surface.blit(
                fonts["small"].render(key, True, accent),
                (x + 8, 655),
            )
            surface.blit(
                fonts["small"].render(label, True, INK),
                (x + 8, 673),
            )

        prompt = world.interaction_hint()
        if prompt:
            rendered = fonts["small"].render(prompt, True, INK)
            box = rendered.get_rect(
                center=(640, 610)
            ).inflate(32, 18)

            pygame.draw.rect(
                surface,
                (5, 10, 17),
                box,
                border_radius=12,
            )
            pygame.draw.rect(
                surface,
                accent,
                box,
                1,
                border_radius=12,
            )
            surface.blit(
                rendered,
                rendered.get_rect(center=box.center),
            )

        if world.notice_timer > 0 and world.notice:
            rendered = fonts["small"].render(
                world.notice,
                True,
                GOLD,
            )
            box = rendered.get_rect(
                center=(640, 165)
            ).inflate(28, 14)

            pygame.draw.rect(
                surface,
                (8, 13, 20),
                box,
                border_radius=10,
            )
            surface.blit(
                rendered,
                rendered.get_rect(center=box.center),
            )

    @staticmethod
    def _bar(
        surface,
        font,
        rect,
        value,
        maximum,
        color,
        label,
    ):
        ratio = (
            0
            if maximum <= 0
            else max(0, min(1, value / maximum))
        )

        pygame.draw.rect(
            surface,
            (32, 39, 49),
            rect,
            border_radius=7,
        )
        pygame.draw.rect(
            surface,
            color,
            (
                rect.x,
                rect.y,
                int(rect.width * ratio),
                rect.height,
            ),
            border_radius=7,
        )
        surface.blit(
            font.render(
                f"{label} {int(value)}/{int(maximum)}",
                True,
                INK,
            ),
            (rect.x, rect.y - 20),
        )
