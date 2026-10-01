import math
import random

import pygame

PALETA = {
    "W": (255, 255, 255),
    "C": (0, 220, 255),
    "B": (0, 90, 220),
    "G": (120, 120, 140),
    "R": (230, 30, 30),
    "Y": (255, 230, 0),
    "O": (255, 130, 0),
    "P": (110, 0, 160),
    "L": (180, 90, 230),
    "D": (60, 0, 100),
    "M": (200, 20, 40),
    "K": (225, 225, 210),
    "N": (150, 150, 145),
    "Q": (170, 170, 160),
    "V": (60, 120, 170),
    "A": (100, 225, 70),
    "E": (30, 120, 40),
    "X": (10, 10, 10),
    "F": (165, 120, 80),
    "T": (120, 80, 50),
    "U": (70, 45, 30),
    "H": (190, 190, 205),
    "Z": (70, 70, 85),
    "I": (240, 60, 120),
    "J": (25, 25, 55),
}


def trocar_cores(desenho, trocas):
    """Devolve uma cópia do desenho trocando letras. Ex.: {"B": "M"} troca azul por vermelho."""
    return ["".join(trocas.get(letra, letra) for letra in linha) for linha in desenho]


def criar_sprite(desenho, escala, cor_unica=None):
    """Transforma um desenho em texto numa imagem pixelada.

    escala: tamanho de cada pixel na tela (3 = cada letra vira um quadrado 3x3).
    cor_unica: se informada, pinta tudo de uma cor só (usado no "piscar" do boss).
    """
    largura = len(desenho[0])
    for numero, linha in enumerate(desenho):
        if len(linha) != largura:
            raise ValueError(f"Linha {numero} do desenho tem tamanho diferente das outras")

    sprite = pygame.Surface((largura * escala, len(desenho) * escala), pygame.SRCALPHA)
    for y, linha in enumerate(desenho):
        for x, letra in enumerate(linha):
            if letra == ".":
                continue
            cor = cor_unica or PALETA[letra]
            pygame.draw.rect(sprite, cor, (x * escala, y * escala, escala, escala))
    return sprite


DESENHO_NAVE = [
    "......W......",
    ".....WCW.....",
    ".....WCW.....",
    "....WBCBW....",
    "....WBBBW....",
    ".R..WBBBW..R.",
    ".R.WBBBBBW.R.",
    ".WWBBBBBBBWW.",
    "WBBBBBBBBBBBW",
    "WBBGGBBBGGBBW",
    "WBG..BBB..GBW",
    ".G...GGG...G.",
]

DESENHO_CHAMA_1 = [
    "OYO",
    ".O.",
]
DESENHO_CHAMA_2 = [
    "YOY",
    "OYO",
    ".Y.",
]

DESENHO_BOSS = [
    "..........VVVVVVVV..........",
    "........VVWVVVVVVVVV........",
    ".......VVWVVAAAAVVVVV.......",
    ".......VWVVAAAAAAVVVV.......",
    "......VVVVAXXAAXXAVVVV......",
    "......VVVVAXXAAXXAVVVV......",
    "......VVVVAAAAAAAAVVVV......",
    "......VVVVVAAEEAAVVVVV......",
    "......VVVVVEAAAAEVVVVV......",
    "....PPPPPPPPPPPPPPPPPPPP....",
    "...PPLLRRLLLLLLLLLLRRLLPP...",
    "..PPLLRRRRLLLLLLLLRRRRLLPP..",
    ".PPPPPPPPPPPPPPPPPPPPPPPPPP.",
    "PDDDDDDDDDDDDDDDDDDDDDDDDDDP",
    "PDDYDDYDDYDDYDDYDDYDDYDDYDDP",
    ".PDDDDDDDDDDDDDDDDDDDDDDDDP.",
    "..PPPPPPPPPPPPPPPPPPPPPPPP..",
    "....PP..PP..PPPP..PP..PP....",
    "....RR..RR...RR...RR..RR....",
]

DESENHO_TIRO_JOGADOR = [
    "WW",
    "CC",
    "CC",
    "BB",
]

DESENHO_ESTRELA = [
    "...Y...",
    "..YYY..",
    "YYYWYYY",
    ".YYYYY.",
    "..YYY..",
    ".YY.YY.",
    ".Y...Y.",
]

DESENHO_LUA = [
    ".....KKKKKK.....",
    "...KKKKKKKKKK...",
    "..KKKKKKKKKQKN..",
    ".KKKQQKKKKKKKKN.",
    ".KKQQQKKKKKKKKN.",
    "KKKKQKKKKKKKKKNN",
    "KKKKKKKKQQKKKKNN",
    "KKKKKKKQQQQKKKNN",
    "KKKKKKKKQQKKKKNN",
    "KKQKKKKKKKKKKNNN",
    "KKKKKKKKKKKKKNNN",
    ".KKKKKKKQKKKKNN.",
    ".KKKKKKKKKKKNNN.",
    "..KKKKKKKKKNNN..",
    "...KKKKKKNNNN...",
    ".....NNNNNN.....",
]

