# OS ETERNOS — O Sonho de Valdrak

Action-RPG narrativo em Python/pygame-ce, desenvolvido a partir do conto **OS ETERNOS**.

A V2 combina história ramificada, exploração top-down, combate, aliados, bosses, poderes, progressão, inventário, save/load e múltiplos finais.

## Estado atual — V2 Beta

- prólogo interativo;
- 7 capítulos;
- 242 caminhos narrativos auditados;
- 5 finais;
- exploração RPG por capítulo;
- mapas TMX compatíveis com Tiled;
- tiles e sprites reais CC0 da Kenney;
- protagonista, aliados, inimigos e bosses por spritesheet;
- câmera top-down;
- colisão por object layer dos mapas;
- ataque, Pulso de Código e dash;
- seis Eternos com poderes;
- NPCs, inimigos e 7 Guardiões/Bosses;
- loot e inventário;
- XP e níveis;
- menu de pausa;
- save/load;
- galeria de finais;
- créditos;
- áudio em camadas;
- sons CC0 externos;
- build Windows automatizado com PyInstaller.

## Stack

- Python 3.12
- pygame-ce
- PyTMX
- pyscroll
- Pillow
- PyInstaller
- Tiled Map Editor para editar os mapas TMX

As dependências estão em `requirements.txt`.

## Instalação no Windows / VS Code

No PowerShell, execute **somente comandos de terminal**:

```powershell
cd C:\Users\Usuario\Jogo_primeiro_periodo
git switch v2-interface-grafica
git pull
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python eternos.py
```

> **Importante:** não cole código Python como `rects = []`, `for ...`, `if ...` ou `return ...` diretamente no PowerShell. Código Python fica nos arquivos `.py` e é executado com `python arquivo.py`.

## Controles

| Tecla | Ação |
|---|---|
| WASD / Setas | Mover |
| Espaço | Ataque |
| Q | Pulso de Código |
| Shift | Dash |
| R | Poder/ajuda de um Eterno |
| E | Falar / interagir / escolher caminho |
| 1 | Poção Nórdica |
| 2 | Essência Rúnica |
| I / Tab | Inventário |
| Esc / P | Menu de pausa |
| F5 | Salvar |
| F9 | Carregar |
| M | Áudio on/off |
| - / + | Volume |
| F11 | Tela cheia |

## Menu de pausa

`Esc` ou `P` abre:

- Continuar
- Salvar jogo
- Carregar jogo
- Inventário
- Áudio
- Controles
- Galeria de finais
- Créditos
- Sair

# Plano de construção e status

## Fase 1 — Tilemap real

**Implementado.**

- `map_loader.py`
- `assets/maps/chapter_01.tmx` até `chapter_07.tmx`
- PyTMX
- mapas editáveis no Tiled
- colisões via object layer
- tiles CC0 Kenney

## Fase 2 — Sprites

**Implementado.**

- `sprite_animator.py`
- spritesheet CC0 Kenney
- player
- aliados
- inimigos
- bosses
- estados idle, walk, attack, hurt, dash e pulse

## Fase 3 — Aliados

**Implementado.**

- Thorvald — Raio de Torv
- Aurel — Olho do Céu
- Kaion — Lâmina do Vento
- Brenor — Fogo da Forja
- Eiran — Cura da Aurora
- Noctar — Sombra dos Corvos

Eles ajudam automaticamente e também podem ser acionados com `R`.

## Fase 4 — HUD

**Implementado em `hud.py`.**

- HUD compacta
- vida e energia
- região
- XP/nível
- itens
- barra de boss
- dock de habilidades
- prompt contextual

## Fase 5 — Áudio

**Implementado em quatro camadas.**

1. ambiente;
2. combate;
3. poderes;
4. UI.

Sons externos CC0 vêm de Kenney RPG Audio e `code4fukui/sound-cc0`.

## Fase 6 — Progressão e persistência

**Implementado.**

- save/load;
- autosave;
- inventário;
- XP e nível;
- finais desbloqueáveis;
- galeria persistente.

## Fase 7 — Distribuição

**Implementado.**

- `OsEternos.spec`
- `.github/workflows/windows-beta.yml`
- geração de `OsEternosV2.exe`
- artefato Windows via GitHub Actions

## Estrutura principal

```text
Jogo_primeiro_periodo/
├── assets/
│   ├── maps/
│   ├── kenney/
│   │   ├── roguelike/
│   │   ├── characters/
│   │   ├── ui/
│   │   └── audio/
│   └── audio/cc0/
├── eternos.py
├── engine.py
├── story_data.py
├── rpg_world.py
├── rpg_entities.py
├── gameplay.py
├── map_loader.py
├── sprite_animator.py
├── hud.py
├── character_visuals.py
├── world_art.py
├── pause_menu.py
├── ending_gallery.py
├── credits.py
├── audio.py
├── savegame.py
├── OsEternos.spec
└── requirements.txt
```

