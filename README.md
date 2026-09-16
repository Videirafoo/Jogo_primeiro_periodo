# Jogo de Adivinhação em Python

Projeto didático do primeiro período que transforma fundamentos de Python em um **jogo completo, executável e testado**.

**Nível:** iniciante  
**Objetivo:** praticar lógica de programação usando um jogo de terminal simples de entender, jogar e modificar.

## Como jogar

O computador escolhe um número secreto e você tenta descobri-lo antes de acabar o limite de tentativas.

Durante a partida, o jogo informa:

- se o número secreto é maior ou menor que o palpite;
- se o palpite está frio, morno, quente ou muito quente;
- quantas tentativas ainda restam;
- a pontuação conquistada ao acertar.

Quanto menos tentativas forem usadas, maior a pontuação.

## Dificuldades

| Modo | Intervalo | Tentativas | Pontuação |
|---|---:|---:|---:|
| Fácil | 1 a 50 | 10 | multiplicador x1 |
| Normal | 1 a 100 | 8 | multiplicador x2 |
| Difícil | 1 a 500 | 10 | multiplicador x3 |

O programa também guarda a **melhor pontuação da sessão** enquanto estiver aberto.

## Executar

É necessário ter Python 3 instalado.

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

Os testes verificam as principais regras do jogo, incluindo comparação de palpites, dicas de proximidade, pontuação, validação de entrada, dificuldades e partidas completas.

## O que este projeto pratica

- variáveis e constantes;
- funções;
- dicionários;
- `if`, `elif` e `else`;
- `for` e `while`;
- tratamento de erros com `try/except`;
- validação de entrada;
- números aleatórios com `random`;
- contadores e pontuação;
- organização com `main()`;
- testes automatizados com `unittest`;
- GitHub Actions.

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

## Fluxo do programa

```text
iniciar
  ↓
escolher dificuldade
  ↓
gerar número secreto
  ↓
receber palpite
  ↓
validar entrada
  ↓
comparar palpite
  ↓
mostrar dica
  ↓
acertou? ── não ──→ próxima tentativa
  ↓ sim
calcular pontuação
  ↓
mostrar resultado
  ↓
jogar novamente?
```

## Como estudar este projeto

1. execute uma partida em cada dificuldade;
2. abra `main.py` e localize a função de cada parte do jogo;
3. leia `EXPLICACAO.md`;
4. execute `python -m unittest -v`;
5. altere uma regra simples, como quantidade de tentativas;
6. execute os testes novamente e observe se o comportamento continua correto.

## Qualidade

O GitHub Actions executa automaticamente:

1. validação da sintaxe Python;
2. suíte de testes com `unittest`.

Isso permite verificar cada nova alteração sem depender somente de testes manuais.

## Possíveis evoluções futuras

Estas ideias não fazem parte da versão atual:

- ranking persistido em JSON;
- escolha de nome do jogador;
- recorde salvo entre execuções;
- interface gráfica;
- versão web.

O projeto continua propositalmente simples para que o código permaneça compatível com o nível de aprendizagem de um estudante no início do curso.

## Autor

**Fernando Otávio Videira Junior**  
Engenharia de Software — Universidade de Vassouras, Campus Saquarema
