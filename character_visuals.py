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

from character_art import draw_eterno_character, draw_eterno_portrait


def draw_ally(surface, name, pos, offset, seconds, index=0):
    style = ALLY_STYLES.get(name, {"color": CYAN, "symbol": "eye"})
    x = int(pos.x - offset.x)
    y = int(pos.y - offset.y)
    draw_eterno_character(surface, name, (x, y), seconds=seconds, index=index)
    color = style["color"]
    radius = 38 + int((math.sin(seconds * 3 + index) + 1) * 3)
    pygame.draw.circle(surface, color, (x, y - 3), radius, 1)
    _draw_symbol(surface, style["symbol"], (x, y - 55), color, 20, seconds)


def draw_portrait(surface, name, rect, accent=None):
    if name in ALLY_STYLES:
        draw_eterno_portrait(surface, name, rect)
        return

    color = accent or CYAN
    pygame.draw.rect(surface, DARK, rect, border_radius=16)
    pygame.draw.rect(surface, color, rect, 2, border_radius=16)
    cx, cy = rect.center
    pygame.draw.circle(surface, (28, 37, 49), (cx, cy + 25), 42)
    pygame.draw.circle(surface, (207, 171, 141), (cx, cy - 22), 25)
    pygame.draw.polygon(
        surface,
        (31, 32, 38),
        [
            (cx - 27, cy - 27),
            (cx - 11, cy - 53),
            (cx + 21, cy - 48),
            (cx + 29, cy - 23),
        ],
    )

# V2.5 final authored renderers
from sprite_v25 import draw_actor_v25
from character_art import draw_viking_npc


def draw_ally(surface, name, pos, offset, seconds, index=0):
    style = ALLY_STYLES.get(
        name,
        {"color": CYAN, "symbol": "eye"},
    )
    x = int(pos.x - offset.x)
    y = int(pos.y - offset.y)
    facing = pygame.Vector2(
        math.cos(seconds * 0.22 + index * 0.7),
        0.75,
    )

    rendered = draw_actor_v25(
        surface,
        name,
        (x, y),
        facing,
        "walk",
        seconds + index * 0.11,
        scale=1.20,
    )
    if not rendered:
        draw_eterno_character(
            surface,
            name,
            (x, y),
            seconds=seconds,
            index=index,
        )

    color = style["color"]
    radius = 39 + int(
        (math.sin(seconds * 2.6 + index) + 1) * 2
    )
    pygame.draw.circle(
        surface,
        color,
        (x, y - 2),
        radius,
        1,
    )


def _is_character_speaker(name):
    if name in ALLY_STYLES:
        return True
    keywords = (
        "Edda",
        "Orm",
        "Sigrun",
        "Hilda",
        "Torsten",
        "Yrsa",
        "Voz da Porta",
    )
    return any(key in str(name) for key in keywords)


def _draw_lore_emblem(surface, rect, accent, seconds):
    cx, cy = rect.center
    pygame.draw.rect(
        surface,
        (10, 15, 22),
        rect,
        border_radius=18,
    )
    pygame.draw.rect(
        surface,
        accent,
        rect,
        2,
        border_radius=18,
    )
    radius = min(rect.width, rect.height) // 3
    pygame.draw.circle(
        surface,
        accent,
        (cx, cy),
        radius,
        2,
    )
    points = []
    for index in range(6):
        angle = (
            seconds * 0.25
            + index * math.tau / 6
        )
        points.append(
            (
                int(cx + math.cos(angle) * radius * 0.72),
                int(cy + math.sin(angle) * radius * 0.72),
            )
        )
    pygame.draw.lines(
        surface,
        accent,
        True,
        points,
        2,
    )
    pygame.draw.line(
        surface,
        accent,
        (cx, cy - radius + 8),
        (cx, cy + radius - 8),
        3,
    )
    pygame.draw.circle(
        surface,
        GOLD,
        (cx, cy),
        5,
    )


def draw_dialogue_box(
    surface,
    fonts,
    speaker,
    body,
    accent,
    portrait_name=None,
):
    # Smaller dialogue card keeps more of the adventure visible.
    panel = pygame.Rect(92, 492, 1096, 166)
    shadow = pygame.Surface(
        (panel.width + 12, panel.height + 12),
        pygame.SRCALPHA,
    )
    pygame.draw.rect(
        shadow,
        (0, 0, 0, 110),
        shadow.get_rect(),
        border_radius=23,
    )
    surface.blit(
        shadow,
        (panel.x + 5, panel.y + 7),
    )
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

    portrait = pygame.Rect(112, 531, 100, 112)
    name = portrait_name or speaker
    if name in ALLY_STYLES:
        pygame.draw.rect(
            surface,
            (8, 13, 20),
            portrait,
            border_radius=16,
        )
        pygame.draw.rect(
            surface,
            ALLY_STYLES[name]["color"],
            portrait,
            2,
            border_radius=16,
        )
        draw_actor_v25(
            surface,
            name,
            (
                portrait.centerx,
                portrait.bottom - 42,
            ),
            pygame.Vector2(0, 1),
            "idle",
            pygame.time.get_ticks() / 1000,
            scale=1.42,
        )
    elif _is_character_speaker(name):
        draw_viking_npc(
            surface,
            (
                portrait.centerx,
                portrait.bottom - 39,
            ),
            1,
            accent,
            near=False,
        )
        pygame.draw.rect(
            surface,
            accent,
            portrait,
            2,
            border_radius=16,
        )
    else:
        _draw_lore_emblem(
            surface,
            portrait,
            accent,
            pygame.time.get_ticks() / 1000,
        )

    title = fonts["heading"].render(
        str(speaker),
        True,
        accent,
    )
    surface.blit(title, (235, 530))

    lines = _wrap(
        fonts["body"],
        body,
        900,
    )
    for index, line in enumerate(lines[:3]):
        surface.blit(
            fonts["body"].render(
                line,
                True,
                INK,
            ),
            (235, 571 + index * 27),
        )
