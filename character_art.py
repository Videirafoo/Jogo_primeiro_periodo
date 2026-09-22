import math

import pygame

from animation_v24 import direction8, pose
from sprite_v25 import draw_actor_v25

from weapon_art import (
    CYAN,
    GOLD,
    RED,
    VIOLET,
    draw_sword,
    draw_viking_axe,
)


SKIN = (207, 171, 141)
SKIN_SHADOW = (166, 126, 103)
HAIR = (32, 29, 31)
TUNIC = (40, 77, 91)
TUNIC_LIGHT = (54, 119, 133)
CLOAK = (31, 41, 55)
LEATHER = (83, 52, 34)
BOOT = (45, 33, 30)
STEEL_DARK = (73, 82, 92)
INK = (8, 12, 18)


NPC_PALETTES = {
    1: ((60, 78, 99), CYAN),
    2: ((92, 83, 70), GOLD),
    3: ((113, 58, 53), RED),
    4: ((51, 77, 63), (84, 210, 139)),
    5: ((80, 93, 104), (190, 218, 231)),
    6: ((110, 59, 42), (245, 137, 69)),
    7: ((67, 52, 91), VIOLET),
}


def _body_shadow(surface, x, y, scale):
    shadow = pygame.Surface(
        (int(58 * scale), int(18 * scale)),
        pygame.SRCALPHA,
    )
    pygame.draw.ellipse(
        shadow,
        (0, 0, 0, 110),
        shadow.get_rect(),
    )
    surface.blit(
        shadow,
        shadow.get_rect(
            center=(x, int(y + 25 * scale))
        ),
    )


def draw_protagonist(
    surface,
    center,
    facing,
    state,
    seconds,
    accent,
):
    if draw_actor_v25(
        surface,
        "protagonist",
        center,
        facing,
        state,
        seconds,
        scale=1.24,
    ):
        return True

    x, y = int(center[0]), int(center[1])
    scale = 1.0

    anim = pose(state, seconds)
    walk = math.sin(seconds * (14 if state == "run" else 11))
    y += int(anim["bob"])

    _body_shadow(
        surface,
        x,
        y,
        scale,
    )

    left_leg = (
        x - 7 - int(walk * 2)
        if state == "walk"
        else x - 7
    )
    right_leg = (
        x + 7 + int(walk * 2)
        if state == "walk"
        else x + 7
    )

    pygame.draw.line(
        surface,
        BOOT,
        (left_leg, y + 8),
        (left_leg - 2, y + 27),
        7,
    )
    pygame.draw.line(
        surface,
        BOOT,
        (right_leg, y + 8),
        (right_leg + 2, y + 27),
        7,
    )

    cloak = [
        (x - 18, y - 20),
        (x + 18, y - 20),
        (x + 24, y + 15),
        (x + 12, y + 24),
        (x - 16, y + 24),
        (x - 23, y + 13),
    ]
    pygame.draw.polygon(
        surface,
        INK,
        [(px + 1, py + 2) for px, py in cloak],
    )
    pygame.draw.polygon(
        surface,
        CLOAK,
        cloak,
    )

    torso = pygame.Rect(
        x - 13,
        y - 19,
        26,
        34,
    )
    pygame.draw.rect(
        surface,
        TUNIC,
        torso,
        border_radius=7,
    )
    pygame.draw.rect(
        surface,
        TUNIC_LIGHT,
        pygame.Rect(
            x - 9,
            y - 16,
            6,
            26,
        ),
        border_radius=3,
    )

    pygame.draw.line(
        surface,
        LEATHER,
        (x - 13, y - 2),
        (x + 13, y - 2),
        4,
    )
    pygame.draw.circle(
        surface,
        accent,
        (x, y - 2),
        3,
    )

    pygame.draw.line(
        surface,
        SKIN_SHADOW,
        (x - 13, y - 11),
        (x - 23, y + 5),
        6,
    )
    pygame.draw.line(
        surface,
        SKIN_SHADOW,
        (x + 13, y - 11),
        (x + 23, y + 5),
        6,
    )

    head_y = y - 34
    pygame.draw.circle(
        surface,
        INK,
        (x, head_y),
        14,
    )
    pygame.draw.circle(
        surface,
        SKIN,
        (x, head_y + 1),
        12,
    )

    hair = [
        (x - 12, head_y - 5),
        (x - 8, head_y - 13),
        (x + 1, head_y - 15),
        (x + 12, head_y - 8),
        (x + 9, head_y - 2),
        (x + 2, head_y - 7),
        (x - 4, head_y - 2),
    ]
    pygame.draw.polygon(
        surface,
        HAIR,
        hair,
    )

    facing_name = direction8(facing)
    direction = -1 if facing_name in {"W", "NW", "SW"} else 1

    pygame.draw.circle(
        surface,
        (38, 27, 23),
        (x + 4 * direction, head_y + 1),
        2,
    )

    # Rune gauntlet remains visible even outside attacks.
    gauntlet_x = x - 23 if direction > 0 else x + 23
    pygame.draw.circle(
        surface,
        accent,
        (gauntlet_x, y + 6),
        7,
        2,
    )
    pygame.draw.circle(
        surface,
        accent,
        (gauntlet_x, y + 6),
        2,
    )

    weapon_center = (
        x + 28 * direction,
        y - 1,
    )

    if state in {"attack", "attack1", "attack2", "heavy"}:
        angle = float(anim["weapon"])
        if direction < 0:
            angle = -angle
        draw_sword(
            surface,
            weapon_center,
            angle=angle,
            scale=0.74 if state == "heavy" else 0.63,
            rune_color=accent,
            motion=1.0,
        )
    else:
        draw_sword(
            surface,
            (
                x + 19 * direction,
                y + 4,
            ),
            angle=-150 if direction > 0 else 150,
            scale=0.40,
            rune_color=accent,
        )

    if state == "hurt":
        overlay = pygame.Surface(
            (70, 85),
            pygame.SRCALPHA,
        )
        overlay.fill(
            (210, 42, 42, 42)
        )
        surface.blit(
            overlay,
            overlay.get_rect(
                center=(x, y - 4)
            ),
        )

    return True


