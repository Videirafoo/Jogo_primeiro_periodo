from pathlib import Path
import math
import pygame

SHEET_PATH = (
    Path(__file__).with_name("assets")
    / "kenney"
    / "characters"
    / "characters.png"
)

TILE_SIZE = 16
SPACING = 1
COLUMNS = 54

ROLE_INDEX = {
    "player": 0,
    "Thorvald": 1,
    "Aurel": 2,
    "Kaion": 3,
    "Brenor": 4,
    "Eiran": 5,
    "Noctar": 6,
    "wolf": 114,
    "raider": 165,
    "raven": 218,
}


class SpriteLibrary:
    def __init__(self):
        self.sheet = None
        self.cache = {}

    def _ensure(self):
        if self.sheet is None and SHEET_PATH.exists():
            self.sheet = pygame.image.load(str(SHEET_PATH)).convert_alpha()

    def tile(self, index):
        self._ensure()
        if self.sheet is None:
            return None
        if index in self.cache:
            return self.cache[index].copy()

        col = index % COLUMNS
        row = index // COLUMNS
        rect = pygame.Rect(
            col * (TILE_SIZE + SPACING),
            row * (TILE_SIZE + SPACING),
            TILE_SIZE,
            TILE_SIZE,
        )
        image = self.sheet.subsurface(rect).copy()
        self.cache[index] = image
        return image.copy()


LIBRARY = SpriteLibrary()


def draw_actor(
    surface,
    role,
    center,
    state="idle",
    facing=None,
    seconds=0.0,
    boss=False,
    tint=None,
):
    image = LIBRARY.tile(ROLE_INDEX.get(role, 0))
    if image is None:
        return False

    scale = 4 if boss else 3
    size = TILE_SIZE * scale
    image = pygame.transform.scale(image, (size, size))

    if facing is not None and getattr(facing, "x", 0) < -0.15:
        image = pygame.transform.flip(image, True, False)

    bob = 0
    if state == "walk":
        phase = math.sin(seconds * 12)
        bob = int(phase * 3)
        squeeze = 2 + int(abs(phase) * 2)
        image = pygame.transform.scale(
            image,
            (size + squeeze, size - squeeze),
        )
    elif state == "attack":
        image = pygame.transform.rotate(image, -8)
    elif state == "dash":
        image.set_alpha(205)
    elif state == "hurt":
        overlay = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        overlay.fill((120, 20, 20, 60))
        image.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    if tint:
        overlay = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        overlay.fill((*tint[:3], 28))
        image.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    rect = image.get_rect(
        center=(int(center[0]), int(center[1] + bob))
    )

    shadow = pygame.Surface(
        (int(rect.width * 0.65), 16),
        pygame.SRCALPHA,
    )
    pygame.draw.ellipse(shadow, (0, 0, 0, 95), shadow.get_rect())
    surface.blit(
        shadow,
        shadow.get_rect(center=(rect.centerx, rect.bottom - 2)),
    )
    surface.blit(image, rect)
    return True
