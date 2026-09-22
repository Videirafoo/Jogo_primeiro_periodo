from pathlib import Path
import pygame
import pytmx
from pytmx.util_pygame import load_pygame

ASSETS = Path(__file__).with_name("assets")

REGION_TINTS = {
    1: (112, 132, 112),
    2: (126, 124, 116),
    3: (148, 118, 102),
    4: (98, 128, 101),
    5: (150, 160, 168),
    6: (145, 105, 91),
    7: (116, 102, 148),
}


class MapScene:
    def __init__(self, chapter_number):
        self.chapter_number = chapter_number
        self.path = ASSETS / "maps" / f"chapter_{chapter_number:02d}.tmx"
        self.available = self.path.exists()
        self.tmx = None
        self.surface = None
        self.collision_rects = []
        self.width = 1800
        self.height = 1080
        if self.available:
            self._load()

    def _load(self):
        if pygame.display.get_surface() is None:
            pygame.display.set_mode((1, 1))

        self.tmx = load_pygame(str(self.path), pixelalpha=True)
        self.width = self.tmx.width * self.tmx.tilewidth
        self.height = self.tmx.height * self.tmx.tileheight
        self.surface = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA,
        )

        target_size = (
            self.tmx.tilewidth,
            self.tmx.tileheight,
        )

        for layer in self.tmx.visible_layers:
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue

            for x, y, gid in layer:
                if not gid:
                    continue

                image = self.tmx.get_tile_image_by_gid(gid)
                if image is None:
                    continue

                if image.get_size() != target_size:
                    image = pygame.transform.scale(
                        image,
                        target_size,
                    )

                self.surface.blit(
                    image,
                    (
                        x * self.tmx.tilewidth,
                        y * self.tmx.tileheight,
                    ),
                )

        tint = pygame.Surface(
            self.surface.get_size()
        )
        tint.fill(
            REGION_TINTS.get(
                self.chapter_number,
                (135, 135, 135),
            )
        )
        self.surface.blit(
            tint,
            (0, 0),
            special_flags=pygame.BLEND_RGB_MULT,
        )

        shade = pygame.Surface(
            self.surface.get_size(),
            pygame.SRCALPHA,
        )
        shade.fill((8, 14, 20, 34))
        self.surface.blit(shade, (0, 0))

        for group in self.tmx.objectgroups:
            if group.name != "collision":
                continue

            for obj in group:
                self.collision_rects.append(
                    pygame.Rect(
                        int(obj.x),
                        int(obj.y),
                        int(obj.width),
                        int(obj.height),
                    )
                )

    def draw(self, surface, camera):
        if self.surface is None:
            return False

        source = pygame.Rect(
            int(camera.x),
            int(camera.y),
            surface.get_width(),
            surface.get_height(),
        )
        surface.blit(
            self.surface,
            (0, 0),
            source,
        )
        return True
