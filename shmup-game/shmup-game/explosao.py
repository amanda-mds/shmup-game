import relogio

TEMPO_POR_QUADRO = 70


class Explosao:
    """Animação de explosão que toca uma vez e some."""

    def __init__(self, centro, quadros, atraso=0):
        self.quadros = quadros
        self.centro = centro
        self.inicio = relogio.agora() + atraso

    def quadro_atual(self):
        return (relogio.agora() - self.inicio) // TEMPO_POR_QUADRO

    def acabou(self):
        return self.quadro_atual() >= len(self.quadros)

    def desenhar(self, tela):
        numero = self.quadro_atual()
        if 0 <= numero < len(self.quadros):
            quadro = self.quadros[numero]
            tela.blit(quadro, quadro.get_rect(center=self.centro))