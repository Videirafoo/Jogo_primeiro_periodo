import os
import random
import sys

import pygame

import main as jogo


LARGURA = 1000
ALTURA = 700
FPS = 60

FUNDO = (12, 18, 32)
PAINEL = (25, 34, 52)
PAINEL_CLARO = (34, 46, 68)
TEXTO = (241, 245, 249)
TEXTO_SUAVE = (160, 174, 192)
DESTAQUE = (94, 234, 212)
DESTAQUE_2 = (129, 140, 248)
SUCESSO = (74, 222, 128)
ALERTA = (250, 204, 21)
ERRO = (248, 113, 113)


def criar_estado():
    return {
        "tela": "perfil",
        "nome": "",
        "entrada_nome": "",
        "entrada": "",
        "configuracao": None,
        "numero_secreto": None,
        "tentativa": 1,
        "limite_inferior": 1,
        "limite_superior": 100,
        "palpites": set(),
        "usou_dica": False,
        "mensagem": "Digite seu nome para começar.",
        "cor_mensagem": TEXTO_SUAVE,
        "finalizada": False,
    }


def criar_fontes():
    return {
        "titulo": pygame.font.SysFont("arial", 42, bold=True),
        "subtitulo": pygame.font.SysFont("arial", 24, bold=True),
        "normal": pygame.font.SysFont("arial", 20),
        "pequena": pygame.font.SysFont("arial", 16),
        "botao": pygame.font.SysFont("arial", 19, bold=True),
    }


def desenhar_texto(tela, texto, fonte, cor, x, y, centro=False):
    superficie = fonte.render(str(texto), True, cor)
    retangulo = superficie.get_rect()
    if centro:
        retangulo.center = (x, y)
    else:
        retangulo.topleft = (x, y)
    tela.blit(superficie, retangulo)
    return retangulo


def desenhar_botao(tela, fonte, texto, retangulo, mouse, destaque=False):
    cor = PAINEL_CLARO
    if retangulo.collidepoint(mouse):
        cor = (46, 62, 90)
    if destaque:
        cor = DESTAQUE_2 if not retangulo.collidepoint(mouse) else (150, 160, 255)

    pygame.draw.rect(tela, cor, retangulo, border_radius=14)
    pygame.draw.rect(tela, (75, 91, 116), retangulo, width=1, border_radius=14)
    desenhar_texto(
        tela,
        texto,
        fonte,
        TEXTO,
        retangulo.centerx,
        retangulo.centery,
        centro=True,
    )


def desenhar_cabecalho(tela, fontes, titulo, subtitulo=""):
    desenhar_texto(tela, titulo, fontes["titulo"], TEXTO, 60, 50)
    if subtitulo:
        desenhar_texto(tela, subtitulo, fontes["normal"], TEXTO_SUAVE, 62, 108)
    pygame.draw.line(tela, (52, 66, 88), (60, 145), (940, 145), 1)


def iniciar_partida(estado, configuracao, numero_secreto=None):
    estado["configuracao"] = configuracao
    estado["numero_secreto"] = (
        numero_secreto
        if numero_secreto is not None
        else random.randint(configuracao["minimo"], configuracao["maximo"])
    )
    estado["tentativa"] = 1
    estado["limite_inferior"] = configuracao["minimo"]
    estado["limite_superior"] = configuracao["maximo"]
    estado["palpites"] = set()
    estado["usou_dica"] = False
    estado["entrada"] = ""
    estado["finalizada"] = False
    estado["mensagem"] = "Digite um número e pressione Enter."
    estado["cor_mensagem"] = TEXTO_SUAVE
    estado["tela"] = "jogo"


def finalizar_partida(estado, venceu):
    configuracao = estado["configuracao"]
    if venceu:
        pontos = jogo.calcular_pontuacao(
            estado["tentativa"],
            configuracao["multiplicador"],
            estado["usou_dica"],
        )
    else:
        pontos = 0

    resultado = jogo.criar_resultado(
        pontos,
        estado["tentativa"],
        estado["usou_dica"],
        venceu,
    )
    estatisticas = jogo.carregar_estatisticas(estado["nome"])
    jogo.atualizar_estatisticas(estatisticas, resultado, configuracao["nome"])
    jogo.salvar_estatisticas(estado["nome"], estatisticas)
    estado["finalizada"] = True
    return pontos


