# OS ETERNOS — O SONHO DE VALDRAK

Jogo narrativo interativo em Python + Pygame, ambientado em Valdrak: uma terra viking presa entre sonho, magia, memória e tecnologia.

## História

O protagonista dorme em um dia comum e desperta dentro de Valdrak.

Vikings, runas, cavalos, lobos de ferro e uma força que parece conhecer as memórias dos sonhadores cercam o caminho.

O poder do protagonista é **Tecnologia**:

- Scanner de Runas;
- Mapa Holográfico;
- Pulso de Código.

Durante a jornada, outros sonhadores podem formar **Os Eternos**:

- Thorvald — Raio de Torv;
- Aurel — Olho do Céu;
- Kaion — Lâmina do Vento;
- Brenor — Fogo da Forja;
- Eiran — Cura da Aurora;
- Noctar — Sombra dos Corvos.

## Como a V2 funciona

A história começa diretamente no prólogo. Não existe menu antes do conto.

Cada trecho da narrativa aparece em uma cena própria. Depois, o jogador toma decisões que alteram Coragem, Sabedoria, Tecnologia, Amizade, Caos, Marcas, aliados, ferramentas e o final.

A campanha possui:

- prólogo com 16 momentos narrativos;
- 7 capítulos;
- escolhas ramificadas;
- 242 caminhos completos atualmente válidos;
- 5 finais;
- efeitos sonoros;
- interface gráfica redimensionável;
- fullscreen;
- HUD de atributos, aliados e tecnologia.

## Controles

| Tecla | Ação |
|---|---|
| Enter / Espaço | Revelar ou continuar a narrativa |
| 1 / 2 / 3 | Escolher uma ação |
| M | Ligar/desligar áudio |
| F11 | Tela cheia |
| Esc | Sair |
| R | Sonhar novamente após o final |

Também é possível usar o mouse.

## Rodar no Windows / VS Code

Abra o terminal na pasta do projeto:

```powershell
git switch v2-interface-grafica
git pull
```

Crie o ambiente:

```powershell
python -m venv .venv
```

Ative:

```powershell
.\.venv\Scripts\Activate.ps1
```

Atualize o ambiente desta V2:

```powershell
pip uninstall -y pygame
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Execute:

```powershell
python eternos.py
```

## Testes

```powershell
python -m unittest -v
```

Smoke gráfico:

```powershell
python eternos.py --smoke
```

## Estrutura

```text
Jogo_primeiro_periodo/
├── eternos.py
├── engine.py
├── story_data.py
├── ui.py
├── audio.py
├── test_engine.py
├── requirements.txt
├── README.md
├── EXPLICACAO.md
├── INSTRUCOES.md
└── .github/
    └── workflows/
        └── python.yml
```

## Arquitetura

### story_data.py

Conteúdo canônico recuperado do jogo original: prólogo, aliados, capítulos, escolhas, requisitos, consequências, atributos e finais.

### engine.py

Motor independente da interface: estado, aliados, ferramentas, requisitos, efeitos, progressão e seleção do final.

### ui.py

Design visual do jogo: cenas, painéis, HUD, botões, backgrounds procedurais e adaptação de tela.

### audio.py

Efeitos sonoros gerados em tempo de execução para chuva, trovão, tecnologia, runas, fogo, portal, espada e outros eventos.

### eternos.py

Loop principal da V2 gráfica.

## Princípio desta versão

A narrativa vem primeiro.

O jogo deve ser lido e vivido como um conto interativo: cena → narração → consequência → escolha → nova cena.

As escolhas mudam o caminho, mas não podem impedir o jogador de chegar ao fim da história.

## Autor

**Fernando Otávio Videira Junior**  
Engenharia de Software — Universidade de Vassouras, Campus Saquarema
