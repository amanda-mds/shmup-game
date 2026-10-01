import math
import random

import relogio
import sprites
from config import LARGURA, ALTURA, VELOCIDADE_ITEM

BALANCO = 25
PISCA_A_PARTIR_DE = 0.75

POWERUPS = ["triplo", "escudo", "rapido"]


class Item:
    """Item que cai do topo da tela balançando. Quem encostar pega.

    tipo pode ser:
      "vida"   -> recupera 1 vida (o coraçãozinho)
      "triplo" -> tiro triplo por alguns segundos
      "escudo" -> escudo que aguenta um tiro
      "rapido" -> atira duas vezes mais rápido por alguns segundos
    """

    def __init__(self, tipo):
        self.tipo = tipo
        self.sprite = sprites.ITENS[tipo]
        largura = self.sprite.get_width()
        self.centro_x = random.randint(BALANCO + largura, LARGURA - BALANCO - largura)
        self.y = float(-self.sprite.get_height())
        self.quadros_vivo = 0
        self.rect = self.sprite.get_rect(centerx=self.centro_x, top=round(self.y))

    def atualizar(self):
        self.quadros_vivo += 1
        self.y += VELOCIDADE_ITEM
        deslocamento = math.sin(self.quadros_vivo / 25) * BALANCO
        self.rect.centerx = round(self.centro_x + deslocamento)
        self.rect.y = round(self.y)

    def saiu_da_tela(self):
        return self.rect.top > ALTURA

    def pode_ser_pego_por(self, jogador):
        if self.tipo == "vida":
            return jogador.precisa_de_vida()
        return jogador.esta_vivo()

    def aplicar(self, jogador):
        if self.tipo == "vida":
            jogador.ganhar_vida()
        else:
            jogador.ganhar_powerup(self.tipo)

    def desenhar(self, tela):
        if self.y > ALTURA * PISCA_A_PARTIR_DE and (relogio.agora() // 120) % 2 == 0:
            return
        tela.blit(self.sprite, self.rect)