def processar_palpite(estado, palpite):
    configuracao = estado["configuracao"]
    minimo = configuracao["minimo"]
    maximo = configuracao["maximo"]

    if palpite < minimo or palpite > maximo:
        estado["mensagem"] = f"Digite um número entre {minimo} e {maximo}."
        estado["cor_mensagem"] = ERRO
        return None

    if palpite in estado["palpites"]:
        estado["mensagem"] = "Esse número já foi usado. Tente outro."
        estado["cor_mensagem"] = ALERTA
        return None

    estado["palpites"].add(palpite)
    resultado = jogo.avaliar_palpite(palpite, estado["numero_secreto"])

    if resultado == "acertou":
        pontos = finalizar_partida(estado, True)
        estado["mensagem"] = f"Acertou! Você fez {pontos} pontos."
        estado["cor_mensagem"] = SUCESSO
        return "acertou"

    if resultado == "maior":
        estado["limite_inferior"] = max(estado["limite_inferior"], palpite + 1)
        direcao = "O número secreto é MAIOR."
    else:
        estado["limite_superior"] = min(estado["limite_superior"], palpite - 1)
        direcao = "O número secreto é MENOR."

    proximidade = jogo.classificar_distancia(
        palpite,
        estado["numero_secreto"],
        maximo - minimo + 1,
    )
    estado["mensagem"] = f"{direcao} {proximidade}"
    estado["cor_mensagem"] = ALERTA
    estado["tentativa"] += 1

    if estado["tentativa"] > configuracao["tentativas"]:
        estado["tentativa"] = configuracao["tentativas"]
        finalizar_partida(estado, False)
        estado["mensagem"] = (
            f"Fim de jogo. O número era {estado['numero_secreto']}."
        )
        estado["cor_mensagem"] = ERRO
        return "derrota"

    return resultado
def usar_dica(estado):
    if estado["finalizada"]:
        return

    if estado["usou_dica"]:
        estado["mensagem"] = "A dica desta partida já foi usada."
        estado["cor_mensagem"] = ALERTA
        return

    estado["usou_dica"] = True
    estado["mensagem"] = "DICA: " + jogo.gerar_dica(estado["numero_secreto"])
    estado["cor_mensagem"] = DESTAQUE


def desenhar_perfil(tela, fontes, estado, mouse):
    desenhar_cabecalho(
        tela,
        fontes,
        "Desafio do Número Secreto",
        "V2 gráfica — escolha seu perfil para começar",
    )

    caixa = pygame.Rect(220, 245, 560, 70)
    pygame.draw.rect(tela, PAINEL, caixa, border_radius=16)
    pygame.draw.rect(tela, DESTAQUE_2, caixa, width=2, border_radius=16)

    texto = estado["entrada_nome"] or "Seu nome"
    cor = TEXTO if estado["entrada_nome"] else TEXTO_SUAVE
    desenhar_texto(tela, texto, fontes["subtitulo"], cor, 250, 265)

    botao = pygame.Rect(350, 355, 300, 58)
    desenhar_botao(tela, fontes["botao"], "ENTRAR NO JOGO", botao, mouse, True)

    desenhar_texto(
        tela,
        "Enter também confirma",
        fontes["pequena"],
        TEXTO_SUAVE,
        500,
        450,
        centro=True,
    )
    return {"entrar": botao}


def desenhar_menu(tela, fontes, estado, mouse):
    desenhar_cabecalho(
        tela,
        fontes,
        f"Olá, {estado['nome']}",
        "Escolha para onde quer ir",
    )

    botoes = {}
    itens = [
        ("jogar", "JOGAR", True),
        ("estatisticas", "ESTATÍSTICAS", False),
        ("ranking", "RANKING", False),
        ("conquistas", "CONQUISTAS", False),
        ("regras", "REGRAS", False),
        ("sair", "SAIR", False),
    ]

    inicio_y = 190
    for indice, (chave, texto, destaque) in enumerate(itens):
        coluna = indice % 2
        linha = indice // 2
        rect = pygame.Rect(140 + coluna * 370, inicio_y + linha * 100, 320, 68)
        desenhar_botao(tela, fontes["botao"], texto, rect, mouse, destaque)
        botoes[chave] = rect

    desenhar_texto(
        tela,
        "V1.1 preservada no terminal • V2 roda com Pygame",
        fontes["pequena"],
        TEXTO_SUAVE,
        500,
        580,
        centro=True,
    )
    return botoes


