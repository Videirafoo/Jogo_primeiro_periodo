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

A V2 mistura narrativa, decisão e gameplay. O jogador lê a cena, escolhe um caminho e entra em desafios jogáveis que alteram atributos e consequências.

A campanha possui:

- prólogo com 16 momentos narrativos e primeiro desafio ainda no prólogo;
- 7 capítulos;
- escolhas ramificadas;
- exploração top-down por capítulo com câmera seguindo o personagem;
- combate corpo a corpo contra lobos de ferro;
- Pulso de Código com energia e cooldown;
- dash;
- XP e níveis;
- aliados acompanhando o protagonista;
- três santuários físicos para escolher caminhos;
- exploração de runas com WASD/setas;
- desafios de timing para combate, portões e tecnologia;
- esquiva de machados e lobos de ferro;
- desempenho do jogador afetando Coragem, Sabedoria, Tecnologia e Caos;
- 242 caminhos completos atualmente válidos;
- 5 finais;
- áudio ambiente contínuo para chuva, vento, bosque, fogo, tecnologia e portal;
- efeitos sonoros separados para acontecimentos;
- interface gráfica redimensionável;
- fullscreen;
- HUD compacto de atributos, aliados e tecnologia.

## Controles

| Tecla | Ação |
|---|---|
| Enter / Espaço | Revelar/continuar narrativa ou acertar desafios de timing |
| 1 / 2 / 3 | Escolher uma ação |
| WASD / Setas | Mover no scanner de runas e nas esquivas |
| Clique | Escolher ações e interagir em desafios |
| E | Interagir com santuários/caminhos |
| Espaço | Ataque corpo a corpo durante exploração |
| Q | Pulso de Código |
| Shift | Dash |
| M | Ligar/desligar áudio |
| - / + | Ajustar volume |
| F5 | Salvar |
| F9 | Carregar |
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
├── gameplay.py
├── rpg_world.py
├── savegame.py
├── story_data.py
├── ui.py
├── audio.py
├── test_engine.py
├── test_gameplay.py
├── test_rpg_world.py
├── test_savegame.py
├── test_audio.py
├── REFERENCIAS_RPG.md
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

### gameplay.py

Desafios jogáveis da campanha: rastreamento de runas, timing e esquiva.

### rpg_world.py

Exploração top-down: jogador, câmera, colisão, inimigos, combate, Pulso de Código, dash, partículas, XP, nível, aliados acompanhantes e santuários de decisão.

### savegame.py

Persistência do capítulo, atributos narrativos, aliados e progressão RPG.

### audio.py

Áudio procedural separado em ambiente contínuo e efeitos de acontecimentos. Chuva, vento, bosque, fogo, tecnologia e portal usam loops próprios; trovão, espada, machado, cavalo, lobo, runa e outros eventos usam SFX independentes.

### eternos.py

Loop principal da V2 gráfica.

## Princípio desta versão

Narrativa e gameplay trabalham juntos.

O fluxo principal é: cena → escolha → desafio jogável → consequência → progressão → nova cena.

As escolhas mudam o caminho, mas não podem impedir o jogador de chegar ao fim da história.

## Autor

**Fernando Otávio Videira Junior**  
Engenharia de Software — Universidade de Vassouras, Campus Saquarema