## Assets e licenças

### Kenney

CC0 1.0.

Packs usados:

- Roguelike Base Pack
- Roguelike Characters Pack
- UI Adventure Pack
- RPG Audio

Crédito recomendado: **Art & audio by Kenney (kenney.nl) — CC0**.

### sound-cc0

Fonte: https://github.com/code4fukui/sound-cc0

CC0 / domínio público.

As licenças originais ficam dentro de `assets/`.

## Testes

```powershell
python -m unittest -v
python eternos.py --smoke
```

O CI valida sintaxe, testes e smoke gráfico.

## Build local

```powershell
pyinstaller --noconfirm OsEternos.spec
```

Resultado:

```text
dist/OsEternosV2.exe
```

## Build Beta pelo GitHub

Workflow:

```text
Windows V2 Beta
```

Ele instala dependências, roda testes, cria o EXE e publica o artefato `OsEternosV2-Windows`.

## Evolução depois da Beta

A base técnica fica preparada para:

1. trocar sprites Kenney por arte própria;
2. desenhar tiles exclusivos de Valdrak;
3. animações frame-a-frame;
4. retratos ilustrados;
5. trilha musical autoral;
6. mais quests e NPCs;
7. balanceamento de bosses;
8. gamepad;
9. opções gráficas e acessibilidade;
10. release candidata.

O motor foi separado dos assets para que o gráfico possa evoluir sem desmontar os sistemas de gameplay.

## V2.1 — World Expansion

A V2.1 transforma as sete regiões de Valdrak em espaços com exploração opcional, histórias próprias e atalhos secretos, além do caminho principal.

### 28 lugares exploráveis

Cada região recebeu quatro pontos especiais:

- uma ruína;
- um ponto de lore/microconto;
- um acampamento;
- uma passagem secreta.

São **28 lugares novos**, incluindo **7 passagens secretas**.

Entre eles:

- Ponte do Corvo Quebrado;
- Pântano dos Sussurros;
- Cripta das Três Chaves;
- Mercado dos Ossos;
- Taverna do Martelo Torto;
- Catacumbas do Campeão;
- Lago dos Nomes;
- Casa da Bruxa de Musgo;
- Torre da Matilha;
- Mina de Ferro Azul;
- Rio de Lava Negra;
- Arquivo dos Ferreiros;
- Biblioteca Impossível;
- Sala dos Espelhos;
- Jardim do Despertar.

### Novos contos e mistérios

Cada ponto possui um microconto conectado ao mistério central. As novas histórias introduzem:

- outros sonhadores que podem ter passado por Valdrak;
- memórias perdidas e vendidas;
- referências à faculdade dentro do sonho;
- versões alternativas dos acontecimentos;
- a origem dos Lobos de Ferro;
- projetos escondidos na Forja;
- diferentes possibilidades para o despertar;
- pistas de que Valdrak pode existir antes de Os Eternos.

### Passagens secretas

Cada região possui uma passagem própria. Ela só desperta depois que o jogador encontra outros pontos daquela região.

As passagens funcionam como atalhos físicos e narrativos: túneis, raízes, pontes invertidas, elevadores rúnicos e espaços que dobram o mapa.

### Missões regionais

Cada região ganhou uma missão secundária de exploração:

1. Os Marcos da Estrada;
2. As Três Chaves do Portão;
3. Juramentos da Vila;
4. Vozes Entre as Raízes;
5. A Trilha da Matilha;
6. Segredos da Forja Morta;
7. Fragmentos do Despertar.

Ao descobrir três pontos de uma região, a missão regional é concluída e concede XP extra e uma **Chave Rúnica**.

### Novos itens e recompensas

O inventário agora também registra:

- Relíquia de Memória;
- Chave Rúnica.

Descobertas podem entregar XP, fragmentos, relíquias, poções, cura, energia e chaves.

### Graphic Overhaul V2.1

A captura real da V2 Beta mostrou excesso de microtiles, contraste muito claro no HUD e elementos procedurais fora de escala. A V2.1 corrige essa direção:

- macrotiles visuais de 48 px;
- menos mosaico aleatório e ruído;
- tint própria para cada uma das sete regiões;
- remoção de árvores/pedras procedurais gigantes quando o TMX está ativo;
- sprites menores e mais proporcionais;
- HUD escura, compacta e com maior área livre para o mundo;
- HUD com descobertas, missão regional, relíquias e chaves;
- colisões centrais removidas dos mapas gerados para evitar paredes invisíveis;
- atmosfera procedural preservada apenas como camada cinematográfica.

Arquivos principais desta etapa:

- `world_expansion.py`
- `map_loader.py`
- `hud.py`
- `rpg_world.py`
- `test_world_expansion.py`

A próxima evolução visual continua preparada para substituir gradualmente os assets CC0 por arte autoral de Valdrak, sem reescrever os sistemas de exploração e narrativa.
