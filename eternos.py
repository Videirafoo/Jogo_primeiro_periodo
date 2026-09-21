import os
import sys

import pygame

from audio import Audio
from engine import StoryEngine
from story_data import GAME
import ui


LOGICAL_SIZE = (ui.WIDTH, ui.HEIGHT)
FPS = 60


class GameApp:
    def __init__(self, headless=False):
        pygame.init()
        pygame.display.set_caption("OS ETERNOS — O Sonho de Valdrak")

        flags = 0 if headless else pygame.RESIZABLE
        self.window = pygame.display.set_mode(LOGICAL_SIZE, flags)
        self.canvas = pygame.Surface(LOGICAL_SIZE)
        self.clock = pygame.time.Clock()
        self.fonts = ui.fonts()
        self.audio = Audio()
        self.engine = StoryEngine(GAME)

        self.running = True
        self.fullscreen = False
        self.headless = headless

        self.phase = "opening"
        self.opening_index = 0
        self.scene_index = 0
        self.result_items = []
        self.result_index = 0
        self.ending = None
        self.ending_index = 0

        self.reveal = 0.0
        self.message = ""
        self.choice_rects = []
        self.continue_rect = None
        self.restart_rect = None

        self.current_sfx = ""
        self._play_current_item()

    def current_item(self):
        if self.phase == "opening":
            return GAME["opening"][self.opening_index]

        if self.phase == "chapter":
            chapter = self.engine.current_chapter
            return chapter["scene"][self.scene_index]

        if self.phase == "result":
            return self.result_items[self.result_index]

        if self.phase == "ending":
            return self.ending["text"][self.ending_index]

        return {"text": "", "sfx": ""}

    def current_text(self):
        return self.current_item().get("text", "")

    def current_title(self):
        if self.phase == "opening":
            if self.opening_index == 0:
                return "O sonho começa"
            if self.opening_index >= 12:
                return "Poder despertado"
            return "Valdrak"

        if self.phase in {"chapter", "choices", "result"}:
            chapter = self.engine.current_chapter
            return chapter["title"]

        if self.phase == "ending":
            return self.ending["title"]

        if self.phase == "finished":
            return "O sonho termina"

        return GAME["title"]

    def current_chapter_label(self):
        if self.phase == "opening":
            return "Prólogo"

        if self.phase in {"chapter", "choices", "result"}:
            chapter = self.engine.current_chapter
            return f"Capítulo {chapter['number']} de {len(GAME['chapters'])}"

        if self.phase in {"ending", "finished"}:
            return "Final"

        return ""

    def _play_current_item(self):
        item = self.current_item()
        self.current_sfx = item.get("sfx", "rune")
        self.audio.play(self.current_sfx, 0.28)
        self.reveal = 0.0

    def reveal_complete(self):
        return int(self.reveal) >= len(self.current_text())

    def update(self, dt):
        if self.phase in {"opening", "chapter", "result", "ending"}:
            self.reveal = min(
                len(self.current_text()),
                self.reveal + dt * 75,
            )

    def advance(self):
        if self.phase in {"opening", "chapter", "result", "ending"}:
            if not self.reveal_complete():
                self.reveal = float(len(self.current_text()))
                return

        if self.phase == "opening":
            if self.opening_index + 1 < len(GAME["opening"]):
                self.opening_index += 1
                self._play_current_item()
            else:
                self.phase = "chapter"
                self.scene_index = 0
                self._play_current_item()
            return

        if self.phase == "chapter":
            chapter = self.engine.current_chapter
            if self.scene_index + 1 < len(chapter["scene"]):
                self.scene_index += 1
                self._play_current_item()
            else:
                self.phase = "choices"
                self.message = ""
                self.audio.play("choice", 0.22)
            return

        if self.phase == "result":
            if self.result_index + 1 < len(self.result_items):
                self.result_index += 1
                self._play_current_item()
            else:
                self._next_chapter_or_ending()
            return

        if self.phase == "ending":
            if self.ending_index + 1 < len(self.ending["text"]):
                self.ending_index += 1
                self._play_current_item()
            else:
                self.phase = "finished"
                self.audio.play("ending_good", 0.42)

    def _next_chapter_or_ending(self):
        next_chapter = self.engine.advance_chapter()

        if next_chapter is None:
            self.ending = self.engine.choose_ending()
            self.ending_index = 0
            self.phase = "ending"
            self._play_current_item()
            return

        self.scene_index = 0
        self.phase = "chapter"
        self._play_current_item()

    def choose(self, index):
        if self.phase != "choices":
            return

        chapter = self.engine.current_chapter
        if index < 0 or index >= len(chapter["choices"]):
            return

        choice = chapter["choices"][index]
        result = self.engine.apply_choice(choice)

        if not result["ok"]:
            self.message = result["reason"]
            self.audio.play("error", 0.32)
            return

        if result["new_ally"]:
            ally = result["new_ally"]
            self.message = f"Aliado: {ally['name']} — {ally['power']}"
        elif result["new_tool"]:
            self.message = f"Tecnologia desbloqueada: {result['new_tool']}"
        else:
            self.message = ""

        self.audio.play("choice", 0.25)
        for sfx in result.get("sfx_sequence", [])[:1]:
            self.audio.play(sfx, 0.24)

        self.result_items = list(result["result"])
        self.result_index = 0

        if self.result_items:
            self.phase = "result"
            self._play_current_item()
        else:
            self._next_chapter_or_ending()

    def toggle_fullscreen(self):
        if self.headless:
            return

        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else pygame.RESIZABLE
        size = (0, 0) if self.fullscreen else LOGICAL_SIZE
        self.window = pygame.display.set_mode(size, flags)

    def restart(self):
        self.engine.reset()
        self.phase = "opening"
        self.opening_index = 0
        self.scene_index = 0
        self.result_items = []
        self.result_index = 0
        self.ending = None
        self.ending_index = 0
        self.message = ""
        self._play_current_item()

    def input_to_canvas(self, pos):
        window_w, window_h = self.window.get_size()
        scale = min(window_w / ui.WIDTH, window_h / ui.HEIGHT)
        draw_w = int(ui.WIDTH * scale)
        draw_h = int(ui.HEIGHT * scale)
        offset_x = (window_w - draw_w) // 2
        offset_y = (window_h - draw_h) // 2

        x = (pos[0] - offset_x) / max(scale, 0.001)
        y = (pos[1] - offset_y) / max(scale, 0.001)
        return int(x), int(y)

    def handle_key(self, event):
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.phase != "choices" and self.phase != "finished":
                self.advance()
            return

        if self.phase == "choices":
            if event.key in (pygame.K_1, pygame.K_KP1):
                self.choose(0)
            elif event.key in (pygame.K_2, pygame.K_KP2):
                self.choose(1)
            elif event.key in (pygame.K_3, pygame.K_KP3):
                self.choose(2)

        if event.key == pygame.K_m:
            enabled = self.audio.toggle()
            self.message = "Áudio ligado" if enabled else "Áudio desligado"

        if event.key == pygame.K_F11:
            self.toggle_fullscreen()

        if event.key == pygame.K_r and self.phase == "finished":
            self.restart()

        if event.key == pygame.K_ESCAPE:
            self.running = False

    def handle_click(self, pos):
        point = self.input_to_canvas(pos)

        if self.phase == "choices":
            for index, rect in enumerate(self.choice_rects):
                if rect.collidepoint(point):
                    self.choose(index)
                    return

        if self.phase == "finished":
            if self.restart_rect and self.restart_rect.collidepoint(point):
                self.restart()
            return

        if self.continue_rect and self.continue_rect.collidepoint(point):
            self.advance()

    def draw(self):
        seconds = pygame.time.get_ticks() / 1000
        item = self.current_item()
        key = item.get("sfx", self.current_sfx or "rune")
        accent = ui.draw_scene_background(self.canvas, key, seconds)

        ui.draw_header(
            self.canvas,
            self.fonts,
            self.current_chapter_label(),
            self.current_title(),
            accent,
        )

        if self.phase == "choices":
            self._draw_choices(accent)
        elif self.phase == "finished":
            self._draw_finished(accent)
        else:
            self._draw_narration(accent)

        self._draw_footer(accent)
        self._present()

    def _draw_narration(self, accent):
        full = self.current_text()
        visible = full[: int(self.reveal)]

        title_map = {
            "opening": "NARRATIVA",
            "chapter": "CENA",
            "result": "CONSEQUÊNCIA",
            "ending": "DESFECHO",
        }
        label = title_map.get(self.phase, "VALDRAK")

        ui.draw_story_panel(
            self.canvas,
            self.fonts,
            label,
            visible,
            accent,
        )

        ui.draw_status(
            self.canvas,
            self.fonts,
            self.engine.status_snapshot(),
            self.engine.ally_names(),
            self.engine.state["tools"],
            accent,
        )

        self.continue_rect = ui.draw_continue(
            self.canvas,
            self.fonts,
            accent,
            "REVELAR" if not self.reveal_complete() else "CONTINUAR",
        )
        self.choice_rects = []
        self.restart_rect = None

    def _draw_choices(self, accent):
        chapter = self.engine.current_chapter

        ui.text(
            self.canvas,
            "ESCOLHA SEU CAMINHO",
            self.fonts["small"],
            accent,
            (58, 178),
        )
        ui.text(
            self.canvas,
            "Cada decisão altera atributos, aliados, tecnologia e o final.",
            self.fonts["body"],
            ui.INK,
            (58, 205),
        )

        self.choice_rects = []
        mouse = self.input_to_canvas(pygame.mouse.get_pos())

        base_y = 252
        for index, choice in enumerate(chapter["choices"]):
            rect = pygame.Rect(58, base_y + index * 104, 820, 88)
            visual_choice = dict(choice)
            visual_choice["_number"] = str(index + 1)

            available = self.engine.choice_available(choice)
            reason = self.engine.availability_reason(choice)

            ui.draw_choice(
                self.canvas,
                self.fonts,
                visual_choice,
                rect,
                accent,
                mouse,
                locked=not available,
                reason=reason,
            )
            self.choice_rects.append(rect)

        ui.draw_status(
            self.canvas,
            self.fonts,
            self.engine.status_snapshot(),
            self.engine.ally_names(),
            self.engine.state["tools"],
            accent,
        )

        if self.message:
            ui.text(
                self.canvas,
                self.message,
                self.fonts["small"],
                ui.GOLD,
                (58, 650),
            )

        self.continue_rect = None
        self.restart_rect = None

    def _draw_finished(self, accent):
        rect = pygame.Rect(175, 205, 930, 360)
        ui.rounded_panel(
            self.canvas,
            rect,
            (10, 18, 29),
            accent,
            24,
        )

        ui.text(
            self.canvas,
            "FIM",
            self.fonts["hero"],
            accent,
            (640, 260),
            "center",
        )
        ui.text(
            self.canvas,
            self.ending["title"],
            self.fonts["title"],
            ui.INK,
            (640, 326),
            "center",
        )

        allies = ", ".join(self.engine.ally_names()) or "Nenhum"
        tools = ", ".join(self.engine.state["tools"]) or "Nenhuma"

        ui.text(
            self.canvas,
            f"Aliados encontrados: {allies}",
            self.fonts["body"],
            ui.MUTED,
            (640, 385),
            "center",
        )
        ui.text(
            self.canvas,
            f"Tecnologia: {tools}",
            self.fonts["small"],
            ui.MUTED,
            (640, 424),
            "center",
        )

        self.restart_rect = pygame.Rect(490, 485, 300, 58)
        pygame.draw.rect(
            self.canvas,
            accent,
            self.restart_rect,
            border_radius=16,
        )
        ui.text(
            self.canvas,
            "SONHAR NOVAMENTE",
            self.fonts["button"],
            ui.DARK,
            self.restart_rect.center,
            "center",
        )

        self.continue_rect = None
        self.choice_rects = []

    def _draw_footer(self, accent):
        if self.phase == "opening":
            current = self.opening_index + 1
            total = len(GAME["opening"])
        elif self.phase in {"chapter", "choices", "result"}:
            current = self.engine.chapter_index + 1
            total = len(GAME["chapters"])
        else:
            current = len(GAME["chapters"])
            total = len(GAME["chapters"])

        ui.draw_progress(
            self.canvas,
            self.fonts,
            current,
            total,
            accent,
        )

        help_text = "ENTER/ESPAÇO continuar • 1/2/3 escolher • M áudio • F11 tela cheia • ESC sair"
        ui.text(
            self.canvas,
            help_text,
            self.fonts["small"],
            ui.MUTED,
            (58, 653),
        )

    def _present(self):
        window_w, window_h = self.window.get_size()
        scale = min(window_w / ui.WIDTH, window_h / ui.HEIGHT)
        draw_size = (
            max(1, int(ui.WIDTH * scale)),
            max(1, int(ui.HEIGHT * scale)),
        )
        frame = pygame.transform.smoothscale(self.canvas, draw_size)

        self.window.fill((0, 0, 0))
        x = (window_w - draw_size[0]) // 2
        y = (window_h - draw_size[1]) // 2
        self.window.blit(frame, (x, y))
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

            self.update(dt)
            self.draw()

        pygame.quit()


