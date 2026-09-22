from pathlib import Path
import math

import pygame

from animation_v24 import DIRECTIONS_8, direction8, frame_index


FRAME_W = 56
FRAME_H = 72
FRAMES = 4
CHAR_STATES = (
    "idle",
    "walk",
    "run",
    "attack1",
    "attack2",
    "heavy",
    "dash",
    "hurt",
    "death",
    "power",
)
ENEMY_STATES = ("idle", "walk", "attack", "hurt")
BOSS_STATES = ("idle", "walk", "attack", "power")

ROOT = Path(__file__).with_name("assets") / "valdrak" / "sprites_v25"

ACTORS = {
    "protagonist": ((42, 92, 108), (70, 224, 235), (37, 29, 27), "sword"),
    "Thorvald": ((47, 79, 116), (93, 184, 255), (120, 84, 51), "axe"),
    "Aurel": ((115, 92, 42), (245, 220, 115), (215, 190, 126), "staff"),
    "Kaion": ((34, 92, 104), (113, 224, 232), (28, 31, 36), "sword"),
    "Brenor": ((121, 58, 41), (245, 137, 69), (124, 70, 43), "hammer"),
    "Eiran": ((46, 96, 68), (84, 210, 139), (174, 159, 121), "staff"),
    "Noctar": ((68, 45, 96), (158, 116, 255), (24, 21, 29), "daggers"),
}

ENEMIES = {
    "wolf": ((81, 95, 107), (225, 82, 92), "wolf"),
    "alpha_wolf": ((134, 149, 163), (190, 218, 231), "wolf"),
    "raider": ((121, 75, 63), (231, 190, 93), "axe"),
    "berserker": ((157, 58, 49), (255, 101, 79), "axes"),
    "archer": ((111, 93, 65), (231, 190, 93), "bow"),
    "rune_mage": ((84, 55, 124), (158, 116, 255), "staff"),
    "raven": ((57, 48, 77), (158, 116, 255), "raven"),
    "elite_raider": ((142, 102, 56), (245, 137, 69), "axe"),
}

BOSSES = {
    1: ((57, 99, 140), (85, 170, 255), "axe"),
    2: ((101, 94, 78), (221, 205, 163), "hammer"),
    3: ((138, 48, 47), (225, 82, 92), "axes"),
    4: ((70, 46, 101), (158, 116, 255), "staff"),
    5: ((119, 138, 151), (190, 218, 231), "wolf"),
    6: ((121, 58, 38), (245, 137, 69), "hammer"),
    7: ((60, 42, 91), (175, 105, 255), "sword"),
}

_cache = {}


def _shade(color, delta):
    return tuple(max(0, min(255, value + delta)) for value in color)


def _dir_vector(name):
    mapping = {
        "E": (1, 0),
        "SE": (0.7, 0.7),
        "S": (0, 1),
        "SW": (-0.7, 0.7),
        "W": (-1, 0),
        "NW": (-0.7, -0.7),
        "N": (0, -1),
        "NE": (0.7, -0.7),
    }
    return mapping[name]