def desenhar_dificuldade(tela, fontes, mouse):
    desenhar_cabecalho(
        tela,
        fontes,
        "Escolha a dificuldade",
        "Cada modo muda intervalo, tentativas e multiplicador",
    )

    botoes = {}
    for indice, chave in enumerate(("1", "2", "3")):
        config = jogo.DIFICULDADES[chave]
        y = 190 + indice * 115
        rect = pygame.Rect(160, y, 680, 88)
        pygame.draw.rect(tela, PAINEL, rect, border_radius=16)
        if rect.collidepoint(mouse):
            pygame.draw.rect(tela, PAINEL_CLARO, rect, border_radius=16)

        desenhar_texto(
            tela,
            config["nome"],
            fontes["subtitulo"],
            TEXTO,
            190,
            y + 17,
        )
        detalhe = (
            f"{config['minimo']}–{config['maximo']}  •  "
            f"{config['tentativas']} tentativas  •  "
            f"x{config['multiplicador']}"
        )
        desenhar_texto(tela, detalhe, fontes["normal"], TEXTO_SUAVE, 190, y + 50)
        botoes[chave] = rect

    voltar = pygame.Rect(390, 560, 220, 52)
    desenhar_botao(tela, fontes["botao"], "VOLTAR", voltar, mouse)
    botoes["voltar"] = voltar
    return botoes


def desenhar_jogo(tela, fontes, estado, mouse):
    config = estado["configuracao"]
    desenhar_cabecalho(
        tela,
        fontes,
        f"Modo {config['nome']}",
        f"Acerte o número entre {config['minimo']} e {config['maximo']}",
    )

    painel = pygame.Rect(70, 180, 860, 330)
    pygame.draw.rect(tela, PAINEL, painel, border_radius=20)

    tentativa = min(estado["tentativa"], config["tentativas"])
    desenhar_texto(
        tela,
        f"Tentativa {tentativa}/{config['tentativas']}",
        fontes["subtitulo"],
        TEXTO,
        110,
        215,
    )
    desenhar_texto(
        tela,
        f"Faixa atual: {estado['limite_inferior']} a {estado['limite_superior']}",
        fontes["normal"],
        TEXTO_SUAVE,
        110,
        260,
    )

    caixa = pygame.Rect(110, 315, 430, 72)
    pygame.draw.rect(tela, FUNDO, caixa, border_radius=14)
    pygame.draw.rect(tela, DESTAQUE, caixa, width=2, border_radius=14)
    valor = estado["entrada"] or "Digite seu palpite"
    cor = TEXTO if estado["entrada"] else TEXTO_SUAVE
    desenhar_texto(tela, valor, fontes["subtitulo"], cor, 135, 336)

    dica = pygame.Rect(575, 315, 230, 72)
    texto_dica = "DICA USADA" if estado["usou_dica"] else "USAR DICA"
    desenhar_botao(tela, fontes["botao"], texto_dica, dica, mouse)

    desenhar_texto(
        tela,
        estado["mensagem"],
        fontes["normal"],
        estado["cor_mensagem"],
        110,
        425,
    )

    botoes = {"dica": dica}

    if estado["finalizada"]:
        voltar = pygame.Rect(350, 545, 300, 58)
        desenhar_botao(tela, fontes["botao"], "VOLTAR AO MENU", voltar, mouse, True)
        botoes["voltar"] = voltar
    else:
        desenhar_texto(
            tela,
            "Enter confirma • H usa dica • Esc volta ao menu",
            fontes["pequena"],
            TEXTO_SUAVE,
            500,
            560,
            centro=True,
        )

    return botoes
def desenhar_estatisticas(tela, fontes, estado, mouse):
    estatisticas = jogo.carregar_estatisticas(estado["nome"])
    desenhar_cabecalho(tela, fontes, "Estatísticas", estado["nome"])

    partidas = estatisticas["partidas"]
    vitorias = estatisticas["vitorias"]
    taxa = (vitorias / partidas * 100) if partidas else 0

    cards = [
        ("Partidas", partidas),
        ("Vitórias", vitorias),
        ("Taxa", f"{taxa:.0f}%"),
        ("Recorde", estatisticas["melhor_pontuacao"]),
    ]

    for indice, (rotulo, valor) in enumerate(cards):
        rect = pygame.Rect(70 + indice * 220, 180, 190, 105)
        pygame.draw.rect(tela, PAINEL, rect, border_radius=16)
        desenhar_texto(tela, rotulo, fontes["pequena"], TEXTO_SUAVE, rect.x + 20, rect.y + 18)
        desenhar_texto(tela, valor, fontes["subtitulo"], TEXTO, rect.x + 20, rect.y + 50)

    desenhar_texto(tela, "Últimas partidas", fontes["subtitulo"], TEXTO, 70, 330)
    historico = list(reversed(estatisticas["historico"]))
    if not historico:
        desenhar_texto(tela, "Nenhuma partida registrada.", fontes["normal"], TEXTO_SUAVE, 70, 380)
    else:
        for indice, partida in enumerate(historico):
            resultado = "Vitória" if partida["venceu"] else "Derrota"
            linha = (
                f"{partida['modo']} • {resultado} • "
                f"{partida['tentativas']} tentativa(s) • {partida['pontos']} pts"
            )
            desenhar_texto(tela, linha, fontes["normal"], TEXTO_SUAVE, 70, 380 + indice * 40)

    voltar = pygame.Rect(390, 610, 220, 50)
    desenhar_botao(tela, fontes["botao"], "VOLTAR", voltar, mouse)
    return {"voltar": voltar}