DESENHO_METEORO = [
    "..UTTU..",
    ".UTFFTU.",
    "UTFFTTTU",
    "UTFTTUTU",
    "UTTTUUTU",
    "UTUTTTTU",
    ".UTTTTU.",
    "..UUUU..",
]

DESENHO_CORACAO = [
    ".RR...RR.",
    "RWRR.RRRR",
    "RWRRRRRRR",
    "RRRRRRRRR",
    ".RRRRRRR.",
    "..RRRRR..",
    "...RRR...",
    "....R....",
]


DESENHO_ROBO = [
    "............YY............",
    "............ZZ............",
    "............ZZ............",
    "....HHHHHHHHHHHHHHHHHH....",
    "...HHGGGGGGGGGGGGGGGGHH...",
    "...HGGZZZZZZZZZZZZZZGGH...",
    "...HGZRRRRZZZZZZRRRRZGH...",
    "...HGZRWRRZZZZZZRWRRZGH...",
    "...HGZRRRRZZZZZZRRRRZGH...",
    "...HGGZZZZZZZZZZZZZZGGH...",
    "...HGGGYGYGYGGYGYGYGGGH...",
    "...HGGGGGGGGGGGGGGGGGGH...",
    "HH..HHHHHHHHHHHHHHHHHH..HH",
    "HZH..ZZZZZZZZZZZZZZZZ..HZH",
    "HZH....GGGGGGGGGGGG....HZH",
    "HZZH....CCCCCCCCCC....HZZH",
    ".HZH..................HZH.",
    "H..H..................H..H",
]

DESENHO_TIRO_ROBO = [
    "..I..",
    ".IWI.",
    "IWWWI",
    ".IWI.",
    "..I..",
]


DESENHO_OLHO = [
    "........PPPPPPPP........",
    "......PPLLLLLLLLPP......",
    ".....PLLWWWWWWWWLLP.....",
    "....PLWWWWWWWWWWWWLP....",
    "...PLWWWWWIIIIWWWWWLP...",
    "...PLWWWWIIIIIIWWWWLP...",
    "..PLWWWWIIIXXIIIWWWWLP..",
    "..PLWWWWIIXWXXIIWWWWLP..",
    "..PLWWWWIIXXXXIIWWWWLP..",
    "..PLWWWWIIIXXIIIWWWWLP..",
    "...PLWWWWIIIIIIWWWWLP...",
    "...PLWWWWWIIIIWWWWWLP...",
    "....PLWWWWWWWWWWWWLP....",
    ".....PLLWWWWWWWWLLP.....",
    "......PPLLLLLLLLPP......",
    "....DP.PDP.PP.PDP.PD....",
    "...DP..DP..PP..PD..PD...",
    "..DP..DP...DD...PD..PD..",
    "..D...D....DD....D...D..",
]

DESENHO_TIRO_OLHO = [
    ".EEEE.",
    "EAAAAE",
    "EAWAAE",
    "EAAAAE",
    "EAAAAE",
    ".EEEE.",
]

DESENHO_TELEGUIADO = [
    "..RRR..",
    ".RRRRR.",
    "RRWWWRR",
    "RRWXWRR",
    "RRWWWRR",
    ".RRRRR.",
    "..RRR..",
]


DESENHO_ITEM_TRIPLO = [
    "...OOOOO...",
    "..OJJJJJO..",
    ".OJCJCJCJO.",
    "OJJCJCJCJJO",
    "OJJCJCJCJJO",
    "OJJBJBJBJJO",
    "OJJJJJJJJJO",
    ".OJJJJJJJO.",
    "..OJJJJJO..",
    "...OOOOO...",
]

DESENHO_ITEM_ESCUDO = [
    "...CCCCC...",
    "..CJJJJJC..",
    ".CJBBBBBJC.",
    "CJJBWWWBJJC",
    "CJJBWWWBJJC",
    "CJJBBWBBJJC",
    "CJJJBBBJJJC",
    ".CJJJBJJJC.",
    "..CJJJJJC..",
    "...CCCCC...",
]

DESENHO_ITEM_RAPIDO = [
    "...YYYYY...",
    "..YJJJJJY..",
    ".YJJJJWWJY.",
    "YJJJJWWJJJY",
    "YJJJWWJJJJY",
    "YJJWWWWWJJY",
    "YJJJJWWJJJY",
    "YJJJWWJJJJY",
    ".YJJWJJJJY.",
    "..YJJJJJY..",
    "...YYYYY...",
]


