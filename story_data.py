GAME = {
    "title": "OS ETERNOS",
    "ascii_title": r"""
 ██████╗ ███████╗    ███████╗████████╗███████╗██████╗ ███╗   ██╗ ██████╗ ███████╗
██╔═══██╗██╔════╝    ██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗  ██║██╔═══██╗██╔════╝
██║   ██║███████╗    █████╗     ██║   █████╗  ██████╔╝██╔██╗ ██║██║   ██║███████╗
██║   ██║╚════██║    ██╔══╝     ██║   ██╔══╝  ██╔══██╗██║╚██╗██║██║   ██║╚════██║
╚██████╔╝███████║    ███████╗   ██║   ███████╗██║  ██║██║ ╚████║╚██████╔╝███████║
 ╚═════╝ ╚══════╝    ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝
""",
    "initial_state": {
        "coragem": 0,
        "sabedoria": 0,
        "tecnologia": 0,
        "caos": 0,
        "amizade": 0,
        "reliquias": 0,
        "marcas": 0,
        "tools": [
            "Scanner de Runas",
            "Mapa Holográfico",
            "Pulso de Código",
        ],
    },
    "opening": [
        {
            "sfx": "intro",
            "text": "Fui dormir num dia comum.",
        },
        {
            "sfx": "dream_fall",
            "text": "Mas, no meio da noite, alguma coisa me puxou para baixo. Não foi como adormecer. Foi como cair dentro do próprio sonho.",
        },
        {
            "sfx": "rain",
            "text": "Quando abri os olhos, eu não estava no meu quarto. Estava deitado numa terra fria, escura, com chuva fina batendo no rosto.",
        },
        {
            "sfx": "wind",
            "text": "O lugar parecia antigo. Pinheiros enormes cercavam uma estrada de lama e pedra. O vento carregava cheiro de fumaça, ferro e madeira queimada.",
        },
        {
            "sfx": "horse",
            "text": "Ao longe, ouvi cascos de cavalo batendo contra o chão.",
        },
        {
            "sfx": "sword",
            "text": "Depois veio o som de espadas se chocando, como se uma guerra estivesse acontecendo perto dali.",
        },
        {
            "sfx": "axe_whoosh",
            "text": "Então um machado passou cortando o ar, tão perto que eu senti o vento da lâmina antes de ouvir o impacto.",
        },
        {
            "sfx": "axe_hit",
            "text": "A lâmina acertou uma árvore atrás de mim e partiu a madeira como se fosse papel.",
        },
        {
            "sfx": "crow",
            "text": "Foi quando eu vi a vila: tochas acesas, casas de madeira, homens com peles, escudos redondos, machados, lanças e runas marcadas no rosto.",
        },
        {
            "sfx": "thunder",
            "text": "Eram vikings. Mas não pareciam homens comuns. Eles olhavam para o céu como se conhecessem os trovões pelo nome.",
        },
        {
            "sfx": "gate",
            "text": "Um deles apontou para mim e gritou: — O estranho acordou em Valdrak! Levem-no ao conselho dos antigos!",
        },
        {
            "sfx": "horse",
            "text": "Eu corri sem saber para onde. Só sabia que aquele lugar se chamava Valdrak, uma terra perdida na era dos vikings, presa entre sonho, magia e destino.",
        },
        {
            "sfx": "tech",
            "text": "Enquanto corria, meu celular apareceu na minha mão. Mas não era mais um celular comum. A tela brilhava com símbolos azuis, como se fosse uma ferramenta viva.",
        },
        {
            "sfx": "scanner",
            "text": "Na tela apareceu uma frase: PODER DESPERTADO — TECNOLOGIA. Instrumentos disponíveis: Scanner de Runas, Mapa Holográfico e Pulso de Código.",
        },
        {
            "sfx": "rune",
            "text": "Eu ainda não entendia, mas Valdrak já tinha escolhido meu papel. Outros sonhadores estavam presos ali também. E, se eu os encontrasse, formaríamos um grupo.",
        },
        {
            "sfx": "portal",
            "text": "Só esse grupo poderia chegar à última porta, acordar antes do amanhecer e lembrar de tudo ao voltar para a faculdade.",
        },
    ],
    "allies": {
        "thorvald": {
            "name": "Thorvald",
            "power": "Raio de Torv",
            "description": "Ele acordou em Valdrak antes de você. Descobriu que seus punhos chamam trovões e que o céu responde quando ele grita.",
            "sfx": "thunder",
        },
        "aurel": {
            "name": "Aurel",
            "power": "Olho do Céu",
            "description": "Ele também estava sonhando. Seu poder revela armadilhas, caminhos falsos e decisões que ainda não aconteceram.",
            "sfx": "lightning",
        },
        "kaion": {
            "name": "Kaion",
            "power": "Lâmina do Vento",
            "description": "Ele acordou segurando uma espada que corta o ar antes do inimigo se mover.",
            "sfx": "sword",
        },
        "brenor": {
            "name": "Brenor",
            "power": "Fogo da Forja",
            "description": "Ele descobriu que consegue acender runas antigas e abrir mecanismos esquecidos pelos vikings.",
            "sfx": "fire",
        },
        "eiran": {
            "name": "Eiran",
            "power": "Cura da Aurora",
            "description": "Ele acordou ouvindo vozes feridas. Seu poder acalma o medo e impede que o sonho quebre a mente do grupo.",
            "sfx": "heal",
        },
        "noctar": {
            "name": "Noctar",
            "power": "Sombra dos Corvos",
            "description": "Ele aprendeu a andar entre sombras e escutar segredos que os corvos guardam.",
            "sfx": "shadow",
        },
    },
    "chapters": [
        {
            "number": 1,
            "title": "A Estrada de Valdrak",
            "scene": [
                {"sfx": "rain", "text": "A chuva deixava a estrada pesada. Atrás de mim, os vikings montavam cavalos escuros."},
                {"sfx": "horse", "text": "Os cascos vinham rápidos. CLOC. CLOC. CLOC."},
                {"sfx": "axe_whoosh", "text": "Outro machado passou girando, cortando o ar como uma asa de ferro."},
                {"sfx": "scanner", "text": "Meu celular brilhou. O Scanner de Runas mostrou três rotas: ponte quebrada, bosque dos corvos e pedras azuis."},
            ],
            "choices": [
                {
                    "text": "Usar o Mapa Holográfico e correr para a ponte quebrada.",
                    "sfx_sequence": ["tech", "horse", "thunder"],
                    "result": [
                        {"sfx": "tech", "text": "O mapa abriu no ar, feito luz azul. A rota dizia que a ponte cairia, mas também mostrava uma presença próxima."},
                        {"sfx": "thunder", "text": "Quando a ponte desabou, um homem surgiu no meio dos raios e segurou as pedras com as mãos."},
                        {"sfx": "thunder", "text": "— Eu também acordei aqui — ele disse. — Me chamam de Thorvald. Acho que encontrei meu poder antes de você."},
                    ],
                    "effects": {"coragem": 2, "tecnologia": 2, "amizade": 2},
                    "unlock_ally": "thorvald",
                    "unlock_tool": "Mapa Holográfico",
                },
                {
                    "text": "Entrar no bosque dos corvos.",
                    "sfx_sequence": ["wind", "crow"],
                    "result": [
                        {"sfx": "crow", "text": "O bosque engoliu a luz. Os cavalos não conseguiram passar, mas os corvos começaram a repetir meu nome."},
                        {"sfx": "shadow", "text": "No escuro, percebi que Valdrak não era apenas perigosa. Era inteligente. A terra observava minhas escolhas."},
                    ],
                    "effects": {"sabedoria": 2, "caos": 1},
                },
                {
                    "text": "Seguir as pedras azuis e analisar as runas.",
                    "sfx_sequence": ["scanner", "rune", "tech"],
                    "result": [
                        {"sfx": "scanner", "text": "Apontei o celular para as pedras. O Scanner de Runas traduziu símbolos que ninguém daquele mundo parecia entender."},
                        {"sfx": "rune", "text": "A primeira marca surgiu no meu pulso. Tecnologia e magia começaram a conversar dentro do sonho."},
                    ],
                    "effects": {"sabedoria": 2, "tecnologia": 3, "marcas": 1},
                    "unlock_tool": "Scanner de Runas",
                },
            ],
        },
        {
            "number": 2,
            "title": "O Portão dos Ossos",
            "scene": [
                {"sfx": "gate", "text": "A rota levou até um portão feito de madeira escura, ferro e ossos de animais."},
                {"sfx": "sword", "text": "Sentinelas arrastavam espadas no chão. O som parecia aviso."},
                {"sfx": "wind", "text": "Do alto da muralha, uma voz masculina gritou que havia outros sonhadores presos em Valdrak."},
            ],
            "choices": [
                {
                    "text": "Pedir para Thorvald abrir caminho com o raio.",
                    "requires_ally": "thorvald",
                    "sfx_sequence": ["thunder", "axe_hit", "gate"],
                    "result": [
                        {"sfx": "thunder", "text": "Thorvald bateu os punhos no chão. Um raio caiu sobre o portão e os ossos se espalharam pela lama."},
                        {"sfx": "shield", "text": "Os vikings ergueram escudos, assustados. Pela primeira vez, eles recuaram."},
                    ],
                    "effects": {"coragem": 3, "amizade": 1},
                },
                {
                    "text": "Subir pela muralha e procurar a voz.",
                    "sfx_sequence": ["wind", "lightning"],
                    "result": [
                        {"sfx": "lightning", "text": "No topo da muralha encontrei Aurel. Ele disse que também dormiu em outro mundo e acordou ali."},
                        {"sfx": "scanner", "text": "— Eu vi sua chegada antes de acontecer — ele falou. — E vi que você carrega poder de tecnologia."},
                    ],
                    "effects": {"sabedoria": 2, "amizade": 2},
                    "unlock_ally": "aurel",
                },
                {
                    "text": "Usar o Pulso de Código para abrir a fechadura antiga.",
                    "sfx_sequence": ["tech", "rune", "gate"],
                    "result": [
                        {"sfx": "tech", "text": "O celular emitiu um pulso azul. A fechadura não era mecânica. Era uma runa disfarçada."},
                        {"sfx": "gate", "text": "O portão abriu apenas o suficiente para eu passar. Atrás de mim, as sentinelas gritaram."},
                    ],
                    "effects": {"tecnologia": 3, "sabedoria": 1, "caos": 1},
                    "unlock_tool": "Pulso de Código",
                },
            ],
        },
        {
            "number": 3,
            "title": "A Vila dos Despertos",
            "scene": [
                {"sfx": "crow", "text": "Dentro da vila, todos pararam para me olhar."},
                {"sfx": "fire", "text": "Tochas estalavam nas paredes. Crianças se escondiam. Ferreiros apertavam martelos."},
                {"sfx": "sword", "text": "No centro, um duelo acontecia. Um homem lutava como se não soubesse por que estava ali."},
                {"sfx": "heal", "text": "Perto da forja, outro homem ferido repetia: 'Eu só estava dormindo... eu só estava dormindo...'"},
            ],
            "choices": [
                {
                    "text": "Entrar no duelo e salvar o guerreiro perdido.",
                    "sfx_sequence": ["sword", "shield", "sword"],
                    "result": [
                        {"sfx": "sword", "text": "Peguei uma espada no chão. O golpe inimigo veio pesado, mas uma lâmina cortou o vento antes de mim."},
                        {"sfx": "wind", "text": "Kaion apareceu sorrindo. — Também acordei aqui. Minha espada se move antes do medo."},
                    ],
                    "effects": {"coragem": 2, "amizade": 1},
                    "unlock_ally": "kaion",
                },
                {
                    "text": "Correr até a forja apagada.",
                    "sfx_sequence": ["forge", "fire", "rune"],
                    "result": [
                        {"sfx": "fire", "text": "A forja estava morta. Mas Brenor encostou as mãos no ferro e tudo acendeu de uma vez."},
                        {"sfx": "rune", "text": "— Acordei aqui com fogo nas mãos — ele disse. — Acho que somos parte da mesma história."},
                    ],
                    "effects": {"coragem": 1, "tecnologia": 1, "amizade": 1},
                    "unlock_ally": "brenor",
                },
                {
                    "text": "Ajudar o homem ferido.",
                    "sfx_sequence": ["heal", "wind"],
                    "result": [
                        {"sfx": "heal", "text": "Eiran surgiu ajoelhado ao lado dele. Uma luz fraca saiu de suas mãos e o ferimento fechou."},
                        {"sfx": "heal", "text": "— Eu também estava sonhando — Eiran falou. — Mas acordei ouvindo pedidos de ajuda."},
                    ],
                    "effects": {"amizade": 3, "sabedoria": 1, "caos": -1},
                    "unlock_ally": "eiran",
                },
            ],
        },
        {
            "number": 4,
            "title": "O Bosque que Falava",
            "scene": [
                {"sfx": "wind", "text": "Depois da vila, o caminho entrou no bosque dos corvos."},
                {"sfx": "crow", "text": "Os corvos não cantavam. Eles falavam frases da vida real, como se tivessem roubado memórias de todos nós."},
                {"sfx": "scanner", "text": "Meu Scanner de Runas mostrou três símbolos: olho, corrente e pena."},
            ],
            "choices": [
                {
                    "text": "Usar Aurel para interpretar o símbolo do olho.",
                    "requires_ally": "aurel",
                    "sfx_sequence": ["lightning", "scanner"],
                    "result": [
                        {"sfx": "lightning", "text": "Aurel viu as armadilhas antes delas existirem. Flechas invisíveis passaram onde estaríamos segundos depois."},
                        {"sfx": "tech", "text": "Meu Scanner confirmou: o bosque estava tentando prever nossas escolhas."},
                    ],
                    "effects": {"sabedoria": 3, "tecnologia": 1, "amizade": 1},
                },
                {
                    "text": "Usar Kaion para cortar a corrente.",
                    "requires_ally": "kaion",
                    "sfx_sequence": ["chain", "sword", "shadow"],
                    "result": [
                        {"sfx": "sword", "text": "Kaion cortou a corrente com um golpe limpo. O bosque abriu uma trilha estreita entre as árvores."},
                        {"sfx": "crow", "text": "Os corvos ficaram em silêncio. Era a primeira vez que Valdrak parecia perder uma resposta."},
                    ],
                    "effects": {"coragem": 2, "amizade": 1},
                },
                {
                    "text": "Seguir a pena negra e procurar outro sonhador.",
                    "sfx_sequence": ["crow", "shadow"],
                    "result": [
                        {"sfx": "shadow", "text": "A pena levou até um homem parado entre os corvos. Ele se chamava Noctar."},
                        {"sfx": "crow", "text": "— Eu acordo nas sombras desse lugar todas as noites — ele disse. — E ouvi que você pode abrir a última porta."},
                    ],
                    "effects": {"sabedoria": 1, "amizade": 2},
                    "unlock_ally": "noctar",
                },
            ],
        },
        {
            "number": 5,
            "title": "A Caçada dos Lobos de Ferro",
            "scene": [
                {"sfx": "wolf", "text": "A neve começou do nada."},
                {"sfx": "horse", "text": "Cavaleiros desceram a colina. Atrás deles, lobos com placas de ferro corriam farejando nossas marcas."},
                {"sfx": "axe_whoosh", "text": "Um machado passou girando entre duas árvores e acertou a neve, abrindo um buraco escuro."},
            ],
            "choices": [
                {
                    "text": "Usar Thorvald para invocar raio contra os lobos.",
                    "requires_ally": "thorvald",
                    "sfx_sequence": ["wolf", "thunder", "lightning"],
                    "result": [
                        {"sfx": "thunder", "text": "Thorvald ergueu os braços. Um raio caiu entre os lobos e transformou a neve em vapor."},
                        {"sfx": "horse", "text": "Os cavalos recuaram. Os vikings gritaram como se tivessem visto um deus antigo."},
                    ],
                    "effects": {"coragem": 3, "amizade": 1},
                },
                {
                    "text": "Usar Eiran para acalmar o medo do grupo.",
                    "requires_ally": "eiran",
                    "sfx_sequence": ["heal", "wind"],
                    "result": [
                        {"sfx": "heal", "text": "Eiran colocou a mão no peito e respirou fundo. A luz dele passou por nós como manhã depois de tempestade."},
                        {"sfx": "wolf", "text": "Até os lobos hesitaram. O medo deixou de controlar nossos passos."},
                    ],
                    "effects": {"amizade": 2, "sabedoria": 1, "caos": -2},
                },
                {
                    "text": "Usar o Pulso de Código para confundir as runas dos lobos.",
                    "requires_tool": "Pulso de Código",
                    "sfx_sequence": ["tech", "scanner", "wolf"],
                    "result": [
                        {"sfx": "tech", "text": "O Pulso de Código atingiu as placas de ferro dos lobos. As runas nelas começaram a falhar."},
                        {"sfx": "wolf", "text": "Os lobos correram em círculos, perdendo nosso rastro na neve."},
                    ],
                    "effects": {"tecnologia": 3, "sabedoria": 1},
                },
            ],
        },
        {
            "number": 6,
            "title": "A Forja do Sol Morto",
            "scene": [
                {"sfx": "forge", "text": "A montanha abriu uma entrada enorme, como se fosse a boca de um monstro antigo."},
                {"sfx": "fire", "text": "Dentro dela havia uma forja apagada, maior que uma casa."},
                {"sfx": "rune", "text": "Na parede, três runas esperavam: fogo, sombra e código."},
                {"sfx": "scanner", "text": "Meu celular mostrou que a última porta só abriria se magia antiga e tecnologia trabalhassem juntas."},
            ],
            "choices": [
                {
                    "text": "Usar Brenor para acender a runa de fogo.",
                    "requires_ally": "brenor",
                    "sfx_sequence": ["forge", "fire", "rune", "gate"],
                    "result": [
                        {"sfx": "fire", "text": "Brenor colocou as mãos na pedra. A forja acordou como um sol vermelho preso dentro da montanha."},
                        {"sfx": "gate", "text": "Uma parte da porta se abriu."},
                    ],
                    "effects": {"amizade": 1, "marcas": 1, "tecnologia": 1},
                },
                {
                    "text": "Usar Noctar para atravessar a sombra e abrir por dentro.",
                    "requires_ally": "noctar",
                    "sfx_sequence": ["shadow", "crow", "gate"],
                    "result": [
                        {"sfx": "shadow", "text": "Noctar desapareceu na parede escura. Os corvos fizeram silêncio."},
                        {"sfx": "gate", "text": "Quando ele voltou, a porta estava destravada e ele sabia o nome da sombra que nos seguia."},
                    ],
                    "effects": {"sabedoria": 2, "amizade": 1},
                },
                {
                    "text": "Usar Scanner de Runas e Pulso de Código juntos.",
                    "requires_tool": "Scanner de Runas",
                    "sfx_sequence": ["scanner", "tech", "rune", "portal"],
                    "result": [
                        {"sfx": "scanner", "text": "O Scanner traduziu a runa. O Pulso de Código respondeu com luz azul."},
                        {"sfx": "portal", "text": "Pela primeira vez, Valdrak aceitou uma força que não era daquele tempo: tecnologia."},
                    ],
                    "effects": {"tecnologia": 4, "sabedoria": 2, "marcas": 1},
                },
            ],
        },
        {
            "number": 7,
            "title": "A Última Porta de Valdrak",
            "scene": [
                {"sfx": "portal", "text": "A última porta não ficava em um castelo."},
                {"sfx": "wind", "text": "Ela ficava num salão impossível: metade templo viking, metade corredor de faculdade."},
                {"sfx": "rune", "text": "Carteiras viraram tronos. Quadros viraram escudos. O chão era pedra. O teto era céu."},
                {"sfx": "wake", "text": "Do outro lado da porta, ouvi o despertador tocando."},
                {"sfx": "shadow", "text": "Atrás de nós, a sombra de Valdrak disse: — Quem acorda sem lembrar, volta para cá sem escolha."},
            ],
            "choices": [
                {
                    "text": "Atravessar a porta sozinho e acordar.",
                    "sfx_sequence": ["portal", "wake"],
                    "result": [
                        {"sfx": "wake", "text": "Atravessei a luz. Valdrak quebrou em pedaços de chuva, espada, cavalo e fogo."},
                    ],
                    "effects": {"sabedoria": 2},
                },
                {
                    "text": "Reunir o grupo e atravessar com todos.",
                    "requires_any_ally_count": 4,
                    "sfx_sequence": ["thunder", "fire", "tech", "ending_good"],
                    "result": [
                        {"sfx": "ending_good", "text": "O grupo atravessou junto. Cada poder virou lembrança. Cada lembrança virou prova de que tudo aconteceu."},
                    ],
                    "effects": {"amizade": 4, "marcas": 1, "tecnologia": 2},
                },
                {
                    "text": "Usar seu poder de tecnologia para gravar Valdrak antes de acordar.",
                    "requires_tool": "Mapa Holográfico",
                    "sfx_sequence": ["scanner", "tech", "portal"],
                    "result": [
                        {"sfx": "tech", "text": "Ativei o Mapa Holográfico e gravei símbolos, rotas, vozes e rostos."},
                        {"sfx": "portal", "text": "Quando a porta abriu, levei comigo a única coisa que Valdrak não esperava: memória digital."},
                    ],
                    "effects": {"tecnologia": 5, "sabedoria": 2, "marcas": 1},
                },
            ],
        },
    ],
    "endings": [
        {
            "id": "grupo_dos_despertos",
            "condition": {"amizade_min": 11, "allies_min": 4},
            "title": "Final: O Grupo dos Despertos",
            "text": [
                {"sfx": "wake", "text": "Acordei com o despertador gritando do lado da cama."},
                {"sfx": "wind", "text": "Por alguns segundos, ainda senti cheiro de chuva, ferro e fumaça."},
                {"sfx": "choice", "text": "Eu estava atrasado para a faculdade."},
                {"sfx": "wake", "text": "Peguei minhas coisas correndo e fui."},
                {"sfx": "ending_good", "text": "Quando encontrei meus amigos, contei tudo: Valdrak, os vikings, os lobos, os machados, os poderes e a última porta."},
                {"sfx": "tech", "text": "Eles riram no começo. Depois ficaram quietos quando descrevi exatamente como cada um apareceu no sonho."},
                {"sfx": "rune", "text": "Naquele dia, o grupo ganhou um nome: Os Eternos."},
            ],
        },
        {
            "id": "tecnologo_de_valdrak",
            "condition": {"tecnologia_min": 12, "sabedoria_min": 7},
            "title": "Final: O Tecnólogo de Valdrak",
            "text": [
                {"sfx": "wake", "text": "Acordei atrasado, com o celular na mão."},
                {"sfx": "scanner", "text": "A tela piscou por um segundo com um mapa azul que não deveria existir."},
                {"sfx": "tech", "text": "Na faculdade, contei aos meus amigos que meu poder no sonho era tecnologia."},
                {"sfx": "rune", "text": "Scanner de Runas. Mapa Holográfico. Pulso de Código."},
                {"sfx": "ending_good", "text": "Eles disseram que parecia história de jogo. E foi aí que percebi: talvez fosse mesmo para virar um."},
            ],
        },
        {
            "id": "marca_de_valdrak",
            "condition": {"marcas_min": 4},
            "title": "Final: A Marca de Valdrak",
            "text": [
                {"sfx": "wake", "text": "Acordei assustado e atrasado."},
                {"sfx": "rune", "text": "No pulso, uma marca azul apareceu por alguns segundos antes de sumir."},
                {"sfx": "wind", "text": "Na faculdade, tentei contar a história como brincadeira, mas minha voz saiu séria."},
                {"sfx": "shadow", "text": "Porque eu sabia: Valdrak ainda existia em algum lugar entre o sono e o medo."},
            ],
        },
        {
            "id": "sombra_de_valdrak",
            "condition": {"caos_min": 10},
            "title": "Final: A Sombra de Valdrak",
            "text": [
                {"sfx": "wake", "text": "Acordei como se tivesse caído de volta no corpo."},
                {"sfx": "horse", "text": "Na rua, por um segundo, ouvi cascos."},
                {"sfx": "axe_whoosh", "text": "Depois ouvi o vento de um machado cortando o ar."},
                {"sfx": "shadow", "text": "Na faculdade, contei a história rindo. Mas por dentro eu sabia que uma parte de Valdrak tinha acordado comigo."},
            ],
        },
        {
            "id": "sonho_que_virou_jogo",
            "condition": {},
            "title": "Final: O Sonho que Virou Jogo",
            "text": [
                {"sfx": "wake", "text": "Acordei atrasado para a faculdade."},
                {"sfx": "choice", "text": "No caminho, tentei organizar tudo na cabeça: os vikings, Valdrak, os poderes, o grupo e minha tecnologia."},
                {"sfx": "ending_good", "text": "Quando encontrei meus amigos, contei o sonho inteiro."},
                {"sfx": "tech", "text": "Eles disseram que parecia um jogo. E talvez esse fosse o verdadeiro motivo de eu ter sonhado."},
            ],
        },
    ],
}