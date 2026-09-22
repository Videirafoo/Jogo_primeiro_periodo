import pygame


class CinematicDirector:
    def __init__(self, region, profile):
        self.region = region
        self.profile = profile
        self.profile.setdefault("v26_cinematics", [])
        self.active = False
        self.timer = 0.0
        self.duration = 0.0
        self.title = ""
        self.subtitle = ""
        self.kind = "region"
        intro_id = f"region_{region}"
        if intro_id not in self.profile["v26_cinematics"]:
            self.profile["v26_cinematics"].append(intro_id)
            self.start(
                f"REGIÃO {region}",
                "Valdrak muda conforme suas escolhas.",
                duration=3.0,
                kind="region",
            )

    def start(self, title, subtitle, duration=2.8, kind="event"):
        self.active = True
        self.timer = duration
        self.duration = duration
        self.title = str(title)
        self.subtitle = str(subtitle)
        self.kind = kind

    def update(self, dt):
        if not self.active:
            return
        self.timer = max(0.0, self.timer - dt)
        if self.timer <= 0:
            self.active = False

    def draw(self, surface, fonts, accent):
        if not self.active:
            return
        progress = 1.0 - self.timer / max(0.01, self.duration)
        fade_in = min(1.0, progress / 0.18)
        fade_out = min(1.0, self.timer / 0.45)
        alpha = int(255 * min(fade_in, fade_out))

        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, int(alpha * 0.82)), (0, 0, 1280, 64))
        pygame.draw.rect(overlay, (0, 0, 0, int(alpha * 0.82)), (0, 656, 1280, 64))
        overlay.fill((0, 0, 0, int(alpha * 0.08)), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(overlay, (0, 0))

        title = fonts["title"].render(self.title, True, accent)
        subtitle = fonts["body"].render(self.subtitle, True, (226, 232, 238))
        title.set_alpha(alpha)
        subtitle.set_alpha(alpha)
        surface.blit(title, title.get_rect(center=(640, 115)))
        surface.blit(subtitle, subtitle.get_rect(center=(640, 155)))
