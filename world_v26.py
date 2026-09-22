import math
import random

import pygame

from npc_art_v27 import draw_npc_v27


REGION_TITLES = {
    1: "Estrada de Valdrak",
    2: "Portão dos Ossos",
    3: "Vila dos Despertos",
    4: "Bosque dos Corvos",
    5: "Terras dos Lobos de Ferro",
    6: "Forja dos Eternos",
    7: "Última Porta",
}

REGION_MINI_STORIES = {
    1: [
        "A estrada foi construída sobre uma cidade que ninguém consegue lembrar.",
        "As pedras azuis aquecem quando alguém sonha com o mesmo lugar duas noites seguidas.",
    ],
    2: [
        "Cada osso no portão pertenceu a alguém que tentou acordar cedo demais.",
        "Há uma passagem sob a muralha que só aparece quando a névoa cobre as runas.",
    ],
    3: [
        "Os moradores da vila juram ter chegado em anos diferentes, mas todos lembram da mesma tempestade.",
        "A arena foi um mercado antes de se tornar lugar de duelos.",
    ],
    4: [
        "Os corvos repetem nomes que ainda não foram ditos.",
        "No coração do bosque existe um templo que muda de posição durante a noite.",
    ],
    5: [
        "Os Lobos de Ferro não caçam carne. Eles seguem assinaturas de memória.",
        "Sob o gelo existe uma ponte inteira, preservada desde a primeira guerra de Valdrak.",
    ],
    6: [
        "A lava negra é memória queimada até virar matéria.",
        "Os martelos da forja continuam batendo mesmo quando nenhum ferreiro está presente.",
    ],
    7: [
        "A Última Porta não separa dois lugares, mas duas versões da mesma pessoa.",
        "Nidh guarda um nome gravado na pedra que o protagonista ainda não conhece.",
    ],
}

VILLAGER_NAMES = {
    1: ["Edda", "Hakon", "Runa", "Ivar", "Liv", "Sten", "Astrid"],
    2: ["Orm", "Ylva", "Knut", "Solveig", "Eirik", "Tora", "Bjorn"],
    3: ["Sigrun", "Freja", "Leif", "Ingrid", "Arne", "Kari", "Sven"],
    4: ["Hilda", "Ragnhild", "Odin", "Mira", "Egil", "Vera", "Ulrik"],
    5: ["Yrsa", "Fen", "Nora", "Asgeir", "Magne", "Sif", "Tor"],
    6: ["Torsten", "Bera", "Gunnar", "Alva", "Einar", "Rikke", "Brand"],
    7: ["Voz da Porta", "Njal", "Skadi", "Ravn", "Embla", "Vidar", "Saga"],
}

ROLES = (
    "vidente",
    "ferreiro",
    "caçador",
    "mercador",
    "guarda",
    "curandeira",
    "viajante",
)

ROLE_COLORS = {
    "vidente": (146, 102, 204),
    "ferreiro": (174, 83, 48),
    "caçador": (73, 112, 70),
    "mercador": (192, 151, 72),
    "guarda": (83, 112, 145),
    "curandeira": (81, 154, 118),
    "viajante": (110, 103, 94),
}

CONSEQUENCE_LABELS = {
    "proteger": "A vila ergueu fogueiras e patrulhas.",
    "libertar": "A vila abriu caminhos e acolheu viajantes.",
}

RARE_EVENTS = {
    1: ("Chuva de Runas", "Símbolos azuis caem como faíscas e revelam uma trilha antiga.", "rune"),
    2: ("Procissão da Névoa", "Silhuetas atravessam o portão sem deixar pegadas.", "voice_mystic"),
    3: ("Mercado Fantasma", "Barracas aparecem por alguns minutos com mercadorias impossíveis.", "rare_event"),
    4: ("Revoada Negra", "Centenas de corvos cobrem o céu e formam uma palavra.", "crow"),
    5: ("Uivo de Ferro", "A neve vibra com um uivo que vem debaixo do gelo.", "wolf"),
    6: ("Batida Sem Ferreiro", "Todos os martelos da Forja golpeiam ao mesmo tempo.", "forge"),
    7: ("Segundo Céu", "Por alguns segundos, outra Valdrak aparece acima da primeira.", "portal"),
}

