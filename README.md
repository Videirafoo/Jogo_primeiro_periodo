# Jogo de Adivinhação em Python

Pequeno projeto didático para quem está começando em programação e quer transformar fundamentos de Python em um **programa completo e executável**.

**Nível:** iniciante  
**Objetivo:** sair de exercícios isolados e entender como várias estruturas trabalham juntas em um mesmo fluxo.

## O que este projeto ensina

- variáveis;
- funções;
- `if`, `elif` e `else`;
- laços `while`;
- tratamento de erros com `try/except`;
- validação de entrada;
- números aleatórios;
- organização com `main()`;
- repetição de partidas.

## Como funciona

O computador escolhe um número aleatório entre **1 e 100**. O jogador informa palpites e recebe dicas dizendo se o número secreto é maior ou menor.

Ao acertar, o programa mostra a quantidade de tentativas e pergunta se o usuário deseja jogar novamente.

## Executar

```bash
python main.py
```

## Estrutura

```text
jogo_primeiro_periodo/
├── main.py
├── README.md
├── EXPLICACAO.md
├── .gitignore
└── .github/
    └── workflows/
        └── python.yml
```

## Como estudar este projeto

1. execute uma partida completa;
2. leia `EXPLICACAO.md`;
3. identifique onde o programa valida entradas;
4. altere o intervalo do número secreto;
5. implemente uma melhoria sem copiar a solução pronta;
6. teste manualmente antes de fazer commit.

## Desafios de evolução

- [ ] níveis de dificuldade;
- [ ] limite de tentativas;
- [ ] sistema de pontuação;
- [ ] ranking salvo em JSON;
- [ ] testes automatizados;
- [ ] interface gráfica;
- [ ] versão web;
- [ ] versão mobile.

## Qualidade

O GitHub Actions valida automaticamente a sintaxe Python em pushes e pull requests.

## Próximo passo

Depois deste projeto, o caminho recomendado é criar mini sistemas com **arquivos/JSON, CRUD, validação e testes**.

## Tecnologias

`Python 3` · `Git` · `GitHub Actions`

## Autor

**Fernando Otávio Videira Junior**  
Engenharia de Software — Universidade de Vassouras, Campus Saquarema

> Um projeto pequeno, mas completo, ensina mais integração de conceitos do que vários exercícios desconectados.