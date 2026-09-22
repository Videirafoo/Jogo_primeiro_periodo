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