def smoke():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    app = GameApp(headless=True)
    rendered = 0

    for index in range(len(GAME["opening"])):
        app.phase = "opening"
        app.opening_index = index
        app.reveal = float(len(app.current_text()))
        app.draw()
        rendered += 1

    app.phase = "chapter"
    app.engine.chapter_index = 0

    while app.engine.current_chapter is not None:
        chapter = app.engine.current_chapter

        for index in range(len(chapter["scene"])):
            app.phase = "chapter"
            app.scene_index = index
            app.reveal = float(len(app.current_text()))
            app.draw()
            rendered += 1

        app.phase = "choices"
        app.draw()
        rendered += 1

        available = app.engine.available_choices()
        if not available:
            raise RuntimeError(
                f"Capítulo {chapter['number']} sem escolhas disponíveis."
            )

        first = chapter["choices"].index(available[0])
        app.choose(first)

        if app.phase == "result":
            for index in range(len(app.result_items)):
                app.result_index = index
                app.reveal = float(len(app.current_text()))
                app.draw()
                rendered += 1

            app._next_chapter_or_ending()

    if app.phase != "ending":
        app.ending = app.engine.choose_ending()
        app.ending_index = 0
        app.phase = "ending"

    for index in range(len(app.ending["text"])):
        app.ending_index = index
        app.reveal = float(len(app.current_text()))
        app.draw()
        rendered += 1

    app.phase = "finished"
    app.draw()
    rendered += 1

    pygame.quit()
    print(
        "Smoke OS ETERNOS concluído com sucesso. "
        f"{rendered} telas renderizadas."
    )


def main():
    GameApp().run()


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        smoke()
    else:
        main()
