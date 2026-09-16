import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main


class JogoAdivinhacaoTests(unittest.TestCase):
    def test_avaliar_palpite(self):
        self.assertEqual(main.avaliar_palpite(10, 20), "maior")
        self.assertEqual(main.avaliar_palpite(30, 20), "menor")
        self.assertEqual(main.avaliar_palpite(20, 20), "acertou")

    def test_classificar_distancia_se_adapta_ao_intervalo(self):
        self.assertEqual(main.classificar_distancia(48, 50, 50), "Muito quente!")
        self.assertEqual(main.classificar_distancia(40, 50, 100), "Quente.")
        self.assertEqual(main.classificar_distancia(25, 50, 100), "Morno.")
        self.assertEqual(main.classificar_distancia(1, 50, 100), "Frio.")

    def test_calcular_pontuacao(self):
        self.assertEqual(main.calcular_pontuacao(1, 1), 1000)
        self.assertEqual(main.calcular_pontuacao(3, 2), 1600)
        self.assertEqual(main.calcular_pontuacao(20, 3), 300)

    def test_calcular_pontuacao_com_dica(self):
        self.assertEqual(main.calcular_pontuacao(1, 2, True), 1700)

    def test_gerar_dica(self):
        self.assertIn("par", main.gerar_dica(20))
        self.assertIn("divisível por 5", main.gerar_dica(20))
        self.assertIn("ímpar", main.gerar_dica(21))
        self.assertIn("não é divisível por 5", main.gerar_dica(21))

    @patch("builtins.input", side_effect=["abc", "0", "101", "50"])
    def test_ler_numero_valida_entrada(self, _):
        with patch("builtins.print"):
            valor = main.ler_numero("Palpite: ", 1, 100)
        self.assertEqual(valor, 50)

    @patch("builtins.input", return_value="")
    def test_ler_nome_usa_padrao(self, _):
        self.assertEqual(main.ler_nome(), "Jogador")

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

    @patch("main.random.randint", return_value=42)
    @patch("builtins.input", side_effect=["dica", "42"])
    def test_jogar_com_dica_aplica_penalidade(self, _, __):
        configuracao = main.DIFICULDADES["2"]
        with patch("builtins.print"):
            pontos = main.jogar(configuracao)
        self.assertEqual(pontos, 1700)

    @patch("main.random.randint", return_value=42)
    @patch("builtins.input", side_effect=["30", "30", "42"])
    def test_palpite_repetido_nao_gasta_tentativa(self, _, __):
        configuracao = main.DIFICULDADES["2"]
        with patch("builtins.print"):
            pontos = main.jogar(configuracao)
        self.assertEqual(pontos, 1800)

    @patch("main.random.randint", return_value=10)
    @patch("builtins.input", side_effect=[str(i) for i in range(1, 10)] + ["11"])
    def test_jogar_retorna_zero_ao_esgotar_tentativas(self, _, __):
        configuracao = main.DIFICULDADES["1"]
        with patch("builtins.print"):
            pontos = main.jogar(configuracao)
        self.assertEqual(pontos, 0)

    def test_atualizar_estatisticas(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "inexistente.json"
            estatisticas = main.carregar_estatisticas(caminho)
        main.atualizar_estatisticas(estatisticas, 1600, "Normal")
        self.assertEqual(estatisticas["partidas"], 1)
        self.assertEqual(estatisticas["vitorias"], 1)
        self.assertEqual(estatisticas["melhor_pontuacao"], 1600)
        self.assertEqual(estatisticas["melhor_por_modo"]["Normal"], 1600)

    def test_salvar_e_carregar_estatisticas(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "dados.json"
            dados = {
                "partidas": 4,
                "vitorias": 3,
                "melhor_pontuacao": 2000,
                "melhor_por_modo": {"Normal": 2000},
            }
            self.assertTrue(main.salvar_estatisticas(dados, caminho))
            carregados = main.carregar_estatisticas(caminho)
            self.assertEqual(carregados, dados)

    def test_carregar_estatisticas_corrompidas_usa_padrao(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "dados.json"
            caminho.write_text("{arquivo quebrado", encoding="utf-8")
            dados = main.carregar_estatisticas(caminho)
            self.assertEqual(dados["partidas"], 0)
            self.assertEqual(dados["vitorias"], 0)

    @patch("builtins.input", return_value="sim")
    def test_deseja_jogar_novamente_sim(self, _):
        self.assertTrue(main.deseja_jogar_novamente())

    @patch("builtins.input", return_value="n")
    def test_deseja_jogar_novamente_nao(self, _):
        self.assertFalse(main.deseja_jogar_novamente())


if __name__ == "__main__":
    unittest.main()
