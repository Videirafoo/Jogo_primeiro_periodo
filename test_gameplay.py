import os
import unittest
from collections import defaultdict

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from eternos import GameApp
from gameplay import Challenge


class ChallengeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_capitulos_possuem_desafio(self):
        kinds = [Challenge(number).kind for number in range(1, 8)]
        self.assertIn("rune", kinds)
        self.assertIn("timing", kinds)
        self.assertIn("dodge", kinds)

    def test_rune_pode_ser_concluido(self):
        challenge = Challenge(1)
        keys = defaultdict(bool)

        while not challenge.finished:
            challenge.cursor.update(challenge.target)
            challenge.update(0.01, keys)

        self.assertTrue(challenge.success)
        self.assertGreaterEqual(challenge.collected, challenge.rune_goal)

    def test_timing_pode_ser_concluido(self):
        challenge = Challenge(2)

        for _ in range(3):
            challenge.marker = challenge.target_center
            challenge._timing_press()

        self.assertTrue(challenge.finished)
        self.assertTrue(challenge.success)
        self.assertEqual(challenge.timing_hits, 3)

    def test_timing_falha_apos_tres_erros(self):
        challenge = Challenge(3)

        for _ in range(3):
            challenge.marker = 0.0
            challenge.target_center = 0.8
            challenge._timing_press()

        self.assertTrue(challenge.finished)
        self.assertFalse(challenge.success)

    def test_dodge_sobrevive_ate_o_tempo_final(self):
        challenge = Challenge(5)
        keys = defaultdict(bool)
        challenge.hazards = []
        challenge.spawn_timer = 999
        challenge.elapsed = challenge.survive_for - 0.02
        challenge.update(0.03, keys)

        self.assertTrue(challenge.finished)
        self.assertTrue(challenge.success)

    def test_falha_nao_bloqueia_resultado(self):
        challenge = Challenge(6)
        challenge._finish(False, "falhou")

        self.assertTrue(challenge.finished)
        self.assertFalse(challenge.success)
        self.assertTrue(challenge.result_text)

    def test_prologo_abre_desafio_jogavel(self):
        app = GameApp(headless=True)
        app.phase = "opening"
        app.opening_index = 6
        app.reveal = float(len(app.current_text()))

        app.advance()

        self.assertEqual(app.phase, "challenge")
        self.assertEqual(app.challenge_context, "prologue")
        self.assertEqual(app.challenge.kind, "dodge")

        app.challenge._finish(True, "ok")
        app._finish_challenge()

        self.assertEqual(app.phase, "opening")
        self.assertEqual(app.opening_index, 7)
        self.assertTrue(app.prologue_action_done)

    def test_escolha_abre_desafio_antes_da_consequencia(self):
        app = GameApp(headless=True)
        app.phase = "choices"
        app.engine.chapter_index = 0

        app.choose(0)

        self.assertEqual(app.phase, "challenge")
        self.assertEqual(app.challenge_context, "choice")

        app.challenge._finish(True, "ok")
        app._finish_challenge()

        self.assertEqual(app.phase, "result")
        self.assertIn("Desafio superado", app.message)


if __name__ == "__main__":
    unittest.main()
