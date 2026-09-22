import pygame

INK = (245, 247, 250)
MUTED = (156, 169, 184)
RED = (224, 74, 83)
CYAN = (69, 215, 230)
GOLD = (230, 188, 91)
DARK = (7, 11, 17)
DARK_2 = (13, 20, 29)


class RPGHUD:
    def panel(self, surface, rect, accent, brown=False):
        layer = pygame.Surface(
            rect.size,
            pygame.SRCALPHA,
        )
        fill = (
            (22, 15, 11, 226)
            if brown
            else (7, 12, 19, 228)
        )
        layer.fill(fill)
        surface.blit(layer, rect)

        pygame.draw.rect(
            surface,
            (
                accent[0],
                accent[1],
                accent[2],
                255,
            ),
            rect,
            1,
            border_radius=14,
        )

        inner = rect.inflate(-6, -6)
        pygame.draw.rect(
            surface,
            (50, 61, 74),
            inner,
            1,
            border_radius=11,
        )

    def draw(self, surface, fonts, world, theme):
        accent = theme["accent"]

        region = pygame.Rect(
            18,
            14,
            300,
            70,
        )
        self.panel(
            surface,
            region,
            accent,
        )

        surface.blit(
            fonts["heading"].render(
                theme["name"],
                True,
                INK,
            ),
            (34, 25),
        )

        found, total = world.exploration_progress()
        meta = (
            f"NÍVEL {world.profile['level']}  "
            f"XP {world.profile['xp']}/{world.profile['xp_next']}  "
            f"DESCOBERTAS {found}/{total}"
        )

        surface.blit(
            fonts["small"].render(
                meta,
                True,
                MUTED,
            ),
            (35, 56),
        )

        vitals = pygame.Rect(
            330,
            14,
            400,
            70,
        )
        self.panel(
            surface,
            vitals,
            accent,
        )

        self._bar(
            surface,
            fonts["small"],
            pygame.Rect(
                358,
                34,
                344,
                10,
            ),
            world.player.health,
            world.profile["max_health"],
            RED,
            "VIDA",
        )

        self._bar(
            surface,
            fonts["small"],
            pygame.Rect(
                358,
                66,
                344,
                10,
            ),
            world.player.energy,
            world.profile["max_energy"],
            CYAN,
            "ENERGIA",
        )

        info = pygame.Rect(
            742,
            14,
            520,
            70,
        )
        self.panel(
            surface,
            info,
            accent,
            brown=True,
        )

        inventory = world.profile["inventory"]
        relics = inventory.get(
            "reliquia",
            0,
        )
        keys = inventory.get(
            "chave",
            0,
        )

        items = (
            f"POÇÃO {inventory['pocao']}   "
            f"ESSÊNCIA {inventory['essencia']}   "
            f"FRAG {inventory['fragmento']}   "
            f"RELÍQUIA {relics}   "
            f"CHAVE {keys}"
        )

        surface.blit(
            fonts["small"].render(
                items,
                True,
                INK,
            ),
            (760, 30),
        )

        quest = world.active_objective()
        surface.blit(
            fonts["small"].render(
                f"MISSÃO: {quest}",
                True,
                MUTED,
            ),
            (760, 57),
        )

        boss = world.boss()
        if boss and not boss.dead:
            ratio = (
                max(0, boss.hp)
                / boss.max_hp
            )

            bar = pygame.Rect(
                360,
                98,
                500,
                12,
            )

            pygame.draw.rect(
                surface,
                (30, 18, 20),
                bar,
                border_radius=7,
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
                border_radius=7,
            )

            label = fonts["small"].render(
                f"GUARDIÃO — {boss.name}",
                True,
                GOLD,
            )
            surface.blit(
                label,
                label.get_rect(
                    center=(640, 92)
                ),
            )

        dock = pygame.Rect(
            455,
            662,
            370,
            42,
        )
        self.panel(
            surface,
            dock,
            accent,
        )

        abilities = [
            ("ESPAÇO", "ATAQUE"),
            ("Q", "PULSO"),
            ("SHIFT", "DASH"),
            ("R", "ETERNO"),
        ]

        for index, (
            key,
            label,
        ) in enumerate(abilities):
            x = 464 + index * 89
            cell = pygame.Rect(
                x,
                668,
                80,
                29,
            )

            pygame.draw.rect(
                surface,
                DARK_2,
                cell,
                border_radius=8,
            )
            pygame.draw.rect(
                surface,
                accent,
                cell,
                1,
                border_radius=8,
            )

            surface.blit(
                fonts["small"].render(
                    key,
                    True,
                    accent,
                ),
                (x + 6, 669),
            )

            surface.blit(
                fonts["small"].render(
                    label,
                    True,
                    INK,
                ),
                (x + 6, 683),
            )

        prompt = world.interaction_hint()
        if prompt:
            rendered = fonts["small"].render(
                prompt,
                True,
                INK,
            )
            box = rendered.get_rect(
                center=(640, 628)
            ).inflate(
                30,
                16,
            )

            pygame.draw.rect(
                surface,
                DARK,
                box,
                border_radius=10,
            )
            pygame.draw.rect(
                surface,
                accent,
                box,
                1,
                border_radius=10,
            )

            surface.blit(
                rendered,
                rendered.get_rect(
                    center=box.center
                ),
            )

        if (
            world.notice_timer > 0
            and world.notice
        ):
            rendered = fonts["small"].render(
                world.notice,
                True,
                GOLD,
            )
            box = rendered.get_rect(
                center=(640, 154)
            ).inflate(
                28,
                12,
            )

            pygame.draw.rect(
                surface,
                DARK,
                box,
                border_radius=9,
            )

            surface.blit(
                rendered,
                rendered.get_rect(
                    center=box.center
                ),
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
            else max(
                0,
                min(
                    1,
                    value / maximum,
                ),
            )
        )

        pygame.draw.rect(
            surface,
            (28, 36, 46),
            rect,
            border_radius=6,
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
            border_radius=6,
        )

        surface.blit(
            font.render(
                (
                    f"{label} "
                    f"{int(value)}/"
                    f"{int(maximum)}"
                ),
                True,
                INK,
            ),
            (
                rect.x,
                rect.y - 18,
            ),
        )
