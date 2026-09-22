import os
import sys

import pygame

from audio import Audio
from engine import StoryEngine
from ending_gallery import EndingGallery
from gameplay import Challenge
from pause_menu import PauseMenu
from rpg_world import RPGWorld
from savegame import load_game, save_game, slot_path
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
        self.gallery = EndingGallery(
            GAME["endings"]
        )

        self.running = True
        self.fullscreen = False
        self.headless = headless
        self.paused = False
        self.pause_menu = PauseMenu()
        self.current_save_slot = 1

        self.phase = "opening"
        self.opening_index = 0
        self.scene_index = 0
        self.result_items = []
        self.result_index = 0
        self.ending = None
        self.ending_index = 0
        self.challenge = None
        self.challenge_context = None
        self.pending_choice_result = None
        self.prologue_action_done = False
        self.world = None
        self.rpg_profile = {
            "level": 1,
            "xp": 0,
            "xp_next": 4,
            "max_health": 100,
            "health": 100,
            "max_energy": 100,
            "energy": 100,
            "kills": 0,
        }

        self.reveal = 0.0
        self.message = ""
        self.choice_rects = []
        self.continue_rect = None
        self.restart_rect = None

        self.current_sfx = ""
        self.transition_alpha = 210
        self._start_exploration()
        if self.world:
            opening = GAME["opening"][0].get(
                "text",
                "Fui dormir num dia comum.",
            )
            self.world.start_story_echo(
                "O SONHO COMEÇA",
                opening
                + " Quando abri os olhos, eu já podia caminhar por Valdrak.",
            )

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

        if self.phase == "challenge" and self.challenge_context == "prologue":
            return "Primeiro perigo"

        if self.phase == "explore" and self.engine.current_chapter:
            return f"Explore — {self.engine.current_chapter['title']}"

        if self.phase in {"chapter", "choices", "challenge", "result"}:
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

        if self.phase == "challenge" and self.challenge_context == "prologue":
            return "Prólogo"

        if self.phase == "explore" and self.engine.current_chapter:
            chapter = self.engine.current_chapter
            return f"Capítulo {chapter['number']} de {len(GAME['chapters'])}"

        if self.phase in {"chapter", "choices", "challenge", "result"}:
            chapter = self.engine.current_chapter
            return f"Capítulo {chapter['number']} de {len(GAME['chapters'])}"

        if self.phase in {"ending", "finished"}:
            return "Final"

        return ""

    def _play_current_item(self):
        item = self.current_item()
        self.current_sfx = item.get("sfx", "rune")
        self.audio.set_ambience(self.current_sfx)
        self.audio.play(self.current_sfx, 0.56)
        self.reveal = 0.0
        self.transition_alpha = 180

    def reveal_complete(self):
        return int(self.reveal) >= len(self.current_text())

    def update(self, dt):
        if self.paused:
            return

        if self.transition_alpha > 0:
            self.transition_alpha = max(
                0,
                self.transition_alpha - int(dt * 520),
            )

        if self.phase == "explore" and self.world:
            self.world.update(dt, pygame.key.get_pressed())

            for event_name in self.world.pop_events():
                self.audio.play(event_name, 0.58)

            if self.world.music_state != self.world.last_music_state:
                self.audio.set_ambience(
                    self.world.music_state,
                    direct=True,
                )
                self.world.last_music_state = self.world.music_state

            if self.world.requested_travel_chapter is not None:
                target = self.world.requested_travel_chapter
                self.engine.chapter_index = target - 1
                self._start_exploration()
                if self.world:
                    self.world.notice = (
                        f"Fast Travel concluído • Região {target}"
                    )
                    self.world.notice_timer = 2.8
                return

            if self.world.selected_choice is not None:
                index = self.world.selected_choice
                reward = self.world.apply_rewards()
                self.world = None
                self.phase = "choices"
                if reward:
                    self.message = reward
                self.choose(index)
            return

        if self.phase == "challenge" and self.challenge:
            self.challenge.update(dt, pygame.key.get_pressed())
            for event_name in self.challenge.pop_events():
                self.audio.play(event_name, 0.58)
            return

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
            if self.opening_index == 6 and not self.prologue_action_done:
                self._start_prologue_challenge()
                return

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
                self._start_exploration()
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
        self.message = ""
        next_chapter = self.engine.advance_chapter()

        if next_chapter is None:
            self.ending = self.engine.choose_ending()
            self.gallery.unlock(
                self.ending.get("id")
            )
            self.ending_index = 0
            self.phase = "ending"
            self._play_current_item()
            return

        self.scene_index = 0
        self._start_exploration()
        if self.world:
            self.world.start_story_echo()

    def _start_exploration(self):
        chapter = self.engine.current_chapter
        if chapter is None:
            return

        self.world = RPGWorld(
            chapter,
            self.engine,
            self.rpg_profile,
        )
        self.phase = "explore"
        self.message = ""
        self.transition_alpha = 170
        self.audio.set_ambience(
            self.world.theme["ambience"],
            direct=True,
        )
        self.audio.play("rune", 0.38)
        self.quick_save(silent=True)

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

        self.audio.play("choice", 0.50)
        sequence = result.get("sfx_sequence", [])
        if sequence:
            self.audio.play(sequence[0], 0.58)

        self.pending_choice_result = result
        self.challenge = Challenge(chapter["number"])
        self.challenge_context = "choice"
        self.phase = "challenge"
        self.transition_alpha = 165

        ambience = {
            1: "rain",
            2: "wind",
            3: "fire",
            4: "forest",
            5: "wind",
            6: "fire",
            7: "portalhum",
        }.get(chapter["number"], "wind")
        self.audio.set_ambience(ambience, direct=True)

    def _start_prologue_challenge(self):
        self.challenge = Challenge(0)
        self.challenge_context = "prologue"
        self.pending_choice_result = None
        self.phase = "challenge"
        self.transition_alpha = 165
        self.message = "Desvie do machado para continuar vivo."
        self.audio.set_ambience("rain", direct=True)
        self.audio.play("axe_whoosh", 0.62)

    def _finish_challenge(self):
        if not self.challenge:
            return

        if self.challenge_context == "prologue":
            if self.challenge.success:
                self.engine.state["coragem"] = self.engine.state.get("coragem", 0) + 1
                self.message = "Você desviou a tempo • +1 Coragem"
            else:
                self.engine.state["caos"] = self.engine.state.get("caos", 0) + 1
                self.message = "O machado passou perto demais • +1 Caos"

            self.prologue_action_done = True
            self.challenge = None
            self.challenge_context = None
            self.phase = "opening"

            if self.opening_index + 1 < len(GAME["opening"]):
                self.opening_index += 1
                self._play_current_item()
            return

        if not self.pending_choice_result:
            return

        if self.challenge.success:
            bonus_key = {
                1: "tecnologia",
                2: "tecnologia",
                3: "coragem",
                4: "sabedoria",
                5: "coragem",
                6: "tecnologia",
                7: "sabedoria",
            }.get(self.engine.current_chapter["number"], "coragem")

            self.engine.state[bonus_key] = self.engine.state.get(bonus_key, 0) + 1
            bonus_name = {
                "coragem": "Coragem",
                "sabedoria": "Sabedoria",
                "tecnologia": "Tecnologia",
            }[bonus_key]
            challenge_message = f"Desafio superado • +1 {bonus_name}"
        else:
            self.engine.state["caos"] = self.engine.state.get("caos", 0) + 1
            challenge_message = "Desafio falhou • +1 Caos"

        unlock_message = self.message
        self.message = (
            f"{challenge_message} • {unlock_message}"
            if unlock_message
            else challenge_message
        )

        result = self.pending_choice_result
        self.result_items = list(result["result"])
        self.result_index = 0
        self.pending_choice_result = None
        self.challenge = None
        self.challenge_context = None

        if self.result_items:
            self.phase = "result"
            self._play_current_item()
        else:
            self._next_chapter_or_ending()

    def quick_save(self, silent=False):
        saved = save_game(
            self.engine,
            self.rpg_profile,
            self.phase,
            self.opening_index,
            self.scene_index,
            path=slot_path(self.current_save_slot),
        )

        if not silent:
            self.message = (
                "Jogo salvo"
                if saved
                else "Não foi possível salvar"
            )

        return saved

    def quick_load(self):
        data = load_game(
            path=slot_path(self.current_save_slot)
        )
        if data is None:
            self.message = "Nenhum save válido encontrado"
            self.audio.play("error", 0.42)
            return False

        engine_data = data["engine"]
        self.engine.state = engine_data["state"]
        self.engine.allies = list(engine_data["allies"])
        self.engine.history = list(engine_data["history"])
        self.engine.chapter_index = engine_data["chapter_index"]
        self.rpg_profile = dict(data["rpg_profile"])

        self.opening_index = data.get("opening_index", 0)
        self.scene_index = data.get("scene_index", 0)
        self.challenge = None
        self.challenge_context = None
        self.pending_choice_result = None
        self.world = None
        self.result_items = []
        self.result_index = 0
        self.ending = None
        self.ending_index = 0

        resume_phase = data.get("resume_phase", "chapter")

        if resume_phase == "explore" and self.engine.current_chapter:
            self._start_exploration()
        elif resume_phase == "opening":
            self.phase = "opening"
            self._play_current_item()
        else:
            self.phase = "chapter"
            self.scene_index = 0
            self._play_current_item()

        self.message = "Save carregado"
        self.audio.play("wake", 0.42)
        return True

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
        self.challenge = None
        self.challenge_context = None
        self.pending_choice_result = None
        self.prologue_action_done = False
        self.world = None
        self.rpg_profile = {
            "level": 1,
            "xp": 0,
            "xp_next": 4,
            "max_health": 100,
            "health": 100,
            "max_energy": 100,
            "energy": 100,
            "kills": 0,
        }
        self.message = ""
        self._start_exploration()
        if self.world:
            opening = GAME["opening"][0].get(
                "text",
                "Fui dormir num dia comum.",
            )
            self.world.start_story_echo(
                "O SONHO COMEÇA",
                opening
                + " Quando abri os olhos, eu já podia caminhar por Valdrak.",
            )

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

    def _handle_pause_action(self, action):
        if action is None:
            return
        if action == "resume":
            self.paused = False
            self.pause_menu.reset()
            return
        if action == "save":
            self.quick_save()
            return
        if action == "load":
            self.quick_load()
            return
        if action == "inventory":
            if self.world:
                self.world.inventory_open = True
                self.paused = False
                self.pause_menu.reset()
            else:
                self.message = "Inventário disponível durante a exploração"
            return
        if action == "audio":
            enabled = self.audio.toggle()
            self.message = "Áudio ligado" if enabled else "Áudio desligado"
            return
        if action == "quit":
            self.running = False

    def handle_key(self, event):
        if self.paused:
            action = self.pause_menu.handle_key(event)
            self._handle_pause_action(action)
            return

        if event.key == pygame.K_ESCAPE:
            if self.phase == "explore" and self.world:
                if (
                    self.world.overlay_screen
                    or self.world.living.interior
                    or self.world.world_v27.interior
                    or self.world.dungeon_v28.active
                    or self.world.adventure_v28.current_site
                    or self.world.inventory_open
                ):
                    self.world.handle_key(event)
                    return
            self.paused = True
            self.pause_menu.reset()
            return

        if event.key == pygame.K_v:
            enabled = self.audio.toggle()
            self.message = "Áudio ligado" if enabled else "Áudio desligado"
            return

        if event.key == pygame.K_F11:
            self.toggle_fullscreen()
            return

        if event.key == pygame.K_F6:
            self.current_save_slot = (
                self.current_save_slot % 3
            ) + 1
            self.rpg_profile[
                "current_save_slot"
            ] = self.current_save_slot
            self.message = (
                f"Slot de save: {self.current_save_slot}"
            )
            if self.world:
                self.world.notice = self.message
                self.world.notice_timer = 1.8
            return

        if event.key == pygame.K_F5:
            self.quick_save()
            if self.world:
                self.world.notice = self.message
                self.world.notice_timer = 1.8
            return

        if event.key == pygame.K_F9:
            self.quick_load()
            if self.world:
                self.world.notice = self.message
                self.world.notice_timer = 1.8
            return

        if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            volume = self.audio.adjust_volume(-0.10)
            self.message = f"Volume {int(volume * 100)}%"
            if self.world:
                self.world.notice = self.message
                self.world.notice_timer = 1.5
            return

        if event.key in (pygame.K_EQUALS, pygame.K_KP_PLUS):
            volume = self.audio.adjust_volume(0.10)
            self.message = f"Volume {int(volume * 100)}%"
            if self.world:
                self.world.notice = self.message
                self.world.notice_timer = 1.5
            return

        if self.phase == "explore" and self.world:
            self.world.handle_key(event)
            return

        if self.phase == "challenge" and self.challenge:
            if (
                self.challenge.finished
                and event.key in (pygame.K_RETURN, pygame.K_SPACE)
            ):
                self._finish_challenge()
            else:
                self.challenge.handle_key(event)
            return

        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.phase not in {"choices", "finished"}:
                self.advance()
            return

        if self.phase == "choices":
            if event.key in (pygame.K_1, pygame.K_KP1):
                self.choose(0)
            elif event.key in (pygame.K_2, pygame.K_KP2):
                self.choose(1)
            elif event.key in (pygame.K_3, pygame.K_KP3):
                self.choose(2)
            return

        if event.key == pygame.K_r and self.phase == "finished":
            self.restart()

    def handle_click(self, pos):
        point = self.input_to_canvas(pos)

        if self.paused:
            action = self.pause_menu.handle_click(point)
            self._handle_pause_action(action)
            return

        if self.phase == "explore" and self.world:
            self.world.handle_click(point)
            return

        if self.phase == "challenge" and self.challenge:
            if self.challenge.finished:
                self._finish_challenge()
            else:
                self.challenge.handle_click(point)
            return

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

        if self.phase == "explore" and self.world:
            self.world.draw(self.canvas, self.fonts)

            if self.transition_alpha > 0:
                fade = pygame.Surface(LOGICAL_SIZE, pygame.SRCALPHA)
                fade.fill((0, 0, 0, self.transition_alpha))
                self.canvas.blit(fade, (0, 0))

            if self.paused:
                self.pause_menu.draw(
                    self.canvas, self.fonts, self.audio,
                    self.phase,
                    bool(self.world),
                    self.gallery,
                )

            self._present()
            return

        item = self.current_item()

        if self.phase == "challenge" and self.challenge:
            key = {
                "rune": "scanner",
                "timing": "tech",
                "dodge": "wolf",
            }.get(self.challenge.kind, "rune")
        else:
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
        elif self.phase == "challenge":
            self._draw_challenge(accent)
        elif self.phase == "finished":
            self._draw_finished(accent)
        else:
            self._draw_narration(accent)

        self._draw_footer(accent)

        if self.transition_alpha > 0:
            fade = pygame.Surface(LOGICAL_SIZE, pygame.SRCALPHA)
            fade.fill((0, 0, 0, self.transition_alpha))
            self.canvas.blit(fade, (0, 0))

        if self.paused:
            self.pause_menu.draw(
                self.canvas,
                self.fonts,
                self.audio,
                self.phase,
                bool(self.world),
                self.gallery,
            )

        self._present()

    def _draw_challenge(self, accent):
        ui.draw_status(
            self.canvas,
            self.fonts,
            self.engine.status_snapshot(),
            self.engine.ally_names(),
            self.engine.state["tools"],
            accent,
        )

        if self.challenge:
            self.challenge.draw(
                self.canvas,
                self.fonts,
                accent,
            )

        self.continue_rect = None
        self.choice_rects = []
        self.restart_rect = None

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

        if self.message and self.phase == "result":
            notice = pygame.Rect(88, 535, 850, 34)
            ui.rounded_panel(
                self.canvas,
                notice,
                (20, 31, 43),
                accent,
                10,
            )
            ui.text(
                self.canvas,
                self.message,
                self.fonts["small"],
                ui.GOLD,
                (104, 543),
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

        ui.draw_status(
            self.canvas,
            self.fonts,
            self.engine.status_snapshot(),
            self.engine.ally_names(),
            self.engine.state["tools"],
            accent,
        )

        ui.text(
            self.canvas,
            "ESCOLHA SEU CAMINHO",
            self.fonts["small"],
            accent,
            (58, 280),
        )
        ui.text(
            self.canvas,
            "A escolha muda a história e abre um desafio jogável.",
            self.fonts["body"],
            ui.INK,
            (58, 304),
        )

        self.choice_rects = []
        mouse = self.input_to_canvas(pygame.mouse.get_pos())

        base_y = 342
        for index, choice in enumerate(chapter["choices"]):
            rect = pygame.Rect(58, base_y + index * 92, 1164, 78)
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

        if self.message:
            ui.text(
                self.canvas,
                self.message,
                self.fonts["small"],
                ui.GOLD,
                (58, 624),
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
        elif self.phase == "challenge" and self.challenge_context == "prologue":
            current = self.opening_index + 1
            total = len(GAME["opening"])
        elif self.phase in {"chapter", "choices", "challenge", "result"}:
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

        audio_state = "ON" if self.audio.enabled else "OFF"

        if self.phase == "challenge" and self.challenge:
            if self.challenge.finished:
                controls = "ENTER ou clique para continuar"
            elif self.challenge.kind == "rune":
                controls = "WASD/setas mover • alcance as runas"
            elif self.challenge.kind == "timing":
                controls = "ESPAÇO/clique no momento certo"
            else:
                controls = "A/D ou setas para desviar"

            help_text = (
                f"{controls} • M áudio {audio_state} • "
                "F11 tela cheia • ESC sair"
            )
        else:
            help_text = (
                "ENTER/ESPAÇO continuar • 1/2/3 escolher • "
                f"M áudio {audio_state} • F11 tela cheia • ESC sair"
            )
        ui.text(
            self.canvas,
            help_text,
            self.fonts["small"],
            ui.MUTED,
            (58, 660),
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
                elif event.type == pygame.JOYBUTTONDOWN:
                    gamepad_map = {
                        0: pygame.K_SPACE,
                        1: pygame.K_LSHIFT,
                        2: pygame.K_q,
                        3: pygame.K_r,
                        4: pygame.K_p,
                        5: pygame.K_f,
                        6: pygame.K_m,
                        7: pygame.K_ESCAPE,
                        8: pygame.K_x,
                    }
                    key = gamepad_map.get(event.button)
                    if key is not None:
                        self.handle_key(
                            pygame.event.Event(
                                pygame.KEYDOWN,
                                key=key,
                            )
                        )
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

    app.phase = "opening"
    app.opening_index = 6
    app.reveal = float(len(app.current_text()))
    app.advance()

    if app.phase != "challenge" or app.challenge_context != "prologue":
        raise RuntimeError("Desafio do prólogo não foi iniciado.")

    app.challenge._finish(True, "Smoke do prólogo.")
    app.draw()
    rendered += 1
    app._finish_challenge()

    if app.opening_index != 7:
        raise RuntimeError("Desafio do prólogo não retornou à narrativa.")

    app.restart()

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

        app._start_exploration()
        app.transition_alpha = 0
        app.draw()
        rendered += 1

        available = app.engine.available_choices()
        if not available:
            raise RuntimeError(
                f"Capítulo {chapter['number']} sem escolhas disponíveis."
            )

        first = chapter["choices"].index(available[0])
        app.world.selected_choice = first
        app.update(0.016)

        if app.phase != "challenge":
            raise RuntimeError(
                f"Exploração do capítulo {chapter['number']} "
                "não abriu o desafio."
            )

        if app.phase == "challenge":
            app.challenge.finished = True
            app.challenge.success = True
            app.challenge.result_text = "Smoke do desafio concluído."
            app.draw()
            rendered += 1
            app._finish_challenge()

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
