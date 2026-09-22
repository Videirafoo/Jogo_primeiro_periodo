from pathlib import Path
import pygame
import pytmx
from pytmx.util_pygame import load_pygame

ASSETS = Path(__file__).with_name("assets")


class MapScene:
    def __init__(self, chapter_number):
        self.path = ASSETS / "maps" / f"chapter_{chapter_number:02d}.tmx"
        self.available = self.path.exists()
        self.tmx = None
        self.surface = None
        self.collision_rects = []
        self.width = 1808
        self.height = 1088
        if self.available:
            self._load()

    def _load(self):
        if pygame.display.get_surface() is None:
            pygame.display.set_mode((1, 1))

        self.tmx = load_pygame(str(self.path), pixelalpha=True)
        self.width = self.tmx.width * self.tmx.tilewidth
        self.height = self.tmx.height * self.tmx.tileheight
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for layer in self.tmx.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if not gid:
                        continue
                    image = self.tmx.get_tile_image_by_gid(gid)
                    if image:
                        self.surface.blit(
                            image,
                            (x * self.tmx.tilewidth, y * self.tmx.tileheight),
                        )

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
        surface.blit(self.surface, (0, 0), source)
        return True
