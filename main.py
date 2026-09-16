import random


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


def ler_numero(mensagem, minimo, maximo):
    """Lê um número inteiro dentro do intervalo informado."""
    while True:
        try:
            valor = int(input(mensagem))
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")
            continue

        if minimo <= valor <= maximo:
            return valor

        print(f"Digite um número entre {minimo} e {maximo}.")


def ler_opcao(mensagem, opcoes_validas):
    """Lê uma opção textual e só retorna quando ela for válida."""
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in opcoes_validas:
            return resposta
        print("Opção inválida. Tente novamente.")


def escolher_dificuldade():
    """Mostra o menu de dificuldade e retorna a configuração escolhida."""
    print("\nEscolha a dificuldade:")
    print("1 - Fácil   | número de 1 a 50  | 10 tentativas")
    print("2 - Normal  | número de 1 a 100 | 8 tentativas")
    print("3 - Difícil | número de 1 a 500 | 10 tentativas")
    print("0 - Sair")

    opcao = ler_opcao("Opção: ", {"0", "1", "2", "3"})
    if opcao == "0":
        return None
    return DIFICULDADES[opcao]


def avaliar_palpite(palpite, numero_secreto):
    """Compara o palpite com o número secreto."""
    if palpite < numero_secreto:
        return "maior"
    if palpite > numero_secreto:
        return "menor"
    return "acertou"


def classificar_distancia(palpite, numero_secreto):
    """Retorna uma dica simples de proximidade."""
    distancia = abs(numero_secreto - palpite)

    if distancia <= 5:
        return "Muito quente!"
    if distancia <= 15:
        return "Quente."
    if distancia <= 30:
        return "Morno."
    return "Frio."


def calcular_pontuacao(tentativas_usadas, multiplicador):
    """Calcula a pontuação: menos tentativas geram mais pontos."""
    pontos_base = max(100, 1000 - (tentativas_usadas - 1) * 100)
    return pontos_base * multiplicador


def jogar(configuracao):
    """Executa uma partida e retorna a pontuação conquistada."""
    minimo = configuracao["minimo"]
    maximo = configuracao["maximo"]
    limite = configuracao["tentativas"]
    numero_secreto = random.randint(minimo, maximo)

    print(f"\n=== MODO {configuracao['nome'].upper()} ===")
    print(f"Descubra o número entre {minimo} e {maximo}.")
    print(f"Você tem {limite} tentativas.")

    for tentativa in range(1, limite + 1):
        restantes = limite - tentativa + 1
        print(f"\nTentativa {tentativa}/{limite} | Restantes: {restantes}")
        palpite = ler_numero("Seu palpite: ", minimo, maximo)
        resultado = avaliar_palpite(palpite, numero_secreto)

        if resultado == "acertou":
            pontos = calcular_pontuacao(tentativa, configuracao["multiplicador"])
            print(f"\nAcertou! O número secreto era {numero_secreto}.")
            print(f"Você conseguiu em {tentativa} tentativa(s).")
            print(f"Pontuação da partida: {pontos} pontos.")
            return pontos

        if resultado == "maior":
            print("O número secreto é MAIOR.")
        else:
            print("O número secreto é MENOR.")

        print(classificar_distancia(palpite, numero_secreto))

    print(f"\nFim de jogo. O número secreto era {numero_secreto}.")
    return 0


def deseja_jogar_novamente():
    """Pergunta se o usuário deseja iniciar outra partida."""
    resposta = ler_opcao("\nJogar novamente? [S/N]: ", {"s", "sim", "n", "nao", "não"})
    return resposta in {"s", "sim"}


def mostrar_cabecalho():
    print("=" * 46)
    print("           JOGO DE ADIVINHAÇÃO")
    print("=" * 46)
    print("Escolha uma dificuldade, tente acertar o número")
    print("e faça a maior pontuação possível.")


def main():
    melhor_pontuacao = 0
    partidas = 0

    mostrar_cabecalho()

    while True:
        configuracao = escolher_dificuldade()

        if configuracao is None:
            break

        pontos = jogar(configuracao)
        partidas += 1
        melhor_pontuacao = max(melhor_pontuacao, pontos)

        print(f"\nPartidas jogadas: {partidas}")
        print(f"Melhor pontuação desta sessão: {melhor_pontuacao}")

        if not deseja_jogar_novamente():
            break

    print("\nObrigado por jogar!")


if __name__ == "__main__":
    main()
