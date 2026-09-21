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
Capítulo
  ↓
Cena narrativa
  ↓
Escolha
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

Isso permite redimensionar, usar diferentes monitores, ativar F11 e manter o layout consistente.

## 9. Narração

A narrativa é revelada progressivamente. Enter/Espaço revela o restante do texto e, no próximo acionamento, avança.

## 10. Áudio

O módulo `audio.py` gera efeitos sonoros em tempo de execução para chuva, vento, cavalo, espada, machado, trovão, runa, tecnologia, fogo, portal e outros eventos.

A tecla M controla o áudio.

## 11. Testes

`test_engine.py` valida conteúdo, requisitos, efeitos, aliados, tecnologia, finais e todos os caminhos possíveis.

O GitHub Actions também executa um smoke gráfico headless.

## 12. Próxima evolução visual

- ilustrações próprias para cada capítulo;
- retratos dos aliados;
- partículas específicas;
- transições cinematográficas;
- trilha ambiente;
- save/load;
- galeria de finais;
- créditos;
- empacotamento Windows.
