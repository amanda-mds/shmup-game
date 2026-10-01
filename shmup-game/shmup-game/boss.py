import math
import random

import pygame

import relogio
from config import LARGURA, ALTURA
from tiro import Tiro

TEMPO_PISCANDO = 60
TEMPO_ANTES_DO_PRIMEIRO = 1500
PAUSA_FURIOSO = 0.7
ALTURA_DO_BOSS = 50


class Laser:
    """Raio vertical. Primeiro aparece uma linha de aviso piscando, depois o raio de verdade.

    O aviso dá tempo de sair do caminho, então ele é difícil de ignorar mas justo.
    """

    TEMPO_AVISO = 900
    TEMPO_ATIVO = 600
    LARGURA_DESENHO = 26
    LARGURA_DANO = 18

    def __init__(self, centro_x, topo):
        self.inicio = relogio.agora()
        self.rect = pygame.Rect(0, topo, self.LARGURA_DANO, ALTURA - topo)
        self.rect.centerx = centro_x

    def tempo_passado(self):
        return relogio.agora() - self.inicio

    def esta_ativo(self):
        return self.TEMPO_AVISO <= self.tempo_passado() < self.TEMPO_AVISO + self.TEMPO_ATIVO

    def acabou(self):
        return self.tempo_passado() >= self.TEMPO_AVISO + self.TEMPO_ATIVO

    def desenhar(self, tela):
        x = self.rect.centerx
        topo = self.rect.top
        if not self.esta_ativo():
            if (relogio.agora() // 100) % 2 == 0:
                pygame.draw.line(tela, (255, 60, 60), (x, topo), (x, ALTURA), 2)
            return
        largura = self.LARGURA_DESENHO + (relogio.agora() // 50) % 3 * 2
        pygame.draw.rect(tela, (255, 60, 180), (x - largura // 2, topo, largura, ALTURA - topo))
        pygame.draw.rect(tela, (255, 255, 255), (x - largura // 4, topo, largura // 2, ALTURA - topo))


class Boss:
    """Classe base de todos os bosses.

    Aqui fica tudo que os bosses têm em comum: entrar na tela, andar de um lado para
    o outro, levar dano, ficar furioso na metade da vida, sortear ataques e desenhar.

    Cada boss de verdade (no bosses.py) herda desta classe e só precisa dizer:
      - o nome, a vida, a velocidade e os sprites (atributos da classe)
      - quais são os ataques dele (método criar_ataques)
    """

    NOME = "BOSS"
    VIDA_POR_JOGADOR = 50
    VELOCIDADE = 3
    SPRITE = None
    SPRITE_FURIOSO = None
    SPRITE_ACERTADO = None
    TIRO = None

    def __init__(self, quantidade_jogadores):
        self.sprite = self.SPRITE
        self.rect = self.sprite.get_rect(centerx=LARGURA // 2, bottom=0)
        self.vida_maxima = self.VIDA_POR_JOGADOR * quantidade_jogadores
        self.vida = self.vida_maxima
        self.velocidade = self.VELOCIDADE
        self.furioso = False
        self.entrou = False

        self.tiros = []
        self.lasers = []
        self.agendados = []
        self.parado_ate = 0

        self.tempo_ultimo_dano = -TEMPO_PISCANDO
        self.tempo_proximo_ataque = 0
        self.ultimo_ataque = None
        self.ataques = self.criar_ataques()

    def criar_ataques(self):
        """Lista de (método do ataque, pausa em milissegundos depois dele).

        Cada boss filho é obrigado a escrever o seu.
        """
        raise NotImplementedError("Cada boss precisa definir os próprios ataques")


    def atirar_em_angulo(self, angulo, velocidade, x=None, y=None, sprite=None):
        """Cria um tiro na direção do ângulo (em graus): 0 = direita, 90 = baixo, 180 = esquerda."""
        x = self.rect.centerx if x is None else x
        y = self.rect.bottom if y is None else y
        radianos = math.radians(angulo)
        self.tiros.append(Tiro(x, y, sprite or self.TIRO,
                               math.cos(radianos) * velocidade, math.sin(radianos) * velocidade))

    def angulo_ate(self, alvo, x=None, y=None):
        """Ângulo de um ponto (o boss, por padrão) até o centro de uma nave."""
        x = self.rect.centerx if x is None else x
        y = self.rect.bottom if y is None else y
        return math.degrees(math.atan2(alvo.rect.centery - y, alvo.rect.centerx - x))

    def agendar(self, atraso, funcao):
        """Faz uma função rodar daqui a alguns milissegundos.

        Serve para ataques em sequência, como uma rajada que solta um tiro de cada vez.
        """
        self.agendados.append((relogio.agora() + atraso, funcao))

    def processar_agendados(self):
        agora = relogio.agora()
        prontos = [funcao for momento, funcao in self.agendados if momento <= agora]
        self.agendados = [(momento, funcao) for momento, funcao in self.agendados if momento > agora]
        for funcao in prontos:
            funcao()


    def escolher_ataque(self):
        """Sorteia um ataque, sem repetir o mesmo duas vezes seguidas."""
        opcoes = [ataque for ataque in self.ataques if ataque != self.ultimo_ataque]
        if not opcoes:
            opcoes = self.ataques
        ataque = random.choice(opcoes)
        self.ultimo_ataque = ataque
        return ataque

    def atacar(self, jogadores):
        agora = relogio.agora()
        if agora < self.tempo_proximo_ataque or not jogadores:
            return

        funcao_ataque, pausa = self.escolher_ataque()
        funcao_ataque(jogadores)

        if self.furioso:
            pausa = int(pausa * PAUSA_FURIOSO)
        self.tempo_proximo_ataque = agora + pausa


    def esta_entrando(self):
        return not self.entrou

    def mover(self):
        """Anda de um lado para o outro. Os bosses filhos podem mudar isso."""
        if relogio.agora() < self.parado_ate:
            return
        self.rect.x += self.velocidade
        if self.rect.left <= 0:
            self.rect.left = 0
            self.velocidade = abs(self.velocidade)
        elif self.rect.right >= LARGURA:
            self.rect.right = LARGURA
            self.velocidade = -abs(self.velocidade)

    def verificar_furia(self):
        if not self.furioso and self.vida <= self.vida_maxima // 2:
            self.furioso = True
            self.sprite = self.SPRITE_FURIOSO
            self.velocidade *= 1.5

    def atualizar(self, jogadores):
        if self.esta_entrando():
            self.rect.y += 2
            if self.rect.top >= ALTURA_DO_BOSS:
                self.entrou = True
            self.tempo_proximo_ataque = relogio.agora() + TEMPO_ANTES_DO_PRIMEIRO
            return

        self.mover()
        self.verificar_furia()
        self.processar_agendados()
        self.atacar(jogadores)

        for tiro in self.tiros[:]:
            tiro.atualizar()
            if tiro.saiu_da_tela():
                self.tiros.remove(tiro)
        self.lasers = [laser for laser in self.lasers if not laser.acabou()]

    def levar_dano(self):
        self.vida = max(0, self.vida - 1)
        self.tempo_ultimo_dano = relogio.agora()

    def esta_vivo(self):
        return self.vida > 0

    def limpar_ataques(self):
        """Some com todos os tiros, lasers e ataques agendados (quando o boss morre)."""
        self.tiros.clear()
        self.lasers.clear()
        self.agendados.clear()


    def desenhar(self, tela):
        for laser in self.lasers:
            laser.desenhar(tela)

        if relogio.agora() - self.tempo_ultimo_dano < TEMPO_PISCANDO:
            tela.blit(self.SPRITE_ACERTADO, self.rect)
        else:
            tela.blit(self.sprite, self.rect)

        for tiro in self.tiros:
            tiro.desenhar(tela)