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

O módulo `gameplay.py` adiciona três famílias de desafio:

- exploração de runas com movimento;
- timing para combate, portões e tecnologia;
- esquiva de machados e lobos.

Falhar não bloqueia a campanha. Sucesso concede bônus coerentes com o capítulo; falha adiciona Caos.

## 11. Áudio

O módulo `audio.py` separa ambiente contínuo de efeitos. Chuva, vento, bosque, fogo, tecnologia e portal permanecem tocando em loop, enquanto acontecimentos como trovão, espada, machado, cavalo, lobo, runa e portão usam canais de SFX.

A tecla M controla o áudio.

## 12. Testes

`test_engine.py`, `test_gameplay.py` e `test_audio.py` validam narrativa, requisitos, caminhos, desafios, integração e áudio.

O GitHub Actions também executa um smoke gráfico headless da campanha completa.

## 13. Próxima evolução

- ilustrações próprias para cada capítulo;
- retratos dos aliados;
- partículas específicas;
- transições cinematográficas;
- save/load;
- galeria de finais;
- créditos;
- empacotamento Windows.