def _draw_weapon(frame, x, y, gear, accent, facing, swing, boss=False):
    dx, dy = _dir_vector(facing)
    side = 1 if dx >= 0 else -1
    scale = 1.35 if boss else 1.0
    hand = (int(x + side * 13 * scale), int(y + 2 * scale))
    angle = math.atan2(dy, dx if abs(dx) > 0.1 else side)
    length = int(23 * scale)
    ex = int(hand[0] + math.cos(angle + swing) * length)
    ey = int(hand[1] + math.sin(angle + swing) * length)

    wood = (111, 73, 45)
    steel = (174, 188, 199)
    dark = (55, 62, 69)

    if gear in {"axe", "axes"}:
        pygame.draw.line(frame, wood, hand, (ex, ey), max(3, int(4 * scale)))
        nx = -math.sin(angle + swing)
        ny = math.cos(angle + swing)
        blade = [
            (ex, ey),
            (int(ex + nx * 12 * scale), int(ey + ny * 12 * scale)),
            (int(ex + nx * 17 * scale + math.cos(angle + swing) * 8 * scale),
             int(ey + ny * 17 * scale + math.sin(angle + swing) * 8 * scale)),
            (int(ex - nx * 5 * scale), int(ey - ny * 5 * scale)),
        ]
        pygame.draw.polygon(frame, dark, blade)
        pygame.draw.lines(frame, steel, False, blade[:3], max(1, int(2 * scale)))
        pygame.draw.line(frame, accent, blade[1], blade[2], 1)
        if gear == "axes":
            _draw_weapon(frame, x - side * 3, y + 3, "axe", accent, facing, -swing - 0.8, boss)
        return

    if gear in {"sword", "daggers"}:
        pygame.draw.line(frame, dark, hand, (ex, ey), max(4, int(5 * scale)))
        pygame.draw.line(frame, steel, hand, (ex, ey), max(2, int(3 * scale)))
        pygame.draw.line(frame, accent, hand, (ex, ey), 1)
        if gear == "daggers":
            _draw_weapon(frame, x - side * 5, y + 2, "sword", accent, facing, -swing - 0.7, boss)
        return

    if gear == "hammer":
        pygame.draw.line(frame, wood, hand, (ex, ey), max(4, int(5 * scale)))
        head = pygame.Rect(0, 0, int(20 * scale), int(10 * scale))
        head.center = (ex, ey)
        pygame.draw.rect(frame, dark, head, border_radius=2)
        pygame.draw.rect(frame, accent, head.inflate(-4, -4), border_radius=2)
        return

    if gear == "staff":
        pygame.draw.line(frame, wood, hand, (ex, ey), max(3, int(4 * scale)))
        pygame.draw.circle(frame, accent, (ex, ey), max(5, int(6 * scale)), 2)
        pygame.draw.circle(frame, accent, (ex, ey), max(2, int(2 * scale)))
        return

    if gear == "bow":
        rect = pygame.Rect(ex - 9, ey - 14, 18, 28)
        pygame.draw.arc(frame, wood, rect, -1.4, 1.4, 2)
        pygame.draw.line(frame, (210, 204, 179), (ex + 2, ey - 13), (ex + 2, ey + 13), 1)