def desenhar_ranking(tela, fontes, mouse):
    desenhar_cabecalho(tela, fontes, "Ranking local", "Top 5 por melhor pontuação")
    ranking = jogo.obter_ranking()

    if not ranking:
        desenhar_texto(tela, "Ainda não há jogadores no ranking.", fontes["normal"], TEXTO_SUAVE, 70, 200)
    else:
        for indice, jogador in enumerate(ranking, start=1):
            rect = pygame.Rect(120, 170 + (indice - 1) * 78, 760, 62)
            pygame.draw.rect(tela, PAINEL, rect, border_radius=14)
            desenhar_texto(tela, f"{indice}º", fontes["subtitulo"], DESTAQUE, rect.x + 22, rect.y + 17)
            desenhar_texto(tela, jogador["nome"], fontes["normal"], TEXTO, rect.x + 90, rect.y + 19)
            detalhe = f"{jogador['pontos']} pts • {jogador['vitorias']} vitória(s)"
            desenhar_texto(tela, detalhe, fontes["normal"], TEXTO_SUAVE, rect.x + 430, rect.y + 19)

    voltar = pygame.Rect(390, 610, 220, 50)
    desenhar_botao(tela, fontes["botao"], "VOLTAR", voltar, mouse)
    return {"voltar": voltar}


def desenhar_conquistas(tela, fontes, estado, mouse):
    desenhar_cabecalho(tela, fontes, "Conquistas", estado["nome"])
    estatisticas = jogo.carregar_estatisticas(estado["nome"])
    liberadas = set(estatisticas["conquistas"])

    conquistas = [
        ("Primeira vitória", "Vença sua primeira partida"),
        ("De primeira", "Acerte o número na primeira tentativa"),
        ("Sem dica", "Vença sem usar DICA"),
        ("Mestre do Difícil", "Vença no modo Difícil"),
        ("5 vitórias", "Acumule cinco vitórias"),
    ]

    for indice, (nome, descricao) in enumerate(conquistas):
        rect = pygame.Rect(100, 170 + indice * 78, 800, 62)
        pygame.draw.rect(tela, PAINEL, rect, border_radius=14)
        desbloqueada = nome in liberadas
        marcador = "✓" if desbloqueada else "○"
        cor = SUCESSO if desbloqueada else TEXTO_SUAVE
        desenhar_texto(tela, marcador, fontes["subtitulo"], cor, rect.x + 20, rect.y + 15)
        desenhar_texto(tela, nome, fontes["normal"], TEXTO, rect.x + 70, rect.y + 9)
        desenhar_texto(tela, descricao, fontes["pequena"], TEXTO_SUAVE, rect.x + 70, rect.y + 35)

    voltar = pygame.Rect(390, 610, 220, 50)
    desenhar_botao(tela, fontes["botao"], "VOLTAR", voltar, mouse)
    return {"voltar": voltar}


def desenhar_regras(tela, fontes, mouse):
    desenhar_cabecalho(tela, fontes, "Regras", "Use lógica para encontrar o número secreto")

    regras = [
        "Escolha uma dificuldade.",
        "Digite um palpite dentro da faixa permitida.",
        "O jogo informa se o número secreto é maior ou menor.",
        "Frio, morno e quente indicam proximidade.",
        "Palpites repetidos não gastam tentativa.",
        "A tecla H libera uma dica uma vez por partida.",
        "Usar dica reduz a pontuação final em 15%.",
        "Quanto menos tentativas, maior a pontuação.",
    ]

    for indice, regra in enumerate(regras, start=1):
        desenhar_texto(
            tela,
            f"{indice}. {regra}",
            fontes["normal"],
            TEXTO_SUAVE,
            100,
            180 + (indice - 1) * 48,
        )

    voltar = pygame.Rect(390, 610, 220, 50)
    desenhar_botao(tela, fontes["botao"], "VOLTAR", voltar, mouse)
    return {"voltar": voltar}


