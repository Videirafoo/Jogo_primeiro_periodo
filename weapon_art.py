import math

import pygame


INK = (226, 233, 238)
STEEL_DARK = (73, 82, 92)
STEEL = (148, 161, 174)
STEEL_LIGHT = (224, 231, 234)
WOOD_DARK = (62, 39, 27)
WOOD = (112, 72, 45)
WOOD_LIGHT = (161, 105, 61)
LEATHER = (73, 45, 32)
GOLD = (231, 190, 93)
RED = (225, 82, 92)
CYAN = (70, 224, 235)
VIOLET = (158, 116, 255)


def _rotated_point(point, center, angle):
    px, py = point
    cx, cy = center
    radians = math.radians(angle)
    cosine = math.cos(radians)
    sine = math.sin(radians)
    dx = px - cx
    dy = py - cy
    return (
        cx + dx * cosine - dy * sine,
        cy + dx * sine + dy * cosine,
    )


def _draw_axe_local(surface, center, scale=1.0, rune_color=None):
    x, y = center
    shaft_w = max(4, int(7 * scale))
    shaft_h = int(76 * scale)

    handle = pygame.Rect(
        int(x - shaft_w / 2),
        int(y - shaft_h * 0.35),
        shaft_w,
        shaft_h,
    )

    pygame.draw.rect(
        surface,
        WOOD_DARK,
        handle.inflate(4, 2),
        border_radius=max(2, int(shaft_w / 2)),
    )
    pygame.draw.rect(
        surface,
        WOOD,
        handle,
        border_radius=max(2, int(shaft_w / 2)),
    )
    pygame.draw.line(
        surface,
        WOOD_LIGHT,
        (handle.left + 2, handle.top + 4),
        (handle.left + 2, handle.bottom - 5),
        max(1, int(1 * scale)),
    )

    grip_top = int(y + shaft_h * 0.18)
    for offset in range(0, int(22 * scale), max(4, int(5 * scale))):
        pygame.draw.line(
            surface,
            LEATHER,
            (
                int(x - shaft_w / 2 - 2),
                grip_top + offset,
            ),
            (
                int(x + shaft_w / 2 + 2),
                grip_top + offset + max(2, int(2 * scale)),
            ),
            max(2, int(2 * scale)),
        )

    head_y = int(y - shaft_h * 0.31)
    neck = max(5, int(8 * scale))
    blade_w = int(42 * scale)
    blade_h = int(34 * scale)

    head = [
        (x - neck, head_y - int(10 * scale)),
        (x - int(17 * scale), head_y - int(15 * scale)),
        (x - blade_w, head_y - int(7 * scale)),
        (x - blade_w - int(5 * scale), head_y + int(4 * scale)),
        (x - int(25 * scale), head_y + int(17 * scale)),
        (x - neck, head_y + int(13 * scale)),
        (x + int(10 * scale), head_y + int(11 * scale)),
        (x + int(19 * scale), head_y + int(2 * scale)),
        (x + int(10 * scale), head_y - int(9 * scale)),
    ]

    shadow = [(int(px + 2), int(py + 3)) for px, py in head]
    pygame.draw.polygon(surface, (26, 31, 37), shadow)
    pygame.draw.polygon(surface, STEEL_DARK, head)

    inner = [
        (x - int(8 * scale), head_y - int(7 * scale)),
        (x - int(18 * scale), head_y - int(10 * scale)),
        (x - int(34 * scale), head_y - int(5 * scale)),
        (x - int(37 * scale), head_y + int(2 * scale)),
        (x - int(21 * scale), head_y + int(11 * scale)),
        (x - int(7 * scale), head_y + int(9 * scale)),
    ]
    pygame.draw.polygon(surface, STEEL, inner)

    edge = [
        (x - blade_w, head_y - int(7 * scale)),
        (x - blade_w - int(5 * scale), head_y + int(4 * scale)),
        (x - int(25 * scale), head_y + int(17 * scale)),
    ]
    pygame.draw.lines(
        surface,
        STEEL_LIGHT,
        False,
        edge,
        max(2, int(2 * scale)),
    )

    pygame.draw.circle(
        surface,
        (47, 52, 58),
        (int(x), head_y),
        max(4, int(5 * scale)),
    )

    if rune_color:
        pygame.draw.line(
            surface,
            rune_color,
            (
                int(x - 18 * scale),
                head_y - int(5 * scale),
            ),
            (
                int(x - 25 * scale),
                head_y + int(7 * scale),
            ),
            max(1, int(2 * scale)),
        )
        pygame.draw.line(
            surface,
            rune_color,
            (
                int(x - 25 * scale),
                head_y + int(7 * scale),
            ),
            (
                int(x - 13 * scale),
                head_y + int(5 * scale),
            ),
            max(1, int(2 * scale)),
        )


