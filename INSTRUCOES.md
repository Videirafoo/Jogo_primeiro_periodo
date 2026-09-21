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
- `WASD` / setas: mover em exploração e esquiva;
- `Espaço` / clique: acertar desafios de timing;
- `M`: áudio;
- `F11`: tela cheia;
- `Esc`: sair.

A chuva e outros ambientes ficam tocando continuamente quando a cena pede. Os acontecimentos usam efeitos separados.
