"""Efeitos sonoros e música, gerados no próprio código (sem arquivos de áudio).

Um som digital é uma lista de números que dizem para onde a caixa de som empurra
o ar a cada instante. Aqui esses números são calculados com ondas simples, as mesmas
dos videogames antigos:
  - onda quadrada: som "bipado" e forte, típico de 8 bits
  - onda triangular: som mais suave, bom para o baixo da música
  - ruído: números aleatórios, que soam como explosão
"""
import math
import random
from array import array

import pygame

TAXA_DESEJADA = 22050


def frequencia(nota):
    """Converte o nome da nota em frequência. Ex.: "A4" = 440 Hz, "C#5", "G3"."""
    nomes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    nome, oitava = nota[:-1], int(nota[-1])
    semitons_desde_la4 = nomes.index(nome) - 9 + (oitava - 4) * 12
    return 440 * 2 ** (semitons_desde_la4 / 12)


def onda(fase, forma):
    """Valor da onda (entre -1 e 1) num ponto do ciclo. fase vai de 0 até 1."""
    if forma == "quadrada":
        return 1.0 if fase < 0.5 else -1.0
    if forma == "quadrada_fina":
        return 1.0 if fase < 0.25 else -1.0
    return 4 * abs(fase - 0.5) - 1


class Sons:
    """Cria todos os sons quando o jogo abre e toca quando o jogo pede.

    Se o computador não tiver saída de som, o jogo continua funcionando, só que mudo.
    """

    VOLUME_MUSICA = 0.35

    def __init__(self):
        self.ligado = True
        self.disponivel = False
        self.efeitos = {}
        self.musica = None
        self.canal_musica = None

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            configuracao = pygame.mixer.get_init()
            if configuracao is None:
                return
            self.taxa, formato, self.canais = configuracao
            if formato != -16:
                return
            pygame.mixer.set_num_channels(16)
            self.criar_sons()
            self.disponivel = True
        except pygame.error:
            self.disponivel = False


    def tom(self, freq_inicio, freq_fim, duracao, forma="quadrada", volume=0.3):
        """Um som que escorrega de uma frequência para outra e vai sumindo."""
        total = int(self.taxa * duracao)
        amostras = []
        fase = 0.0
        for i in range(total):
            progresso = i / total
            freq = freq_inicio + (freq_fim - freq_inicio) * progresso
            fase = (fase + freq / self.taxa) % 1
            amostras.append(onda(fase, forma) * volume * (1 - progresso))
        return amostras

    def ruido(self, duracao, volume=0.3):
        """Chiado que vai ficando mais grave e mais baixo: som de explosão."""
        total = int(self.taxa * duracao)
        amostras = []
        valor = 0.0
        for i in range(total):
            progresso = i / total
            repeticao = 1 + int(progresso * 12)
            if i % repeticao == 0:
                valor = random.uniform(-1, 1)
            amostras.append(valor * volume * (1 - progresso) ** 2)
        return amostras

    def melodia(self, notas, forma="quadrada", volume=0.25):
        """Toca uma lista de (nota, duração em segundos). Use None como nota para pausa."""
        amostras = []
        for nota, duracao in notas:
            total = int(self.taxa * duracao)
            if nota is None:
                amostras.extend([0.0] * total)
                continue
            freq = frequencia(nota)
            fase = 0.0
            for i in range(total):
                fase = (fase + freq / self.taxa) % 1
                progresso = i / total
                envelope = 1.0 - 0.4 * progresso
                if progresso > 0.85:
                    envelope *= (1 - progresso) / 0.15
                amostras.append(onda(fase, forma) * volume * envelope)
        return amostras

    def misturar(self, *faixas):
        """Soma várias faixas de som tocando ao mesmo tempo."""
        tamanho = max(len(faixa) for faixa in faixas)
        resultado = [0.0] * tamanho
        for faixa in faixas:
            for i, valor in enumerate(faixa):
                resultado[i] += valor
        return resultado

    def para_som(self, amostras):
        """Transforma a lista de números (entre -1 e 1) num som que o Pygame toca."""
        inteiros = array("h")
        for valor in amostras:
            valor = max(-1.0, min(1.0, valor))
            inteiro = int(valor * 32767)
            for _ in range(self.canais):
                inteiros.append(inteiro)
        return pygame.mixer.Sound(buffer=inteiros.tobytes())


    def criar_sons(self):
        receitas = {
            "tiro": self.tom(1200, 500, 0.06, "quadrada_fina", 0.10),
            "acerto": self.tom(300, 150, 0.04, "quadrada", 0.08),
            "dano": self.misturar(self.tom(420, 70, 0.35, "quadrada", 0.25), self.ruido(0.15, 0.15)),
            "escudo": self.tom(1500, 500, 0.18, "triangular", 0.35),
            "explosao": self.ruido(0.5, 0.35),
            "explosao_grande": self.ruido(1.3, 0.45),
            "item": self.melodia([("C5", 0.06), ("E5", 0.06), ("G5", 0.06), ("C6", 0.12)], "triangular", 0.35),
            "powerup": self.melodia([("G5", 0.05), ("C6", 0.05), ("E6", 0.05), ("G6", 0.12)], "quadrada_fina", 0.15),
            "alerta": self.melodia([("A4", 0.12), (None, 0.06), ("A4", 0.12), (None, 0.06), ("A5", 0.25)],
                                   "quadrada", 0.15),
            "pausa": self.melodia([("E5", 0.05), ("A5", 0.08)], "quadrada_fina", 0.15),
            "vitoria": self.melodia([("C5", 0.12), ("E5", 0.12), ("G5", 0.12), ("C6", 0.12),
                                     ("G5", 0.12), ("C6", 0.45)], "quadrada", 0.18),
            "game_over": self.melodia([("G4", 0.2), ("E4", 0.2), ("C4", 0.2), ("G3", 0.6)],
                                      "triangular", 0.35),
        }
        self.efeitos = {nome: self.para_som(amostras) for nome, amostras in receitas.items()}
        self.musica = self.para_som(self.criar_musica())
        self.musica.set_volume(self.VOLUME_MUSICA)

    def criar_musica(self):
        """Música de fundo curtinha em loop: melodia na onda quadrada e baixo na triangular.

        São 4 compassos com os acordes Lá menor, Lá menor, Fá e Sol.
        """
        colcheia = 60 / 140 / 2

        melodia = [
            "A4", "C5", "E5", "A5", "G5", "E5", "C5", "E5",
            "A4", "C5", "E5", "G5", "A5", "G5", "E5", "D5",
            "F4", "A4", "C5", "F5", "E5", "C5", "A4", "C5",
            "G4", "B4", "D5", "G5", "F5", "D5", "B4", "D5",
        ]
        baixo = []
        for raiz in ("A", "A", "F", "G"):
            baixo += [raiz + "2", raiz + "3"] * 4

        faixa_melodia = self.melodia([(nota, colcheia) for nota in melodia], "quadrada_fina", 0.12)
        faixa_baixo = self.melodia([(nota, colcheia) for nota in baixo], "triangular", 0.28)
        return self.misturar(faixa_melodia, faixa_baixo)


    def tocar(self, nome):
        if self.ligado and self.disponivel:
            self.efeitos[nome].play()

    def tocar_musica(self):
        if self.ligado and self.disponivel and self.canal_musica is None:
            self.canal_musica = self.musica.play(loops=-1)

    def parar_musica(self):
        if self.canal_musica is not None:
            self.canal_musica.stop()
            self.canal_musica = None

    def pausar(self):
        if self.disponivel:
            pygame.mixer.pause()

    def continuar(self):
        if self.disponivel:
            pygame.mixer.unpause()

    def alternar(self):
        """Liga ou desliga todos os sons. Devolve se ficou ligado."""
        self.ligado = not self.ligado
        if not self.ligado:
            self.parar_musica()
            if self.disponivel:
                pygame.mixer.stop()
        return self.ligado