UNIQUE_ENCOUNTERS = {
    1: ("O Cartógrafo Sem Rosto", "Ele oferece um mapa que mostra caminhos que ainda não existem."),
    2: ("A Criança do Portão", "Ela conhece o nome de pessoas que o protagonista ainda não encontrou."),
    3: ("O Campeão Sem Sombra", "Um guerreiro desafia você sem explicar de onde veio."),
    4: ("A Mulher dos Corvos", "Ela pede silêncio e entrega uma pena coberta de runas."),
    5: ("O Lobo Branco", "Ele não ataca. Apenas espera que você o siga."),
    6: ("O Ferreiro Morto", "Seu martelo continua quente apesar de suas mãos serem frias."),
    7: ("A Outra Voz", "Uma versão da sua própria voz responde antes de você falar."),
}

QUESTS = {
    1: {
        "title": "A Ponte que Lembra",
        "giver": "Edda",
        "target": "raider",
        "need": 3,
        "choices": (
            ("proteger", "Reforçar a vila e fechar a ponte."),
            ("libertar", "Abrir a ponte e deixar os viajantes passarem."),
        ),
    },
    2: {
        "title": "Ossos que Sussurram",
        "giver": "Orm",
        "target": "rune_mage",
        "need": 2,
        "choices": (
            ("proteger", "Selar as vozes sob o Portão."),
            ("libertar", "Quebrar o selo e ouvir os mortos."),
        ),
    },
    3: {
        "title": "O Campeão da Vila",
        "giver": "Sigrun",
        "target": "berserker",
        "need": 3,
        "choices": (
            ("proteger", "Defender a arena para os moradores."),
            ("libertar", "Abrir a arena para todos os despertos."),
        ),
    },
    4: {
        "title": "As Sete Penas",
        "giver": "Hilda",
        "target": "raven",
        "need": 4,
        "choices": (
            ("proteger", "Queimar o ninho dos corvos."),
            ("libertar", "Seguir os corvos até o templo."),
        ),
    },
    5: {
        "title": "Matilha de Ferro",
        "giver": "Yrsa",
        "target": "alpha_wolf",
        "need": 2,
        "choices": (
            ("proteger", "Caçar a matilha perto da vila."),
            ("libertar", "Poupar o lobo branco e seguir sua trilha."),
        ),
    },
    6: {
        "title": "O Coração da Forja",
        "giver": "Torsten",
        "target": "elite_raider",
        "need": 2,
        "choices": (
            ("proteger", "Reativar a forja para os Eternos."),
            ("libertar", "Desligar a forja e liberar as memórias."),
        ),
    },
    7: {
        "title": "A Porta Escolhe",
        "giver": "Voz da Porta",
        "target": "rune_mage",
        "need": 3,
        "choices": (
            ("proteger", "Fechar a realidade alternativa."),
            ("libertar", "Abrir a passagem e aceitar a segunda Valdrak."),
        ),
    },
}

CONTRACT_TARGETS = {
    1: ("wolf", "raider", "archer"),
    2: ("raider", "rune_mage", "elite_raider"),
    3: ("berserker", "archer", "raider"),
    4: ("raven", "rune_mage", "wolf"),
    5: ("wolf", "alpha_wolf", "berserker"),
    6: ("elite_raider", "rune_mage", "berserker"),
    7: ("rune_mage", "elite_raider", "alpha_wolf"),
}


def _ensure(profile):
    profile.setdefault("v26_time", 7.5)
    profile.setdefault("v26_quests", {})
    profile.setdefault("v26_contracts", {})
    profile.setdefault("v26_consequences", {})
    profile.setdefault("v26_secrets", [])
    profile.setdefault("v26_encounters", [])
    profile.setdefault("v26_lore", [])
    profile.setdefault("v26_rare_events", 0)
    profile.setdefault("coins", 0)


