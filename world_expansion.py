import math
import pygame

INK = (238, 243, 248)
MUTED = (158, 174, 190)
GOLD = (231, 190, 93)
CYAN = (70, 224, 235)
GREEN = (84, 210, 139)
RED = (225, 82, 92)
VIOLET = (158, 116, 255)

TYPE_COLORS = {
    "lore": VIOLET,
    "ruin": GOLD,
    "camp": (245, 137, 69),
    "passage": CYAN,
}

REGION_EXPANSION = {
    1: {
        "quest": "Os Marcos da Estrada",
        "places": [
            {
                "id": "ponte_corvo",
                "name": "Ponte do Corvo Quebrado",
                "type": "ruin",
                "pos": (280, 250),
                "story": (
                    "A ponte foi destruída na primeira noite em que Valdrak apareceu. "
                    "Nas pedras ainda há nomes riscados por viajantes que juravam ter acordado aqui antes."
                ),
                "reward": "fragmento",
            },
            {
                "id": "pantano_sussurros",
                "name": "Pântano dos Sussurros",
                "type": "lore",
                "pos": (1490, 260),
                "story": (
                    "A água repete frases ditas no mundo acordado. "
                    "Você escuta uma voz da faculdade chamando seu nome, embora não exista ninguém por perto."
                ),
            },
            {
                "id": "capela_afundada",
                "name": "Capela Afundada",
                "type": "camp",
                "pos": (360, 850),
                "story": (
                    "Velas queimam debaixo da chuva sem apagar. "
                    "Um altar partido guarda o símbolo dos Eternos antes mesmo de o grupo existir."
                ),
            },
            {
                "id": "atalho_pedras_azuis",
                "name": "Atalho das Pedras Azuis",
                "type": "passage",
                "pos": (1480, 820),
                "target": (510, 350),
                "story": (
                    "As pedras formam uma trilha impossível. "
                    "Quando você pisa na última, o caminho dobra sobre si mesmo e encurta a estrada."
                ),
            },
        ],
    },
    2: {
        "quest": "As Três Chaves do Portão",
        "places": [
            {
                "id": "cripta_tres_chaves",
                "name": "Cripta das Três Chaves",
                "type": "ruin",
                "pos": (280, 260),
                "story": (
                    "Três fechaduras sem portas cercam um sarcófago vazio. "
                    "No fundo existe um mapa indicando que o Portão dos Ossos já foi aberto por alguém da sua turma."
                ),
                "reward": "fragmento",
            },
            {
                "id": "mercado_ossos",
                "name": "Mercado dos Ossos",
                "type": "lore",
                "pos": (1480, 280),
                "story": (
                    "Mercadores mascarados trocam lembranças em vez de moedas. "
                    "Uma lembrança sua está exposta numa banca, mas você não recorda de tê-la perdido."
                ),
            },
            {
                "id": "escadaria_vigia",
                "name": "Escadaria do Vigia",
                "type": "camp",
                "pos": (350, 835),
                "story": (
                    "No alto, um vigia sem rosto mantém uma fogueira acesa. "
                    "Ele aponta para o norte e diz apenas: 'não confie na primeira porta'."
                ),
            },
            {
                "id": "tunel_sem_rosto",
                "name": "Túnel dos Sem-Rosto",
                "type": "passage",
                "pos": (1500, 820),
                "target": (470, 360),
                "story": (
                    "O túnel não aparece no mapa. "
                    "Sombras repetem seus passos um segundo atrasadas até você surgir do outro lado do Portão."
                ),
            },
        ],
    },
    3: {
        "quest": "Juramentos da Vila",
        "places": [
            {
                "id": "taverna_martelo",
                "name": "Taverna do Martelo Torto",
                "type": "camp",
                "pos": (300, 250),
                "story": (
                    "Guerreiros contam batalhas que ainda não aconteceram. "
                    "O dono serve uma bebida sem nome e promete que nenhum sonho termina na primeira morte."
                ),
            },
            {
                "id": "rua_despertos",
                "name": "Rua dos Despertos",
                "type": "lore",
                "pos": (1480, 250),
                "story": (
                    "Cada casa possui uma cama vazia e um despertador parado. "
                    "As placas têm nomes de pessoas que afirmam nunca ter visitado Valdrak."
                ),
            },
            {
                "id": "catacumbas_campeao",
                "name": "Catacumbas do Campeão",
                "type": "ruin",
                "pos": (340, 835),
                "story": (
                    "Debaixo da arena, campeões derrotados gravaram seus últimos pensamentos nas paredes. "
                    "Uma inscrição recente descreve exatamente a roupa que você está usando."
                ),
                "reward": "fragmento",
            },
            {
                "id": "arquibancada_juramentos",
                "name": "Arquibancada dos Juramentos",
                "type": "passage",
                "pos": (1500, 815),
                "target": (525, 365),
                "story": (
                    "Atrás de uma fileira quebrada existe uma escada descendente. "
                    "Ela termina numa passagem usada pelos antigos vencedores para fugir da arena."
                ),
            },
        ],
    },
    4: {
        "quest": "Vozes Entre as Raízes",
        "places": [
            {
                "id": "lago_nomes",
                "name": "Lago dos Nomes",
                "type": "lore",
                "pos": (290, 250),
                "story": (
                    "A superfície mostra nomes em vez de reflexos. "
                    "Ao tocar a água, um deles desaparece e surge escrito no seu pulso por alguns segundos."
                ),
            },
            {
                "id": "clareira_corvos",
                "name": "Clareira dos Corvos",
                "type": "camp",
                "pos": (1490, 260),
                "story": (
                    "Centenas de corvos formam um círculo perfeito e deixam um espaço vazio para você. "
                    "No centro há brasas verdes que restauram forças sem produzir calor."
                ),
            },
            {
                "id": "casa_bruxa_musgo",
                "name": "Casa da Bruxa de Musgo",
                "type": "ruin",
                "pos": (360, 830),
                "story": (
                    "A casa parece abandonada, mas uma chaleira ainda ferve. "
                    "No teto, raízes desenham o mapa de uma região de Valdrak que não deveria existir."
                ),
                "reward": "fragmento",
            },
            {
                "id": "passagem_raizes",
                "name": "Passagem das Raízes",
                "type": "passage",
                "pos": (1490, 820),
                "target": (500, 360),
                "story": (
                    "As raízes se afastam quando reconhecem a Marca de Valdrak. "
                    "O túnel vegetal leva a uma clareira distante em poucos segundos."
                ),
            },
        ],
    },
    5: {
        "quest": "A Trilha da Matilha",
        "places": [
            {
                "id": "vale_nevasca",
                "name": "Vale da Nevasca",
                "type": "camp",
                "pos": (290, 260),
                "story": (
                    "A tempestade para apenas dentro de um pequeno círculo de pedras. "
                    "Ali, pegadas humanas viram pegadas de lobo antes de desaparecer."
                ),
            },
            {
                "id": "torre_matilha",
                "name": "Torre da Matilha",
                "type": "lore",
                "pos": (1490, 250),
                "story": (
                    "A torre emite um uivo metálico quando a lua aparece. "
                    "Os lobos de ferro não obedecem a um alfa: obedecem a uma frequência."
                ),
            },
            {
                "id": "mina_ferro_azul",
                "name": "Mina de Ferro Azul",
                "type": "ruin",
                "pos": (350, 835),
                "story": (
                    "O minério pulsa como circuito elétrico sob o gelo. "
                    "Você encontra uma placa com o mesmo símbolo usado no seu Pulso de Código."
                ),
                "reward": "fragmento",
            },
            {
                "id": "ponte_congelada",
                "name": "Ponte Congelada",
                "type": "passage",
                "pos": (1500, 820),
                "target": (500, 350),
                "story": (
                    "Sob o gelo existe outra ponte, invertida. "
                    "Ao atravessar, você surge no lado oposto do vale sem lembrar do percurso."
                ),
            },
        ],
    },
    6: {
        "quest": "Segredos da Forja Morta",
        "places": [
            {
                "id": "rio_lava_negra",
                "name": "Rio de Lava Negra",
                "type": "lore",
                "pos": (290, 250),
                "story": (
                    "A lava é negra e reflete o céu como um espelho. "
                    "Brenor diz que aquilo não é fogo: são memórias queimadas até virarem matéria."
                ),
            },
            {
                "id": "sala_bigornas",
                "name": "Sala das Cem Bigornas",
                "type": "camp",
                "pos": (1490, 250),
                "story": (
                    "Nenhum ferreiro está presente, mas martelos continuam trabalhando sozinhos. "
                    "Uma bigorna guarda sua energia e devolve seu corpo renovado."
                ),
            },
            {
                "id": "arquivo_ferreiros",
                "name": "Arquivo dos Ferreiros",
                "type": "ruin",
                "pos": (350, 835),
                "story": (
                    "Tabletes de metal registram armas que nunca foram fabricadas. "
                    "Entre elas aparece um projeto chamado 'Chave do Despertar'."
                ),
                "reward": "fragmento",
            },
            {
                "id": "elevador_runico",
                "name": "Elevador Rúnico",
                "type": "passage",
                "pos": (1500, 820),
                "target": (520, 360),
                "story": (
                    "Plataformas sobem sem cordas nem engrenagens. "
                    "O elevador atravessa uma camada invisível da montanha e reaparece perto da forja central."
                ),
            },
        ],
    },
    7: {
        "quest": "Fragmentos do Despertar",
        "places": [
            {
                "id": "biblioteca_impossivel",
                "name": "Biblioteca Impossível",
                "type": "lore",
                "pos": (285, 250),
                "story": (
                    "Os livros contam versões diferentes da mesma noite. "
                    "Um deles descreve você fechando Valdrak; outro descreve você escolhendo permanecer."
                ),
            },
            {
                "id": "corredor_faculdade",
                "name": "Corredor da Faculdade",
                "type": "camp",
                "pos": (1490, 250),
                "story": (
                    "O piso de pedra se transforma em corredor de faculdade por alguns metros. "
                    "Ao longe, toca um sinal de aula que nenhum relógio de Valdrak consegue medir."
                ),
            },
            {
                "id": "sala_espelhos",
                "name": "Sala dos Espelhos",
                "type": "ruin",
                "pos": (350, 835),
                "story": (
                    "Cada espelho mostra um final diferente. "
                    "Num deles, Os Eternos nunca se conheceram. Em outro, todos já estavam esperando por você."
                ),
                "reward": "fragmento",
            },
            {
                "id": "jardim_despertar",
                "name": "Jardim do Despertar",
                "type": "passage",
                "pos": (1500, 820),
                "target": (520, 350),
                "story": (
                    "Flores crescem ao redor de despertadores enterrados. "
                    "Quando um toca, o jardim se dobra e abre um caminho curto até a Última Porta."
                ),
            },
        ],
    },
}


