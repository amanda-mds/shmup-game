import pygame


LARGURA = 480
ALTURA = 640
FPS = 60
TITULO = "Nave vs Boss"

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (0, 120, 255)
AZUL_CLARO = (80, 160, 255)
VERMELHO = (220, 0, 0)
AMARELO = (255, 220, 0)
VERDE = (0, 200, 0)
ROXO = (140, 0, 180)
CINZA = (150, 150, 170)

VIDAS_JOGADOR = 3
VELOCIDADE_JOGADOR = 5
VELOCIDADE_TIRO = 8
INTERVALO_TIRO = 250
TEMPO_INVENCIVEL = 1000


CONTROLES_VERMELHO = {
    "esquerda": [pygame.K_a],
    "direita": [pygame.K_d],
    "cima": [pygame.K_w],
    "baixo": [pygame.K_s],
    "atirar": [pygame.K_SPACE],
}

CONTROLES_AZUL = {
    "esquerda": [pygame.K_LEFT],
    "direita": [pygame.K_RIGHT],
    "cima": [pygame.K_UP],
    "baixo": [pygame.K_DOWN],
    "atirar": [pygame.K_RETURN, pygame.K_KP_ENTER],
}

CONTROLES_SOLO = {
    "esquerda": [pygame.K_LEFT, pygame.K_a],
    "direita": [pygame.K_RIGHT, pygame.K_d],
    "cima": [pygame.K_UP, pygame.K_w],
    "baixo": [pygame.K_DOWN, pygame.K_s],
    "atirar": [pygame.K_SPACE],
}

TECLAS_PAUSA = [pygame.K_p, pygame.K_ESCAPE]
TECLA_SOM = pygame.K_n

INTERVALO_CORACAO_SOLO = 22000
INTERVALO_CORACAO_DUPLA = 18000
INTERVALO_POWERUP = 15000
VELOCIDADE_ITEM = 1.5

TEMPO_TIRO_TRIPLO = 8000
TEMPO_TIRO_RAPIDO = 8000

VELOCIDADE_TIRO_BOSS = 5

PONTOS_POR_ACERTO = 10
PONTOS_POR_BOSS = 1000
PONTOS_POR_ITEM = 100
PONTOS_POR_VIDA_NO_FIM = 500