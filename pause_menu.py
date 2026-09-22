import pygame


INK = (238, 243, 248)
MUTED = (151, 166, 183)
PANEL = (8, 14, 22)
PANEL_2 = (18, 29, 42)
GOLD = (231, 190, 93)
CYAN = (70, 224, 235)


class PauseMenu:
    OPTIONS = [
        ("CONTINUAR", "resume"),
        ("SALVAR JOGO", "save"),
        ("CARREGAR JOGO", "load"),
        ("INVENTÁRIO", "inventory"),
        ("ÁUDIO", "audio"),
        ("CONTROLES", "controls"),
        ("GALERIA DE FINAIS", "gallery"),
        ("CRÉDITOS", "credits"),
        ("SAIR DO JOGO", "quit"),
    ]

    def __init__(self):
        self.selected = 0
        self.screen = "menu"
        self.rects = []

    def reset(self):
        self.selected = 0
        self.screen = "menu"

    def handle_key(self, event):
        if self.screen in {"controls", "gallery", "credits"}:
            if event.key in (
                pygame.K_ESCAPE,
                pygame.K_RETURN,
                pygame.K_SPACE,
            ):
                self.screen = "menu"
            return None

        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % len(self.OPTIONS)
            return None

        if event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % len(self.OPTIONS)
            return None

        if event.key == pygame.K_ESCAPE:
            return "resume"

        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            action = self.OPTIONS[self.selected][1]
            if action in {"controls", "gallery", "credits"}:
                self.screen = action
                return None
            return action

        return None

    def handle_click(self, point):
        if self.screen in {"controls", "gallery", "credits"}:
            self.screen = "menu"
            return None

        for index, rect in enumerate(self.rects):
            if rect.collidepoint(point):
                self.selected = index
                action = self.OPTIONS[index][1]
                if action in {"controls", "gallery", "credits"}:
                    self.screen = action
                    return None
                return action

        return None

    def draw(self, surface, fonts, audio, phase, has_world, gallery=None):
        veil = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 190))
        surface.blit(veil, (0, 0))

        panel = pygame.Rect(350, 78, 580, 570)
        pygame.draw.rect(surface, PANEL, panel, border_radius=24)
        pygame.draw.rect(surface, CYAN, panel, 2, border_radius=24)

        title = fonts["title"].render("OS ETERNOS", True, INK)
        surface.blit(title, title.get_rect(center=(640, 120)))

        sub = fonts["small"].render(
            "MENU DE PAUSA • VALDRAK",
            True,
            CYAN,
        )
        surface.blit(sub, sub.get_rect(center=(640, 158)))

        if self.screen == "controls":
            self._draw_controls(surface, fonts, panel)
            return

        if self.screen == "gallery":
            self._draw_gallery(
                surface,
                fonts,
                panel,
                gallery,
            )
            return

        if self.screen == "credits":
            self._draw_credits(
                surface,
                fonts,
                panel,
            )
            return

        self.rects = []
        y = 184
        for index, (label, action) in enumerate(self.OPTIONS):
            disabled = action == "inventory" and not has_world
            rect = pygame.Rect(405, y + index * 47, 470, 40)
            self.rects.append(rect)

            selected = index == self.selected
            bg = (31, 50, 69) if selected else PANEL_2
            border = CYAN if selected else (55, 70, 85)
            color = MUTED if disabled else INK

            pygame.draw.rect(surface, bg, rect, border_radius=12)
            pygame.draw.rect(surface, border, rect, 1, border_radius=12)
            rendered = fonts["button"].render(label, True, color)
            surface.blit(rendered, rendered.get_rect(center=rect.center))

        volume = int(audio.master_volume * 100)
        footer = (
            f"Áudio {'ON' if audio.enabled else 'OFF'} • "
            f"Volume {volume}% • Estado: {phase}"
        )
        rendered = fonts["small"].render(footer, True, MUTED)
        surface.blit(rendered, rendered.get_rect(center=(640, 622)))

    def _draw_controls(self, surface, fonts, panel):
        heading = fonts["heading"].render("CONTROLES", True, GOLD)
        surface.blit(heading, (405, 200))

        rows = [
            ("WASD / Setas / Analógico", "Mover"),
            ("Espaço / A", "Ataque / confirmar"),
            ("F / RB", "Ataque pesado"),
            ("P / LB", "Parry"),
            ("Shift / B", "Dash / esquiva perfeita"),
            ("Q / X", "Pulso de Código"),
            ("R / Y", "Poder dos Eternos"),
            ("X / R3", "Execução em Guardião atordoado"),
            ("E", "Interagir"),
            ("M / J / C / G", "Mapa / Quests / Codex / Equipamentos"),
            ("H", "Contratos / caçadas"),
            ("L", "Facções / quests opcionais / destino"),
            ("Y", "Inventário avançado / build / comparação"),
            ("Z", "Companheiros / amizade / skills"),
            ("K / T / U", "Craft / Talentos / Upgrade"),
            ("O", "Acessibilidade / dificuldade"),
            ("F5 / F9 / F6", "Salvar / carregar / trocar slot"),
            ("V / - / +", "Áudio / volume"),
            ("Esc / Start", "Pausa"),
        ]

        y = 248
        for key, action in rows:
            key_surf = fonts["button"].render(key, True, CYAN)
            action_surf = fonts["body"].render(action, True, INK)
            surface.blit(key_surf, (410, y))
            surface.blit(action_surf, (610, y + 1))
            y += 25

        hint = fonts["small"].render(
            "Enter, Espaço, Esc ou clique para voltar",
            True,
            MUTED,
        )
        surface.blit(hint, hint.get_rect(center=(640, 600)))

    def _draw_gallery(
        self,
        surface,
        fonts,
        panel,
        gallery,
    ):
        heading = fonts["heading"].render(
            "GALERIA DE FINAIS",
            True,
            GOLD,
        )
        surface.blit(heading, (405, 195))

        entries = (
            gallery.entries()
            if gallery
            else []
        )
        y = 245

        for entry in entries:
            unlocked = entry["unlocked"]
            title = (
                entry["title"]
                if unlocked
                else "Final bloqueado"
            )
            status = (
                "DESBLOQUEADO"
                if unlocked
                else "???"
            )
            color = (
                CYAN
                if unlocked
                else MUTED
            )

            surface.blit(
                fonts["body"].render(
                    title,
                    True,
                    color,
                ),
                (405, y),
            )
            surface.blit(
                fonts["small"].render(
                    status,
                    True,
                    color,
                ),
                (735, y + 4),
            )
            y += 55

        surface.blit(
            fonts["small"].render(
                "Esc ou Enter para voltar",
                True,
                MUTED,
            ),
            (405, 575),
        )

    def _draw_credits(
        self,
        surface,
        fonts,
        panel,
    ):
        from credits import CREDITS

        heading = fonts["heading"].render(
            "CRÉDITOS",
            True,
            GOLD,
        )
        surface.blit(heading, (405, 190))

        y = 232
        for line in CREDITS:
            if y > 575:
                break

            color = INK if line else MUTED
            surface.blit(
                fonts["small"].render(
                    line,
                    True,
                    color,
                ),
                (405, y),
            )
            y += 24

        surface.blit(
            fonts["small"].render(
                "Esc ou Enter para voltar",
                True,
                MUTED,
            ),
            (405, 600),
        )
