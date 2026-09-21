import json
import random
from pathlib import Path


ARQUIVO_DADOS = Path(__file__).with_name("dados_jogador.json")
VERSAO_DADOS = 2
LIMITE_HISTORICO = 5

DIFICULDADES = {
    "1": {
        "nome": "Fácil",
        "minimo": 1,
        "maximo": 50,
        "tentativas": 10,
        "multiplicador": 1,
    },
    "2": {
        "nome": "Normal",
        "minimo": 1,
        "maximo": 100,
        "tentativas": 8,
        "multiplicador": 2,
    },
    "3": {
        "nome": "Difícil",
        "minimo": 1,
        "maximo": 500,
        "tentativas": 10,
        "multiplicador": 3,
    },
}


def ler_opcao(mensagem, opcoes_validas):
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in opcoes_validas:
            return resposta
        print("Opção inválida. Tente novamente.")


def normalizar_nome(nome):
    nome = " ".join(nome.split())
    if not nome:
        return "Jogador"
    return nome[:30].title()


def ler_nome():
    return normalizar_nome(input("Digite seu nome: "))


def mostrar_menu_principal():
    print("\n=== MENU PRINCIPAL ===")
    print("1 - Jogar")
    print("2 - Estatísticas")
    print("3 - Ranking")
    print("4 - Conquistas")
    print("5 - Regras")
    print("6 - Zerar meu progresso")
    print("0 - Sair")
    return ler_opcao("Opção: ", {"0", "1", "2", "3", "4", "5", "6"})


def escolher_dificuldade():
    print("\nEscolha a dificuldade:")
    print("1 - Fácil   | número de 1 a 50  | 10 tentativas | x1")
    print("2 - Normal  | número de 1 a 100 | 8 tentativas  | x2")
    print("3 - Difícil | número de 1 a 500 | 10 tentativas | x3")
    print("0 - Voltar")

    opcao = ler_opcao("Opção: ", {"0", "1", "2", "3"})
    if opcao == "0":
        return None
    return DIFICULDADES[opcao]


def avaliar_palpite(palpite, numero_secreto):
    if palpite < numero_secreto:
        return "maior"
    if palpite > numero_secreto:
        return "menor"
    return "acertou"


def classificar_distancia(palpite, numero_secreto, tamanho_intervalo=100):
    distancia = abs(numero_secreto - palpite)
    referencia = max(1, tamanho_intervalo)
    proporcao = distancia / referencia

    if proporcao <= 0.05:
        return "Muito quente!"
    if proporcao <= 0.15:
        return "Quente."
    if proporcao <= 0.30:
        return "Morno."
    return "Frio."


def calcular_pontuacao(tentativas_usadas, multiplicador, usou_dica=False):
    pontos_base = max(100, 1000 - (tentativas_usadas - 1) * 100)
    pontos = pontos_base * multiplicador

    if usou_dica:
        pontos = int(pontos * 0.85)

    return pontos


def gerar_dica(numero_secreto):
    paridade = "par" if numero_secreto % 2 == 0 else "ímpar"

    if numero_secreto % 5 == 0:
        return f"O número é {paridade} e também é divisível por 5."
    return f"O número é {paridade} e não é divisível por 5."


def estatisticas_vazias():
    return {
        "partidas": 0,
        "vitorias": 0,
        "melhor_pontuacao": 0,
        "melhor_por_modo": {},
        "historico": [],
        "conquistas": [],
    }


def dados_vazios():
    return {
        "versao": VERSAO_DADOS,
        "jogadores": {},
    }


def carregar_dados(caminho=ARQUIVO_DADOS):
    if not caminho.exists():
        return dados_vazios()

    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (OSError, json.JSONDecodeError):
        return dados_vazios()

    if isinstance(dados.get("jogadores"), dict):
        dados["versao"] = VERSAO_DADOS
        return dados

    if "partidas" in dados:
        return {
            "versao": VERSAO_DADOS,
            "formato_antigo": dados,
            "jogadores": {},
        }

    return dados_vazios()


def completar_estatisticas(estatisticas):
    padrao = estatisticas_vazias()
    for chave, valor in padrao.items():
        estatisticas.setdefault(chave, valor.copy() if isinstance(valor, (dict, list)) else valor)
    return estatisticas


def carregar_estatisticas(nome, caminho=ARQUIVO_DADOS):
    nome = normalizar_nome(nome)
    dados = carregar_dados(caminho)

    if nome in dados["jogadores"]:
        return completar_estatisticas(dados["jogadores"][nome])

    if "formato_antigo" in dados:
        return completar_estatisticas(dados["formato_antigo"])

    return estatisticas_vazias()


