import math

import pygame


ROLE_STYLE = {
    "vidente": {
        "cloth": (91, 65, 129),
        "trim": (174, 132, 235),
        "hair": (192, 192, 205),
        "skin": (204, 166, 137),
        "item": "rune",
    },
    "ferreiro": {
        "cloth": (111, 58, 41),
        "trim": (221, 126, 67),
        "hair": (70, 47, 35),
        "skin": (188, 142, 112),
        "item": "hammer",
    },
    "caçador": {
        "cloth": (52, 91, 63),
        "trim": (119, 154, 89),
        "hair": (68, 48, 34),
        "skin": (201, 159, 128),
        "item": "bow",
    },
    "mercador": {
        "cloth": (128, 91, 43),
        "trim": (229, 188, 91),
        "hair": (88, 58, 35),
        "skin": (214, 174, 138),
        "item": "pouch",
    },
    "guarda": {
        "cloth": (59, 82, 112),
        "trim": (151, 177, 201),
        "hair": (63, 50, 42),
        "skin": (198, 153, 123),
        "item": "spear",
    },
    "curandeira": {
        "cloth": (49, 105, 78),
        "trim": (111, 202, 151),
        "hair": (118, 83, 55),
        "skin": (218, 177, 145),
        "item": "herb",
    },
    "viajante": {
        "cloth": (86, 78, 70),
        "trim": (143, 131, 116),
        "hair": (51, 43, 39),
        "skin": (194, 148, 116),
        "item": "pack",
    },
}


def _face(surface, x, y, style, facing, seconds, index):
    skin = style["skin"]
    hair = style["hair"]
    pygame.draw.circle(surface, skin, (x, y), 11)

    # Distinct hair silhouettes per NPC index and role.
    variant = index % 4
    if variant == 0:
        pygame.draw.arc(
            surface,
            hair,
            (x - 12, y - 13, 24, 18),
            math.pi,
            math.tau,
            6,
        )
    elif variant == 1:
        pygame.draw.polygon(
            surface,
            hair,
            [
                (x - 12, y - 3),
                (x - 8, y - 13),
                (x + 5, y - 14),
                (x + 12, y - 4),
                (x + 8, y - 1),
                (x - 7, y - 2),
            ],
        )
    elif variant == 2:
        pygame.draw.circle(surface, hair, (x - 7, y - 8), 6)
        pygame.draw.circle(surface, hair, (x + 1, y - 11), 7)
        pygame.draw.circle(surface, hair, (x + 8, y - 7), 5)
    else:
        pygame.draw.rect(
            surface,
            hair,
            (x - 10, y - 14, 20, 9),
            border_radius=4,
        )

    # Brows, eyes, nose and beard/mouth improve face legibility.
    side = 1 if getattr(facing, "x", 0) >= 0 else -1
    pygame.draw.line(
        surface,
        (65, 45, 36),
        (x - 6, y - 2),
        (x - 2, y - 3),
        1,
    )
    pygame.draw.line(
        surface,
        (65, 45, 36),
        (x + 2, y - 3),
        (x + 6, y - 2),
        1,
    )
    pygame.draw.circle(surface, (34, 30, 27), (x - 4, y), 1)
    pygame.draw.circle(surface, (34, 30, 27), (x + 4, y), 1)
    pygame.draw.line(
        surface,
        (147, 104, 83),
        (x + side, y + 1),
        (x + side * 2, y + 5),
        1,
    )
    pygame.draw.line(
        surface,
        (111, 67, 55),
        (x - 3, y + 7),
        (x + 3, y + 7),
        1,
    )

    if index % 3 == 0:
        pygame.draw.arc(
            surface,
            hair,
            (x - 8, y + 3, 16, 12),
            0.15,
            math.pi - 0.15,
            2,
        )