def _draw_humanoid(frame, body, accent, hair, gear, facing, state, tick, boss=False):
    cx = FRAME_W // 2
    cy = FRAME_H // 2 + (6 if boss else 10)
    dx, dy = _dir_vector(facing)
    side = 1 if dx >= 0 else -1
    back = dy < -0.45
    scale = 1.28 if boss else 1.0

    walk = math.sin((tick / FRAMES) * math.tau)
    if state in {"idle", "hurt"}:
        walk *= 0.25
    if state == "run":
        walk *= 1.45

    if state == "death":
        pygame.draw.ellipse(frame, (0, 0, 0, 90), (cx - 22, cy + 17, 44, 10))
        pygame.draw.ellipse(frame, body, (cx - 23, cy + 5, 46, 16))
        pygame.draw.circle(frame, (207, 171, 141), (cx + 17, cy + 9), 8)
        return

    leg_offset = int(walk * 4)
    boot = (42, 31, 29)
    pygame.draw.line(frame, boot, (cx - 7, cy + 8), (cx - 8 - leg_offset, cy + 24), max(4, int(5 * scale)))
    pygame.draw.line(frame, boot, (cx + 7, cy + 8), (cx + 8 + leg_offset, cy + 24), max(4, int(5 * scale)))

    cloak = _shade(body, -30)
    pygame.draw.polygon(
        frame,
        cloak,
        [
            (cx - int(16 * scale), cy - int(15 * scale)),
            (cx + int(16 * scale), cy - int(15 * scale)),
            (cx + int(20 * scale), cy + int(16 * scale)),
            (cx, cy + int(23 * scale)),
            (cx - int(20 * scale), cy + int(16 * scale)),
        ],
    )
    pygame.draw.rect(
        frame,
        body,
        (
            cx - int(13 * scale),
            cy - int(18 * scale),
            int(26 * scale),
            int(31 * scale),
        ),
        border_radius=max(4, int(6 * scale)),
    )
    pygame.draw.line(frame, (83, 52, 34), (cx - 12, cy), (cx + 12, cy), max(2, int(3 * scale)))
    pygame.draw.circle(frame, accent, (cx, cy), max(2, int(3 * scale)))

    head_y = cy - int(30 * scale)
    pygame.draw.circle(frame, (18, 18, 22), (cx, head_y + 1), int(12 * scale))
    pygame.draw.circle(frame, (207, 171, 141), (cx, head_y), int(10 * scale))

    if back:
        pygame.draw.polygon(
            frame,
            hair,
            [
                (cx - 11, head_y - 5),
                (cx - 5, head_y - 13),
                (cx + 7, head_y - 12),
                (cx + 11, head_y - 3),
                (cx + 7, head_y + 5),
                (cx - 8, head_y + 5),
            ],
        )
    else:
        pygame.draw.polygon(
            frame,
            hair,
            [
                (cx - 11, head_y - 4),
                (cx - 6, head_y - 12),
                (cx + 4, head_y - 13),
                (cx + 11, head_y - 5),
                (cx + 6, head_y),
                (cx - 3, head_y - 3),
            ],
        )
        eye_x = cx + int(side * 4)
        pygame.draw.circle(frame, (42, 29, 23), (eye_x, head_y + 1), 1)

    if boss:
        pygame.draw.circle(frame, accent, (cx, cy - 5), int(24 * scale), 2)
        pygame.draw.circle(frame, _shade(accent, 35), (cx, cy - 5), int(28 * scale), 1)

    swing = 0.15
    if state in {"attack1", "attack", "power"}:
        swing = -1.4 + tick * 0.65
    elif state == "attack2":
        swing = 1.4 - tick * 0.65
    elif state == "heavy":
        swing = -2.0 + tick * 0.9
    elif state == "dash":
        swing = -2.5
    _draw_weapon(frame, cx, cy, gear, accent, facing, swing, boss=boss)


def _draw_wolf(frame, color, accent, facing, state, tick, boss=False):
    cx = FRAME_W // 2
    cy = FRAME_H // 2 + 13
    dx, dy = _dir_vector(facing)
    stretch = 4 if state in {"walk", "attack"} else 0
    body_w = 34 + stretch
    body_h = 17
    scale = 1.25 if boss else 1.0
    pygame.draw.ellipse(frame, color, (cx - int(body_w*scale/2), cy - 8, int(body_w*scale), int(body_h*scale)))
    hx = cx + int(dx * 17 * scale)
    hy = cy + int(dy * 10 * scale) - 5
    pygame.draw.circle(frame, _shade(color, 15), (hx, hy), int(8 * scale))
    pygame.draw.polygon(frame, color, [(hx - 6, hy - 5), (hx - 3, hy - 13), (hx + 1, hy - 6)])
    pygame.draw.polygon(frame, color, [(hx + 6, hy - 5), (hx + 3, hy - 13), (hx - 1, hy - 6)])
    pygame.draw.circle(frame, accent, (hx + (2 if dx >= 0 else -2), hy - 1), 2)
    stride = math.sin((tick / FRAMES) * math.tau) * 4
    for off in (-10, 10):
        pygame.draw.line(frame, _shade(color,-25), (cx + off, cy + 5), (cx + off + int(stride), cy + 19), 3)


def _draw_raven(frame, color, accent, facing, state, tick, boss=False):
    cx = FRAME_W // 2
    cy = FRAME_H // 2 + 4
    flap = math.sin((tick / FRAMES) * math.tau) * 16
    pygame.draw.polygon(frame, color, [(cx, cy), (cx - 25, cy - 10 - int(flap)), (cx - 8, cy + 13)])
    pygame.draw.polygon(frame, color, [(cx, cy), (cx + 25, cy - 10 - int(flap)), (cx + 8, cy + 13)])
    pygame.draw.circle(frame, _shade(color, 12), (cx, cy - 5), 9)
    pygame.draw.circle(frame, accent, (cx + 3, cy - 7), 2)


