import math
import textwrap

import pygame


WIDTH = 1280
HEIGHT = 720

INK = (236, 242, 248)
MUTED = (160, 174, 190)
DARK = (8, 13, 22)
PANEL = (15, 24, 38)
PANEL_2 = (24, 36, 54)
CYAN = (74, 222, 232)
BLUE = (81, 127, 255)
GOLD = (231, 190, 93)
RED = (235, 94, 105)
GREEN = (90, 210, 142)
VIOLET = (158, 116, 255)
LOCKED = (88, 100, 116)


def fonts():
    return {
        "hero": pygame.font.SysFont("georgia", 48, bold=True),
        "title": pygame.font.SysFont("georgia", 30, bold=True),
        "heading": pygame.font.SysFont("segoeui", 23, bold=True),
        "body": pygame.font.SysFont("segoeui", 20),
        "small": pygame.font.SysFont("segoeui", 15),
        "button": pygame.font.SysFont("segoeui", 17, bold=True),
        "stat": pygame.font.SysFont("consolas", 15, bold=True),
    }


def lerp(a, b, amount):
    return int(a + (b - a) * amount)


def gradient(surface, top, bottom):
    height = surface.get_height()
    width = surface.get_width()
    for y in range(height):
        amount = y / max(1, height - 1)
        color = (
            lerp(top[0], bottom[0], amount),
            lerp(top[1], bottom[1], amount),
            lerp(top[2], bottom[2], amount),
        )
        pygame.draw.line(surface, color, (0, y), (width, y))


def scene_palette(key):
    palettes = {
        "rain": ((15, 28, 43), (5, 12, 20), CYAN),
        "wind": ((20, 34, 50), (7, 14, 23), (138, 183, 214)),
        "horse": ((39, 31, 28), (12, 13, 18), GOLD),
        "sword": ((40, 43, 51), (10, 13, 20), (198, 211, 225)),
        "axe_whoosh": ((41, 36, 44), (12, 12, 20), RED),
        "axe_hit": ((55, 35, 26), (14, 12, 15), RED),
        "crow": ((26, 24, 40), (6, 8, 15), VIOLET),
        "thunder": ((26, 35, 62), (6, 9, 20), (170, 194, 255)),
        "lightning": ((35, 43, 72), (7, 11, 21), (205, 220, 255)),
        "gate": ((43, 35, 29), (10, 11, 16), GOLD),
        "tech": ((6, 40, 48), (5, 13, 22), CYAN),
        "scanner": ((7, 38, 53), (5, 13, 23), CYAN),
        "rune": ((33, 24, 54), (7, 9, 18), VIOLET),
        "runes": ((33, 24, 54), (7, 9, 18), VIOLET),
        "portal": ((41, 25, 68), (6, 9, 19), (177, 122, 255)),
        "fire": ((63, 29, 20), (18, 10, 12), (255, 146, 76)),
        "forge": ((57, 28, 21), (17, 10, 12), (255, 151, 78)),
        "heal": ((20, 54, 48), (7, 15, 19), GREEN),
        "shadow": ((24, 18, 38), (5, 7, 13), VIOLET),
        "wolf": ((34, 40, 48), (8, 11, 17), (189, 208, 222)),
        "wake": ((52, 54, 66), (12, 16, 25), GOLD),
        "ending_good": ((20, 50, 45), (5, 13, 19), GREEN),
        "victory": ((20, 50, 45), (5, 13, 19), GREEN),
    }
    return palettes.get(key, ((18, 30, 47), (6, 11, 18), CYAN))


