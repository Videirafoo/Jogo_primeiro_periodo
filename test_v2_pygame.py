import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"

import app_pygame
import main


class JogoPygameV2Tests(unittest.TestCase):
    def test_criar_estado_inicia_no_perfil(self):
        estado = app_pygame.criar_estado()
        self.assertEqual(estado["tela"], "perfil")
        self.assertFalse(estado["finalizada"])

    def test_iniciar_partida_configura_estado(self):
        estado = app_pygame.criar_estado()
        app_pygame.iniciar_partida(
            estado,
            main.DIFICULDADES["2"],
            numero_secreto=74,
        )
        self.assertEqual(estado["tela"], "jogo")
        self.assertEqual(estado["numero_secreto"], 74)
        self.assertEqual(estado["limite_inferior"], 1)
        self.assertEqual(estado["limite_superior"], 100)

    def test_processar_palpite_atualiza_faixa(self):
        estado = app_pygame.criar_estado()
        estado["nome"] = "Teste"
        app_pygame.iniciar_partida(
            estado,
            main.DIFICULDADES["2"],
            numero_secreto=74,
        )
        app_pygame.processar_palpite(estado, 50)
        self.assertEqual(estado["limite_inferior"], 51)
        self.assertEqual(estado["tentativa"], 2)

    def test_palpite_repetido_nao_gasta_tentativa(self):
        estado = app_pygame.criar_estado()
        estado["nome"] = "Teste"
        app_pygame.iniciar_partida(
            estado,
            main.DIFICULDADES["2"],
            numero_secreto=74,
        )
        app_pygame.processar_palpite(estado, 50)
        tentativa = estado["tentativa"]
        app_pygame.processar_palpite(estado, 50)
        self.assertEqual(estado["tentativa"], tentativa)

    def test_usar_dica_apenas_uma_vez(self):
        estado = app_pygame.criar_estado()
        app_pygame.iniciar_partida(
            estado,
            main.DIFICULDADES["1"],
            numero_secreto=20,
        )
        app_pygame.usar_dica(estado)
        primeira = estado["mensagem"]
        app_pygame.usar_dica(estado)
        self.assertTrue(estado["usou_dica"])
        self.assertIn("DICA", primeira)
        self.assertIn("já foi usada", estado["mensagem"])


if __name__ == "__main__":
    unittest.main()
