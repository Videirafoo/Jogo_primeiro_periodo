import tempfile
import unittest
from pathlib import Path

from engine import StoryEngine
from savegame import load_game, save_game
from story_data import GAME


class SaveGameTests(unittest.TestCase):
    def test_salvar_e_carregar_estado(self):
        engine = StoryEngine(GAME)
        engine.state["coragem"] = 7
        engine.allies.append("thorvald")
        profile = {
            "level": 3,
            "xp": 2,
            "xp_next": 10,
            "max_health": 116,
            "health": 90,
            "max_energy": 112,
            "energy": 70,
            "kills": 8,
        }

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "save.json"

            saved = save_game(
                engine,
                profile,
                "explore",
                5,
                2,
                path,
            )
            loaded = load_game(path)

        self.assertTrue(saved)
        self.assertEqual(
            loaded["engine"]["state"]["coragem"],
            7,
        )
        self.assertIn(
            "thorvald",
            loaded["engine"]["allies"],
        )
        self.assertEqual(
            loaded["rpg_profile"]["level"],
            3,
        )
        self.assertEqual(
            loaded["resume_phase"],
            "explore",
        )

    def test_save_corrompido_retorna_none(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "save.json"
            path.write_text("{quebrado", encoding="utf-8")
            self.assertIsNone(load_game(path))

    def test_fase_instavel_retorna_para_capitulo(self):
        engine = StoryEngine(GAME)
        profile = {"level": 1}

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "save.json"
            save_game(
                engine,
                profile,
                "challenge",
                0,
                0,
                path,
            )
            loaded = load_game(path)

        self.assertEqual(
            loaded["resume_phase"],
            "chapter",
        )


if __name__ == "__main__":
    unittest.main()