class Villager:
    def __init__(self, region, name, role, index):
        self.region = region
        self.name = name
        self.role = role
        self.index = index
        self.color = ROLE_COLORS[role]
        base_x = 430 + (index % 4) * 220
        base_y = 330 + (index // 4) * 220
        self.home = pygame.Vector2(base_x, base_y)
        self.work = pygame.Vector2(
            520 + (index * 173) % 770,
            260 + (index * 137) % 470,
        )
        self.market = pygame.Vector2(
            870 + (index % 3) * 95,
            545 + (index % 2) * 70,
        )
        self.pos = self.home.copy()
        self.target = self.home.copy()
        self.speed = 38 + index * 2
        self.facing = pygame.Vector2(0, 1)
        self.phase = index * 0.7

    def _schedule_target(self, hour):
        if 6 <= hour < 8:
            return self.market
        if 8 <= hour < 17:
            return self.work
        if 17 <= hour < 20:
            return self.market
        return self.home

    def update(self, dt, hour):
        self.target = self._schedule_target(hour)
        delta = self.target - self.pos
        if delta.length() > 8:
            direction = delta.normalize()
            self.facing = direction
            self.pos += direction * self.speed * dt
        else:
            self.phase += dt

    def dialogue(self, director, world):
        hour = director.hour
        quest = QUESTS[self.region]
        quest_state = director.quest_state
        consequence = director.profile["v26_consequences"].get(str(self.region))

        if self.name == quest["giver"]:
            return director.quest_dialogue(world)

        if consequence:
            return (
                f"{self.name}: {CONSEQUENCE_LABELS[consequence]} "
                f"Eu ainda lembro de quando você decidiu isso."
            )

        if world.boss_alive():
            if self.role == "guarda":
                return f"{self.name}: O Guardião ainda controla os caminhos. Não baixe a guarda."
            if self.role == "mercador":
                return f"{self.name}: Enquanto o Guardião viver, todo suprimento custa uma viagem perigosa."
        else:
            if self.role == "curandeira":
                return f"{self.name}: Depois da queda do Guardião, as pessoas voltaram a dormir sem pesadelos."

        if hour >= 20 or hour < 6:
            return f"{self.name}: A noite muda os caminhos. Algumas portas só existem agora."
        if self.role == "ferreiro":
            return f"{self.name}: Ferro de Valdrak guarda marcas de quem o empunhou."
        if self.role == "caçador":
            return f"{self.name}: Há pegadas recentes fora da trilha. Talvez uma caça rara."
        if self.role == "viajante":
            return f"{self.name}: Vim de uma estrada que não aparece no seu mapa."
        return f"{self.name}: Hoje a vila parece diferente. Valdrak reage a cada escolha."

    def draw(self, surface, camera, fonts, seconds, near=False):
        x = int(self.pos.x - camera.x)
        y = int(self.pos.y - camera.y)
        if not (-80 < x < 1360 and -100 < y < 810):
            return
        draw_npc_v27(
            surface,
            (x, y),
            self.role,
            self.facing,
            seconds,
            index=self.index,
            near=near,
            name=self.name,
            fonts=fonts,
        )
        return

        bob = int(abs(math.sin(seconds * 5 + self.phase)) * 2)
        pygame.draw.ellipse(surface, (0, 0, 0), (x - 18, y + 18, 36, 10))
        cape = tuple(max(0, c - 28) for c in self.color)
        pygame.draw.polygon(
            surface,
            cape,
            [(x - 13, y - 7 + bob), (x + 13, y - 7 + bob), (x + 18, y + 25), (x - 18, y + 25)],
        )
        pygame.draw.rect(surface, self.color, (x - 11, y - 9 + bob, 22, 29), border_radius=6)
        pygame.draw.circle(surface, (207, 171, 141), (x, y - 21 + bob), 10)
        pygame.draw.polygon(
            surface,
            (38, 33, 31),
            [(x - 10, y - 25 + bob), (x - 4, y - 34 + bob), (x + 9, y - 29 + bob), (x + 10, y - 22 + bob)],
        )
        pygame.draw.circle(surface, self.color, (x, y), 27, 1)
        if self.role == "ferreiro":
            pygame.draw.line(surface, (155, 119, 75), (x + 12, y), (x + 24, y - 20), 4)
            pygame.draw.rect(surface, (87, 92, 98), (x + 19, y - 25, 12, 8), border_radius=2)
        elif self.role == "guarda":
            pygame.draw.line(surface, (165, 175, 184), (x + 12, y + 2), (x + 24, y - 25), 3)
        elif self.role == "vidente":
            pygame.draw.circle(surface, (170, 125, 240), (x, y - 43), 5, 2)

        if near:
            role = self.role.upper()
            label = fonts["small"].render(f"E — {self.name} • {role}", True, (238, 243, 248))
            box = label.get_rect(center=(x, y - 52)).inflate(16, 8)
            pygame.draw.rect(surface, (6, 10, 16), box, border_radius=8)
            pygame.draw.rect(surface, self.color, box, 1, border_radius=8)
            surface.blit(label, label.get_rect(center=box.center))


class SecretSpot:
    def __init__(self, region, index, pos, text):
        self.region = region
        self.index = index
        self.id = f"v26_secret_{region}_{index}"
        self.pos = pygame.Vector2(pos)
        self.text = text

    def draw(self, surface, camera, seconds, discovered=False, near=False):
        x = int(self.pos.x - camera.x)
        y = int(self.pos.y - camera.y)
        if not (-80 < x < 1360 and -80 < y < 800):
            return
        if not discovered and not near:
            return
        color = (158, 116, 255)
        radius = 15 + int((math.sin(seconds * 3 + self.index) + 1) * 3)
        pygame.draw.circle(surface, color, (x, y), radius, 2)
        pygame.draw.line(surface, color, (x, y - 10), (x, y + 10), 2)
        pygame.draw.line(surface, color, (x - 8, y), (x + 8, y), 2)


class UniqueEncounter:
    def __init__(self, region, pos):
        self.region = region
        self.id = f"v26_encounter_{region}"
        self.name, self.text = UNIQUE_ENCOUNTERS[region]
        self.pos = pygame.Vector2(pos)

    def draw(self, surface, camera, fonts, seconds, done=False, near=False):
        if done:
            return
        x = int(self.pos.x - camera.x)
        y = int(self.pos.y - camera.y)
        if not (-80 < x < 1360 and -100 < y < 810):
            return
        pulse = 33 + int(math.sin(seconds * 2.2) * 4)
        pygame.draw.circle(surface, (10, 12, 17), (x, y), 25)
        pygame.draw.circle(surface, (231, 190, 93), (x, y), pulse, 2)
        pygame.draw.polygon(
            surface,
            (214, 221, 227),
            [(x, y - 28), (x - 13, y + 18), (x + 13, y + 18)],
            2,
        )
        if near:
            label = fonts["small"].render(f"E — encontro único: {self.name}", True, (238, 243, 248))
            box = label.get_rect(center=(x, y - 48)).inflate(16, 8)
            pygame.draw.rect(surface, (6, 10, 16), box, border_radius=8)
            pygame.draw.rect(surface, (231, 190, 93), box, 1, border_radius=8)
            surface.blit(label, label.get_rect(center=box.center))


class WorldQuestDirector:
    def __init__(self, region, profile, seed=0):
        self.region = region
        self.profile = profile
        _ensure(profile)
        self.rng = random.Random(62000 + region + seed)
        self.hour = float(profile.get("v26_time", 7.5))
        self.rare_timer = self.rng.uniform(28.0, 42.0)
        self.pending_choice = False
        self.villagers = [
            Villager(region, name, ROLES[index % len(ROLES)], index)
            for index, name in enumerate(VILLAGER_NAMES[region])
        ]
        stories = REGION_MINI_STORIES[region]
        self.secrets = [
            SecretSpot(region, 0, (250, 860), stories[0]),
            SecretSpot(region, 1, (1540, 180), stories[1]),
        ]
        self.encounter = UniqueEncounter(region, (1490, 815))
        self._ensure_quest()
        self._ensure_contracts()

    def _ensure_quest(self):
        key = str(self.region)
        self.profile["v26_quests"].setdefault(
            key,
            {
                "stage": 0,
                "kills": 0,
                "choice": None,
                "complete": False,
            },
        )

    @property
    def quest_state(self):
        return self.profile["v26_quests"][str(self.region)]

    def _ensure_contracts(self):
        region_key = str(self.region)
        if region_key in self.profile["v26_contracts"]:
            return
        self.profile["v26_contracts"][region_key] = []
        for index, archetype in enumerate(CONTRACT_TARGETS[self.region]):
            self.profile["v26_contracts"][region_key].append(
                {
                    "id": f"contract_{self.region}_{index}",
                    "target": archetype,
                    "need": 2 + index,
                    "kills": 0,
                    "accepted": False,
                    "complete": False,
                    "reward": 25 + index * 20 + self.region * 3,
                }
            )

    @property
    def contracts(self):
        return self.profile["v26_contracts"][str(self.region)]

    def update(self, dt, world):
        self.hour = (self.hour + dt * 0.018) % 24
        self.profile["v26_time"] = self.hour
        for npc in self.villagers:
            npc.update(dt, self.hour)

        self.rare_timer -= dt
        if self.rare_timer <= 0:
            self.rare_timer = self.rng.uniform(32.0, 55.0)
            if self.rng.random() < 0.58:
                title, text, sfx = RARE_EVENTS[self.region]
                self.profile["v26_rare_events"] += 1
                return {
                    "kind": "rare",
                    "title": title,
                    "text": text,
                    "sfx": sfx,
                }
        return None

    def nearest(self, player_pos):
        candidates = []
        for npc in self.villagers:
            candidates.append((player_pos.distance_to(npc.pos), "npc", npc))
        for secret in self.secrets:
            candidates.append((player_pos.distance_to(secret.pos), "secret", secret))
        candidates.append((player_pos.distance_to(self.encounter.pos), "encounter", self.encounter))
        distance, kind, obj = min(candidates, key=lambda row: row[0])
        if distance <= 90:
            return kind, obj
        return None

    def interact(self, world):
        nearest = self.nearest(world.player.pos)
        if not nearest:
            return None
        kind, obj = nearest

        if kind == "npc":
            text = obj.dialogue(self, world)
            return {
                "speaker": obj.name,
                "text": text,
                "sfx": "voice_mystic" if obj.role == "vidente" else "voice_low",
            }

        if kind == "secret":
            if obj.id not in self.profile["v26_secrets"]:
                self.profile["v26_secrets"].append(obj.id)
                self.profile["v26_lore"].append(obj.text)
                self.profile["coins"] += 18
                if self.quest_state["stage"] == 3:
                    self.quest_state["stage"] = 4
                return {
                    "speaker": "SEGREDO DE VALDRAK",
                    "text": obj.text + "  +18 moedas.",
                    "sfx": "secret",
                }
            return {
                "speaker": "SEGREDO JÁ DESCOBERTO",
                "text": obj.text,
                "sfx": "rune",
            }

        if obj.id in self.profile["v26_encounters"]:
            return {
                "speaker": obj.name,
                "text": "Este encontro já mudou seu caminho.",
                "sfx": "voice_low",
            }
        self.profile["v26_encounters"].append(obj.id)
        self.profile["coins"] += 35
        self.profile["v26_lore"].append(obj.text)
        return {
            "speaker": obj.name,
            "text": obj.text + "  O encontro rende 35 moedas e um novo registro de lore.",
            "sfx": "rare_event",
        }

    def quest_dialogue(self, world):
        quest = QUESTS[self.region]
        state = self.quest_state
        if state["complete"]:
            choice = state["choice"]
            return (
                f"{quest['title']} foi concluída. "
                f"{CONSEQUENCE_LABELS.get(choice, 'Valdrak mudou.')}"
            )
        if state["stage"] == 0:
            state["stage"] = 1
            return (
                f"Missão iniciada: {quest['title']}. "
                f"Derrote {quest['need']} inimigos do tipo {quest['target']}."
            )
        if state["stage"] == 1:
            return (
                f"{quest['title']}: {state['kills']}/{quest['need']} "
                f"{quest['target']} derrotados."
            )
        if state["stage"] == 2:
            self.pending_choice = True
            return (
                f"{quest['title']}: escolha o destino da região. "
                f"1 — {quest['choices'][0][1]}  2 — {quest['choices'][1][1]}"
            )
        if state["stage"] == 3:
            return (
                "Sua decisão foi tomada. Agora descubra um segredo desta região "
                "antes de voltar."
            )
        if state["stage"] == 4:
            state["stage"] = 5
            state["complete"] = True
            self.profile["coins"] += 80 + self.region * 10
            self.profile["skill_points"] = self.profile.get("skill_points", 0) + 1
            return (
                f"Quest concluída: {quest['title']}. "
                f"+{80 + self.region * 10} moedas e +1 ponto de talento."
            )
        return f"{quest['title']} aguarda um novo passo."

    def choose_quest(self, option):
        if not self.pending_choice or option not in (1, 2):
            return None
        quest = QUESTS[self.region]
        key, description = quest["choices"][option - 1]
        state = self.quest_state
        state["choice"] = key
        state["stage"] = 3
        self.profile["v26_consequences"][str(self.region)] = key
        self.pending_choice = False
        return (
            f"Decisão registrada: {description} "
            f"{CONSEQUENCE_LABELS[key]}"
        )

    def on_enemy_defeated(self, archetype):
        quest = QUESTS[self.region]
        state = self.quest_state
        messages = []
        if state["stage"] == 1 and archetype == quest["target"]:
            state["kills"] += 1
            if state["kills"] >= quest["need"]:
                state["stage"] = 2
                messages.append(
                    f"{quest['title']}: objetivo de combate concluído. Volte a {quest['giver']}."
                )

        for contract in self.contracts:
            if (
                contract["accepted"]
                and not contract["complete"]
                and contract["target"] == archetype
            ):
                contract["kills"] += 1
                if contract["kills"] >= contract["need"]:
                    contract["complete"] = True
                    self.profile["coins"] += contract["reward"]
                    messages.append(
                        f"Contrato concluído: {contract['target']} • +{contract['reward']} moedas"
                    )
        return messages

    def accept_contract(self, index):
        if not 0 <= index < len(self.contracts):
            return "Contrato inválido"
        contract = self.contracts[index]
        if contract["complete"]:
            return "Este contrato já foi concluído."
        if contract["accepted"]:
            return (
                f"Contrato ativo: {contract['kills']}/{contract['need']} "
                f"{contract['target']}."
            )
        contract["accepted"] = True
        return (
            f"Contrato aceito: derrote {contract['need']} {contract['target']} "
            f"por {contract['reward']} moedas."
        )

    def draw(self, surface, camera, fonts, seconds, player_pos):
        for npc in self.villagers:
            npc.draw(
                surface,
                camera,
                fonts,
                seconds,
                near=player_pos.distance_to(npc.pos) <= 95,
            )

        for secret in self.secrets:
            discovered = secret.id in self.profile["v26_secrets"]
            near = player_pos.distance_to(secret.pos) <= 105
            secret.draw(surface, camera, seconds, discovered=discovered, near=near)

        self.encounter.draw(
            surface,
            camera,
            fonts,
            seconds,
            done=self.encounter.id in self.profile["v26_encounters"],
            near=player_pos.distance_to(self.encounter.pos) <= 100,
        )

    def draw_contracts(self, surface, fonts, accent):
        veil = pygame.Surface((1280, 720), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 220))
        surface.blit(veil, (0, 0))
        panel = pygame.Rect(175, 90, 930, 540)
        pygame.draw.rect(surface, (7, 12, 19), panel, border_radius=24)
        pygame.draw.rect(surface, accent, panel, 2, border_radius=24)
        title = fonts["title"].render("CONTRATOS & CAÇADAS", True, (238, 243, 248))
        surface.blit(title, (220, 130))
        y = 205
        for index, contract in enumerate(self.contracts, 1):
            status = (
                "CONCLUÍDO"
                if contract["complete"]
                else "ATIVO"
                if contract["accepted"]
                else "DISPONÍVEL"
            )
            line = (
                f"{index}. {contract['target']} — "
                f"{contract['kills']}/{contract['need']} — "
                f"{contract['reward']} moedas — {status}"
            )
            surface.blit(fonts["body"].render(line, True, (220, 226, 232)), (220, y))
            y += 72
        quest = QUESTS[self.region]
        state = self.quest_state
        quest_line = (
            f"QUEST REGIONAL: {quest['title']} • estágio {state['stage']} "
            f"• {'CONCLUÍDA' if state['complete'] else 'EM ANDAMENTO'}"
        )
        surface.blit(fonts["heading"].render(quest_line, True, accent), (220, 455))
        consequence = self.profile["v26_consequences"].get(str(self.region))
        if consequence:
            surface.blit(
                fonts["small"].render(CONSEQUENCE_LABELS[consequence], True, (231, 190, 93)),
                (220, 502),
            )
        surface.blit(
            fonts["small"].render(
                "1/2/3 aceita contrato • H/Esc fecha • fale com moradores para quests",
                True,
                (150, 164, 179),
            ),
            (220, 585),
        )

    def journal_lines(self):
        quest = QUESTS[self.region]
        state = self.quest_state
        lines = [
            f"{REGION_TITLES[self.region]} — {self.hour:04.1f}h",
            f"Quest: {quest['title']} • estágio {state['stage']}",
            f"Segredos: {sum(1 for s in self.secrets if s.id in self.profile['v26_secrets'])}/2",
            f"Encontro único: {'feito' if self.encounter.id in self.profile['v26_encounters'] else 'não encontrado'}",
            f"Eventos raros vistos: {self.profile['v26_rare_events']}",
        ]
        return lines
