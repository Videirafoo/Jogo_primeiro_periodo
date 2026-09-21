import os
import unittest
from copy import deepcopy

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from engine import StoryEngine
from story_data import GAME


class StoryEngineTests(unittest.TestCase):
    def test_conteudo_principal_recuperado(self):
        self.assertEqual(GAME["title"], "OS ETERNOS")
        self.assertEqual(len(GAME["opening"]), 16)
        self.assertEqual(len(GAME["chapters"]), 7)
        self.assertEqual(len(GAME["endings"]), 5)

    def test_protagonista_comeca_com_tecnologia_do_prologo(self):
        engine = StoryEngine(GAME)
        self.assertIn("Scanner de Runas", engine.state["tools"])
        self.assertIn("Mapa Holográfico", engine.state["tools"])
        self.assertIn("Pulso de Código", engine.state["tools"])

    def test_primeiro_capitulo_tem_tres_escolhas(self):
        engine = StoryEngine(GAME)
        self.assertEqual(engine.current_chapter["title"], "A Estrada de Valdrak")
        self.assertEqual(len(engine.available_choices()), 3)

    def test_escolha_aplica_atributos(self):
        engine = StoryEngine(GAME)
        choice = engine.current_chapter["choices"][0]
        result = engine.apply_choice(choice)
        self.assertTrue(result["ok"])
        self.assertEqual(engine.state["coragem"], 2)
        self.assertEqual(engine.state["tecnologia"], 2)
        self.assertEqual(engine.state["amizade"], 2)

    def test_escolha_desbloqueia_thorvald(self):
        engine = StoryEngine(GAME)
        choice = engine.current_chapter["choices"][0]
        result = engine.apply_choice(choice)
        self.assertEqual(result["new_ally"]["name"], "Thorvald")
        self.assertIn("thorvald", engine.allies)

    def test_requisito_de_aliado_bloqueia_quando_ausente(self):
        engine = StoryEngine(GAME)
        engine.chapter_index = 3
        choice = engine.current_chapter["choices"][0]
        self.assertFalse(engine.choice_available(choice))
        self.assertIn("Aurel", engine.availability_reason(choice))

    def test_requisito_de_ferramenta_disponivel(self):
        engine = StoryEngine(GAME)
        engine.chapter_index = 5
        choice = engine.current_chapter["choices"][2]
        self.assertTrue(engine.choice_available(choice))

    def test_status_possui_atributos_centrais(self):
        snapshot = StoryEngine(GAME).status_snapshot()
        self.assertIn("coragem", snapshot)
        self.assertIn("sabedoria", snapshot)
        self.assertIn("tecnologia", snapshot)
        self.assertIn("amizade", snapshot)
        self.assertIn("caos", snapshot)
        self.assertIn("marcas", snapshot)

    def test_final_padrao_sempre_existe(self):
        engine = StoryEngine(GAME)
        ending = engine.choose_ending()
        self.assertEqual(ending["id"], "sonho_que_virou_jogo")

    def test_final_tecnologia(self):
        engine = StoryEngine(GAME)
        engine.state["tecnologia"] = 12
        engine.state["sabedoria"] = 7
        ending = engine.choose_ending()
        self.assertEqual(ending["id"], "tecnologo_de_valdrak")

    def test_final_grupo(self):
        engine = StoryEngine(GAME)
        engine.state["amizade"] = 11
        engine.allies = ["thorvald", "aurel", "kaion", "brenor"]
        ending = engine.choose_ending()
        self.assertEqual(ending["id"], "grupo_dos_despertos")

    def test_todos_os_caminhos_alcancam_o_final(self):
        dead_ends = []
        completed = 0

        def walk(engine):
            nonlocal completed
            chapter = engine.current_chapter

            if chapter is None:
                completed += 1
                return

            available = [
                index
                for index, choice in enumerate(chapter["choices"])
                if engine.choice_available(choice)
            ]

            if not available:
                dead_ends.append(chapter["number"])
                return

            for index in available:
                clone = deepcopy(engine)
                choice = clone.current_chapter["choices"][index]
                clone.apply_choice(choice)
                clone.advance_chapter()
                walk(clone)

        walk(StoryEngine(GAME))

        self.assertEqual(dead_ends, [])
        self.assertGreater(completed, 0)


if __name__ == "__main__":
    unittest.main()