def draw_viking_npc(
    surface,
    center,
    chapter,
    accent,
    near=False,
):
    x, y = int(center[0]), int(center[1])
    base, detail = NPC_PALETTES.get(
        chapter,
        ((74, 82, 92), accent),
    )

    _body_shadow(
        surface,
        x,
        y,
        1.0,
    )

    cloak = [
        (x - 18, y - 18),
        (x + 18, y - 18),
        (x + 23, y + 24),
        (x - 23, y + 24),
    ]
    pygame.draw.polygon(
        surface,
        (8, 12, 17),
        [(px + 2, py + 2) for px, py in cloak],
    )
    pygame.draw.polygon(
        surface,
        base,
        cloak,
    )

    pygame.draw.line(
        surface,
        LEATHER,
        (x - 17, y - 2),
        (x + 17, y - 2),
        4,
    )

    pygame.draw.circle(
        surface,
        SKIN_SHADOW,
        (x, y - 31),
        14,
    )
    pygame.draw.circle(
        surface,
        SKIN,
        (x, y - 32),
        12,
    )

    helmet = [
        (x - 13, y - 34),
        (x - 8, y - 45),
        (x + 7, y - 45),
        (x + 13, y - 34),
        (x + 9, y - 29),
        (x - 9, y - 29),
    ]
    pygame.draw.polygon(
        surface,
        (46, 52, 60),
        helmet,
    )
    pygame.draw.line(
        surface,
        detail,
        (x, y - 44),
        (x, y - 29),
        2,
    )

    # Different chapters visibly carry different tools.
    if chapter in (1, 2, 3, 5):
        draw_viking_axe(
            surface,
            (x + 25, y - 2),
            angle=-30,
            scale=0.42,
            rune_color=detail,
        )
    elif chapter == 6:
        pygame.draw.line(
            surface,
            LEATHER,
            (x + 19, y + 18),
            (x + 31, y - 27),
            5,
        )
        pygame.draw.rect(
            surface,
            (96, 100, 104),
            (x + 20, y - 34, 24, 13),
            border_radius=3,
        )
    else:
        pygame.draw.line(
            surface,
            detail,
            (x + 20, y + 19),
            (x + 28, y - 31),
            5,
        )
        pygame.draw.circle(
            surface,
            detail,
            (x + 29, y - 34),
            6,
            2,
        )

    if near:
        pulse = 36 + int(
            (math.sin(pygame.time.get_ticks() / 240) + 1) * 3
        )
        pygame.draw.circle(
            surface,
            accent,
            (x, y - 4),
            pulse,
            2,
        )

    return True

ETERNAL_PALETTES = {
    "Thorvald": {"cloth": (43, 73, 105), "accent": (93, 184, 255), "hair": (116, 86, 58), "gear": "axe"},
    "Aurel": {"cloth": (104, 84, 42), "accent": (245, 220, 115), "hair": (214, 187, 120), "gear": "staff"},
    "Kaion": {"cloth": (37, 78, 87), "accent": (113, 224, 232), "hair": (29, 31, 35), "gear": "blade"},
    "Brenor": {"cloth": (105, 54, 37), "accent": (245, 137, 69), "hair": (125, 65, 42), "gear": "hammer"},
    "Eiran": {"cloth": (42, 83, 61), "accent": (84, 210, 139), "hair": (178, 165, 128), "gear": "staff"},
    "Noctar": {"cloth": (61, 42, 86), "accent": (158, 116, 255), "hair": (21, 20, 27), "gear": "dagger"},
}


