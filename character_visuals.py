import math

import pygame

from sprite_animator import draw_actor


INK = (236, 242, 248)
DARK = (8, 13, 20)
GOLD = (231, 190, 93)
CYAN = (70, 224, 235)
GREEN = (84, 210, 139)
VIOLET = (158, 116, 255)
RED = (225, 82, 92)
ORANGE = (245, 137, 69)


ALLY_STYLES = {
    "Thorvald": {
        "color": (100, 180, 255),
        "power": "Raio de Torv",
        "symbol": "bolt",
    },
    "Aurel": {
        "color": (245, 220, 115),
        "power": "Olho do Céu",
        "symbol": "eye",
    },
    "Kaion": {
        "color": (155, 225, 235),
        "power": "Lâmina do Vento",
        "symbol": "blade",
    },
    "Brenor": {
        "color": ORANGE,
        "power": "Fogo da Forja",
        "symbol": "fire",
    },
    "Eiran": {
        "color": GREEN,
        "power": "Cura da Aurora",
        "symbol": "heal",
    },
    "Noctar": {
        "color": VIOLET,
        "power": "Sombra dos Corvos",
        "symbol": "shadow",
    },
}


BOSS_AURAS = {
    1: (85, 170, 255),
    2: (215, 205, 170),
    3: RED,
    4: VIOLET,
    5: (180, 205, 220),
    6: ORANGE,
    7: (175, 105, 255),
}


def draw_ally(surface, name, pos, offset, seconds, index=0):
    style = ALLY_STYLES.get(
        name,
        {
            "color": CYAN,
            "power": "Poder Desperto",
            "symbol": "eye",
        },
    )
    color = style["color"]
    x = int(pos.x - offset.x)
    y = int(pos.y - offset.y)
    bob = int(math.sin(seconds * 5 + index) * 2)

    rendered = draw_actor(
        surface,
        name,
        (x, y),
        state="walk",
        seconds=seconds,
        tint=color,
    )

    if not rendered:
        pygame.draw.rect(
            surface,
            color,
            (x - 11, y - 9 + bob, 22, 30),
            border_radius=7,
        )
        pygame.draw.circle(
            surface,
            (205, 173, 145),
            (x, y - 18 + bob),
            10,
        )

    pygame.draw.circle(
        surface,
        color,
        (x, y),
        28,
        1,
    )

    radius = 35 + int((math.sin(seconds * 3 + index) + 1) * 3)
    _draw_symbol(
        surface,
        style["symbol"],
        (x, y - 38),
        color,
        radius,
        seconds,
    )


def draw_portrait(surface, name, rect, accent=None):
    style = ALLY_STYLES.get(name, None)
    color = accent or (style["color"] if style else CYAN)

    pygame.draw.rect(
        surface,
        DARK,
        rect,
        border_radius=16,
    )
    pygame.draw.rect(
        surface,
        color,
        rect,
        2,
        border_radius=16,
    )

    cx = rect.centerx
    cy = rect.centery + 8

    pygame.draw.circle(
        surface,
        (26, 35, 47),
        (cx, cy + 26),
        43,
    )
    pygame.draw.rect(
        surface,
        color,
        (cx - 24, cy - 5, 48, 65),
        border_radius=15,
    )
    pygame.draw.circle(
        surface,
        (209, 177, 148),
        (cx, cy - 35),
        27,
    )

    hair = [
        (cx - 29, cy - 43),
        (cx - 10, cy - 70),
        (cx + 22, cy - 61),
        (cx + 31, cy - 38),
    ]
    pygame.draw.polygon(
        surface,
        (35, 40, 48),
        hair,
    )

    pygame.draw.circle(
        surface,
        (40, 30, 25),
        (cx - 9, cy - 37),
        3,
    )
    pygame.draw.circle(
        surface,
        (40, 30, 25),
        (cx + 9, cy - 37),
        3,
    )

    if style:
        _draw_symbol(
            surface,
            style["symbol"],
            (cx, rect.bottom - 22),
            color,
            18,
            0,
        )


