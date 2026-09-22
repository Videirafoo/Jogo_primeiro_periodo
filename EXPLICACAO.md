# Explicação — OS ETERNOS V2

## 1. Direção correta do projeto

A V2 representa o jogo narrativo **OS ETERNOS — O Sonho de Valdrak**.

O jogo de adivinhação numérica foi preservado separadamente e não faz parte desta branch.

## 2. Fluxo

Ao executar `python eternos.py`, o jogador entra diretamente na primeira frase do conto.

Não existe tela Iniciar.

```text
Prólogo
  ↓
Primeiro desafio jogável
  ↓
Capítulo
  ↓
Cena narrativa
  ↓
Escolha
  ↓
Desafio jogável
  ↓
Consequência
  ↓
Atributos / aliados / tecnologia
  ↓
Próximo capítulo
  ↓
Final determinado pelo caminho
```

## 3. Estado do jogo

O motor mantém coragem, sabedoria, tecnologia, caos, amizade, marcas, ferramentas, aliados e histórico de escolhas.

## 4. Tecnologia

O protagonista possui três instrumentos apresentados no próprio prólogo:

- Scanner de Runas;
- Mapa Holográfico;
- Pulso de Código.

A V2 inicia o estado de acordo com essa narrativa para impedir contradições e caminhos bloqueados.

## 5. Aliados

Os aliados possuem nome, poder e descrição. Eles podem liberar opções especiais ao longo da história.

## 6. Escolhas

Algumas escolhas exigem um aliado ou instrumento. Quando um requisito não existe, a opção aparece visualmente bloqueada, mas as demais continuam disponíveis.

Uma verificação automatizada percorre todos os caminhos válidos da campanha.

```text
242 caminhos completos
0 caminhos sem saída
```

## 7. Finais

O motor verifica os finais em ordem e escolhe o primeiro cujas condições foram alcançadas.

Há finais relacionados ao grupo de aliados, tecnologia e sabedoria, marcas de Valdrak, caos e um final padrão.

## 8. Interface gráfica

A tela lógica é 1280x720 e é escalada para a janela real, preservando proporção.

O HUD foi reorganizado em uma faixa superior compacta para impedir sobreposição entre status, tecnologia, narrativa e botão de continuar. As escolhas usam a largura útil e os desafios têm área própria de ação.

## 9. Narração

A narrativa é revelada progressivamente. Enter/Espaço revela o restante do texto e, no próximo acionamento, avança.

## 10. Gameplay

Além dos desafios, cada capítulo agora possui uma área explorável em `rpg_world.py`.

Nela o jogador pode:

- mover o protagonista com câmera seguindo;
- lutar contra lobos;
- usar ataque corpo a corpo;
- usar Pulso de Código;
- executar dash;
- ganhar XP e subir de nível;
- ver aliados acompanhando o personagem;
- conversar com um NPC em cada capítulo;
- enfrentar lobos, saqueadores e corvos sombrios;
- derrotar um Guardião/Boss por capítulo;
- coletar poções, essências e fragmentos;
- abrir um inventário visual com `I`/`TAB`;
- receber assistência automática dos Eternos já encontrados;
- ver poderes próprios de Thorvald, Aurel, Kaion, Brenor, Eiran e Noctar;
- receber hit-stop, screen shake e flashes em impactos;
- conversar com NPCs usando retratos e caixa de diálogo;
- enfrentar bosses com aura visual própria;
- escolher o caminho chegando fisicamente a um santuário e pressionando `E`.

O módulo `gameplay.py` mantém três famílias de desafio:

- exploração de runas com movimento;
- timing para combate, portões e tecnologia;
- esquiva de machados e lobos.

Falhar não bloqueia a campanha. Sucesso concede bônus coerentes com o capítulo; falha adiciona Caos.

## 11. Áudio

O módulo `audio.py` separa ambiente contínuo de efeitos. Chuva, vento, bosque, fogo, tecnologia e portal permanecem tocando em loop, enquanto acontecimentos como trovão, espada, machado, cavalo, lobo, runa e portão usam canais de SFX.

A tecla M controla o áudio.

## 12. Testes

`test_engine.py`, `test_gameplay.py`, `test_rpg_world.py`, `test_savegame.py` e `test_audio.py` validam narrativa, requisitos, caminhos, exploração, combate, progressão, save/load, desafios, integração e áudio.

O GitHub Actions também executa um smoke gráfico headless da campanha completa.

## 13. Save e áudio

`savegame.py` salva capítulo, atributos narrativos, aliados e progressão RPG. `F5` salva e `F9` carrega.

O volume geral pode ser ajustado com `-` e `+`, além do mute com `M`.

## 14. Próxima evolução

- ilustrações próprias para cada capítulo;
- retratos dos aliados;
- partículas específicas;
- transições cinematográficas;
- galeria de finais;
- créditos;
- empacotamento Windows.


## Graphic Overhaul V2 Beta

A V2 usa mapas TMX via PyTMX, tiles e sprites CC0 da Kenney, HUD própria, galeria de finais e pipeline PyInstaller para Windows.

Para rodar, use apenas comandos no PowerShell. Código Python deve permanecer nos arquivos .py e nunca deve ser colado linha por linha no PowerShell.

## World Expansion V2.1

A nova etapa amplia Valdrak com 28 pontos especiais distribuídos nas sete regiões: ruínas, acampamentos, microcontos e sete passagens secretas. O jogador registra descobertas, Relíquias de Memória e Chaves Rúnicas, e cada região possui uma missão secundária concluída após três descobertas.

O tilemap também foi revisto com macrotiles de 48 px, menos ruído visual, tint própria por região, sprites mais proporcionais e HUD escura/compacta.

## Combat & Audio Art Pass V2.2

A V2.2 inicia a substituição definitiva dos elementos temporários de combate por identidade autoral de Valdrak. O protagonista possui silhueta própria, manopla rúnica e espada visível. NPCs ganharam roupa, elmo e ferramentas próprias. Machados vikings agora possuem cabo de madeira, couro, cabeça de aço, fio, runas, rotação e rastro de movimento. Hroth usa dois machados e os demais Guardiões recebem armas diferentes.

O áudio de combate passou a priorizar o banco autoral assets/audio/valdrak com variantes de passos, cortes, impactos, machados, escudos, runas e derrota de Guardião.

## Adventure From First Second V2.3

A V2.3 inicia diretamente na exploração de Valdrak. O tutorial usa ações reais do jogador, a narrativa aparece dentro do mundo e cada região recebeu três baús de aventura.


## Living Valdrak V2.4

A V2.4 adiciona mundo vivo, eventos aleatórios, interiores, puzzles, oito famílias de inimigos, loot com raridades, sete Guardiões com movesets únicos, mapa mundial, Fast Travel, Quest Log, Codex e trilha dinâmica.

## Visual RPG & Systems Pass V2.5

A V2.5 é o maior passe de RPG da linha V2: sprite-sheets autorais com oito direções, frame-a-frame, iluminação dinâmica, dungeons multi-sala, Combat 2.0, Loot 2.0, crafting, upgrades, talentos, vendedores, save slots, gamepad e acessibilidade.

## World & Quest Quality Pass V2.6

A V2.6 adiciona vilas com rotinas, horário persistente, diálogos condicionais, quests multi-etapa com escolhas e consequências, contratos, caçadas, segredos, lore e encontros únicos. O World Art II acrescenta rios, montanhas, cachoeira, lava, cidades, castelos, templos e landmarks. Cinemáticas in-engine e trilhas regionais/boss completam o passe.