def draw_viking_axe(
    surface,
    center,
    angle=0.0,
    scale=1.0,
    rune_color=None,
    motion=0.0,
):
    padding = int(125 * scale)
    canvas = pygame.Surface(
        (padding * 2, padding * 2),
        pygame.SRCALPHA,
    )
    local_center = (padding, padding)

    if motion > 0:
        for index in range(3, 0, -1):
            ghost = pygame.Surface(
                canvas.get_size(),
                pygame.SRCALPHA,
            )
            _draw_axe_local(
                ghost,
                local_center,
                scale,
                rune_color,
            )
            ghost = pygame.transform.rotate(
                ghost,
                angle - index * 13,
            )
            ghost.set_alpha(
                max(18, int(42 * motion / index))
            )
            rect = ghost.get_rect(center=center)
            surface.blit(ghost, rect)

    _draw_axe_local(
        canvas,
        local_center,
        scale,
        rune_color,
    )
    rotated = pygame.transform.rotate(
        canvas,
        angle,
    )
    rect = rotated.get_rect(center=center)
    surface.blit(rotated, rect)


def _draw_sword_local(surface, center, scale=1.0, rune_color=CYAN):
    x, y = center
    blade_len = int(72 * scale)
    blade_w = max(5, int(7 * scale))

    points = [
        (x, y - blade_len),
        (x + blade_w, y - int(11 * scale)),
        (x, y - int(3 * scale)),
        (x - blade_w, y - int(11 * scale)),
    ]
    pygame.draw.polygon(surface, STEEL_DARK, points)

    inner = [
        (x, y - blade_len + int(6 * scale)),
        (x + int(3 * scale), y - int(12 * scale)),
        (x, y - int(7 * scale)),
        (x - int(3 * scale), y - int(12 * scale)),
    ]
    pygame.draw.polygon(surface, STEEL_LIGHT, inner)

    pygame.draw.line(
        surface,
        rune_color,
        (int(x), int(y - blade_len + 14 * scale)),
        (int(x), int(y - 24 * scale)),
        max(1, int(1 * scale)),
    )

    guard_y = int(y - 5 * scale)
    pygame.draw.line(
        surface,
        GOLD,
        (
            int(x - 16 * scale),
            guard_y,
        ),
        (
            int(x + 16 * scale),
            guard_y,
        ),
        max(3, int(4 * scale)),
    )

    pygame.draw.line(
        surface,
        LEATHER,
        (int(x), int(y)),
        (int(x), int(y + 28 * scale)),
        max(5, int(6 * scale)),
    )
    pygame.draw.circle(
        surface,
        GOLD,
        (int(x), int(y + 31 * scale)),
        max(4, int(5 * scale)),
    )


def draw_sword(
    surface,
    center,
    angle=0.0,
    scale=1.0,
    rune_color=CYAN,
    motion=0.0,
):
    padding = int(115 * scale)
    canvas = pygame.Surface(
        (padding * 2, padding * 2),
        pygame.SRCALPHA,
    )
    local_center = (padding, padding)

    if motion > 0:
        for index in range(3, 0, -1):
            ghost = pygame.Surface(
                canvas.get_size(),
                pygame.SRCALPHA,
            )
            _draw_sword_local(
                ghost,
                local_center,
                scale,
                rune_color,
            )
            ghost = pygame.transform.rotate(
                ghost,
                angle - index * 10,
            )
            ghost.set_alpha(
                max(14, int(36 * motion / index))
            )
            surface.blit(
                ghost,
                ghost.get_rect(center=center),
            )

    _draw_sword_local(
        canvas,
        local_center,
        scale,
        rune_color,
    )
    rotated = pygame.transform.rotate(
        canvas,
        angle,
    )
    surface.blit(
        rotated,
        rotated.get_rect(center=center),
    )


def draw_boss_weapon(
    surface,
    chapter,
    center,
    seconds,
    scale=1.0,
):
    angle = math.sin(seconds * 2.1) * 7

    if chapter == 3:
        draw_viking_axe(
            surface,
            center,
            -38 + angle,
            scale=1.15 * scale,
            rune_color=RED,
        )
        draw_viking_axe(
            surface,
            (center[0] + 18, center[1] + 3),
            42 - angle,
            scale=1.0 * scale,
            rune_color=GOLD,
        )
        return

    if chapter in (1, 2):
        draw_viking_axe(
            surface,
            center,
            -28 + angle,
            scale=0.9 * scale,
            rune_color=CYAN if chapter == 1 else GOLD,
        )
        return

    if chapter == 6:
        # Forge hammer: deliberately much heavier than an axe.
        x, y = center
        pygame.draw.line(
            surface,
            WOOD,
            (x - 22, y + 34),
            (x + 15, y - 30),
            max(7, int(8 * scale)),
        )
        head = pygame.Rect(
            x - 2,
            y - 48,
            int(46 * scale),
            int(25 * scale),
        )
        pygame.draw.rect(
            surface,
            STEEL_DARK,
            head,
            border_radius=5,
        )
        pygame.draw.rect(
            surface,
            (180, 79, 42),
            head.inflate(-7, -7),
            border_radius=4,
        )
        return

    if chapter == 7:
        draw_sword(
            surface,
            center,
            -18 + angle,
            scale=1.05 * scale,
            rune_color=VIOLET,
        )
        return

    draw_sword(
        surface,
        center,
        -20 + angle,
        scale=0.86 * scale,
        rune_color=VIOLET if chapter == 4 else CYAN,
    )