class ExplorationPlace:
    def __init__(self, data, profile):
        self.data = data
        self.id = data["id"]
        self.name = data["name"]
        self.kind = data["type"]
        self.pos = pygame.Vector2(data["pos"])
        self.target = data.get("target")
        self.story = data["story"]
        self.reward = data.get("reward")
        self.profile = profile

    @property
    def discovered(self):
        return self.id in self.profile.get("discoveries", [])

    def draw(self, surface, camera, font, seconds, near=False):
        x = int(self.pos.x - camera.x)
        y = int(self.pos.y - camera.y)
        color = TYPE_COLORS[self.kind]

        pulse = 3 + int((math.sin(seconds * 3 + x * 0.01) + 1) * 2)
        pygame.draw.circle(surface, (8, 12, 18), (x, y), 22 + pulse)
        pygame.draw.circle(surface, color, (x, y), 18, 2)

        if self.kind == "lore":
            pygame.draw.polygon(
                surface,
                color,
                [(x, y - 12), (x + 10, y), (x, y + 12), (x - 10, y)],
                2,
            )
        elif self.kind == "ruin":
            pygame.draw.rect(surface, color, (x - 9, y - 11, 18, 22), 2)
            pygame.draw.line(surface, color, (x - 9, y - 3), (x + 9, y - 3), 2)
        elif self.kind == "camp":
            pygame.draw.polygon(
                surface,
                color,
                [(x, y - 12), (x - 10, y + 10), (x + 10, y + 10)],
            )
        else:
            pygame.draw.circle(surface, color, (x, y), 9, 2)
            pygame.draw.line(surface, color, (x - 13, y), (x + 13, y), 2)

        if self.discovered:
            pygame.draw.circle(surface, GREEN, (x + 16, y - 16), 5)

        if near:
            label = font.render(self.name, True, INK)
            box = label.get_rect(center=(x, y - 38)).inflate(16, 8)
            pygame.draw.rect(surface, (7, 12, 19), box, border_radius=7)
            pygame.draw.rect(surface, color, box, 1, border_radius=7)
            surface.blit(label, label.get_rect(center=box.center))


