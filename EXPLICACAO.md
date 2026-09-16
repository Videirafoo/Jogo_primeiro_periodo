# Explicação do Projeto

Este arquivo explica como os principais conceitos de Python aparecem na versão atual do jogo.

## 1. Importação

```python
import random
```

A biblioteca `random` é usada para gerar o número secreto da partida.

## 2. Configuração das dificuldades

As dificuldades ficam organizadas em um dicionário:

```python
DIFICULDADES = {
    "1": {
        "nome": "Fácil",
        "minimo": 1,
        "maximo": 50,
        "tentativas": 10,
        "multiplicador": 1,
    }
}
```

Isso evita espalhar vários números pelo código e deixa as regras fáceis de localizar.

Cada dificuldade informa:

- nome;
- número mínimo;
- número máximo;
- quantidade de tentativas;
- multiplicador da pontuação.

## 3. Funções

O programa foi dividido em funções pequenas, cada uma com uma responsabilidade.

### `ler_numero()`

Recebe a entrada do jogador e só aceita números dentro do intervalo permitido.

### `ler_opcao()`

Valida opções de menu, como dificuldade e jogar novamente.

### `escolher_dificuldade()`

Mostra o menu e retorna as regras do modo escolhido.

### `avaliar_palpite()`

Compara o palpite com o número secreto e retorna:

- `maior`;
- `menor`;
- `acertou`.

### `classificar_distancia()`

Calcula a distância entre o palpite e o número secreto usando:

```python
distancia = abs(numero_secreto - palpite)
```

Depois informa se o palpite está frio, morno, quente ou muito quente.

### `calcular_pontuacao()`

Quanto menos tentativas o jogador usa, maior a pontuação.

A dificuldade também aplica um multiplicador.

### `jogar()`

Controla uma partida completa:

1. gera o número secreto;
2. controla o limite de tentativas;
3. recebe palpites;
4. mostra dicas;
5. calcula a pontuação ao acertar;
6. encerra a partida quando as tentativas acabam.

### `deseja_jogar_novamente()`

Pergunta se outra partida deve ser iniciada.

### `main()`

Organiza o programa inteiro e mantém:

- número de partidas jogadas;
- melhor pontuação da sessão.

## 4. Tratamento de erros

O jogador pode digitar texto por engano sem encerrar o programa:

```python
try:
    valor = int(input(mensagem))
except ValueError:
    print("Entrada inválida. Digite um número inteiro.")
```

Depois o laço continua pedindo uma entrada válida.

## 5. Condicionais

O resultado do palpite é analisado com condicionais:

```python
if palpite < numero_secreto:
    return "maior"
if palpite > numero_secreto:
    return "menor"
return "acertou"
```

Esse trecho é uma das principais regras do jogo.

## 6. Repetição

Existem dois tipos principais de repetição.

### `while`

É usado para continuar pedindo uma entrada até o usuário informar um valor válido.

### `for`

É usado para limitar a quantidade de tentativas:

```python
for tentativa in range(1, limite + 1):
```

Dessa forma, a partida realmente pode terminar sem o jogador acertar.

## 7. Pontuação

A pontuação começa com um valor base e diminui conforme o número de tentativas aumenta.

Depois é aplicado o multiplicador da dificuldade.

Exemplo:

- acertar rapidamente no modo fácil gera uma boa pontuação;
- acertar rapidamente no modo difícil gera ainda mais pontos.

## 8. Testes automatizados

O arquivo `test_main.py` usa a biblioteca `unittest`, que já faz parte do Python.

Os testes verificam funções como:

- avaliação do palpite;
- proximidade do número;
- cálculo da pontuação;
- validação de entradas;
- seleção de dificuldade;
- vitória;
- derrota por limite de tentativas.

Para executar:

```bash
python -m unittest -v
```

## 9. Ponto de entrada

```python
if __name__ == "__main__":
    main()
```

Isso faz `main()` executar apenas quando `main.py` é iniciado diretamente.

Também permite que `test_main.py` importe as funções sem iniciar o jogo automaticamente.

## 10. O que melhorou em relação à primeira versão

A primeira versão já permitia adivinhar números e jogar novamente.

A versão atual adiciona:

- três dificuldades;
- limite real de tentativas;
- dicas de proximidade;
- pontuação;
- melhor pontuação da sessão;
- menu para sair;
- funções mais fáceis de testar;
- testes automatizados;
- CI executando os testes.

Mesmo com essas melhorias, o código continua usando conceitos que podem ser estudados no início da graduação.