def draw_eterno_character(surface, name, center, seconds=0.0, index=0):
    style = ETERNAL_PALETTES.get(name, ETERNAL_PALETTES["Kaion"])
    x, y = int(center[0]), int(center[1])
    y += int(math.sin(seconds * 6 + index) * 2)
    cloth = style["cloth"]
    accent = style["accent"]
    hair = style["hair"]

    shadow = pygame.Surface((62, 18), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 115), shadow.get_rect())
    surface.blit(shadow, shadow.get_rect(center=(x, y + 31)))

    pygame.draw.line(surface, BOOT, (x - 8, y + 12), (x - 10, y + 29), 7)
    pygame.draw.line(surface, BOOT, (x + 8, y + 12), (x + 10, y + 29), 7)

    cloak = [
        (x - 20, y - 18),
        (x + 20, y - 18),
        (x + 26, y + 22),
        (x, y + 30),
        (x - 26, y + 22),
    ]
    pygame.draw.polygon(surface, (7, 10, 15), [(px + 2, py + 3) for px, py in cloak])
    pygame.draw.polygon(surface, tuple(max(0, c - 16) for c in cloth), cloak)

    pygame.draw.rect(surface, cloth, (x - 15, y - 21, 30, 37), border_radius=7)
    pygame.draw.line(surface, LEATHER, (x - 14, y - 2), (x + 14, y - 2), 4)
    pygame.draw.circle(surface, accent, (x, y - 2), 4)
    pygame.draw.circle(surface, STEEL_DARK, (x - 16, y - 16), 7)
    pygame.draw.circle(surface, STEEL_DARK, (x + 16, y - 16), 7)

    head_y = y - 39
    pygame.draw.circle(surface, (9, 12, 16), (x, head_y + 1), 16)
    pygame.draw.circle(surface, SKIN, (x, head_y), 13)

    if name == "Brenor":
        pygame.draw.polygon(
            surface,
            hair,
            [
                (x - 10, head_y + 5),
                (x + 10, head_y + 5),
                (x + 7, head_y + 18),
                (x, head_y + 22),
                (x - 7, head_y + 18),
            ],
        )
    elif name == "Noctar":
        pygame.draw.rect(surface, (28, 24, 36), (x - 12, head_y - 1, 24, 10), border_radius=4)
        pygame.draw.circle(surface, accent, (x + 5, head_y + 2), 2)
    elif name == "Aurel":
        hood = [
            (x - 15, head_y - 2),
            (x - 7, head_y - 18),
            (x + 7, head_y - 18),
            (x + 15, head_y - 2),
            (x + 11, head_y + 9),
            (x - 11, head_y + 9),
        ]
        pygame.draw.lines(surface, accent, True, hood, 4)
    else:
        pygame.draw.polygon(
            surface,
            hair,
            [
                (x - 13, head_y - 4),
                (x - 8, head_y - 14),
                (x + 4, head_y - 15),
                (x + 13, head_y - 7),
                (x + 8, head_y - 1),
                (x - 3, head_y - 5),
            ],
        )

    pygame.draw.circle(surface, (35, 26, 23), (x - 5, head_y), 2)
    pygame.draw.circle(surface, (35, 26, 23), (x + 5, head_y), 2)

    gear = style["gear"]
    if gear == "axe":
        draw_viking_axe(surface, (x + 28, y - 1), angle=-27, scale=0.48, rune_color=accent)
    elif gear == "blade":
        draw_sword(surface, (x + 26, y - 2), angle=-22, scale=0.47, rune_color=accent)
    elif gear == "hammer":
        pygame.draw.line(surface, WOOD, (x + 20, y + 24), (x + 31, y - 29), 7)
        pygame.draw.rect(surface, STEEL_DARK, (x + 18, y - 38, 31, 16), border_radius=4)
        pygame.draw.line(surface, accent, (x + 22, y - 31), (x + 44, y - 31), 2)
    elif gear == "dagger":
        draw_sword(surface, (x + 24, y + 4), angle=-35, scale=0.32, rune_color=accent)
        draw_sword(surface, (x - 24, y + 4), angle=35, scale=0.32, rune_color=accent)
    else:
        pygame.draw.line(surface, WOOD, (x + 23, y + 26), (x + 28, y - 38), 6)
        pygame.draw.circle(surface, accent, (x + 29, y - 42), 8, 2)
        pygame.draw.circle(surface, accent, (x + 29, y - 42), 3)

    return True


def draw_eterno_portrait(surface, name, rect):
    style = ETERNAL_PALETTES.get(name, ETERNAL_PALETTES["Kaion"])
    accent = style["accent"]
    pygame.draw.rect(surface, (7, 11, 17), rect, border_radius=16)
    pygame.draw.rect(surface, accent, rect, 2, border_radius=16)
    draw_eterno_character(
        surface,
        name,
        (rect.centerx, rect.centery + 25),
        seconds=0.0,
    )
