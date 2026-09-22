import math

import pygame

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
    x, y = int(center[0]), int(center[1])
    scale = 1.0

    walk = math.sin(seconds * 11)
    bob = int(abs(walk) * 2) if state == "walk" else 0
    y += bob

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

    direction = 1
    if facing is not None and getattr(facing, "x", 0) < -0.15:
        direction = -1

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

    if state == "attack":
        angle = (
            -55
            if direction > 0
            else 55
        )
        angle += math.sin(seconds * 24) * 12
        draw_sword(
            surface,
            weapon_center,
            angle=angle,
            scale=0.63,
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
