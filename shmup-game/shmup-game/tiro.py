import math

import relogio
from config import LARGURA, ALTURA

TEMPO_POR_QUADRO = 120


class Tiro:
    """Um tiro que anda em linha reta. Serve tanto para as naves quanto para os bosses.

    O sprite pode ser uma imagem só (laser das naves) ou uma lista de imagens,
    que viram uma animação (estrela piscando do boss).
    """

    def __init__(self, centro_x, y, sprite, velocidade_x, velocidade_y):
        if isinstance(sprite, list):
            self.quadros = sprite
        else:
            self.quadros = [sprite]

        self.rect = self.quadros[0].get_rect(centerx=round(centro_x), top=round(y))
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.velocidade_x = velocidade_x
        self.velocidade_y = velocidade_y

    def atualizar(self):
        self.pos_x += self.velocidade_x
        self.pos_y += self.velocidade_y
        self.rect.x = round(self.pos_x)
        self.rect.y = round(self.pos_y)

    def saiu_da_tela(self):
        return (
            self.rect.bottom < -20
            or self.rect.top > ALTURA
            or self.rect.right < 0
            or self.rect.left > LARGURA
        )

    def desenhar(self, tela):
        quadro = (relogio.agora() // TEMPO_POR_QUADRO) % len(self.quadros)
        tela.blit(self.quadros[quadro], self.rect)


class TiroTeleguiado(Tiro):
    """Tiro que vai virando na direção de uma nave por um tempo e depois segue reto.

    Herda tudo do Tiro e só muda o atualizar(): antes de andar, ele gira um
    pouquinho na direção do alvo. Como ele não pode virar muito de uma vez,
    dá para despistar fazendo uma curva rápida.
    """

    GIRO_MAXIMO = 2.5

    def __init__(self, centro_x, y, sprite, angulo, velocidade, alvo, tempo_perseguindo):
        radianos = math.radians(angulo)
        super().__init__(centro_x, y, sprite,
                         math.cos(radianos) * velocidade, math.sin(radianos) * velocidade)
        self.angulo = angulo
        self.velocidade = velocidade
        self.alvo = alvo
        self.persegue_ate = relogio.agora() + tempo_perseguindo

    def atualizar(self):
        if relogio.agora() < self.persegue_ate and self.alvo.esta_vivo():
            distancia_x = self.alvo.rect.centerx - self.rect.centerx
            distancia_y = self.alvo.rect.centery - self.rect.centery
            angulo_desejado = math.degrees(math.atan2(distancia_y, distancia_x))

            diferenca = (angulo_desejado - self.angulo + 180) % 360 - 180
            giro = max(-self.GIRO_MAXIMO, min(self.GIRO_MAXIMO, diferenca))
            self.angulo += giro

            radianos = math.radians(self.angulo)
            self.velocidade_x = math.cos(radianos) * self.velocidade
            self.velocidade_y = math.sin(radianos) * self.velocidade

        super().atualizar()