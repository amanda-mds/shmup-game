"""Os três bosses do jogo, em ordem de fase.

Todos herdam da classe Boss (boss.py), que já sabe andar, levar dano, ficar furioso
e sortear ataques. Aqui cada um só diz quem ele é e quais são os ataques dele.
"""
import math
import random

import relogio
import sprites
from boss import Boss, Laser
from config import LARGURA, VELOCIDADE_TIRO_BOSS
from tiro import Tiro, TiroTeleguiado


class DiscoAlienigena(Boss):
    """Fase 1: o disco voador com o alienígena que joga estrelas."""

    NOME = "DISCO ALIENÍGENA"
    VIDA_POR_JOGADOR = 45
    VELOCIDADE = 3
    SPRITE = sprites.BOSS
    SPRITE_FURIOSO = sprites.BOSS_FURIOSO
    SPRITE_ACERTADO = sprites.BOSS_ACERTADO
    TIRO = sprites.TIRO_BOSS

    def criar_ataques(self):
        return [
            (self.ataque_leque, 900),
            (self.ataque_mirado, 800),
            (self.ataque_anel, 1300),
            (self.ataque_parede, 1700),
        ]

    def ataque_leque(self, jogadores):
        """5 estrelas abrindo em leque para baixo."""
        for angulo in (60, 75, 90, 105, 120):
            self.atirar_em_angulo(angulo, 4)

    def ataque_mirado(self, jogadores):
        """3 estrelas rápidas mirando em uma das naves. Não dá para ficar parada."""
        angulo = self.angulo_ate(random.choice(jogadores))
        for desvio in (-10, 0, 10):
            self.atirar_em_angulo(angulo + desvio, VELOCIDADE_TIRO_BOSS)

    def ataque_anel(self, jogadores):
        """Semicírculo de estrelas com uma brecha em lugar aleatório."""
        angulos = list(range(15, 166, 15))
        inicio_brecha = random.randint(1, len(angulos) - 3)
        del angulos[inicio_brecha:inicio_brecha + 2]
        for angulo in angulos:
            self.atirar_em_angulo(angulo, 3)

    def ataque_parede(self, jogadores):
        """Uma fileira de estrelas lentas descendo do topo, com um buraco para passar."""
        espaco = 24
        posicoes = list(range(espaco // 2, LARGURA, espaco))
        inicio_buraco = random.randint(0, len(posicoes) - 3)
        del posicoes[inicio_buraco:inicio_buraco + 3]
        for x in posicoes:
            self.tiros.append(Tiro(x, -10, self.TIRO, 0, 2))


class RoboDestruidor(Boss):
    """Fase 2: robô que varre a tela, solta laser e faz chover parafusos de energia."""

    NOME = "ROBÔ DESTRUIDOR"
    VIDA_POR_JOGADOR = 60
    VELOCIDADE = 2
    SPRITE = sprites.ROBO
    SPRITE_FURIOSO = sprites.ROBO_FURIOSO
    SPRITE_ACERTADO = sprites.ROBO_ACERTADO
    TIRO = sprites.TIRO_ROBO

    def criar_ataques(self):
        return [
            (self.ataque_varredura, 1600),
            (self.ataque_laser, 1700),
            (self.ataque_chuva, 1800),
            (self.ataque_garras, 1300),
        ]

    def ataque_varredura(self, jogadores):
        """Uma rajada que vai varrendo de um lado para o outro, um tiro de cada vez.

        Dá para ver de que lado ela começa e correr para o outro.
        """
        angulos = [35 + i * 7 for i in range(16)]
        if random.random() < 0.5:
            angulos.reverse()
        for numero, angulo in enumerate(angulos):
            self.agendar(numero * 70, lambda angulo=angulo: self.atirar_em_angulo(angulo, 3.5))

    def ataque_laser(self, jogadores):
        """Mira um laser em cada nave. Primeiro avisa, depois dispara."""
        for jogador in jogadores:
            self.lasers.append(Laser(jogador.rect.centerx, self.rect.bottom))
        self.parado_ate = relogio.agora() + Laser.TEMPO_AVISO + Laser.TEMPO_ATIVO

    def ataque_chuva(self, jogadores):
        """10 tiros caindo do topo em lugares aleatórios, um atrás do outro."""
        for numero in range(10):
            def cair():
                x = random.randint(20, LARGURA - 20)
                desvio = random.uniform(-0.5, 0.5)
                self.tiros.append(Tiro(x, -10, self.TIRO, desvio, 3))
            self.agendar(numero * 130, cair)

    def ataque_garras(self, jogadores):
        """As duas garras atiram, alternando, mirando nas naves."""
        alvo = random.choice(jogadores)
        for numero in range(6):
            garra = 10 if numero % 2 == 0 else self.rect.width - 10

            def atirar(garra=garra):
                if not alvo.esta_vivo():
                    return
                origem_x = self.rect.x + garra
                angulo = self.angulo_ate(alvo, origem_x, self.rect.bottom)
                self.atirar_em_angulo(angulo, 4.5, origem_x, self.rect.bottom)

            self.agendar(numero * 160, atirar)


class OlhoCosmico(Boss):
    """Fase 3: um olho gigante que flutua e solta tiros que perseguem a nave."""

    NOME = "OLHO CÓSMICO"
    VIDA_POR_JOGADOR = 75
    VELOCIDADE = 2
    SPRITE = sprites.OLHO
    SPRITE_FURIOSO = sprites.OLHO_FURIOSO
    SPRITE_ACERTADO = sprites.OLHO_ACERTADO
    TIRO = sprites.TIRO_OLHO

    def criar_ataques(self):
        return [
            (self.ataque_teleguiado, 1800),
            (self.ataque_anel_completo, 1300),
            (self.ataque_flor, 1700),
            (self.ataque_olhar, 1400),
        ]

    def mover(self):
        """Além de ir de um lado para o outro, sobe e desce devagar, como se flutuasse."""
        super().mover()
        self.rect.top = 50 + round(math.sin(relogio.agora() / 400) * 12)

    def ataque_teleguiado(self, jogadores):
        """3 bolinhas vermelhas que perseguem uma nave por um tempo. Faça curvas para despistar."""
        alvo = random.choice(jogadores)
        for numero in range(3):
            def soltar():
                angulo = 90 + random.uniform(-35, 35)
                self.tiros.append(TiroTeleguiado(self.rect.centerx, self.rect.bottom - 10,
                                                 sprites.TIRO_TELEGUIADO, angulo, 2.6,
                                                 alvo, tempo_perseguindo=1600))
            self.agendar(numero * 250, soltar)

    def ataque_anel_completo(self, jogadores):
        """Anel de tiros para todos os lados, com uma brecha em lugar aleatório."""
        quantidade = 22
        inicio_brecha = random.randint(2, 8)
        for numero in range(quantidade):
            if inicio_brecha <= numero < inicio_brecha + 3:
                continue
            angulo = numero * 360 / quantidade
            self.atirar_em_angulo(angulo, 2.4, y=self.rect.centery)

    def ataque_flor(self, jogadores):
        """3 ondas de tiros em todas as direções, cada uma girada um pouco, formando uma flor."""
        for onda in range(3):
            def soltar_onda(onda=onda):
                for numero in range(10):
                    self.atirar_em_angulo(numero * 36 + onda * 12, 2.2, y=self.rect.centery)
            self.agendar(onda * 300, soltar_onda)

    def ataque_olhar(self, jogadores):
        """Uma sequência de 7 tiros rápidos, cada um mirando onde a nave está naquele momento."""
        alvo = random.choice(jogadores)
        for numero in range(7):
            def atirar():
                if alvo.esta_vivo():
                    self.atirar_em_angulo(self.angulo_ate(alvo), VELOCIDADE_TIRO_BOSS)
            self.agendar(numero * 110, atirar)


FASES = [DiscoAlienigena, RoboDestruidor, OlhoCosmico]