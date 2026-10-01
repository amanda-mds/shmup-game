import pygame

import relogio
import sprites
from config import (
    LARGURA, ALTURA,
    VIDAS_JOGADOR, VELOCIDADE_JOGADOR, VELOCIDADE_TIRO, INTERVALO_TIRO,
    TEMPO_INVENCIVEL, TEMPO_TIRO_TRIPLO, TEMPO_TIRO_RAPIDO,
)
from tiro import Tiro


def apertou(teclas, lista_de_teclas):
    """True se qualquer uma das teclas da lista estiver apertada."""
    return any(teclas[tecla] for tecla in lista_de_teclas)


class Jogador:
    """Uma nave controlada por um jogador.

    Cada nave recebe seus próprios sprites e controles, então dá para criar
    quantas quiser (a vermelha e a azul usam essa mesma classe).
    """

    def __init__(self, sprite, icone, sprite_tiro, controles, centro_x):
        self.sprite = sprite
        self.icone = icone
        self.sprite_tiro = sprite_tiro
        self.controles = controles
        self.posicao_inicial = centro_x
        self.rect = self.sprite.get_rect(centerx=centro_x, bottom=ALTURA - 30)
        self.vidas = VIDAS_JOGADOR
        self.tiros = []
        self.tempo_ultimo_tiro = -INTERVALO_TIRO
        self.tempo_ultimo_dano = -TEMPO_INVENCIVEL

        self.tiro_triplo_ate = 0
        self.tiro_rapido_ate = 0
        self.escudo = False


    @property
    def hitbox(self):
        """Área que leva dano. É menor que o desenho: as pontas das asas não contam.

        Isso é comum em jogos de navinha e deixa o jogo mais justo, porque um tiro
        que só "raspou" na asa não tira vida.
        """
        return self.rect.inflate(-16, -14)


    def mover(self, teclas):
        if apertou(teclas, self.controles["esquerda"]) and self.rect.left > 0:
            self.rect.x -= VELOCIDADE_JOGADOR
        if apertou(teclas, self.controles["direita"]) and self.rect.right < LARGURA:
            self.rect.x += VELOCIDADE_JOGADOR
        if apertou(teclas, self.controles["cima"]) and self.rect.top > ALTURA // 2:
            self.rect.y -= VELOCIDADE_JOGADOR
        if apertou(teclas, self.controles["baixo"]) and self.rect.bottom < ALTURA - 10:
            self.rect.y += VELOCIDADE_JOGADOR

    def tem_tiro_triplo(self):
        return relogio.agora() < self.tiro_triplo_ate

    def tem_tiro_rapido(self):
        return relogio.agora() < self.tiro_rapido_ate

    def atirar(self):
        """Atira se já deu o tempo. Devolve True quando atirou (para tocar o som)."""
        agora = relogio.agora()
        intervalo = INTERVALO_TIRO // 2 if self.tem_tiro_rapido() else INTERVALO_TIRO
        if agora - self.tempo_ultimo_tiro < intervalo:
            return False

        direcoes_x = (-1.5, 0, 1.5) if self.tem_tiro_triplo() else (0,)
        for velocidade_x in direcoes_x:
            self.tiros.append(Tiro(self.rect.centerx, self.rect.top - 12, self.sprite_tiro,
                                   velocidade_x, -VELOCIDADE_TIRO))
        self.tempo_ultimo_tiro = agora
        return True

    def atualizar(self, teclas):
        """Move, atira e anda com os tiros. Devolve True se atirou neste quadro."""
        self.mover(teclas)
        atirou = False
        if apertou(teclas, self.controles["atirar"]):
            atirou = self.atirar()

        for tiro in self.tiros[:]:
            tiro.atualizar()
            if tiro.saiu_da_tela():
                self.tiros.remove(tiro)
        return atirou


    def esta_invencivel(self):
        """Fica invencível por um tempinho depois de levar dano."""
        return relogio.agora() - self.tempo_ultimo_dano < TEMPO_INVENCIVEL

    def levar_dano(self):
        """Tenta tirar uma vida. Devolve o que aconteceu, para o jogo tocar o som certo:
        None     -> estava invencível, nada aconteceu
        "escudo" -> o escudo segurou o tiro
        "dano"   -> perdeu uma vida
        """
        if self.esta_invencivel():
            return None
        self.tempo_ultimo_dano = relogio.agora()

        if self.escudo:
            self.escudo = False
            return "escudo"

        self.vidas -= 1
        if not self.esta_vivo():
            self.tiros.clear()
            self.tiro_triplo_ate = 0
            self.tiro_rapido_ate = 0
        return "dano"

    def esta_vivo(self):
        return self.vidas > 0

    def precisa_de_vida(self):
        """True se a nave está viva mas perdeu alguma vida."""
        return self.esta_vivo() and self.vidas < VIDAS_JOGADOR

    def ganhar_vida(self):
        if self.precisa_de_vida():
            self.vidas += 1

    def ganhar_powerup(self, tipo):
        agora = relogio.agora()
        if tipo == "triplo":
            self.tiro_triplo_ate = agora + TEMPO_TIRO_TRIPLO
        elif tipo == "rapido":
            self.tiro_rapido_ate = agora + TEMPO_TIRO_RAPIDO
        elif tipo == "escudo":
            self.escudo = True

    def powerups_ativos(self):
        """Lista de (tipo, fração de tempo que falta), para mostrar na tela."""
        agora = relogio.agora()
        ativos = []
        if self.tem_tiro_triplo():
            ativos.append(("triplo", (self.tiro_triplo_ate - agora) / TEMPO_TIRO_TRIPLO))
        if self.tem_tiro_rapido():
            ativos.append(("rapido", (self.tiro_rapido_ate - agora) / TEMPO_TIRO_RAPIDO))
        if self.escudo:
            ativos.append(("escudo", 1))
        return ativos

    def reviver(self):
        """Usado no modo dupla: a nave que caiu volta na fase seguinte com 1 vida."""
        if not self.esta_vivo():
            self.vidas = 1
            self.rect.centerx = self.posicao_inicial
            self.rect.bottom = ALTURA - 30
            self.tempo_ultimo_dano = relogio.agora()


    def desenhar(self, tela):
        for tiro in self.tiros:
            tiro.desenhar(tela)

        if self.esta_invencivel() and (relogio.agora() // 80) % 2 == 0:
            return

        quadro = (relogio.agora() // 100) % len(sprites.CHAMAS)
        chama = sprites.CHAMAS[quadro]
        tela.blit(chama, chama.get_rect(centerx=self.rect.centerx, top=self.rect.bottom))

        tela.blit(self.sprite, self.rect)

        if self.escudo:
            brilho = 150 + (relogio.agora() // 60) % 4 * 30
            pygame.draw.circle(tela, (60, brilho, 255), self.rect.center, 30, 2)