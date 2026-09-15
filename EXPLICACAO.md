# Explicação do Projeto

Este arquivo mostra como os principais conceitos de Python aparecem no jogo.

## 1. Importação

```python
import random
```

A biblioteca `random` permite gerar o número secreto da partida.

## 2. Funções

O projeto separa responsabilidades em funções:

- `ler_numero()` valida a entrada;
- `jogar()` controla uma partida;
- `deseja_jogar_novamente()` controla a repetição;
- `main()` organiza o programa.

Essa separação deixa o código mais fácil de entender e modificar.

## 3. Tratamento de erros

```python
try:
    valor = int(input("Digite: "))
except ValueError:
    print("Entrada inválida")
```

O programa não encerra se o usuário digitar texto no lugar de um número.

## 4. Condicionais

O programa compara o palpite com o número secreto:

```python
if palpite < numero_secreto:
    ...
elif palpite > numero_secreto:
    ...
else:
    ...
```

## 5. Repetição

O `while` mantém a partida ativa até o jogador acertar.

Outro `while` permite iniciar novas partidas.

## 6. Contador

A variável `tentativas` começa em zero e aumenta a cada palpite:

```python
tentativas += 1
```

## 7. Ponto de entrada

```python
if __name__ == "__main__":
    main()
```

Esse padrão faz o programa executar `main()` apenas quando o arquivo é iniciado diretamente.

## Desafio

Tente adicionar três dificuldades:

- fácil: 1 a 50;
- normal: 1 a 100;
- difícil: 1 a 500.

Depois compare quantas tentativas são necessárias em cada nível.
