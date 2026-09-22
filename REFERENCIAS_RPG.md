# Referências de arquitetura RPG

Esta V2 foi comparada com projetos públicos de Pygame para identificar padrões de game design e arquitetura. A implementação de OS ETERNOS continua própria e adaptada ao universo de Valdrak.

## Clear Code — Zelda

Repositório:

https://github.com/clear-code-projects/Zelda

Licença declarada pelo projeto: CC0.

Padrões estudados:

- separação de jogador, arma, magia e inimigos;
- câmera seguindo o personagem;
- animações por estado;
- ataque e magia com cooldown;
- partículas;
- HUD de vida, energia e experiência;
- progressão/upgrades.

Aplicação em OS ETERNOS:

- entidade do protagonista;
- ataque corpo a corpo;
- Pulso de Código;
- vida e energia;
- XP e nível;
- partículas;
- câmera top-down.

## Clear Code — PyDew

Repositório:

https://github.com/clear-code-projects/PyDew

Licença declarada pelo projeto: CC0.

Padrões estudados:

- grupo de sprites com câmera;
- ordenação visual pela posição Y;
- colisões;
- áreas de interação;
- clima;
- transições;
- overlay separado da lógica do mundo.

Aplicação em OS ETERNOS:

- exploração física por capítulo;
- obstáculos e colisão;
- santuários/runa como interação;
- aliados acompanhando o protagonista;
- ambiente contínuo por região;
- HUD separado do mundo.

## Zelda Style RPG

Repositório:

https://github.com/b3mery/Zelda_pygame

Padrões observados:

- organização modular;
- jogador com estados;
- ataque e magia;
- inimigos;
- partículas;
- câmera;
- HUD.

O código não foi copiado. A referência foi usada para validar a separação de responsabilidades.

## RPG Test

Repositório:

https://github.com/lukeshorejones/rpg-test

Padrões observados:

- conteúdo orientado a dados;
- unidades e armas configuráveis;
- mapas;
- build executável;
- configurações de volume.

Aplicação planejada:

- galeria de finais;
- configurações;
- build Windows;
- conteúdo de capítulos mais orientado a dados.

## Regra do projeto

Referências servem para aprender padrões. OS ETERNOS mantém história, sistemas, interface e implementação próprios.
