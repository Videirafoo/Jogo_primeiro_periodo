import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main


def resultado(pontos=0, tentativas=1, usou_dica=False, venceu=False):
    return main.criar_resultado(pontos, tentativas, usou_dica, venceu)


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

    def test_normalizar_nome(self):
        self.assertEqual(main.normalizar_nome("  fernando   videira "), "Fernando Videira")
        self.assertEqual(main.normalizar_nome(""), "Jogador")

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
    def test_escolher_dificuldade_permite_voltar(self, _):
        with patch("builtins.print"):
            dificuldade = main.escolher_dificuldade()
        self.assertIsNone(dificuldade)

    @patch("builtins.input", return_value="4")
    def test_menu_principal(self, _):
        with patch("builtins.print"):
            opcao = main.mostrar_menu_principal()
        self.assertEqual(opcao, "4")

    @patch("main.random.randint", return_value=42)
    @patch("builtins.input", side_effect=["30", "50", "42"])
    def test_jogar_partida_ate_acertar(self, _, __):
        configuracao = main.DIFICULDADES["2"]
        with patch("builtins.print"):
            partida = main.jogar(configuracao)
        self.assertTrue(partida["venceu"])
        self.assertEqual(partida["pontos"], 1600)
        self.assertEqual(partida["tentativas"], 3)

    @patch("main.random.randint", return_value=42)
    @patch("builtins.input", side_effect=["dica", "42"])
    def test_jogar_com_dica_aplica_penalidade(self, _, __):
        configuracao = main.DIFICULDADES["2"]
        with patch("builtins.print"):
            partida = main.jogar(configuracao)
        self.assertEqual(partida["pontos"], 1700)
        self.assertTrue(partida["usou_dica"])

    @patch("main.random.randint", return_value=42)
    @patch("builtins.input", side_effect=["30", "30", "42"])
    def test_palpite_repetido_nao_gasta_tentativa(self, _, __):
        configuracao = main.DIFICULDADES["2"]
        with patch("builtins.print"):
            partida = main.jogar(configuracao)
        self.assertEqual(partida["pontos"], 1800)
        self.assertEqual(partida["tentativas"], 2)

    @patch("main.random.randint", return_value=10)
    @patch("builtins.input", side_effect=[str(i) for i in range(1, 10)] + ["11"])
    def test_jogar_retorna_derrota_ao_esgotar_tentativas(self, _, __):
        configuracao = main.DIFICULDADES["1"]
        with patch("builtins.print"):
            partida = main.jogar(configuracao)
        self.assertFalse(partida["venceu"])
        self.assertEqual(partida["pontos"], 0)
        self.assertEqual(partida["tentativas"], 10)

    def test_atualizar_estatisticas(self):
        estatisticas = main.estatisticas_vazias()
        partida = resultado(1600, 3, False, True)
        main.atualizar_estatisticas(estatisticas, partida, "Normal")
        self.assertEqual(estatisticas["partidas"], 1)
        self.assertEqual(estatisticas["vitorias"], 1)
        self.assertEqual(estatisticas["melhor_pontuacao"], 1600)
        self.assertEqual(estatisticas["melhor_por_modo"]["Normal"], 1600)
        self.assertEqual(len(estatisticas["historico"]), 1)

    def test_historico_mantem_apenas_cinco_partidas(self):
        estatisticas = main.estatisticas_vazias()
        for numero in range(7):
            partida = resultado(100 + numero, 2, False, True)
            main.atualizar_estatisticas(estatisticas, partida, "Fácil")
        self.assertEqual(len(estatisticas["historico"]), 5)
        self.assertEqual(estatisticas["historico"][0]["pontos"], 102)
        self.assertEqual(estatisticas["historico"][-1]["pontos"], 106)

    def test_conquistas_primeira_vitoria_de_primeira_sem_dica(self):
        estatisticas = main.estatisticas_vazias()
        partida = resultado(2000, 1, False, True)
        main.atualizar_estatisticas(estatisticas, partida, "Normal")
        self.assertIn("Primeira vitória", estatisticas["conquistas"])
        self.assertIn("De primeira", estatisticas["conquistas"])
        self.assertIn("Sem dica", estatisticas["conquistas"])

    def test_conquista_mestre_do_dificil(self):
        estatisticas = main.estatisticas_vazias()
        partida = resultado(2400, 3, False, True)
        main.atualizar_estatisticas(estatisticas, partida, "Difícil")
        self.assertIn("Mestre do Difícil", estatisticas["conquistas"])

    def test_conquista_cinco_vitorias(self):
        estatisticas = main.estatisticas_vazias()
        for _ in range(5):
            main.atualizar_estatisticas(
                estatisticas,
                resultado(1000, 2, False, True),
                "Fácil",
            )
        self.assertIn("5 vitórias", estatisticas["conquistas"])

    def test_salvar_e_carregar_estatisticas(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "dados.json"
            dados = main.estatisticas_vazias()
            main.atualizar_estatisticas(
                dados,
                resultado(2000, 1, False, True),
                "Normal",
            )
            self.assertTrue(main.salvar_estatisticas("Fernando", dados, caminho))
            carregados = main.carregar_estatisticas("fernando", caminho)
            self.assertEqual(carregados, dados)

            arquivo = json.loads(caminho.read_text(encoding="utf-8"))
            self.assertEqual(arquivo["versao"], 2)

    def test_estatisticas_ficam_separadas_por_jogador(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "dados.json"
            ana = main.estatisticas_vazias()
            bruno = main.estatisticas_vazias()
            main.atualizar_estatisticas(ana, resultado(1000, 1, False, True), "Fácil")
            main.atualizar_estatisticas(bruno, resultado(1800, 2, False, True), "Normal")
            main.salvar_estatisticas("Ana", ana, caminho)
            main.salvar_estatisticas("Bruno", bruno, caminho)

            self.assertEqual(
                main.carregar_estatisticas("Ana", caminho)["melhor_pontuacao"],
                1000,
            )
            self.assertEqual(
                main.carregar_estatisticas("Bruno", caminho)["melhor_pontuacao"],
                1800,
            )

    def test_ranking_ordena_por_pontuacao(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "dados.json"

            for nome, pontos in [("Ana", 900), ("Bruno", 2500), ("Caio", 1500)]:
                estatisticas = main.estatisticas_vazias()
                main.atualizar_estatisticas(
                    estatisticas,
                    resultado(pontos, 2, False, True),
                    "Normal",
                )
                main.salvar_estatisticas(nome, estatisticas, caminho)

            ranking = main.obter_ranking(caminho)
            self.assertEqual([j["nome"] for j in ranking], ["Bruno", "Caio", "Ana"])

    def test_ranking_limita_em_cinco(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "dados.json"

            for numero in range(7):
                estatisticas = main.estatisticas_vazias()
                main.atualizar_estatisticas(
                    estatisticas,
                    resultado(1000 + numero, 1, False, True),
                    "Fácil",
                )
                main.salvar_estatisticas(f"Jogador {numero}", estatisticas, caminho)

            self.assertEqual(len(main.obter_ranking(caminho)), 5)

    def test_zerar_progresso_remove_apenas_um_jogador(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "dados.json"
            main.salvar_estatisticas("Ana", main.estatisticas_vazias(), caminho)
            bruno = main.estatisticas_vazias()
            main.atualizar_estatisticas(
                bruno,
                resultado(900, 1, False, True),
                "Fácil",
            )
            main.salvar_estatisticas("Bruno", bruno, caminho)

            self.assertTrue(main.zerar_progresso("Ana", caminho))
            self.assertEqual(main.carregar_estatisticas("Ana", caminho)["partidas"], 0)
            self.assertEqual(main.carregar_estatisticas("Bruno", caminho)["partidas"], 1)

    def test_formato_antigo_ainda_pode_ser_lido(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "dados.json"
            antigo = {
                "partidas": 2,
                "vitorias": 1,
                "melhor_pontuacao": 800,
                "melhor_por_modo": {"Normal": 800},
            }
            caminho.write_text(
                json.dumps(antigo, ensure_ascii=False),
                encoding="utf-8",
            )
            carregados = main.carregar_estatisticas("Fernando", caminho)
            self.assertEqual(carregados["partidas"], 2)
            self.assertEqual(carregados["melhor_pontuacao"], 800)
            self.assertEqual(carregados["historico"], [])
            self.assertEqual(carregados["conquistas"], [])

    def test_carregar_estatisticas_corrompidas_usa_padrao(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "dados.json"
            caminho.write_text("{arquivo quebrado", encoding="utf-8")
            dados = main.carregar_estatisticas("Fernando", caminho)
            self.assertEqual(dados["partidas"], 0)
            self.assertEqual(dados["vitorias"], 0)

    def test_mostrar_ranking_vazio(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "dados.json"
            with patch("builtins.print") as imprimir:
                main.mostrar_ranking(caminho)
            textos = " ".join(str(chamada) for chamada in imprimir.call_args_list)
            self.assertIn("Ainda não há jogadores", textos)

    def test_mostrar_conquistas_vazio(self):
        with patch("builtins.print") as imprimir:
            main.mostrar_conquistas("Fernando", main.estatisticas_vazias())
        self.assertTrue(imprimir.called)

    def test_mostrar_regras(self):
        with patch("builtins.print") as imprimir:
            main.mostrar_regras()
        self.assertTrue(imprimir.called)


if __name__ == "__main__":
    unittest.main()
