import random

import pygame

import sprites
from config import LARGURA, ALTURA

VELOCIDADE_LUA = 0.3

INTERVALO_METEORO_MIN = 180
INTERVALO_METEORO_MAX = 420


class Meteoro:
    """Uma pedra com rastro de fogo que atravessa o fundo na diagonal. É só decoração."""

    CORES_RASTRO = [
        (255, 240, 150),
        (255, 220, 80),
        (255, 180, 50),
        (255, 140, 30),
        (230, 100, 20),
        (200, 70, 20),
        (160, 40, 20),
        (110, 25, 20),
        (70, 15, 20),
    ]

    def __init__(self):
        grande = random.random() < 0.4
        self.sprite = sprites.METEORO_GRANDE if grande else sprites.METEORO_PEQUENO
        rapidez = 1.4 if grande else 1.0
        self.tamanho_rastro = 9 if grande else 6

        direcao = random.choice([-1, 1])
        self.velocidade_x = direcao * random.uniform(1.5, 2.5) * rapidez
        self.velocidade_y = random.uniform(2.5, 3.5) * rapidez

        if direcao == 1:
            self.x = random.uniform(-40, LARGURA * 0.6)
        else:
            self.x = random.uniform(LARGURA * 0.4, LARGURA + 40)
        self.y = -self.sprite.get_height() - 10

    def atualizar(self):
        self.x += self.velocidade_x
        self.y += self.velocidade_y

    def saiu_da_tela(self):
        return self.y > ALTURA or self.x < -80 or self.x > LARGURA + 80

    def desenhar(self, tela):
        centro_x = self.x + self.sprite.get_width() / 2
        centro_y = self.y + self.sprite.get_height() / 2

        for i, cor in enumerate(self.CORES_RASTRO, start=1):
            tamanho = max(2, self.tamanho_rastro - (i - 1) * self.tamanho_rastro // len(self.CORES_RASTRO))
            rastro_x = centro_x - self.velocidade_x * i * 1.6
            rastro_y = centro_y - self.velocidade_y * i * 1.6
            pygame.draw.rect(tela, cor, (round(rastro_x - tamanho / 2),
                                         round(rastro_y - tamanho / 2),
                                         tamanho, tamanho))

        tela.blit(self.sprite, (round(self.x), round(self.y)))


class Fundo:
    """Estrelas, lua e meteoros passando pela tela, dando a sensação de que a nave está voando.

    Cada coisa anda numa velocidade diferente: a lua é a mais lenta (parece longe),
    as estrelas variam, e os meteoros cortam a tela na diagonal. Isso dá um efeito
    de profundidade bem estilo jogo antigo.
    """

    CAMADAS = [
        (1, 1, (90, 90, 110), 40),
        (2, 2, (160, 160, 190), 25),
        (4, 2, (255, 255, 255), 10),
    ]

    def __init__(self):
        self.estrelas = []
        for velocidade, tamanho, cor, quantidade in self.CAMADAS:
            for _ in range(quantidade):
                x = random.randint(0, LARGURA)
                y = random.randint(0, ALTURA)
                self.estrelas.append([x, y, velocidade, tamanho, cor])

        self.lua_x = LARGURA - 130
        self.lua_y = 110.0

        self.meteoros = []
        self.quadros_ate_meteoro = random.randint(INTERVALO_METEORO_MIN, INTERVALO_METEORO_MAX)

    def atualizar(self):
        for estrela in self.estrelas:
            estrela[1] += estrela[2]
            if estrela[1] > ALTURA:
                estrela[0] = random.randint(0, LARGURA)
                estrela[1] = 0

        self.lua_y += VELOCIDADE_LUA
        if self.lua_y > ALTURA:
            self.lua_y = -sprites.LUA.get_height()
            self.lua_x = random.randint(20, LARGURA - sprites.LUA.get_width() - 20)

        self.quadros_ate_meteoro -= 1
        if self.quadros_ate_meteoro <= 0:
            self.meteoros.append(Meteoro())
            self.quadros_ate_meteoro = random.randint(INTERVALO_METEORO_MIN, INTERVALO_METEORO_MAX)

        for meteoro in self.meteoros[:]:
            meteoro.atualizar()
            if meteoro.saiu_da_tela():
                self.meteoros.remove(meteoro)

    def desenhar(self, tela):
        for x, y, _, tamanho, cor in self.estrelas:
            pygame.draw.rect(tela, cor, (x, y, tamanho, tamanho))
        tela.blit(sprites.LUA, (self.lua_x, round(self.lua_y)))
        for meteoro in self.meteoros:
            meteoro.desenhar(tela)