def salvar_estatisticas(nome, estatisticas, caminho=ARQUIVO_DADOS):
    nome = normalizar_nome(nome)
    dados = carregar_dados(caminho)
    dados.pop("formato_antigo", None)
    dados["versao"] = VERSAO_DADOS
    dados["jogadores"][nome] = estatisticas

    try:
        with caminho.open("w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        return True
    except OSError:
        print("Aviso: não foi possível salvar as estatísticas.")
        return False


def zerar_progresso(nome, caminho=ARQUIVO_DADOS):
    nome = normalizar_nome(nome)
    dados = carregar_dados(caminho)
    dados.pop("formato_antigo", None)
    dados["jogadores"].pop(nome, None)

    try:
        with caminho.open("w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        return True
    except OSError:
        print("Aviso: não foi possível zerar o progresso.")
        return False


def criar_registro_partida(resultado, modo):
    return {
        "modo": modo,
        "venceu": resultado["venceu"],
        "tentativas": resultado["tentativas"],
        "pontos": resultado["pontos"],
        "usou_dica": resultado["usou_dica"],
    }


def atualizar_conquistas(estatisticas, resultado, modo):
    conquistas = estatisticas["conquistas"]

    if resultado["venceu"] and "Primeira vitória" not in conquistas:
        conquistas.append("Primeira vitória")

    if resultado["venceu"] and resultado["tentativas"] == 1:
        if "De primeira" not in conquistas:
            conquistas.append("De primeira")

    if resultado["venceu"] and not resultado["usou_dica"]:
        if "Sem dica" not in conquistas:
            conquistas.append("Sem dica")

    if resultado["venceu"] and modo == "Difícil":
        if "Mestre do Difícil" not in conquistas:
            conquistas.append("Mestre do Difícil")

    if estatisticas["vitorias"] >= 5 and "5 vitórias" not in conquistas:
        conquistas.append("5 vitórias")


def atualizar_estatisticas(estatisticas, resultado, modo):
    estatisticas["partidas"] += 1

    if resultado["venceu"]:
        estatisticas["vitorias"] += 1
        pontos = resultado["pontos"]
        estatisticas["melhor_pontuacao"] = max(
            estatisticas["melhor_pontuacao"], pontos
        )
        recorde_modo = estatisticas["melhor_por_modo"].get(modo, 0)
        estatisticas["melhor_por_modo"][modo] = max(recorde_modo, pontos)

    estatisticas["historico"].append(criar_registro_partida(resultado, modo))
    estatisticas["historico"] = estatisticas["historico"][-LIMITE_HISTORICO:]
    atualizar_conquistas(estatisticas, resultado, modo)
    return estatisticas


def obter_ranking(caminho=ARQUIVO_DADOS):
    dados = carregar_dados(caminho)
    ranking = []

    for nome, estatisticas in dados["jogadores"].items():
        estatisticas = completar_estatisticas(estatisticas)
        ranking.append(
            {
                "nome": nome,
                "pontos": estatisticas["melhor_pontuacao"],
                "vitorias": estatisticas["vitorias"],
            }
        )

    ranking.sort(key=lambda jogador: (-jogador["pontos"], -jogador["vitorias"], jogador["nome"]))
    return ranking[:5]


def mostrar_ranking(caminho=ARQUIVO_DADOS):
    ranking = obter_ranking(caminho)
    print("\n=== RANKING LOCAL ===")

    if not ranking:
        print("Ainda não há jogadores no ranking.")
        return

    for posicao, jogador in enumerate(ranking, start=1):
        print(
            f"{posicao}º - {jogador['nome']}: "
            f"{jogador['pontos']} pontos | {jogador['vitorias']} vitória(s)"
        )


def mostrar_historico(estatisticas):
    print("\nÚltimas partidas:")

    if not estatisticas["historico"]:
        print("- Nenhuma partida registrada.")
        return

    for partida in reversed(estatisticas["historico"]):
        resultado = "Vitória" if partida["venceu"] else "Derrota"
        dica = "com dica" if partida["usou_dica"] else "sem dica"
        print(
            f"- {partida['modo']}: {resultado} | "
            f"{partida['tentativas']} tentativa(s) | "
            f"{partida['pontos']} pontos | {dica}"
        )


def mostrar_estatisticas(nome, estatisticas):
    partidas = estatisticas["partidas"]
    vitorias = estatisticas["vitorias"]
    taxa = (vitorias / partidas * 100) if partidas else 0

    print("\n" + "-" * 46)
    print(f"ESTATÍSTICAS DE {nome.upper()}")
    print(f"Partidas: {partidas} | Vitórias: {vitorias} | Taxa: {taxa:.0f}%")
    print(f"Melhor pontuação: {estatisticas['melhor_pontuacao']}")

    if estatisticas["melhor_por_modo"]:
        print("Recordes por dificuldade:")
        for modo, pontos in estatisticas["melhor_por_modo"].items():
            print(f"- {modo}: {pontos} pontos")

    mostrar_historico(estatisticas)
    print("-" * 46)


def mostrar_conquistas(nome, estatisticas):
    print(f"\n=== CONQUISTAS DE {nome.upper()} ===")

    if not estatisticas["conquistas"]:
        print("Nenhuma conquista desbloqueada ainda.")
        return

    for conquista in estatisticas["conquistas"]:
        print(f"- {conquista}")


def mostrar_regras():
    print("\n=== REGRAS ===")
    print("1. Escolha uma dificuldade e tente descobrir o número secreto.")
    print("2. A cada erro, o jogo informa se o número é maior ou menor.")
    print("3. Frio, morno e quente mostram o quanto você está perto.")
    print("4. Palpites repetidos e entradas inválidas não gastam tentativa.")
    print("5. Você pode usar DICA uma vez, mas perde 15% da pontuação.")
    print("6. Quanto menos tentativas usar, maior será sua pontuação.")
    print("7. Vitórias especiais podem liberar conquistas.")


def criar_resultado(pontos, tentativas, usou_dica, venceu):
    return {
        "pontos": pontos,
        "tentativas": tentativas,
        "usou_dica": usou_dica,
        "venceu": venceu,
    }


def jogar(configuracao):
    minimo = configuracao["minimo"]
    maximo = configuracao["maximo"]
    limite = configuracao["tentativas"]
    numero_secreto = random.randint(minimo, maximo)

    limite_inferior = minimo
    limite_superior = maximo
    palpites_usados = set()
    usou_dica = False
    tentativa = 1

    print(f"\n=== MODO {configuracao['nome'].upper()} ===")
    print(f"Descubra o número entre {minimo} e {maximo}.")
    print(f"Você tem {limite} tentativas.")
    print("Digite DICA para receber uma pista uma vez.")

    while tentativa <= limite:
        restantes = limite - tentativa + 1
        print(f"\nTentativa {tentativa}/{limite} | Restantes: {restantes}")
        print(f"Faixa atual: {limite_inferior} a {limite_superior}")

        entrada = input("Seu palpite: ").strip().lower()

        if entrada == "dica":
            if usou_dica:
                print("Você já usou a dica desta partida.")
            else:
                print("DICA:", gerar_dica(numero_secreto))
                print("Usar dica reduz a pontuação final em 15%.")
                usou_dica = True
            continue

        try:
            palpite = int(entrada)
        except ValueError:
            print("Entrada inválida. Digite um número ou DICA.")
            continue

        if not minimo <= palpite <= maximo:
            print(f"Digite um número entre {minimo} e {maximo}.")
            continue

        if palpite in palpites_usados:
            print("Você já tentou esse número. Escolha outro sem perder tentativa.")
            continue

        palpites_usados.add(palpite)
        resultado_palpite = avaliar_palpite(palpite, numero_secreto)

        if resultado_palpite == "acertou":
            pontos = calcular_pontuacao(
                tentativa,
                configuracao["multiplicador"],
                usou_dica,
            )
            print(f"\nACERTOU! O número secreto era {numero_secreto}.")
            print(f"Você conseguiu em {tentativa} tentativa(s).")
            print(f"Pontuação da partida: {pontos} pontos.")
            return criar_resultado(pontos, tentativa, usou_dica, True)

        if resultado_palpite == "maior":
            print("O número secreto é MAIOR.")
            limite_inferior = max(limite_inferior, palpite + 1)
        else:
            print("O número secreto é MENOR.")
            limite_superior = min(limite_superior, palpite - 1)

        tamanho_intervalo = maximo - minimo + 1
        print(classificar_distancia(palpite, numero_secreto, tamanho_intervalo))
        tentativa += 1

    print(f"\nFim de jogo. O número secreto era {numero_secreto}.")
    return criar_resultado(0, limite, usou_dica, False)


def mostrar_cabecalho():
    print("=" * 46)
    print("        DESAFIO DO NÚMERO SECRETO")
    print("=" * 46)
    print("Acerte o número, use lógica e tente bater seu recorde.")


def main():
    mostrar_cabecalho()
    nome = ler_nome()
    print(f"\nBem-vindo, {nome}!")

    while True:
        opcao = mostrar_menu_principal()

        if opcao == "1":
            configuracao = escolher_dificuldade()
            if configuracao is None:
                continue

            resultado = jogar(configuracao)
            estatisticas = carregar_estatisticas(nome)
            atualizar_estatisticas(estatisticas, resultado, configuracao["nome"])
            salvar_estatisticas(nome, estatisticas)
            mostrar_estatisticas(nome, estatisticas)

        elif opcao == "2":
            mostrar_estatisticas(nome, carregar_estatisticas(nome))

        elif opcao == "3":
            mostrar_ranking()

        elif opcao == "4":
            mostrar_conquistas(nome, carregar_estatisticas(nome))

        elif opcao == "5":
            mostrar_regras()

        elif opcao == "6":
            resposta = ler_opcao(
                "Tem certeza que deseja zerar seu progresso? [S/N]: ",
                {"s", "sim", "n", "nao", "não"},
            )
            if resposta in {"s", "sim"}:
                zerar_progresso(nome)
                print("Seu progresso foi zerado.")

        else:
            break

    print(f"\nObrigado por jogar, {nome}!")


if __name__ == "__main__":
    main()