def draw_boss_aura(surface, chapter, center, seconds, scale=1.0):
    color = BOSS_AURAS.get(chapter, GOLD)
    x, y = center

    for index in range(3):
        radius = int(
            (42 + index * 14 + math.sin(seconds * 3 + index) * 5)
            * scale
        )
        pygame.draw.circle(
            surface,
            color,
            (x, y),
            radius,
            max(1, 3 - index),
        )

    for index in range(6):
        angle = seconds * 1.8 + index * math.tau / 6
        px = x + math.cos(angle) * 52 * scale
        py = y + math.sin(angle) * 32 * scale
        pygame.draw.circle(
            surface,
            color,
            (int(px), int(py)),
            max(2, int(3 * scale)),
        )


def draw_dialogue_box(
    surface,
    fonts,
    speaker,
    body,
    accent,
    portrait_name=None,
):
    panel = pygame.Rect(58, 486, 1164, 178)
    pygame.draw.rect(
        surface,
        (7, 12, 19),
        panel,
        border_radius=20,
    )
    pygame.draw.rect(
        surface,
        accent,
        panel,
        2,
        border_radius=20,
    )

    portrait = pygame.Rect(78, 504, 130, 140)
    draw_portrait(
        surface,
        portrait_name or speaker,
        portrait,
        accent,
    )

    title = fonts["heading"].render(
        speaker,
        True,
        accent,
    )
    surface.blit(title, (230, 505))

    lines = _wrap(
        fonts["body"],
        body,
        930,
    )
    for index, line in enumerate(lines[:4]):
        rendered = fonts["body"].render(
            line,
            True,
            INK,
        )
        surface.blit(
            rendered,
            (230, 547 + index * 27),
        )


def _wrap(font, text, width):
    words = str(text).split()
    lines = []
    current = ""

    for word in words:
        candidate = (
            word
            if not current
            else f"{current} {word}"
        )
        if font.size(candidate)[0] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def _draw_symbol(surface, symbol, center, color, radius, seconds):
    x, y = int(center[0]), int(center[1])
    r = max(8, int(radius * 0.35))

    if symbol == "bolt":
        points = [
            (x + 2, y - r),
            (x - r // 2, y),
            (x, y),
            (x - 3, y + r),
            (x + r // 2, y - 2),
            (x + 1, y - 2),
        ]
        pygame.draw.polygon(surface, color, points)
        return

    if symbol == "eye":
        pygame.draw.ellipse(
            surface,
            color,
            (x - r, y - r // 2, r * 2, r),
            2,
        )
        pygame.draw.circle(
            surface,
            color,
            (x, y),
            max(2, r // 4),
        )
        return

    if symbol == "blade":
        pygame.draw.line(
            surface,
            color,
            (x - r, y + r),
            (x + r, y - r),
            4,
        )
        pygame.draw.circle(
            surface,
            color,
            (x - r, y + r),
            4,
        )
        return

    if symbol == "fire":
        flame = [
            (x, y - r),
            (x + r // 2, y),
            (x + r // 3, y + r),
            (x, y + r // 2),
            (x - r // 2, y + r),
            (x - r // 2, y),
        ]
        pygame.draw.polygon(
            surface,
            color,
            flame,
        )
        return

    if symbol == "heal":
        pygame.draw.line(
            surface,
            color,
            (x - r, y),
            (x + r, y),
            4,
        )
        pygame.draw.line(
            surface,
            color,
            (x, y - r),
            (x, y + r),
            4,
        )
        return

    if symbol == "shadow":
        pygame.draw.arc(
            surface,
            color,
            (x - r, y - r, r * 2, r * 2),
            math.pi / 2,
            math.pi * 1.5,
            4,
        )
        pygame.draw.circle(
            surface,
            color,
            (x + r // 3, y),
            max(2, r // 5),
        )
