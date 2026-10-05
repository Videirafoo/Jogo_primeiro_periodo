# Project Workflow — Jogo

Este projeto adota uma versão enxuta de **Programação Vibe**, adaptada para jogos.

## Fluxo
Ideia → jogador → core loop → escopo → arquitetura → protótipo → gameplay → testes → polish → build → release → feedback.

Por funcionalidade:
**Entender → Planejar → Implementar → Jogar/Testar → Corrigir → Commit → Documentar.**

## Documentação útil
- GAME_DESIGN.md — objetivo, core loop, regras e progressão.
- ARCHITECTURE.md — cenas/sistemas e responsabilidades.
- TASKS.md — próximas melhorias pequenas.
- TEST_PLAN.md — controles, colisões, vitória/derrota e regressões.
- PERFORMANCE.md — FPS, memória e carregamento, quando necessário.

## Regras
- Jogabilidade primeiro.
- Implementar uma mecânica por vez.
- Testar jogando após cada mudança.
- Não reescrever sistemas funcionando sem necessidade.
- Preservar uma build jogável na main.
- Assets, controles e HUD devem permanecer consistentes.
