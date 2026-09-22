import math

import pygame


PORTRAIT = {
    "player": ((47, 122, 153), (35, 31, 28), (209, 169, 137)),
    "Thorvald": ((74, 111, 154), (189, 189, 190), (203, 163, 134)),
    "Aurel": ((145, 121, 62), (221, 190, 108), (218, 177, 143)),
    "Kaion": ((49, 121, 132), (42, 39, 37), (197, 151, 122)),
    "Brenor": ((153, 76, 49), (86, 49, 36), (196, 145, 114)),
    "Eiran": ((58, 126, 91), (128, 95, 65), (218, 177, 145)),
    "Noctar": ((97, 69, 145), (32, 28, 38), (184, 137, 116)),
}


def draw_portrait_v28(surface, rect, name, seconds=0.0):
    body, hair, skin = PORTRAIT.get(name, PORTRAIT["player"])
    pygame.draw.rect(surface, (10, 15, 22), rect, border_radius=18)
    pygame.draw.rect(surface, body, rect, 2, border_radius=18)
    cx = rect.centerx
    cy = rect.centery + 12
    glow = 42 + int(math.sin(seconds * 2.2) * 3)
    pygame.draw.circle(surface, (*body,), (cx, cy - 18), glow, 2)
    pygame.draw.ellipse(surface, body, (cx - 35, cy + 12, 70, 62))
    pygame.draw.circle(surface, skin, (cx, cy - 22), 29)
    pygame.draw.arc(surface, hair, (cx - 31, cy - 53, 62, 42), math.pi, math.tau, 13)
    pygame.draw.line(surface, (63, 43, 35), (cx - 12, cy - 24), (cx - 4, cy - 26), 2)
    pygame.draw.line(surface, (63, 43, 35), (cx + 4, cy - 26), (cx + 12, cy - 24), 2)
    pygame.draw.circle(surface, (28, 27, 26), (cx - 8, cy - 19), 2)
    pygame.draw.circle(surface, (28, 27, 26), (cx + 8, cy - 19), 2)
    pygame.draw.line(surface, (125, 77, 65), (cx - 7, cy - 2), (cx + 7, cy - 2), 2)


def draw_final_ui_frame(surface, accent):
    # Thin production frame that keeps UI readable without covering playfield.
    pygame.draw.rect(surface, (6, 10, 15), (14, 14, 1252, 692), 2, border_radius=18)
    pygame.draw.line(surface, accent, (36, 36), (170, 36), 2)
    pygame.draw.line(surface, accent, (1110, 684), (1244, 684), 2)


def draw_player_equipment_v28(surface, center, profile, facing):
    equipped = profile.get("equipped", {})
    weapon = equipped.get("weapon")
    armor = equipped.get("armor")
    amulet = equipped.get("amulet")
    rune = equipped.get("rune")
    x, y = int(center[0]), int(center[1])

    rarity_colors = {
        "Comum": (175, 184, 193),
        "Raro": (72, 161, 255),
        "Épico": (165, 95, 255),
        "Lendário": (235, 183, 67),
    }

    if armor:
        color = rarity_colors.get(armor.get("rarity", "Comum"), (175, 184, 193))
        pygame.draw.arc(surface, color, (x - 25, y - 18, 50, 48), 0.15, math.pi - 0.15, 3)

    direction = pygame.Vector2(facing)
    if not direction.length_squared():
        direction.update(0, 1)
    direction = direction.normalize()
    normal = pygame.Vector2(-direction.y, direction.x)

    if weapon:
        color = rarity_colors.get(weapon.get("rarity", "Comum"), (197, 203, 210))
        grip = pygame.Vector2(x, y) + normal * 16 - direction * 2
        tip = grip + direction * 42 + normal * 3
        pygame.draw.line(surface, (112, 75, 44), grip, tip, 4)
        pygame.draw.polygon(
            surface,
            color,
            [
                (int(tip.x), int(tip.y)),
                (int(tip.x + normal.x * 13 - direction.x * 7), int(tip.y + normal.y * 13 - direction.y * 7)),
                (int(tip.x - normal.x * 13 - direction.x * 7), int(tip.y - normal.y * 13 - direction.y * 7)),
            ],
        )

    if amulet:
        pygame.draw.circle(surface, (231, 190, 93), (x, y - 2), 4, 1)

    if rune:
        pygame.draw.circle(surface, (158, 116, 255), (x - 25, y - 12), 7, 2)
