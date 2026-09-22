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


## V2.2 — Combat & Audio Art Pass

A V2.2 substitui elementos temporários de combate por arte autoral de Valdrak.

- machados vikings redesenhados com cabo de madeira, couro, aço, fio e runas;
- machados arremessados agora giram e deixam motion trail;
- protagonista recebeu silhueta autoral, capa, túnica, botas, manopla rúnica e espada visível;
- NPCs receberam corpo, roupa, elmo e ferramentas coerentes com cada região;
- Hroth agora usa dois machados e os demais Guardiões recebem armas visualmente distintas;
- saqueadores passam a carregar machados reais no mundo;
- novo banco de áudio procedural autoral em assets/audio/valdrak;
- três variações de whoosh de machado;
- três impactos de machado;
- três cortes de espada;
- dois impactos de lâmina;
- quatro passos em terreno;
- dois impactos de escudo;
- novo pulso rúnico e impacto de derrota de boss;
- golpes que acertam inimigos agora disparam som de impacto separado do som de corte.

Os novos WAVs são gerados sem samples de terceiros e documentados em assets/audio/valdrak/SOURCE.md.

## V2.3 — Adventure From First Second

A V2.3 começa com controle imediato do personagem em Valdrak. O tutorial acontece dentro do mapa: movimento, ataque, Pulso de Código, dash e conversa com Edda. A narrativa antiga passa a aparecer como ecos e diálogos durante a exploração.

Também entraram 21 baús de aventura, três por região, com recompensas, relíquias, XP e armadilhas.

Os seis Eternos recebem silhuetas e equipamentos próprios: Thorvald com machado e raio, Aurel com cajado dourado, Kaion com espada do vento, Brenor com martelo, Eiran com cajado da aurora e Noctar com máscara e lâminas duplas.


## V2.4 — Living Valdrak

A V2.4 transforma o mapa em um mundo mais vivo. Entraram eventos aleatórios, emboscadas, viajantes, patrulhas vikings, animais e caravanas.

Cada região ganhou seis pontos de aventura:
- Altar Escondido;
- Acampamento Inimigo;
- Caverna Rúnica;
- Casa Abandonada;
- Templo Antigo;
- Masmorra de Valdrak.

Cavernas, casas, templos e masmorras possuem interiores e puzzles rúnicos. Altares liberam Fast Travel. O mapa mundial abre com M, Quest Log com J, Codex com C e equipamentos com G.

O combate recebeu oito famílias de inimigos:
- Viking Raider;
- Berserker;
- Archer;
- Rune Mage;
- Iron Wolf;
- Alpha Wolf;
- Shadow Raven;
- Elite Raider.

O Loot System agora possui:
- armas;
- armaduras;
- amuletos;
- runas;
- raridades Comum, Raro, Épico e Lendário;
- atributos de ataque, defesa, crítico e energia;
- autoequip de itens melhores.

Os sete Guardiões receberam três movimentos próprios cada, telegraph, segunda fase e barra interna de stagger. Ataques normais, Pulso e ataque pesado contribuem para atordoar bosses.

A trilha sonora passou a trocar dinamicamente entre exploração, perigo, boss e interior.

O protagonista possui estados de idle, walk, run, attack1, attack2, heavy, dash, hurt, death e power, com direção calculada em oito orientações.

## V2.5 — Visual RPG & Systems Pass

A V2.5 cria sprite-sheets autorais para o protagonista, seis Eternos, oito famílias de inimigos e sete Guardiões. Os personagens possuem oito direções e estados frame-a-frame para idle, walk, run, combos, ataque pesado, dash, dano, morte e poderes.

O QA visual da V2.4 também motivou mudanças de composição: os seis aliados agora usam formação em duas fileiras, evitando a pilha visual sobre o protagonista, e a caixa de diálogo foi reduzida. Lore e lugares usam emblemas rúnicos em vez de um retrato humano genérico.

Entraram iluminação dinâmica, água animada, vegetação com sway, partículas ambientais e color grading cinematográfico.

Dungeon System II adiciona cinco salas, portas, armadilhas, puzzle, chave, mini-boss e cofre final.

Combat 2.0 adiciona stamina, parry, perfect dodge, combo de três passos, ataque pesado, knockback, status effects e execução de Guardião atordoado.

Loot 2.0 adiciona materiais, crafting, upgrade de arma, talentos, pontos de talento, vendedores, moedas e quests encadeadas de NPC.

A plataforma passa a oferecer três save slots, gamepad, acessibilidade, redução de flash, screen shake configurável e três dificuldades.

## V2.6 — World & Quest Quality Pass

A V2.6 faz Valdrak reagir ao jogador em vez de funcionar apenas como um mapa de combate.

### Mundo vivo
- sete vilas povoadas;
- sete moradores por região;
- NPCs caminham entre casa, trabalho e mercado;
- ciclo de horário persistente;
- diálogos condicionais por horário, Guardião e consequências;
- eventos raros por região;
- um encontro único por região;
- dois segredos de lore por região;
- mini-histórias regionais.

### Quest Quality
Cada região recebe uma quest multi-etapa com objetivo, retorno ao NPC, decisão entre dois caminhos, consequência persistente, descoberta de segredo e recompensa. Também existem três contratos/caçadas por região.

### Art Quality Pass IV / World Art II
- personagens maiores;
- seis Eternos simultâneos;
- partículas de poder;
- impactos estilizados;
- vilas nórdicas;
- montanhas;
- rios;
- cachoeira;
- lava dinâmica;
- castelos;
- templos;
- cidade/arena;
- landmarks;
- mudanças visuais conforme escolhas.

### Cinemáticas / áudio
- entrada de região;
- primeira aproximação do Guardião;
- decisões de quest;
- eventos raros;
- derrota de Guardião;
- cues pseudo-vocais;
- SFX de segredo, contrato e conclusão;
- trilha procedural diferente para cada região;
- perigo, interiores e boss por região.

Nenhuma dependência nova foi adicionada ao requirements.txt.

## V2.7 — Combat, Animation & World Quality

A V2.7 é um passe de qualidade sobre a V2.6.

### V2.6.1 Visual QA
- regressão automática de sobreposição dos seis Eternos;
- teste de clipping das portas/colisões;
- validação dos cinco interiores por região;
- smoke nativo incluído no gate.

### NPC Art Pass
Cada profissão possui roupa, paleta, rosto, cabelo e acessório próprios:
- vidente;
- ferreiro;
- caçador;
- mercador;
- guarda;
- curandeira;
- viajante.

### Combat & Animation Quality
- sprite-sheets passam de 4 para 6 frames;
- parry, dodge, knockdown e execução entram como estados;
- anticipation / active / recovery;
- hit reaction;
- weapon trails;
- perfect-dodge ghost;
- feedback visual de parry;
- câmera/impact feedback;
- cinemática de fase 2 dos bosses.

### World Quality III
Cada região possui taverna, ferreiro, loja, casa e salão com portas, colisão coerente e interiores conectados. Existem moradores nos interiores, ciclo dia/noite, janelas e tochas noturnas, além de clima com impacto real em movimento e stamina.

### Quest System II
- marcadores de objetivo;
- reputação;
- três facções;
- duas quests opcionais por região;
- escolhas alimentam reputação;
- final de Valdrak calculado a partir do estado do mundo.

### Audio Production Pass
- loops regionais mais longos;
- layers procedurais;
- passos em grama, pedra, madeira e neve;
- sons de vila, noite, taverna, ferreiro e portas;
- hooks para voice acting em assets/audio/voices, com fallback procedural.