def criar_explosao(raio, escala, quantidade_quadros=7, semente=1):
    """Gera os quadros de uma explosão em pixel art, sem precisar desenhar à mão.

    Cada quadro é um círculo de pixels maior que o anterior. O centro é mais quente
    (branco e amarelo) e a borda é mais fria (laranja e vermelho). Nos últimos quadros
    o meio vai "apagando", virando um anel de fumaça que some.
    """
    cores = [
        (255, 255, 255),
        (255, 240, 120),
        (255, 180, 40),
        (240, 100, 20),
        (180, 40, 20),
        (90, 30, 30),
    ]
    sorteio = random.Random(semente)
    tamanho = raio * 2 + 1
    quadros = []

    for numero in range(quantidade_quadros):
        progresso = numero / (quantidade_quadros - 1)
        raio_atual = raio * (0.35 + 0.65 * progresso)
        buraco = raio_atual * max(0, progresso - 0.45) * 1.6

        quadro = pygame.Surface((tamanho * escala, tamanho * escala), pygame.SRCALPHA)
        for y in range(tamanho):
            for x in range(tamanho):
                distancia = math.hypot(x - raio, y - raio)
                borda = raio_atual * sorteio.uniform(0.8, 1.0)
                if distancia > borda or distancia < buraco:
                    continue
                calor = distancia / max(borda, 1) * 0.6 + progresso * 0.6
                cor = cores[min(len(cores) - 1, int(calor * len(cores)))]
                pygame.draw.rect(quadro, cor, (x * escala, y * escala, escala, escala))
        quadros.append(quadro)

    return quadros


DESENHO_NAVE_VERMELHA = trocar_cores(DESENHO_NAVE, {"B": "M", "C": "Y", "R": "C"})
DESENHO_TIRO_VERMELHO = trocar_cores(DESENHO_TIRO_JOGADOR, {"C": "Y", "B": "O"})


NAVE_AZUL = criar_sprite(DESENHO_NAVE, 3)
ICONE_AZUL = criar_sprite(DESENHO_NAVE, 2)
TIRO_AZUL = criar_sprite(DESENHO_TIRO_JOGADOR, 3)

NAVE_VERMELHA = criar_sprite(DESENHO_NAVE_VERMELHA, 3)
ICONE_VERMELHO = criar_sprite(DESENHO_NAVE_VERMELHA, 2)
TIRO_VERMELHO = criar_sprite(DESENHO_TIRO_VERMELHO, 3)

CHAMAS = [criar_sprite(DESENHO_CHAMA_1, 3), criar_sprite(DESENHO_CHAMA_2, 3)]

BOSS = criar_sprite(DESENHO_BOSS, 4)
BOSS_FURIOSO = criar_sprite(
    trocar_cores(DESENHO_BOSS, {"P": "M", "L": "O", "R": "Y", "A": "R", "E": "M"}), 4)
BOSS_ACERTADO = criar_sprite(DESENHO_BOSS, 4, cor_unica=(255, 255, 255))

ROBO = criar_sprite(DESENHO_ROBO, 4)
ROBO_FURIOSO = criar_sprite(trocar_cores(DESENHO_ROBO, {"G": "M", "H": "O", "R": "Y"}), 4)
ROBO_ACERTADO = criar_sprite(DESENHO_ROBO, 4, cor_unica=(255, 255, 255))

OLHO = criar_sprite(DESENHO_OLHO, 4)
OLHO_FURIOSO = criar_sprite(trocar_cores(DESENHO_OLHO, {"P": "M", "L": "O", "I": "Y", "D": "R"}), 4)
OLHO_ACERTADO = criar_sprite(DESENHO_OLHO, 4, cor_unica=(255, 255, 255))

TIRO_BOSS = [
    criar_sprite(DESENHO_ESTRELA, 2),
    criar_sprite(trocar_cores(DESENHO_ESTRELA, {"Y": "O", "W": "Y"}), 2),
]
TIRO_ROBO = [
    criar_sprite(DESENHO_TIRO_ROBO, 2),
    criar_sprite(trocar_cores(DESENHO_TIRO_ROBO, {"W": "Y"}), 2),
]
TIRO_OLHO = [
    criar_sprite(DESENHO_TIRO_OLHO, 2),
    criar_sprite(trocar_cores(DESENHO_TIRO_OLHO, {"A": "W", "E": "A"}), 2),
]
TIRO_TELEGUIADO = [
    criar_sprite(DESENHO_TELEGUIADO, 2),
    criar_sprite(trocar_cores(DESENHO_TELEGUIADO, {"R": "M"}), 2),
]

CORACAO = criar_sprite(DESENHO_CORACAO, 3)
ITENS = {
    "vida": CORACAO,
    "triplo": criar_sprite(DESENHO_ITEM_TRIPLO, 3),
    "escudo": criar_sprite(DESENHO_ITEM_ESCUDO, 3),
    "rapido": criar_sprite(DESENHO_ITEM_RAPIDO, 3),
}
ICONES_POWERUP = {
    "triplo": criar_sprite(DESENHO_ITEM_TRIPLO, 2),
    "escudo": criar_sprite(DESENHO_ITEM_ESCUDO, 2),
    "rapido": criar_sprite(DESENHO_ITEM_RAPIDO, 2),
}

EXPLOSAO_PEQUENA = criar_explosao(raio=4, escala=2, quantidade_quadros=5, semente=1)
EXPLOSAO_MEDIA = criar_explosao(raio=9, escala=3, semente=2)
EXPLOSAO_GRANDE = criar_explosao(raio=14, escala=4, quantidade_quadros=8, semente=3)

LUA = criar_sprite(DESENHO_LUA, 4)
METEORO_PEQUENO = criar_sprite(DESENHO_METEORO, 2)
METEORO_GRANDE = criar_sprite(DESENHO_METEORO, 3)