# Rodar OS ETERNOS V2 no Windows

Se você já clonou a branch anteriormente:

```powershell
cd C:\Users\Usuario\Jogo_primeiro_periodo
git switch v2-interface-grafica
git pull
```

Ative a venv:

```powershell
.\.venv\Scripts\Activate.ps1
```

Troque o Pygame antigo pelo pygame-ce usado pelo projeto:

```powershell
pip uninstall -y pygame
pip install -r requirements.txt
```

Execute:

```powershell
python eternos.py
```

Não use `app_pygame.py`. Esse arquivo pertencia ao protótipo de adivinhação arquivado.

## Controles de jogo

- `Enter` / `Espaço`: continuar narrativa;
- `1`, `2`, `3`: escolher caminhos;
- `WASD` / setas: mover na exploração, scanner e esquiva;
- `E`: conversar com NPCs, interagir com santuários e escolher caminhos;
- `Espaço`: ataque corpo a corpo na exploração ou timing nos desafios;
- `Q`: Pulso de Código;
- `Shift`: dash;
- `1`: usar Poção Nórdica na exploração;
- `2`: usar Essência Rúnica na exploração;
- `I` / `Tab`: abrir ou fechar o inventário visual;
- `M`: ligar/desligar áudio;
- `-` / `+`: ajustar volume;
- `F5`: salvar;
- `F9`: carregar;
- `F11`: tela cheia;
- `Esc`: sair.

A chuva e outros ambientes ficam tocando continuamente quando a cena pede. Os acontecimentos usam efeitos separados.


## Graphic Overhaul V2 Beta

A V2 usa mapas TMX via PyTMX, tiles e sprites CC0 da Kenney, HUD própria, galeria de finais e pipeline PyInstaller para Windows.

Para rodar, use apenas comandos no PowerShell. Código Python deve permanecer nos arquivos .py e nunca deve ser colado linha por linha no PowerShell.

## World Expansion V2.1

A nova etapa amplia Valdrak com 28 pontos especiais distribuídos nas sete regiões: ruínas, acampamentos, microcontos e sete passagens secretas. O jogador registra descobertas, Relíquias de Memória e Chaves Rúnicas, e cada região possui uma missão secundária concluída após três descobertas.

O tilemap também foi revisto com macrotiles de 48 px, menos ruído visual, tint própria por região, sprites mais proporcionais e HUD escura/compacta.

## V2.2 Combat & Audio

Atualize a branch v2-interface-grafica e execute normalmente com python eternos.py. A V2.2 não exige dependências adicionais. O novo áudio é carregado automaticamente de assets/audio/valdrak.

## V2.3

Após atualizar a branch, execute python eternos.py. A aventura começa imediatamente no mapa; siga os objetivos de tutorial exibidos no HUD.


## Controles V2.4

- M: mapa mundial;
- J: Quest Log;
- C: Codex;
- G: equipamentos;
- F: ataque pesado;
- V: áudio ON/OFF;
- 1/2/3: puzzles rúnicos em interiores;
- E ou Esc: sair de interiores.

## Controles V2.5

- Espaço: combo;
- F: ataque pesado;
- P: parry;
- Shift: dash / perfect dodge;
- X: execução quando o Guardião estiver atordoado;
- K: crafting;
- T: talentos;
- U: upgrade da arma equipada;
- O: acessibilidade e dificuldade;
- F6: alternar save slot;
- gamepad: A ataque, B dash, X pulso, Y Eterno, LB parry, RB pesado, Start pausa.

## Controles V2.6

- H: contratos e caçadas;
- 1/2: decisões de quests quando solicitado;
- E: conversar, investigar segredos e ativar encontros únicos;
- os demais controles V2.5 continuam válidos.
