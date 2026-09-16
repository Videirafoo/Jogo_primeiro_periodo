# Explicação do Projeto

Este arquivo explica os principais conceitos de Python usados na versão atual do **Desafio do Número Secreto**.

## 1. Importações

```python
import json
import random
from pathlib import Path
```

Cada importação tem uma função:

- `random`: gera o número secreto;
- `json`: salva e carrega o progresso do jogador;
- `Path`: facilita trabalhar com o arquivo de dados.

## 2. Configuração das dificuldades

As dificuldades ficam em um dicionário:

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

Cada modo informa:

- nome;
- número mínimo;
- número máximo;
- quantidade de tentativas;
- multiplicador de pontuação.

Isso deixa as regras centralizadas e fáceis de alterar.

## 3. Entrada do jogador

### `ler_opcao()`

Valida opções de menu, como dificuldade e jogar novamente.

### `ler_nome()`

Lê o nome informado pelo jogador.

Se o jogador apenas pressionar Enter, o programa usa:

```text
Jogador
```

## 4. Comparação do palpite

A função `avaliar_palpite()` compara o valor informado com o número secreto:

```python
if palpite < numero_secreto:
    return "maior"
if palpite > numero_secreto:
    return "menor"
return "acertou"
```

O retorno informa se o próximo palpite deve ser maior, menor ou se o jogador acertou.

## 5. Dica de proximidade

A função `classificar_distancia()` calcula a distância entre o palpite e o número secreto:

```python
distancia = abs(numero_secreto - palpite)
```

Depois transforma essa distância em uma proporção do intervalo do modo.

Isso é importante porque os modos usam intervalos diferentes:

- Fácil: 1 a 50;
- Normal: 1 a 100;
- Difícil: 1 a 500.

Assim, os conceitos de frio, morno, quente e muito quente funcionam de forma mais justa em todas as dificuldades.

## 6. Faixa possível

Durante a partida, o jogo mantém dois valores:

```python
limite_inferior
limite_superior
```

Se o número secreto for maior que o palpite, o limite inferior aumenta.

Se for menor, o limite superior diminui.

Exemplo:

```text
Faixa atual: 1 a 100
Palpite: 50
O número secreto é MAIOR.

Nova faixa:
51 a 100
```

Isso torna a partida mais estratégica e ajuda o jogador a usar lógica.

## 7. Palpites repetidos

Os números já tentados são guardados em um conjunto:

```python
palpites_usados = set()
```

Antes de consumir uma tentativa, o programa verifica:

```python
if palpite in palpites_usados:
```

Se o número já foi usado, o jogador recebe um aviso e não perde tentativa.

## 8. Sistema de dica

Durante a partida é possível digitar:

```text
DICA
```

A função `gerar_dica()` informa:

- se o número é par ou ímpar;
- se é divisível por 5.

A dica só pode ser usada uma vez em cada partida.

Para manter o equilíbrio, ela reduz a pontuação final em 15%.

## 9. Pontuação

A função `calcular_pontuacao()` começa com uma pontuação base.

Quanto mais tentativas forem usadas, menor fica essa pontuação.

Depois o multiplicador da dificuldade é aplicado.

Se o jogador usou a dica:

```python
pontos = int(pontos * 0.85)
```

Isso mantém uma decisão de jogo: receber ajuda ou tentar conquistar a pontuação máxima.

## 10. Salvando o progresso em JSON

O arquivo usado é:

```text
dados_jogador.json
```

O programa salva:

```python
{
    "partidas": 0,
    "vitorias": 0,
    "melhor_pontuacao": 0,
    "melhor_por_modo": {}
}
```

### `carregar_estatisticas()`

Procura o arquivo e carrega os dados já existentes.

Se o arquivo ainda não existir ou estiver inválido, o programa usa os valores iniciais.

### `salvar_estatisticas()`

Usa `json.dump()` para gravar as estatísticas no computador.

### `atualizar_estatisticas()`

Atualiza:

- quantidade de partidas;
- vitórias;
- melhor pontuação geral;
- recorde de cada dificuldade.

## 11. Tratamento de erros

Durante a partida, o jogador pode digitar texto que não seja um número.

O código usa:

```python
try:
    palpite = int(entrada)
except ValueError:
    print("Entrada inválida. Digite um número ou DICA.")
```

Dessa forma, o programa não fecha quando o usuário comete um erro de digitação.

O carregamento do JSON também possui tratamento de erros para impedir que um arquivo inválido quebre o jogo.

## 12. Repetição

O jogo usa principalmente `while`.

Na partida:

```python
while tentativa <= limite:
```

O laço continua até o jogador acertar ou usar todas as tentativas.

Também existem laços de validação que continuam pedindo uma opção enquanto ela for inválida.

## 13. Função `jogar()`

A função `jogar()` controla uma partida completa:

1. gera o número secreto;
2. cria a faixa inicial;
3. registra palpites já usados;
4. aceita número ou `DICA`;
5. valida a entrada;
6. compara o palpite;
7. atualiza a faixa possível;
8. mostra a proximidade;
9. calcula a pontuação;
10. retorna `0` em caso de derrota.

## 14. Função `main()`

A função `main()` organiza o programa inteiro:

1. mostra o título;
2. lê o nome;
3. carrega o progresso salvo;
4. mostra as estatísticas;
5. pede a dificuldade;
6. inicia a partida;
7. atualiza e salva os dados;
8. pergunta se o jogador quer continuar.

## 15. Testes automatizados

O arquivo `test_main.py` usa `unittest`.

A suíte verifica regras como:

- comparação do palpite;
- proximidade adaptativa;
- cálculo de pontuação;
- penalidade ao usar dica;
- geração das dicas;
- escolha de dificuldade;
- vitória;
- derrota;
- palpite repetido sem gastar tentativa;
- salvar e carregar estatísticas;
- recuperação quando o JSON está corrompido.

Para executar:

```bash
python -m unittest -v
```

## 16. GitHub Actions

O arquivo `.github/workflows/python.yml` executa automaticamente:

1. validação da sintaxe;
2. testes automatizados.

Assim, alterações futuras podem ser verificadas no GitHub.

## 17. Ponto de entrada

```python
if __name__ == "__main__":
    main()
```

Isso faz o jogo iniciar apenas quando `main.py` é executado diretamente.

Também permite que `test_main.py` importe as funções sem iniciar uma partida automaticamente.

## 18. Evolução da versão

A versão atual possui:

- três dificuldades;
- limite real de tentativas;
- faixa possível atualizada durante a partida;
- dicas de proximidade adaptadas ao modo;
- comando `DICA`;
- penalidade de pontuação ao usar ajuda;
- proteção contra palpites repetidos;
- nome do jogador;
- estatísticas persistentes em JSON;
- taxa de vitória;
- recorde geral;
- recorde por dificuldade;
- testes automatizados;
- CI no GitHub Actions.

Mesmo com as melhorias, o projeto continua usando conceitos acessíveis para quem está aprendendo programação em Python.