def build_region_places(chapter_number, profile):
    config = REGION_EXPANSION.get(chapter_number, {"places": []})
    return [
        ExplorationPlace(place, profile)
        for place in config["places"]
    ]


def region_progress(chapter_number, profile):
    config = REGION_EXPANSION.get(chapter_number, {"places": []})
    ids = {place["id"] for place in config["places"]}
    found = ids.intersection(profile.get("discoveries", []))
    return len(found), len(ids)


def region_quest_name(chapter_number):
    return REGION_EXPANSION.get(chapter_number, {}).get(
        "quest",
        "Exploração de Valdrak",
    )


def interact_with_place(place, world):
    profile = world.profile
    profile.setdefault("discoveries", [])
    profile.setdefault("completed_region_quests", [])
    profile.setdefault("inventory", {})
    profile["inventory"].setdefault("reliquia", 0)
    profile["inventory"].setdefault("chave", 0)

    first_time = place.id not in profile["discoveries"]

    if place.kind == "passage" and first_time:
        found_before, _total = region_progress(
            world.chapter["number"],
            profile,
        )
        if found_before < 2:
            return {
                "ok": False,
                "title": place.name,
                "text": (
                    place.story
                    + " O selo ainda está adormecido. "
                    + "Descubra dois outros pontos desta região "
                    + "antes de abrir esta passagem."
                ),
                "sfx": "error",
            }

    if first_time:
        profile["discoveries"].append(place.id)
        profile["xp"] += 1

        if place.reward == "fragmento":
            profile["inventory"]["fragmento"] += 1
        elif place.kind == "lore":
            profile["inventory"]["reliquia"] += 1
        elif place.kind == "camp":
            profile["inventory"]["pocao"] += 1

    if place.kind == "camp":
        world.player.health = min(
            profile["max_health"],
            world.player.health + 30,
        )
        world.player.energy = min(
            profile["max_energy"],
            world.player.energy + 35,
        )

    if place.kind == "passage":
        if place.target:
            world.player.pos.update(*place.target)
            world.camera.update(
                max(0, world.player.pos.x - 640),
                max(0, world.player.pos.y - 360),
            )

    found, total = region_progress(
        world.chapter["number"],
        profile,
    )
    chapter_number = world.chapter["number"]

    quest_completed = False
    if (
        found >= 3
        and chapter_number not in profile["completed_region_quests"]
    ):
        profile["completed_region_quests"].append(chapter_number)
        profile["inventory"]["chave"] += 1
        profile["xp"] += 2
        quest_completed = True

    reward_parts = []
    if first_time:
        reward_parts.append("+1 descoberta")
        reward_parts.append("+1 XP")
        if place.reward == "fragmento":
            reward_parts.append("+1 fragmento")
        elif place.kind == "lore":
            reward_parts.append("+1 relíquia")
        elif place.kind == "camp":
            reward_parts.append("+1 poção")

    if quest_completed:
        reward_parts.append("+1 chave rúnica")
        reward_parts.append("+2 XP")

    text = place.story
    if reward_parts:
        text += "  [" + " • ".join(reward_parts) + "]"

    return {
        "ok": True,
        "title": place.name,
        "text": text,
        "sfx": {
            "lore": "rune",
            "ruin": "scanner",
            "camp": "fire",
            "passage": "portal",
        }[place.kind],
    }