def draw_scene_background(surface, key, seconds):
    top, bottom, accent = scene_palette(key)
    gradient(surface, top, bottom)

    horizon = 440
    pygame.draw.polygon(
        surface,
        (7, 12, 18),
        [(0, horizon), (180, 300), (330, 410), (520, 255),
         (720, 405), (900, 285), (1110, 410), (1280, 320),
         (1280, 720), (0, 720)],
    )

    for index in range(12):
        x = 30 + index * 115
        sway = math.sin(seconds * 0.7 + index) * 4
        base_y = 525 + (index % 3) * 18
        pygame.draw.polygon(
            surface,
            (10, 20, 26),
            [(x + sway, base_y - 145),
             (x - 45 + sway, base_y - 25),
             (x + 45 + sway, base_y - 25)],
        )
        pygame.draw.rect(
            surface,
            (17, 23, 26),
            (x - 5 + sway, base_y - 30, 10, 85),
        )

    glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pulse = int(38 + 18 * (math.sin(seconds * 1.3) + 1) / 2)
    pygame.draw.circle(glow, (*accent, pulse), (1025, 205), 150)
    pygame.draw.circle(glow, (*accent, max(10, pulse // 3)), (1025, 205), 235)
    surface.blit(glow, (0, 0))

    for index in range(18):
        angle = seconds * 0.22 + index * (math.pi * 2 / 18)
        radius = 92 + (index % 4) * 18
        x = 1025 + math.cos(angle) * radius
        y = 205 + math.sin(angle) * radius * 0.55
        pygame.draw.circle(surface, accent, (int(x), int(y)), 2)

    if key == "rain":
        for index in range(34):
            x = (index * 83 + int(seconds * 170)) % WIDTH
            y = (index * 47 + int(seconds * 250)) % 470
            pygame.draw.line(surface, (120, 165, 190), (x, y), (x - 12, y + 28), 1)

    if key in {"fire", "forge"}:
        for index in range(24):
            x = 80 + ((index * 137 + int(seconds * 90)) % 1080)
            y = 560 - ((index * 71 + int(seconds * 130)) % 260)
            radius = 2 + index % 3
            pygame.draw.circle(surface, accent, (x, y), radius)

    if key in {"tech", "scanner", "rune", "runes", "portal"}:
        for index in range(5):
            radius = 35 + index * 28 + int((seconds * 18) % 24)
            pygame.draw.circle(surface, accent, (1025, 205), radius, 1)

        for index in range(8):
            x = 760 + index * 55
            y = 315 + int(math.sin(seconds * 1.5 + index) * 18)
            pygame.draw.line(surface, accent, (x, y), (x + 24, y - 18), 2)
            pygame.draw.line(surface, accent, (x + 24, y - 18), (x + 35, y + 8), 2)

    if key in {"thunder", "lightning"}:
        flash = math.sin(seconds * 7.5)
        if flash > 0.88:
            bolt = [(1080, 60), (1020, 155), (1060, 155), (990, 285)]
            pygame.draw.lines(surface, (225, 235, 255), False, bolt, 5)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (3, 7, 13, 90), (0, 0, WIDTH, HEIGHT))
    surface.blit(overlay, (0, 0))
    return accent


def text(surface, value, font, color, position, anchor="topleft"):
    rendered = font.render(str(value), True, color)
    rect = rendered.get_rect()
    setattr(rect, anchor, position)
    surface.blit(rendered, rect)
    return rect


def wrap(value, font, max_width):
    words = str(value).split()
    lines = []
    current = ""

    for word in words:
        attempt = word if not current else f"{current} {word}"
        if font.size(attempt)[0] <= max_width:
            current = attempt
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)
    return lines


def draw_wrapped(surface, value, font, color, x, y, width, line_height=None):
    line_height = line_height or font.get_linesize() + 5
    cursor = y

    for paragraph in str(value).split("\n"):
        if not paragraph:
            cursor += line_height
            continue

        for line in wrap(paragraph, font, width):
            text(surface, line, font, color, (x, cursor))
            cursor += line_height

    return cursor


def rounded_panel(surface, rect, fill=PANEL, border=(67, 82, 102), radius=18):
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    pygame.draw.rect(surface, border, rect, width=1, border_radius=radius)


def draw_header(surface, fs, chapter_label, title, accent):
    text(surface, "OS ETERNOS", fs["heading"], accent, (54, 35))
    text(surface, "O SONHO DE VALDRAK", fs["small"], MUTED, (54, 68))
    if chapter_label:
        text(surface, chapter_label.upper(), fs["small"], GOLD, (1220, 38), "topright")
    if title:
        text(surface, title, fs["title"], INK, (54, 105))
    pygame.draw.line(surface, (*accent,), (54, 150), (1226, 150), 1)


def draw_story_panel(surface, fs, title, body, accent):
    rect = pygame.Rect(58, 375, 820, 285)
    shadow = rect.move(0, 8)
    pygame.draw.rect(surface, (0, 0, 0, 75), shadow, border_radius=22)
    rounded_panel(surface, rect, (12, 20, 31), (*accent,), 22)

    text(surface, title.upper(), fs["small"], accent, (88, 402))
    y = draw_wrapped(
        surface,
        body,
        fs["body"],
        INK,
        88,
        438,
        750,
        31,
    )
    return rect, y


def draw_continue(surface, fs, accent, label="CONTINUAR"):
    rect = pygame.Rect(985, 598, 235, 54)
    pygame.draw.rect(surface, accent, rect, border_radius=15)
    text(surface, label, fs["button"], DARK, rect.center, "center")
    return rect


def draw_choice(surface, fs, choice, rect, accent, mouse, locked=False, reason=""):
    hovered = rect.collidepoint(mouse) and not locked
    fill = PANEL_2 if not hovered else (34, 53, 75)
    border = LOCKED if locked else accent

    rounded_panel(surface, rect, fill, border, 16)

    number = choice.get("_number", "")
    if number:
        text(
            surface,
            number,
            fs["heading"],
            LOCKED if locked else accent,
            (rect.x + 22, rect.y + 18),
        )

    x = rect.x + (65 if number else 22)
    color = LOCKED if locked else INK
    lines = wrap(choice["text"], fs["button"], rect.width - (x - rect.x) - 24)

    for idx, line in enumerate(lines[:2]):
        text(surface, line, fs["button"], color, (x, rect.y + 16 + idx * 23))

    if locked and reason:
        text(surface, reason, fs["small"], LOCKED, (x, rect.bottom - 25))


def draw_status(surface, fs, status, allies, tools, accent):
    rect = pygame.Rect(918, 175, 305, 390)
    rounded_panel(surface, rect, (10, 18, 29), (55, 70, 89), 20)
    text(surface, "STATUS DO SONHO", fs["small"], accent, (944, 200))

    labels = [
        ("COR", "coragem"),
        ("SAB", "sabedoria"),
        ("TEC", "tecnologia"),
        ("AMZ", "amizade"),
        ("CAO", "caos"),
        ("MAR", "marcas"),
    ]

    for index, (label, key) in enumerate(labels):
        y = 240 + index * 40
        value = max(0, status.get(key, 0))
        text(surface, label, fs["stat"], MUTED, (944, y))
        text(surface, str(value), fs["stat"], INK, (1193, y), "topright")
        pygame.draw.rect(surface, (33, 43, 57), (985, y + 3, 185, 10), border_radius=5)
        width = min(185, int(185 * min(value, 15) / 15))
        pygame.draw.rect(surface, accent, (985, y + 3, width, 10), border_radius=5)

    text(surface, "ALIADOS", fs["small"], GOLD, (944, 495))
    ally_text = ", ".join(allies) if allies else "Ainda nenhum"
    draw_wrapped(surface, ally_text, fs["small"], INK, 944, 518, 245, 20)

    text(surface, "TECNOLOGIA", fs["small"], CYAN, (944, 552))
    tool_text = ", ".join(tools) if tools else "Poder despertando..."
    draw_wrapped(surface, tool_text, fs["small"], INK, 944, 575, 245, 19)


def draw_progress(surface, fs, current, total, accent):
    pygame.draw.rect(surface, (31, 43, 57), (58, 682, 1164, 6), border_radius=3)
    progress = 0 if total <= 0 else current / total
    width = int(1164 * max(0.0, min(1.0, progress)))
    pygame.draw.rect(surface, accent, (58, 682, width, 6), border_radius=3)
    text(
        surface,
        f"{current}/{total}",
        fs["small"],
        MUTED,
        (1220, 657),
        "topright",
    )
