import pygame


FACTIONS = (
    "Clãs Livres",
    "Círculo Rúnico",
    "Errantes do Vazio",
)

OPTIONAL_QUESTS = {
    region: [
        {
            "id": f"optional_{region}_hunt",
            "title": "Caçada da Fronteira",
            "target": (
                "wolf"
                if region in {1, 4, 5}
                else "raider"
            ),
            "need": 3,
            "reward": 35 + region * 4,
        },
        {
            "id": f"optional_{region}_elite",
            "title": "Ameaça de Elite",
            "target": (
                "rune_mage"
                if region in {2, 6, 7}
                else "berserker"
            ),
            "need": 2,
            "reward": 55 + region * 5,
        },
    ]
    for region in range(1, 8)
}


def _ensure(profile):
    profile.setdefault(
        "v27_reputation",
        {name: 0 for name in FACTIONS},
    )
    profile.setdefault("v27_optional", {})
    profile.setdefault("v27_world_ending", None)
    profile.setdefault("v27_major_choices", [])


class QuestSystemII:
    def __init__(self, region, profile):
        self.region = region
        self.profile = profile
        _ensure(profile)
        self._ensure_region()

    def _ensure_region(self):
        key = str(self.region)
        if key in self.profile["v27_optional"]:
            return
        self.profile["v27_optional"][key] = [
            {
                **quest,
                "accepted": False,
                "kills": 0,
                "complete": False,
            }
            for quest in OPTIONAL_QUESTS[self.region]
        ]

    @property
    def optional(self):
        return self.profile["v27_optional"][str(self.region)]

    def accept_optional(self, index):
        if not 0 <= index < len(self.optional):
            return "Missão opcional inválida."
        quest = self.optional[index]
        if quest["complete"]:
            return f"{quest['title']} já foi concluída."
        quest["accepted"] = True
        return (
            f"Missão opcional aceita: {quest['title']} • "
            f"{quest['kills']}/{quest['need']} {quest['target']}."
        )

    def on_kill(self, archetype):
        messages = []
        for quest in self.optional:
            if (
                quest["accepted"]
                and not quest["complete"]
                and quest["target"] == archetype
            ):
                quest["kills"] += 1
                if quest["kills"] >= quest["need"]:
                    quest["complete"] = True
                    self.profile["coins"] = self.profile.get("coins", 0) + quest["reward"]
                    self.profile["v27_reputation"]["Clãs Livres"] += 2
                    messages.append(
                        f"Opcional concluída: {quest['title']} • +{quest['reward']} moedas"
                    )
        return messages

    def on_choice(self, consequence):
        if consequence == "proteger":
            self.profile["v27_reputation"]["Círculo Rúnico"] += 3
            self.profile["v27_reputation"]["Clãs Livres"] += 1
        elif consequence == "libertar":
            self.profile["v27_reputation"]["Errantes do Vazio"] += 3
            self.profile["v27_reputation"]["Clãs Livres"] += 1
        marker = f"{self.region}:{consequence}"
        if marker not in self.profile["v27_major_choices"]:
            self.profile["v27_major_choices"].append(marker)

    def ending(self):
        choices = self.profile.get("v26_consequences", {})
        protect = sum(1 for value in choices.values() if value == "proteger")
        liberate = sum(1 for value in choices.values() if value == "libertar")
        rep = self.profile["v27_reputation"]

        if protect >= 5 and rep["Círculo Rúnico"] >= 8:
            return "O Guardião de Valdrak"
        if liberate >= 5 and rep["Errantes do Vazio"] >= 8:
            return "A Segunda Valdrak"
        if rep["Clãs Livres"] >= 10:
            return "A Era dos Clãs Livres"
        return "O Caminho Entre Mundos"

    def finalize_ending(self):
        ending = self.ending()
        self.profile["v27_world_ending"] = ending
        return ending

    def marker_targets(self, v26, enemies):
        markers = []
        state = v26.quest_state
        if state["stage"] in {0, 2, 4}:
            giver = next(
                (
                    npc
                    for npc in v26.villagers
                    if npc.name == v26.quest_dialogue.__self__.profile.get("_unused", "")
                ),
                None,
            )
            # More reliable: first villager is always the regional giver in V2.6 data.
            giver = v26.villagers[0]
            markers.append(("quest", giver.pos, "QUEST"))

        if state["stage"] == 1:
            target_name = {
                1: "raider",
                2: "rune_mage",
                3: "berserker",
                4: "raven",
                5: "alpha_wolf",
                6: "elite_raider",
                7: "rune_mage",
            }[self.region]
            target = next(
                (
                    enemy
                    for enemy in enemies
                    if not enemy.dead
                    and enemy.archetype == target_name
                ),
                None,
            )
            if target:
                markers.append(("target", target.pos, "ALVO"))

        if state["stage"] == 3:
            secret = next(
                (
                    secret
                    for secret in v26.secrets
                    if secret.id not in self.profile["v26_secrets"]
                ),
                None,
            )
            if secret:
                markers.append(("secret", secret.pos, "SEGREDO"))

        return markers

    def draw_markers(self, surface, camera, fonts, v26, enemies):
        colors = {
            "quest": (231, 190, 93),
            "target": (225, 82, 92),
            "secret": (158, 116, 255),
        }
        for kind, pos, label in self.marker_targets(v26, enemies):
            x = int(pos.x - camera.x)
            y = int(pos.y - camera.y)
            if 18 <= x <= 1262 and 80 <= y <= 700:
                color = colors[kind]
                pygame.draw.polygon(
                    surface,
                    color,
                    [(x, y - 54), (x - 9, y - 38), (x + 9, y - 38)],
                )
                text = fonts["small"].render(label, True, color)
                surface.blit(text, text.get_rect(center=(x, y - 67)))
            else:
                # Edge compass marker.
                sx = min(1240, max(40, x))
                sy = min(675, max(95, y))
                pygame.draw.circle(surface, colors[kind], (sx, sy), 12, 2)

    def draw_overlay(self, surface, fonts, accent):
        veil = pygame.Surface((1280, 720), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 222))
        surface.blit(veil, (0, 0))
        panel = pygame.Rect(170, 78, 940, 570)
        pygame.draw.rect(surface, (7, 12, 19), panel, border_radius=24)
        pygame.draw.rect(surface, accent, panel, 2, border_radius=24)

        surface.blit(
            fonts["title"].render("FACÇÕES & QUESTS OPCIONAIS", True, (240, 244, 247)),
            (220, 116),
        )
        y = 182
        for faction in FACTIONS:
            value = self.profile["v27_reputation"][faction]
            surface.blit(
                fonts["body"].render(f"{faction}: {value:+d}", True, accent),
                (220, y),
            )
            y += 42

        y += 18
        for index, quest in enumerate(self.optional, 1):
            status = (
                "CONCLUÍDA"
                if quest["complete"]
                else "ATIVA"
                if quest["accepted"]
                else "DISPONÍVEL"
            )
            line = (
                f"{index}. {quest['title']} — {quest['kills']}/{quest['need']} "
                f"{quest['target']} — {quest['reward']} moedas — {status}"
            )
            surface.blit(
                fonts["body"].render(line, True, (222, 228, 233)),
                (220, y),
            )
            y += 58

        ending = self.profile.get("v27_world_ending")
        preview = ending or self.ending()
        surface.blit(
            fonts["heading"].render(f"Destino provável: {preview}", True, (231, 190, 93)),
            (220, 535),
        )
        surface.blit(
            fonts["small"].render("1/2 aceita opcional • L/Esc fecha • escolhas alteram reputação e final", True, (151, 164, 178)),
            (220, 600),
        )
