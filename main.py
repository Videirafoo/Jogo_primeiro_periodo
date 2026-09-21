import json
import random
from pathlib import Path


ARQUIVO_DADOS = Path(__file__).with_name("dados_jogador.json")

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


def ler_nome():
    nome = input("Digite seu nome: ").strip()
    if not nome:
        return "Jogador"
    return nome[:30]


def mostrar_menu_principal():
    print("\n=== MENU PRINCIPAL ===")
    print("1 - Jogar")
    print("2 - Estatísticas")
    print("3 - Regras")
    print("4 - Zerar meu progresso")
    print("0 - Sair")
    return ler_opcao("Opção: ", {"0", "1", "2", "3", "4"})


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
    }


def carregar_dados(caminho=ARQUIVO_DADOS):
    if not caminho.exists():
        return {"jogadores": {}}

    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (OSError, json.JSONDecodeError):
        return {"jogadores": {}}

    if isinstance(dados.get("jogadores"), dict):
        return dados

    if "partidas" in dados:
        return {"formato_antigo": dados, "jogadores": {}}

    return {"jogadores": {}}


def completar_estatisticas(estatisticas):
    padrao = estatisticas_vazias()
    for chave, valor in padrao.items():
        estatisticas.setdefault(chave, valor)
    return estatisticas


def carregar_estatisticas(nome, caminho=ARQUIVO_DADOS):
    dados = carregar_dados(caminho)

    if nome in dados["jogadores"]:
        return completar_estatisticas(dados["jogadores"][nome])

    if "formato_antigo" in dados:
        return completar_estatisticas(dados["formato_antigo"])

    return estatisticas_vazias()


def salvar_estatisticas(nome, estatisticas, caminho=ARQUIVO_DADOS):
    dados = carregar_dados(caminho)
    dados.pop("formato_antigo", None)
    dados["jogadores"][nome] = estatisticas

    try:
        with caminho.open("w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        return True
    except OSError:
        print("Aviso: não foi possível salvar as estatísticas.")
        return False


def zerar_progresso(nome, caminho=ARQUIVO_DADOS):
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


def atualizar_estatisticas(estatisticas, pontos, modo):
    estatisticas["partidas"] += 1

    if pontos > 0:
        estatisticas["vitorias"] += 1
        estatisticas["melhor_pontuacao"] = max(
            estatisticas["melhor_pontuacao"], pontos
        )
        recorde_modo = estatisticas["melhor_por_modo"].get(modo, 0)
        estatisticas["melhor_por_modo"][modo] = max(recorde_modo, pontos)

    return estatisticas


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

    print("-" * 46)


def mostrar_regras():
    print("\n=== REGRAS ===")
    print("1. Escolha uma dificuldade e tente descobrir o número secreto.")
    print("2. A cada erro, o jogo informa se o número é maior ou menor.")
    print("3. Frio, morno e quente mostram o quanto você está perto.")
    print("4. Palpites repetidos e entradas inválidas não gastam tentativa.")
    print("5. Você pode usar DICA uma vez, mas perde 15% da pontuação.")
    print("6. Quanto menos tentativas usar, maior será sua pontuação.")


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
        resultado = avaliar_palpite(palpite, numero_secreto)

        if resultado == "acertou":
            pontos = calcular_pontuacao(
                tentativa,
                configuracao["multiplicador"],
                usou_dica,
            )
            print(f"\nACERTOU! O número secreto era {numero_secreto}.")
            print(f"Você conseguiu em {tentativa} tentativa(s).")
            print(f"Pontuação da partida: {pontos} pontos.")
            return pontos

        if resultado == "maior":
            print("O número secreto é MAIOR.")
            limite_inferior = max(limite_inferior, palpite + 1)
        else:
            print("O número secreto é MENOR.")
            limite_superior = min(limite_superior, palpite - 1)

        tamanho_intervalo = maximo - minimo + 1
        print(classificar_distancia(palpite, numero_secreto, tamanho_intervalo))
        tentativa += 1

    print(f"\nFim de jogo. O número secreto era {numero_secreto}.")
    return 0


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

            pontos = jogar(configuracao)
            estatisticas = carregar_estatisticas(nome)
            atualizar_estatisticas(estatisticas, pontos, configuracao["nome"])
            salvar_estatisticas(nome, estatisticas)
            mostrar_estatisticas(nome, estatisticas)

        elif opcao == "2":
            estatisticas = carregar_estatisticas(nome)
            mostrar_estatisticas(nome, estatisticas)

        elif opcao == "3":
            mostrar_regras()

        elif opcao == "4":
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
