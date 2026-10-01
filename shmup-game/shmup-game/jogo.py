import random

import pygame

import relogio
import sprites
from config import (
    LARGURA, ALTURA, FPS, TITULO,
    BRANCO, PRETO, VERMELHO, VERDE, AMARELO, CINZA, AZUL_CLARO,
    CONTROLES_VERMELHO, CONTROLES_AZUL, CONTROLES_SOLO, TECLAS_PAUSA, TECLA_SOM,
    INTERVALO_CORACAO_SOLO, INTERVALO_CORACAO_DUPLA, INTERVALO_POWERUP,
    PONTOS_POR_ACERTO, PONTOS_POR_BOSS, PONTOS_POR_ITEM, PONTOS_POR_VIDA_NO_FIM,
)
from jogador import Jogador
from bosses import FASES
from fundo import Fundo
from itens import Item, POWERUPS
from explosao import Explosao
from recordes import Recordes
from sons import Sons

COR_ESPACO = (5, 5, 20)
TEMPO_BANNER = 2500
DURACAO_BOSS_EXPLODINDO = 2300
MOMENTO_EXPLOSAO_FINAL = 1400
DURACAO_DERROTA = 1600
MAIOR_PASSO = 50


class Jogo:
    """Controla o loop principal, os estados do jogo e o desenho da tela.

    Estados:
      "menu"      -> tela inicial
      "jogando"   -> partida rolando
      "transicao" -> boss explodindo ou nave explodindo, antes da próxima tela
      "pausado"   -> tudo congelado
      "vitoria" e "derrota" -> telas de fim
    """

    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption(TITULO)
        self.controle_fps = pygame.time.Clock()

        self.cena = pygame.Surface((LARGURA, ALTURA))
        self.pelicula = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        self.pelicula.fill((0, 0, 0, 160))

        self.fonte_pequena = pygame.font.Font(None, 22)
        self.fonte = pygame.font.Font(None, 28)
        self.fonte_grande = pygame.font.Font(None, 64)

        self.fundo = Fundo()
        self.sons = Sons()
        self.recordes = Recordes()

        self.rodando = True
        self.quantidade_jogadores = 1
        self.estado = "menu"
        self.estado_antes_da_pausa = None
        self.sons.tocar_musica()


    def iniciar_partida(self, quantidade_jogadores):
        self.quantidade_jogadores = quantidade_jogadores
        relogio.zerar()

        if quantidade_jogadores == 1:
            self.jogadores = [
                Jogador(sprites.NAVE_AZUL, sprites.ICONE_AZUL, sprites.TIRO_AZUL,
                        CONTROLES_SOLO, LARGURA // 2),
            ]
            self.intervalo_coracao = INTERVALO_CORACAO_SOLO
        else:
            self.jogadores = [
                Jogador(sprites.NAVE_VERMELHA, sprites.ICONE_VERMELHO, sprites.TIRO_VERMELHO,
                        CONTROLES_VERMELHO, LARGURA // 3),
                Jogador(sprites.NAVE_AZUL, sprites.ICONE_AZUL, sprites.TIRO_AZUL,
                        CONTROLES_AZUL, LARGURA * 2 // 3),
            ]
            self.intervalo_coracao = INTERVALO_CORACAO_DUPLA

        self.pontos = 0
        self.novo_recorde = False
        self.itens = []
        self.explosoes = []
        self.tempo_proximo_coracao = self.intervalo_coracao
        self.tempo_proximo_powerup = INTERVALO_POWERUP
        self.tremor_ate = 0
        self.tremor_forca = 0

        self.sons.parar_musica()
        self.sons.tocar_musica()
        self.iniciar_fase(0)

    def iniciar_fase(self, numero):
        self.fase = numero
        self.boss = FASES[numero](self.quantidade_jogadores)
        self.banner_ate = relogio.agora() + TEMPO_BANNER
        for jogador in self.jogadores:
            jogador.reviver()
        self.estado = "jogando"
        self.sons.tocar("alerta")

    def jogadores_vivos(self):
        return [jogador for jogador in self.jogadores if jogador.esta_vivo()]

    def boss_derrotado(self):
        self.pontos += PONTOS_POR_BOSS * (self.fase + 1)
        self.boss.limpar_ataques()
        self.estado = "transicao"
        self.tipo_transicao = "boss"
        agora = relogio.agora()
        self.fim_transicao = agora + DURACAO_BOSS_EXPLODINDO
        self.boss_some_em = agora + MOMENTO_EXPLOSAO_FINAL
        self.explosao_final_tocou = False

        area = self.boss.rect
        for numero in range(8):
            ponto = (random.randint(area.left + 10, area.right - 10),
                     random.randint(area.top + 10, area.bottom - 10))
            self.explosoes.append(Explosao(ponto, sprites.EXPLOSAO_MEDIA, atraso=numero * 170))
        self.explosoes.append(Explosao(area.center, sprites.EXPLOSAO_GRANDE, atraso=MOMENTO_EXPLOSAO_FINAL))
        self.sons.tocar("explosao")
        self.tremer(3, MOMENTO_EXPLOSAO_FINAL)

    def comecar_derrota(self):
        self.boss.limpar_ataques()
        self.estado = "transicao"
        self.tipo_transicao = "derrota"
        self.fim_transicao = relogio.agora() + DURACAO_DERROTA

    def terminar(self, venceu):
        self.sons.parar_musica()
        if venceu:
            vidas_restantes = sum(jogador.vidas for jogador in self.jogadores_vivos())
            self.pontos += PONTOS_POR_VIDA_NO_FIM * vidas_restantes
            self.estado = "vitoria"
            self.sons.tocar("vitoria")
        else:
            self.estado = "derrota"
            self.sons.tocar("game_over")
        self.novo_recorde = self.recordes.registrar(self.quantidade_jogadores, self.pontos)


    def pausar(self):
        self.estado_antes_da_pausa = self.estado
        self.estado = "pausado"
        self.sons.pausar()
        self.sons.tocar("pausa")

    def continuar(self):
        self.estado = self.estado_antes_da_pausa
        self.sons.continuar()
        self.sons.tocar_musica()

    def voltar_ao_menu(self):
        self.estado = "menu"
        self.sons.continuar()
        self.sons.tocar_musica()


    def tratar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == TECLA_SOM:
                ligou = self.sons.alternar()
                if ligou and self.estado in ("menu", "jogando", "transicao"):
                    self.sons.tocar_musica()
                continue

            if self.estado == "menu":
                if event.key in (pygame.K_1, pygame.K_KP1):
                    self.iniciar_partida(1)
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self.iniciar_partida(2)
                elif event.key == pygame.K_ESCAPE:
                    self.rodando = False

            elif self.estado in ("jogando", "transicao"):
                if event.key in TECLAS_PAUSA:
                    self.pausar()

            elif self.estado == "pausado":
                if event.key in TECLAS_PAUSA:
                    self.continuar()
                elif event.key == pygame.K_m:
                    self.voltar_ao_menu()

            elif self.estado in ("vitoria", "derrota"):
                if event.key == pygame.K_r:
                    self.iniciar_partida(self.quantidade_jogadores)
                elif event.key == pygame.K_m:
                    self.voltar_ao_menu()


    def tremer(self, forca, duracao):
        """Faz a tela tremer por um tempo. Se já estiver tremendo mais forte, mantém."""
        self.tremor_forca = max(forca, self.tremor_forca if relogio.agora() < self.tremor_ate else 0)
        self.tremor_ate = max(self.tremor_ate, relogio.agora() + duracao)

    def jogador_atingido(self, jogador):
        resultado = jogador.levar_dano()
        if resultado == "escudo":
            self.sons.tocar("escudo")
            self.tremer(3, 150)
        elif resultado == "dano":
            if jogador.esta_vivo():
                self.sons.tocar("dano")
                self.tremer(5, 250)
            else:
                self.explosoes.append(Explosao(jogador.rect.center, sprites.EXPLOSAO_MEDIA))
                self.sons.tocar("explosao")
                self.tremer(8, 400)

    def verificar_colisoes(self):
        for jogador in self.jogadores_vivos():
            if self.boss.entrou:
                for tiro in jogador.tiros[:]:
                    if self.boss.esta_vivo() and tiro.rect.colliderect(self.boss.rect):
                        jogador.tiros.remove(tiro)
                        self.boss.levar_dano()
                        self.pontos += PONTOS_POR_ACERTO
                        self.explosoes.append(Explosao(tiro.rect.center, sprites.EXPLOSAO_PEQUENA))
                        self.sons.tocar("acerto")

            if not jogador.esta_invencivel():
                atingido = False
                for tiro in self.boss.tiros[:]:
                    if tiro.rect.colliderect(jogador.hitbox):
                        self.boss.tiros.remove(tiro)
                        atingido = True
                        break
                for laser in self.boss.lasers:
                    if laser.esta_ativo() and laser.rect.colliderect(jogador.hitbox):
                        atingido = True
                if atingido:
                    self.jogador_atingido(jogador)

            for item in self.itens[:]:
                if item.pode_ser_pego_por(jogador) and item.rect.colliderect(jogador.rect):
                    item.aplicar(jogador)
                    self.itens.remove(item)
                    self.pontos += PONTOS_POR_ITEM
                    self.sons.tocar("item" if item.tipo == "vida" else "powerup")

    def atualizar_itens(self):
        agora = relogio.agora()
        tipos_na_tela = [item.tipo for item in self.itens]

        if agora >= self.tempo_proximo_coracao and "vida" not in tipos_na_tela:
            self.itens.append(Item("vida"))
            self.tempo_proximo_coracao = agora + self.intervalo_coracao

        if agora >= self.tempo_proximo_powerup and not any(tipo in POWERUPS for tipo in tipos_na_tela):
            self.itens.append(Item(random.choice(POWERUPS)))
            self.tempo_proximo_powerup = agora + INTERVALO_POWERUP

        for item in self.itens[:]:
            item.atualizar()
            if item.saiu_da_tela():
                self.itens.remove(item)

    def atualizar_partida(self):
        teclas = pygame.key.get_pressed()
        for jogador in self.jogadores_vivos():
            if jogador.atualizar(teclas):
                self.sons.tocar("tiro")
        self.boss.atualizar(self.jogadores_vivos())
        self.atualizar_itens()
        self.verificar_colisoes()

        if not self.boss.esta_vivo():
            self.boss_derrotado()
        elif not self.jogadores_vivos():
            self.comecar_derrota()

    def atualizar_transicao(self):
        agora = relogio.agora()
        teclas = pygame.key.get_pressed()
        for jogador in self.jogadores_vivos():
            jogador.atualizar(teclas)
        for item in self.itens[:]:
            item.atualizar()
            if item.saiu_da_tela():
                self.itens.remove(item)

        if self.tipo_transicao == "boss":
            if not self.explosao_final_tocou and agora >= self.boss_some_em:
                self.explosao_final_tocou = True
                self.sons.tocar("explosao_grande")
                self.tremer(10, 600)
        else:
            self.boss.atualizar([])

        if agora >= self.fim_transicao:
            if self.tipo_transicao == "derrota":
                self.terminar(venceu=False)
            elif self.fase + 1 < len(FASES):
                self.iniciar_fase(self.fase + 1)
            else:
                self.terminar(venceu=True)

    def atualizar(self, milissegundos):
        if self.estado == "pausado":
            return

        self.fundo.atualizar()

        if self.estado in ("jogando", "transicao"):
            relogio.avancar(min(milissegundos, MAIOR_PASSO))
            if self.estado == "jogando":
                self.atualizar_partida()
            else:
                self.atualizar_transicao()
            self.explosoes = [explosao for explosao in self.explosoes if not explosao.acabou()]


    def escrever(self, texto, fonte, cor, centro_x, y):
        superficie = fonte.render(texto, False, cor)
        self.cena.blit(superficie, superficie.get_rect(centerx=centro_x, centery=y))

    def escrever_centralizado(self, texto, fonte, cor, y):
        self.escrever(texto, fonte, cor, LARGURA // 2, y)

    def piscando(self, intervalo=500):
        return (pygame.time.get_ticks() // intervalo) % 2 == 0

    def desenhar_hud(self):
        pontos = self.fonte_pequena.render(f"PONTOS {self.pontos:06d}", False, BRANCO)
        self.cena.blit(pontos, (10, 14))
        fase = self.fonte_pequena.render(f"FASE {self.fase + 1}/{len(FASES)}", False, BRANCO)
        self.cena.blit(fase, fase.get_rect(right=LARGURA - 10, top=14))

        if self.boss.esta_vivo():
            largura_barra = 160
            x = LARGURA // 2 - largura_barra // 2
            proporcao = self.boss.vida / self.boss.vida_maxima
            pygame.draw.rect(self.cena, VERMELHO, (x, 20, largura_barra, 10))
            pygame.draw.rect(self.cena, VERDE, (x, 20, round(largura_barra * proporcao), 10))
            pygame.draw.rect(self.cena, BRANCO, (x - 2, 18, largura_barra + 4, 14), 2)

        for posicao, jogador in enumerate(self.jogadores):
            largura_icone = jogador.icone.get_width() + 6
            for i in range(jogador.vidas):
                if posicao == 0:
                    x = 10 + i * largura_icone
                else:
                    x = LARGURA - 10 - (i + 1) * largura_icone
                self.cena.blit(jogador.icone, (x, ALTURA - 32))

            for i, (tipo, restante) in enumerate(jogador.powerups_ativos()):
                icone = sprites.ICONES_POWERUP[tipo]
                if posicao == 0:
                    x = 10 + i * (icone.get_width() + 6)
                else:
                    x = LARGURA - 10 - (i + 1) * (icone.get_width() + 6)
                self.cena.blit(icone, (x, ALTURA - 62))
                pygame.draw.rect(self.cena, BRANCO, (x, ALTURA - 40, round(icone.get_width() * restante), 2))

        if relogio.agora() < self.banner_ate and self.estado == "jogando":
            self.escrever_centralizado(f"FASE {self.fase + 1}", self.fonte_grande, AMARELO, ALTURA // 2 - 30)
            self.escrever_centralizado(self.boss.NOME, self.fonte, BRANCO, ALTURA // 2 + 15)

    def desenhar_partida(self):
        boss_aparece = not (self.estado_atual_e("transicao") and self.tipo_transicao == "boss"
                            and relogio.agora() >= self.boss_some_em)
        if boss_aparece:
            self.boss.desenhar(self.cena)
        for item in self.itens:
            item.desenhar(self.cena)
        for jogador in self.jogadores_vivos():
            jogador.desenhar(self.cena)
        for explosao in self.explosoes:
            explosao.desenhar(self.cena)
        self.desenhar_hud()

    def estado_atual_e(self, estado):
        """Estado da partida, ignorando a pausa (pausado em cima de "transicao" conta como transição)."""
        if self.estado == "pausado":
            return self.estado_antes_da_pausa == estado
        return self.estado == estado

    def desenhar_pausa(self):
        self.cena.blit(self.pelicula, (0, 0))
        self.escrever_centralizado("PAUSADO", self.fonte_grande, AMARELO, ALTURA // 2 - 50)
        self.escrever_centralizado("P OU ESC PARA CONTINUAR", self.fonte, BRANCO, ALTURA // 2 + 5)
        self.escrever_centralizado("M PARA VOLTAR AO MENU", self.fonte_pequena, CINZA, ALTURA // 2 + 40)
        texto_som = "N: SOM LIGADO" if self.sons.ligado else "N: SOM DESLIGADO"
        self.escrever_centralizado(texto_som, self.fonte_pequena, CINZA, ALTURA // 2 + 65)

    def desenhar_menu(self):
        self.escrever_centralizado("NAVE VS BOSS", self.fonte_grande, AMARELO, 130)

        self.cena.blit(sprites.NAVE_VERMELHA, sprites.NAVE_VERMELHA.get_rect(center=(LARGURA // 2 - 40, 215)))
        self.cena.blit(sprites.NAVE_AZUL, sprites.NAVE_AZUL.get_rect(center=(LARGURA // 2 + 40, 215)))

        if self.piscando():
            self.escrever_centralizado("APERTE 1 - UM JOGADOR", self.fonte, BRANCO, 300)
            self.escrever_centralizado("APERTE 2 - DOIS JOGADORES", self.fonte, BRANCO, 335)

        recorde_1 = self.recordes.obter(1)
        recorde_2 = self.recordes.obter(2)
        self.escrever_centralizado(f"RECORDE  1P: {recorde_1:06d}   2P: {recorde_2:06d}",
                                   self.fonte_pequena, AMARELO, 395)

        self.escrever_centralizado("1 JOGADOR: SETAS OU WASD + ESPAÇO", self.fonte_pequena, CINZA, 460)
        self.escrever_centralizado("VERMELHA: WASD + ESPAÇO", self.fonte_pequena, VERMELHO, 485)
        self.escrever_centralizado("AZUL: SETAS + ENTER", self.fonte_pequena, AZUL_CLARO, 510)
        texto_som = "LIGADO" if self.sons.ligado else "DESLIGADO"
        self.escrever_centralizado(f"P: PAUSA    N: SOM {texto_som}", self.fonte_pequena, CINZA, 550)

    def desenhar_fim(self):
        if self.estado == "vitoria":
            mensagem = "VOCÊ VENCEU!" if self.quantidade_jogadores == 1 else "VOCÊS VENCERAM!"
            self.escrever_centralizado(mensagem, self.fonte_grande, VERDE, ALTURA // 2 - 70)
        else:
            self.escrever_centralizado("GAME OVER", self.fonte_grande, VERMELHO, ALTURA // 2 - 70)

        self.escrever_centralizado(f"PONTOS: {self.pontos:06d}", self.fonte, BRANCO, ALTURA // 2 - 15)
        if self.novo_recorde:
            if self.piscando(300):
                self.escrever_centralizado("NOVO RECORDE!", self.fonte, AMARELO, ALTURA // 2 + 15)
        else:
            recorde = self.recordes.obter(self.quantidade_jogadores)
            self.escrever_centralizado(f"RECORDE: {recorde:06d}", self.fonte_pequena, CINZA, ALTURA // 2 + 15)

        if self.piscando():
            self.escrever_centralizado("APERTE R PARA JOGAR DE NOVO", self.fonte, BRANCO, ALTURA // 2 + 65)
        self.escrever_centralizado("M PARA VOLTAR AO MENU", self.fonte_pequena, CINZA, ALTURA // 2 + 100)

    def deslocamento_do_tremor(self):
        if self.estado not in ("jogando", "transicao") or relogio.agora() >= self.tremor_ate:
            return (0, 0)
        forca = self.tremor_forca
        return (random.randint(-forca, forca), random.randint(-forca, forca))

    def desenhar(self):
        self.cena.fill(COR_ESPACO)
        self.fundo.desenhar(self.cena)

        if self.estado == "menu":
            self.desenhar_menu()
        elif self.estado in ("jogando", "transicao", "pausado"):
            self.desenhar_partida()
            if self.estado == "pausado":
                self.desenhar_pausa()
        else:
            self.desenhar_fim()

        self.tela.fill(PRETO)
        self.tela.blit(self.cena, self.deslocamento_do_tremor())
        pygame.display.flip()

    def executar(self):
        while self.rodando:
            self.tratar_eventos()
            milissegundos = self.controle_fps.tick(FPS)
            self.atualizar(milissegundos)
            self.desenhar()
        pygame.quit()