def _build_sheet(path, actor_kind, style, states, frame_w=FRAME_W, frame_h=FRAME_H, boss=False):
    width = len(DIRECTIONS_8) * FRAMES * frame_w
    height = len(states) * frame_h
    sheet = pygame.Surface((width, height), pygame.SRCALPHA)
    for state_index, state in enumerate(states):
        for direction_index, facing in enumerate(DIRECTIONS_8):
            for tick in range(FRAMES):
                frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                if actor_kind == "humanoid":
                    body, accent, hair, gear = style
                    _draw_humanoid(frame, body, accent, hair, gear, facing, state, tick, boss=boss)
                elif actor_kind == "wolf":
                    color, accent, _gear = style
                    _draw_wolf(frame, color, accent, facing, state, tick, boss=boss)
                elif actor_kind == "raven":
                    color, accent, _gear = style
                    _draw_raven(frame, color, accent, facing, state, tick, boss=boss)
                else:
                    color, accent, gear = style
                    _draw_humanoid(frame, color, accent, (34, 30, 29), gear, facing, state, tick, boss=boss)
                x = (direction_index * FRAMES + tick) * frame_w
                y = state_index * frame_h
                sheet.blit(frame, (x, y))
    pygame.image.save(sheet, path)


def build_all():
    ROOT.mkdir(parents=True, exist_ok=True)
    for name, style in ACTORS.items():
        _build_sheet(ROOT / f"{name.lower()}_v25.png", "humanoid", style, CHAR_STATES)

    for name, style in ENEMIES.items():
        kind = "wolf" if "wolf" in name else "raven" if name == "raven" else "enemy"
        _build_sheet(ROOT / f"enemy_{name}_v25.png", kind, style, ENEMY_STATES)

    for chapter, style in BOSSES.items():
        kind = "wolf" if style[2] == "wolf" else "humanoid"
        hair = (38, 31, 29)
        packed = (style[0], style[1], hair, style[2]) if kind == "humanoid" else style
        _build_sheet(
            ROOT / f"boss_{chapter}_v25.png",
            kind,
            packed,
            BOSS_STATES,
            boss=True,
        )


def _load(path):
    key = str(path)
    surface = _cache.get(key)
    if surface is None and path.exists():
        surface = pygame.image.load(str(path)).convert_alpha()
        _cache[key] = surface
    return surface


def _normalize_state(state, states):
    mapping = {
        "attack": "attack1",
        "pulse": "power",
    }
    state = mapping.get(state, state)
    return state if state in states else states[0]


def draw_actor_v25(
    surface,
    actor,
    center,
    facing,
    state,
    seconds,
    scale=1.0,
    chapter=None,
):
    if actor == "boss":
        path = ROOT / f"boss_{chapter}_v25.png"
        states = BOSS_STATES
    elif actor in ENEMIES:
        path = ROOT / f"enemy_{actor}_v25.png"
        states = ENEMY_STATES
    else:
        path = ROOT / f"{actor.lower()}_v25.png"
        states = CHAR_STATES

    sheet = _load(path)
    if sheet is None:
        return False

    direction_name = direction8(facing)
    d_index = DIRECTIONS_8.index(direction_name)
    normalized = _normalize_state(state, states)
    s_index = states.index(normalized)
    frame = frame_index(normalized, seconds, FRAMES)

    rect = pygame.Rect(
        (d_index * FRAMES + frame) * FRAME_W,
        s_index * FRAME_H,
        FRAME_W,
        FRAME_H,
    )
    image = sheet.subsurface(rect)
    if scale != 1.0:
        image = pygame.transform.smoothscale(
            image,
            (
                int(FRAME_W * scale),
                int(FRAME_H * scale),
            ),
        )
    target = image.get_rect(
        midbottom=(int(center[0]), int(center[1]) + int(30 * scale))
    )
    surface.blit(image, target)
    return True