def desenhar_tela(tela, fontes, estado):
    tela.fill(FUNDO)
    mouse = pygame.mouse.get_pos()

    if estado["tela"] == "perfil":
        return desenhar_perfil(tela, fontes, estado, mouse)
    if estado["tela"] == "menu":
        return desenhar_menu(tela, fontes, estado, mouse)
    if estado["tela"] == "dificuldade":
        return desenhar_dificuldade(tela, fontes, mouse)
    if estado["tela"] == "jogo":
        return desenhar_jogo(tela, fontes, estado, mouse)
    if estado["tela"] == "estatisticas":
        return desenhar_estatisticas(tela, fontes, estado, mouse)
    if estado["tela"] == "ranking":
        return desenhar_ranking(tela, fontes, mouse)
    if estado["tela"] == "conquistas":
        return desenhar_conquistas(tela, fontes, estado, mouse)
    if estado["tela"] == "regras":
        return desenhar_regras(tela, fontes, mouse)

    return {}


def confirmar_nome(estado):
    estado["nome"] = jogo.normalizar_nome(estado["entrada_nome"])
    estado["tela"] = "menu"


def processar_teclado(evento, estado):
    if evento.key == pygame.K_ESCAPE:
        if estado["tela"] == "perfil":
            return "sair"
        estado["tela"] = "menu"
        estado["entrada"] = ""
        return None

    if estado["tela"] == "perfil":
        if evento.key == pygame.K_RETURN:
            confirmar_nome(estado)
        elif evento.key == pygame.K_BACKSPACE:
            estado["entrada_nome"] = estado["entrada_nome"][:-1]
        elif evento.unicode.isprintable() and len(estado["entrada_nome"]) < 30:
            estado["entrada_nome"] += evento.unicode
        return None

    if estado["tela"] != "jogo" or estado["finalizada"]:
        return None

    if evento.key == pygame.K_h:
        usar_dica(estado)
    elif evento.key == pygame.K_BACKSPACE:
        estado["entrada"] = estado["entrada"][:-1]
    elif evento.key == pygame.K_RETURN and estado["entrada"]:
        processar_palpite(estado, int(estado["entrada"]))
        estado["entrada"] = ""
    elif evento.unicode.isdigit() and len(estado["entrada"]) < 5:
        estado["entrada"] += evento.unicode

    return None
def processar_clique(posicao, botoes, estado):
    tela_atual = estado["tela"]

    for chave, rect in botoes.items():
        if not rect.collidepoint(posicao):
            continue

        if tela_atual == "perfil" and chave == "entrar":
            confirmar_nome(estado)
            return None

        if tela_atual == "menu":
            if chave == "jogar":
                estado["tela"] = "dificuldade"
            elif chave in {"estatisticas", "ranking", "conquistas", "regras"}:
                estado["tela"] = chave
            elif chave == "sair":
                return "sair"
            return None

        if tela_atual == "dificuldade":
            if chave == "voltar":
                estado["tela"] = "menu"
            else:
                iniciar_partida(estado, jogo.DIFICULDADES[chave])
            return None

        if tela_atual == "jogo":
            if chave == "dica":
                usar_dica(estado)
            elif chave == "voltar":
                estado["tela"] = "menu"
            return None

        if chave == "voltar":
            estado["tela"] = "menu"
            return None

    return None


def executar_smoke():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    fontes = criar_fontes()
    estado = criar_estado()
    estado["nome"] = "Jogador Teste"

    telas = [
        "perfil",
        "menu",
        "dificuldade",
        "estatisticas",
        "ranking",
        "conquistas",
        "regras",
    ]

    for nome_tela in telas:
        estado["tela"] = nome_tela
        desenhar_tela(tela, fontes, estado)

    iniciar_partida(estado, jogo.DIFICULDADES["1"], numero_secreto=25)
    desenhar_tela(tela, fontes, estado)
    pygame.quit()
    print("Smoke gráfico concluído com sucesso.")


def executar():
    pygame.init()
    pygame.display.set_caption("Desafio do Número Secreto — V2")
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    relogio = pygame.time.Clock()
    fontes = criar_fontes()
    estado = criar_estado()
    executando = True
    botoes = {}

    while executando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False

            elif evento.type == pygame.KEYDOWN:
                acao = processar_teclado(evento, estado)
                if acao == "sair":
                    executando = False

            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                acao = processar_clique(evento.pos, botoes, estado)
                if acao == "sair":
                    executando = False

        botoes = desenhar_tela(tela, fontes, estado)
        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        executar_smoke()
    else:
        executar()
