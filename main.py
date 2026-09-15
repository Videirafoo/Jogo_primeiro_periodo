import random


def ler_numero(mensagem, minimo, maximo):
    """Lê um número inteiro dentro do intervalo informado."""
    while True:
        try:
            valor = int(input(mensagem))

            if minimo <= valor <= maximo:
                return valor

            print(f"Digite um número entre {minimo} e {maximo}.")
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")


def jogar():
    """Executa uma partida do jogo de adivinhação."""
    numero_secreto = random.randint(1, 100)
    tentativas = 0

    print("\n=== JOGO DE ADIVINHAÇÃO ===")
    print("Tente descobrir o número entre 1 e 100.")

    while True:
        palpite = ler_numero("Seu palpite: ", 1, 100)
        tentativas += 1

        if palpite < numero_secreto:
            print("O número secreto é MAIOR.")
        elif palpite > numero_secreto:
            print("O número secreto é MENOR.")
        else:
            print(f"\nAcertou em {tentativas} tentativa(s)!")
            break


def deseja_jogar_novamente():
    """Pergunta se o usuário deseja iniciar outra partida."""
    while True:
        resposta = input("\nJogar novamente? [S/N]: ").strip().lower()

        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False

        print("Digite S para sim ou N para não.")


def main():
    print("Aprendendo Python com um pequeno projeto prático.")

    while True:
        jogar()

        if not deseja_jogar_novamente():
            print("\nObrigado por jogar!")
            break


if __name__ == "__main__":
    main()
