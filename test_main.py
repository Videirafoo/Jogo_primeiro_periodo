import unittest
from unittest.mock import patch

import main


class JogoAdivinhacaoTests(unittest.TestCase):
    def test_avaliar_palpite(self):
        self.assertEqual(main.avaliar_palpite(10, 20), "maior")
        self.assertEqual(main.avaliar_palpite(30, 20), "menor")
        self.assertEqual(main.avaliar_palpite(20, 20), "acertou")

    def test_classificar_distancia(self):
        self.assertEqual(main.classificar_distancia(48, 50), "Muito quente!")
        self.assertEqual(main.classificar_distancia(40, 50), "Quente.")
        self.assertEqual(main.classificar_distancia(25, 50), "Morno.")
        self.assertEqual(main.classificar_distancia(1, 50), "Frio.")

    def test_calcular_pontuacao(self):
        self.assertEqual(main.calcular_pontuacao(1, 1), 1000)
        self.assertEqual(main.calcular_pontuacao(3, 2), 1600)
        self.assertEqual(main.calcular_pontuacao(20, 3), 300)

    @patch("builtins.input", side_effect=["abc", "0", "101", "50"])
    def test_ler_numero_valida_entrada(self, _):
        with patch("builtins.print"):
            valor = main.ler_numero("Palpite: ", 1, 100)
        self.assertEqual(valor, 50)

    @patch("builtins.input", side_effect=["9", "2"])
    def test_escolher_dificuldade(self, _):
        with patch("builtins.print"):
            dificuldade = main.escolher_dificuldade()
        self.assertEqual(dificuldade["nome"], "Normal")
        self.assertEqual(dificuldade["maximo"], 100)
        self.assertEqual(dificuldade["tentativas"], 8)

    @patch("builtins.input", return_value="0")
    def test_escolher_dificuldade_permite_sair(self, _):
        with patch("builtins.print"):
            dificuldade = main.escolher_dificuldade()
        self.assertIsNone(dificuldade)

    @patch("main.random.randint", return_value=42)
    @patch("builtins.input", side_effect=["30", "50", "42"])
    def test_jogar_partida_ate_acertar(self, _, __):
        configuracao = main.DIFICULDADES["2"]
        with patch("builtins.print"):
            pontos = main.jogar(configuracao)
        self.assertEqual(pontos, 1600)

    @patch("main.random.randint", return_value=10)
    @patch("builtins.input", side_effect=["1"] * 10)
    def test_jogar_retorna_zero_ao_esgotar_tentativas(self, _, __):
        configuracao = main.DIFICULDADES["1"]
        with patch("builtins.print"):
            pontos = main.jogar(configuracao)
        self.assertEqual(pontos, 0)

    @patch("builtins.input", return_value="sim")
    def test_deseja_jogar_novamente_sim(self, _):
        self.assertTrue(main.deseja_jogar_novamente())

    @patch("builtins.input", return_value="n")
    def test_deseja_jogar_novamente_nao(self, _):
        self.assertFalse(main.deseja_jogar_novamente())


if __name__ == "__main__":
    unittest.main()
