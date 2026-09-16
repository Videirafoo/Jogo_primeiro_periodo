# Desafio do Número Secreto — Jogo em Python

Projeto didático em Python que transforma fundamentos de programação em um jogo de terminal completo, rejogável, testado e com progresso local.

**Nível:** iniciante  
**Objetivo:** praticar lógica de programação usando um jogo simples de entender, jogar e modificar.

## Como funciona

O computador escolhe um número secreto e o jogador precisa descobri-lo antes de acabar o limite de tentativas.

Durante a partida, o jogo informa:

- se o número secreto é maior ou menor que o palpite;
- se o palpite está frio, morno, quente ou muito quente;
- a faixa possível atual do número secreto;
- quantas tentativas ainda restam;
- a pontuação conquistada ao acertar.

Palpites repetidos não gastam tentativa.

## Dificuldades

| Modo | Intervalo | Tentativas | Multiplicador |
|---|---:|---:|---:|
| Fácil | 1 a 50 | 10 | x1 |
| Normal | 1 a 100 | 8 | x2 |
| Difícil | 1 a 500 | 10 | x3 |

As dicas de proximidade são calculadas proporcionalmente ao tamanho do intervalo. Assim, o modo difícil continua justo mesmo usando números muito maiores.

## Sistema de dica

Durante uma partida, digite:

```text
DICA
```

O jogo informa características do número secreto, como:

- se ele é par ou ímpar;
- se é divisível por 5.

A dica pode ser usada apenas uma vez por partida e reduz a pontuação final em 15%.

## Pontuação

Quanto menos tentativas forem usadas, maior será a pontuação.

A dificuldade aplica um multiplicador e o uso da dica aplica uma pequena penalidade.

Exemplo:

- acertar rapidamente no Fácil gera uma boa pontuação;
- acertar rapidamente no Difícil gera uma pontuação maior;
- usar `DICA` ajuda, mas reduz o total recebido.

## Progresso salvo

O jogo registra automaticamente em `dados_jogador.json`:

- partidas jogadas;
- vitórias;
- taxa de vitória;
- melhor pontuação geral;
- melhor pontuação por dificuldade.

Esse arquivo é criado localmente ao jogar e está no `.gitignore`, portanto não é enviado para o GitHub.

## Executar no VS Code

1. abra a pasta do projeto no VS Code;
2. abra o terminal integrado;
3. execute:

```bash
python main.py
```

No Windows também pode funcionar com:

```bash
py main.py
```

Não existem bibliotecas externas para instalar.

## Executar os testes

```bash
python -m unittest -v
```

A suíte cobre as principais regras do jogo, incluindo:

- comparação de palpites;
- proximidade adaptativa;
- cálculo de pontuação;
- penalidade da dica;
- geração de dicas;
- escolha de dificuldade;
- vitória e derrota;
- palpite repetido sem perda de tentativa;
- criação, atualização e leitura das estatísticas em JSON.

## Conceitos de Python praticados

- variáveis e constantes;
- funções;
- dicionários;
- listas e conjuntos (`set`);
- `if`, `elif` e `else`;
- `for` e `while`;
- `try/except`;
- validação de entrada;
- números aleatórios com `random`;
- leitura e escrita de JSON;
- arquivos com `pathlib.Path`;
- contadores, recordes e pontuação;
- organização com `main()`;
- testes automatizados com `unittest`;
- automação com GitHub Actions.

## Estrutura

```text
Jogo_primeiro_periodo/
├── main.py
├── test_main.py
├── README.md
├── EXPLICACAO.md
├── .gitignore
└── .github/
    └── workflows/
        └── python.yml
```

Ao jogar, também é criado localmente:

```text
dados_jogador.json
```

## Fluxo do jogo

```text
iniciar
  ↓
informar nome
  ↓
carregar progresso
  ↓
escolher dificuldade
  ↓
gerar número secreto
  ↓
receber palpite ou DICA
  ↓
validar entrada
  ↓
comparar palpite
  ↓
atualizar faixa possível + mostrar proximidade
  ↓
acertou? ── não ──→ próxima tentativa
  ↓ sim
calcular pontuação
  ↓
atualizar e salvar estatísticas
  ↓
jogar novamente?
```

## Como estudar este projeto

1. execute uma partida em cada dificuldade;
2. teste o comando `DICA`;
3. tente repetir um palpite e observe que a tentativa não é perdida;
4. termine uma partida e abra `dados_jogador.json`;
5. leia `main.py` e `EXPLICACAO.md`;
6. execute `python -m unittest -v`;
7. altere uma regra simples e execute os testes novamente.

## Qualidade

O GitHub Actions executa automaticamente:

1. validação da sintaxe Python;
2. suíte de testes com `unittest`.

Isso ajuda a impedir que alterações futuras quebrem regras já funcionando.

## Próximas evoluções possíveis

Sem mudar a proposta didática, o projeto ainda pode evoluir para:

- ranking com vários jogadores;
- conquistas;
- modos de jogo adicionais;
- interface gráfica com Tkinter ou Pygame;
- versão web.

## Autor

**Fernando Otávio Videira Junior**  
Engenharia de Software — Universidade de Vassouras, Campus Saquarema
