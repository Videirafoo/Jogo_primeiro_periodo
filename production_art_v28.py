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
