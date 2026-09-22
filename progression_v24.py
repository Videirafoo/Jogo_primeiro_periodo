import random

RARITIES = {
    "Comum": {"mult": 1.0, "color": (185, 192, 201)},
    "Raro": {"mult": 1.25, "color": (72, 161, 255)},
    "Épico": {"mult": 1.60, "color": (165, 95, 255)},
    "Lendário": {"mult": 2.05, "color": (235, 183, 67)},
}

ITEMS = {
    "weapon": [
        ("Machado de Valdrak", 6, "attack"),
        ("Espada Rúnica", 5, "attack"),
        ("Martelo da Forja", 8, "attack"),
        ("Lâmina do Vento", 7, "attack"),
    ],
    "armor": [
        ("Cota Nórdica", 5, "defense"),
        ("Manto do Desperto", 4, "defense"),
        ("Armadura de Ferro Azul", 7, "defense"),
    ],
    "amulet": [
        ("Olho de Aurel", 0.05, "crit"),
        ("Dente do Alfa", 0.04, "crit"),
        ("Marca da Aurora", 8, "energy"),
    ],
    "rune": [
        ("Runa do Trovão", 4, "attack"),
        ("Runa da Pedra", 4, "defense"),
        ("Runa do Código", 10, "energy"),
    ],
}

REGION_NAMES = {
    1: "Estrada de Valdrak",
    2: "Portão dos Ossos",
    3: "Vila dos Despertos",
    4: "Bosque dos Corvos",
    5: "Terras dos Lobos de Ferro",
    6: "Forja Morta",
    7: "Última Porta",
}

CODEX = {
    "valdrak": ("Valdrak", "Um mundo de sonho que reage às escolhas, memórias e marcas do jogador."),
    "eternos": ("Os Eternos", "Seis companheiros ligados a poderes, runas e caminhos diferentes."),
    "lobos": ("Lobos de Ferro", "Predadores artificiais guiados por frequências antigas."),
    "forja": ("Forja Morta", "Uma indústria impossível onde memórias queimadas viram matéria."),
    "guardioes": ("Os Sete Guardiões", "Cada região possui um Guardião com um estilo próprio de combate."),
    "runas": ("Runas", "Símbolos que ligam tecnologia, sonho e magia em Valdrak."),
}


def ensure_progression_profile(profile):
    profile.setdefault("gear_bag", [])
    profile.setdefault("equipped", {
        "weapon": None,
        "armor": None,
        "amulet": None,
        "rune": None,
    })
    profile.setdefault("codex", ["valdrak"])
    profile.setdefault("visited_regions", [1])
    profile.setdefault("fast_travel_regions", [])
    profile.setdefault("living_events", 0)
    profile.setdefault("puzzles_solved", [])
    profile.setdefault("quests_completed", [])


def _rarity(rng, boss=False, elite=False):
    roll = rng.random()
    if boss:
        return "Lendário" if roll < 0.28 else "Épico"
    if elite:
        return "Épico" if roll < 0.34 else "Raro"
    if roll < 0.04:
        return "Lendário"
    if roll < 0.17:
        return "Épico"
    if roll < 0.47:
        return "Raro"
    return "Comum"


def roll_equipment(chapter, rng=None, boss=False, elite=False):
    rng = rng or random.Random()
    slot = rng.choice(list(ITEMS))
    name, value, stat = rng.choice(ITEMS[slot])
    rarity = _rarity(rng, boss=boss, elite=elite)
    mult = RARITIES[rarity]["mult"]
    scaled = value * mult * (1 + max(0, chapter - 1) * 0.07)
    if stat == "crit":
        scaled = round(scaled, 3)
    else:
        scaled = int(round(scaled))
    return {
        "id": f"{slot}-{chapter}-{rng.randrange(100000, 999999)}",
        "name": name,
        "slot": slot,
        "rarity": rarity,
        "stat": stat,
        "value": scaled,
        "chapter": chapter,
    }


def item_score(item):
    if not item:
        return -1
    base = float(item.get("value", 0))
    return base * RARITIES.get(item.get("rarity", "Comum"), RARITIES["Comum"])["mult"]


def add_and_auto_equip(profile, item):
    ensure_progression_profile(profile)
    profile["gear_bag"].append(item)
    slot = item["slot"]
    current = profile["equipped"].get(slot)
    equipped = current is None or item_score(item) > item_score(current)
    if equipped:
        profile["equipped"][slot] = item
    return equipped


def equipment_stats(profile):
    ensure_progression_profile(profile)
    stats = {
        "attack": 0,
        "defense": 0,
        "crit": 0.0,
        "energy": 0,
    }
    for item in profile["equipped"].values():
        if not item:
            continue
        stat = item.get("stat")
        if stat in stats:
            stats[stat] += item.get("value", 0)
    return stats


def unlock_codex(profile, entry):
    ensure_progression_profile(profile)
    if entry in CODEX and entry not in profile["codex"]:
        profile["codex"].append(entry)
        return True
    return False


def quest_lines(profile, chapter, boss_alive=True):
    ensure_progression_profile(profile)
    discoveries = len(profile.get("discoveries", []))
    chests = len(profile.get("opened_chests", []))
    puzzles = len(profile.get("puzzles_solved", []))
    return [
        f"Principal — supere o Guardião da região {chapter}: {'ATIVO' if boss_alive else 'CONCLUÍDO'}",
        f"Exploração — descobertas registradas: {discoveries}",
        f"Caçador de tesouros — baús abertos: {chests}",
        f"Runas antigas — puzzles resolvidos: {puzzles}",
        f"Valdrak vivo — eventos encontrados: {profile.get('living_events', 0)}",
    ]


def codex_lines(profile):
    ensure_progression_profile(profile)
    lines = []
    for key in profile["codex"]:
        title, body = CODEX.get(key, (key, "Registro desconhecido."))
        lines.append((title, body))
    return lines


def world_map_lines(profile, current_chapter):
    ensure_progression_profile(profile)
    visited = set(profile["visited_regions"])
    travel = set(profile["fast_travel_regions"])
    result = []
    for number in range(1, 8):
        if number not in visited:
            status = "DESCONHECIDA"
        elif number in travel:
            status = "FAST TRAVEL"
        elif number == current_chapter:
            status = "ATUAL"
        else:
            status = "VISITADA"
        result.append((number, REGION_NAMES[number], status))
    return result