def _accessory(surface, role, x, y, style, seconds):
    trim = style["trim"]
    item = style["item"]
    if item == "hammer":
        pygame.draw.line(surface, (103, 69, 43), (x + 12, y), (x + 25, y - 22), 4)
        pygame.draw.rect(surface, (92, 100, 108), (x + 18, y - 28, 18, 9), border_radius=2)
    elif item == "spear":
        pygame.draw.line(surface, (157, 168, 180), (x + 15, y + 18), (x + 28, y - 30), 3)
        pygame.draw.polygon(
            surface,
            (199, 209, 217),
            [(x + 28, y - 35), (x + 22, y - 25), (x + 32, y - 27)],
        )
    elif item == "bow":
        pygame.draw.arc(surface, (119, 78, 46), (x + 7, y - 20, 28, 45), -1.4, 1.4, 3)
        pygame.draw.line(surface, (212, 205, 179), (x + 23, y - 18), (x + 23, y + 22), 1)
    elif item == "rune":
        pulse = 6 + int((math.sin(seconds * 4) + 1) * 2)
        pygame.draw.circle(surface, trim, (x + 20, y - 18), pulse, 2)
        pygame.draw.line(surface, trim, (x + 20, y - 23), (x + 20, y - 13), 1)
    elif item == "herb":
        pygame.draw.line(surface, (75, 123, 75), (x + 13, y + 12), (x + 24, y - 9), 2)
        pygame.draw.circle(surface, (111, 187, 112), (x + 26, y - 11), 4)
    elif item == "pouch":
        pygame.draw.rect(surface, (101, 67, 41), (x + 11, y + 4, 15, 17), border_radius=5)
        pygame.draw.circle(surface, trim, (x + 18, y + 7), 2)
    elif item == "pack":
        pygame.draw.rect(surface, (83, 63, 47), (x - 22, y - 4, 12, 25), border_radius=4)


def draw_npc_v27(
    surface,
    pos,
    role,
    facing,
    seconds,
    index=0,
    near=False,
    name="",
    fonts=None,
):
    style = ROLE_STYLE.get(role, ROLE_STYLE["viajante"])
    x, y = int(pos[0]), int(pos[1])
    bob = int(abs(math.sin(seconds * 5.4 + index * 0.8)) * 2)

    # Contact shadow and moving cloak.
    pygame.draw.ellipse(surface, (0, 0, 0), (x - 22, y + 23, 44, 12))
    sway = int(math.sin(seconds * 2.6 + index) * 4)
    cloak = tuple(max(0, c - 28) for c in style["cloth"])
    pygame.draw.polygon(
        surface,
        cloak,
        [
            (x - 17, y - 9 + bob),
            (x + 17, y - 9 + bob),
            (x + 21 + sway, y + 27),
            (x - 20 + sway, y + 27),
        ],
    )

    # Profession-specific clothing layers.
    pygame.draw.rect(
        surface,
        style["cloth"],
        (x - 14, y - 12 + bob, 28, 35),
        border_radius=7,
    )
    pygame.draw.line(
        surface,
        style["trim"],
        (x - 13, y + 3 + bob),
        (x + 13, y + 3 + bob),
        3,
    )
    if role == "guarda":
        pygame.draw.rect(surface, (118, 131, 143), (x - 10, y - 8 + bob, 20, 18), 2)
    elif role == "ferreiro":
        pygame.draw.rect(surface, (82, 54, 37), (x - 12, y + 3 + bob, 24, 18), border_radius=3)
    elif role == "curandeira":
        pygame.draw.line(surface, style["trim"], (x, y - 8), (x, y + 16), 2)
        pygame.draw.line(surface, style["trim"], (x - 7, y + 3), (x + 7, y + 3), 2)

    _face(surface, x, y - 25 + bob, style, facing, seconds, index)
    _accessory(surface, role, x, y, style, seconds)

    pygame.draw.circle(surface, style["trim"], (x, y), 32, 1)

    if near and fonts is not None:
        role_label = role.upper()
        label = fonts["small"].render(
            f"E — {name} • {role_label}",
            True,
            (241, 245, 248),
        )
        box = label.get_rect(center=(x, y - 59)).inflate(16, 8)
        pygame.draw.rect(surface, (6, 10, 16), box, border_radius=8)
        pygame.draw.rect(surface, style["trim"], box, 1, border_radius=8)
        surface.blit(label, label.get_rect(center=box.center))


def draw_interior_resident(
    surface,
    center,
    role,
    seconds,
    name,
    fonts,
):
    draw_npc_v27(
        surface,
        center,
        role,
        pygame.Vector2(0, 1),
        seconds,
        index=2,
        near=True,
        name=name,
        fonts=fonts,
    )
