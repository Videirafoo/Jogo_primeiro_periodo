import random

from progression_v24 import (
    add_and_auto_equip,
    ensure_progression_profile,
    roll_equipment,
)


BALANCE = {
    "Explorador": {
        "enemy_damage": 0.78,
        "player_damage": 1.12,
        "loot": 1.15,
    },
    "Normal": {
        "enemy_damage": 1.0,
        "player_damage": 1.0,
        "loot": 1.0,
    },
    "Saga": {
        "enemy_damage": 1.25,
        "player_damage": 0.92,
        "loot": 1.25,
    },
}

RECIPES = [
    {
        "name": "Poção Nórdica",
        "cost": {"erva": 2, "ferro": 1},
        "reward": ("consumable", "pocao"),
    },
    {
        "name": "Essência Rúnica",
        "cost": {"runa": 2, "carvao": 1},
        "reward": ("consumable", "essencia"),
    },
    {
        "name": "Equipamento Raro",
        "cost": {"ferro": 3, "runa": 3, "couro": 2},
        "reward": ("gear", None),
    },
]

TALENTS = [
    ("Fúria Rúnica", "attack_bonus", 3),
    ("Pele de Ferro", "defense_bonus", 3),
    ("Passo do Vento", "stamina_bonus", 12),
    ("Olho do Caçador", "crit_bonus", 0.03),
]

QUEST_CHAINS = {
    "Edda": [
        "Encontre três sinais rúnicos na Estrada.",
        "Abra um Cofre Rúnico.",
        "Derrote o Guardião e retorne.",
    ],
    "Orm": [
        "Colete Fragmentos de Valdrak.",
        "Resolva um puzzle no Portão.",
    ],
    "Sigrun": [
        "Vença cinco inimigos.",
        "Faça um parry perfeito.",
    ],
    "Torsten": [
        "Encontre ferro e couro.",
        "Crie um equipamento.",
    ],
}


def ensure_meta(profile):
    ensure_progression_profile(profile)
    profile.setdefault("coins", 80)
    profile.setdefault(
        "materials",
        {
            "ferro": 4,
            "runa": 3,
            "couro": 3,
            "erva": 3,
            "carvao": 2,
        },
    )
    profile.setdefault("crafted", 0)
    profile.setdefault("upgrades", {})
    profile.setdefault("skill_points", 1)
    profile.setdefault("talents", {})
    profile.setdefault("npc_quest_steps", {})
    profile.setdefault(
        "accessibility",
        {
            "high_contrast": False,
            "reduce_flash": False,
            "screen_shake": True,
            "large_ui": False,
        },
    )
    profile.setdefault("difficulty", "Normal")
    profile.setdefault("current_save_slot", 1)


def balance(profile):
    ensure_meta(profile)
    return BALANCE.get(profile["difficulty"], BALANCE["Normal"])


def grant_materials(profile, rng=None, elite=False):
    ensure_meta(profile)
    rng = rng or random.Random()
    pool = ["ferro", "runa", "couro", "erva", "carvao"]
    count = 2 if elite else 1
    found = []
    for _ in range(count):
        key = rng.choice(pool)
        profile["materials"][key] += 1
        found.append(key)
    profile["coins"] += 10 if elite else 4
    return found


def craft(profile, index, chapter, rng=None):
    ensure_meta(profile)
    if index < 0 or index >= len(RECIPES):
        return False, "Receita inválida"
    recipe = RECIPES[index]
    for key, amount in recipe["cost"].items():
        if profile["materials"].get(key, 0) < amount:
            return False, f"Materiais insuficientes para {recipe['name']}"

    for key, amount in recipe["cost"].items():
        profile["materials"][key] -= amount

    kind, value = recipe["reward"]
    if kind == "consumable":
        profile["inventory"][value] += 1
        reward = recipe["name"]
    else:
        item = roll_equipment(
            chapter,
            rng or random.Random(),
            elite=True,
        )
        # Force at least Raro in crafting.
        if item["rarity"] == "Comum":
            item["rarity"] = "Raro"
            item["value"] = max(1, int(item["value"] * 1.25))
        add_and_auto_equip(profile, item)
        reward = f"{item['rarity']} {item['name']}"

    profile["crafted"] += 1
    if profile["crafted"] % 2 == 0:
        profile["skill_points"] += 1
    return True, f"Criado: {reward}"


def upgrade_equipped(profile, slot="weapon"):
    ensure_meta(profile)
    item = profile["equipped"].get(slot)
    if not item:
        return False, "Nenhum item equipado neste slot"
    level = profile["upgrades"].get(item["id"], 0)
    cost = 25 + level * 18
    if profile["coins"] < cost:
        return False, f"Moedas insuficientes: requer {cost}"
    profile["coins"] -= cost
    profile["upgrades"][item["id"]] = level + 1
    item["value"] = round(item["value"] * 1.12, 3)
    return True, f"{item['name']} agora está +{level + 1}"


def unlock_talent(profile, index):
    ensure_meta(profile)
    if index < 0 or index >= len(TALENTS):
        return False, "Talento inválido"
    name, key, value = TALENTS[index]
    if profile["talents"].get(key):
        return False, f"{name} já foi desbloqueado"
    if profile["skill_points"] <= 0:
        return False, "Sem pontos de talento"
    profile["skill_points"] -= 1
    profile["talents"][key] = value
    if key == "stamina_bonus":
        profile["max_stamina"] = profile.get("max_stamina", 100) + value
        profile["stamina"] = profile["max_stamina"]
    return True, f"Talento desbloqueado: {name}"


def talent_bonus(profile, key):
    ensure_meta(profile)
    return profile["talents"].get(key, 0)


def vendor_stock(chapter, rng=None):
    rng = rng or random.Random(44000 + chapter)
    return [
        roll_equipment(chapter, rng, elite=index > 0)
        for index in range(3)
    ]


def buy_item(profile, item):
    ensure_meta(profile)
    prices = {
        "Comum": 25,
        "Raro": 48,
        "Épico": 85,
        "Lendário": 140,
    }
    price = prices[item["rarity"]]
    if profile["coins"] < price:
        return False, f"Requer {price} moedas"
    profile["coins"] -= price
    equipped = add_and_auto_equip(profile, item)
    return True, (
        f"Comprou {item['rarity']} {item['name']}"
        + (" • equipado" if equipped else "")
    )


def quest_step(profile, npc_name):
    ensure_meta(profile)
    short = npc_name.split(",")[0]
    chain = QUEST_CHAINS.get(short)
    if not chain:
        return None
    index = profile["npc_quest_steps"].get(short, 0)
    if index >= len(chain):
        return f"{short}: nossa jornada aqui está concluída."
    objective = chain[index]
    profile["npc_quest_steps"][short] = index + 1
    profile["coins"] += 12
    if (index + 1) == len(chain):
        profile["skill_points"] += 1
        return (
            f"{short}: {objective} • cadeia concluída, "
            "+12 moedas e +1 ponto de talento."
        )
    return f"{short}: {objective} • +12 moedas."


def cycle_difficulty(profile):
    ensure_meta(profile)
    keys = list(BALANCE)
    current = keys.index(profile["difficulty"])
    profile["difficulty"] = keys[(current + 1) % len(keys)]
    return profile["difficulty"]


def toggle_accessibility(profile, key):
    ensure_meta(profile)
    profile["accessibility"][key] = not profile["accessibility"][key]
    return profile["accessibility"][key]
