"""Relógio da partida.

O pygame.time.get_ticks() continua contando mesmo com o jogo pausado. Se o boss usasse
ele, ao voltar da pausa todos os ataques que "venceram" durante a pausa sairiam de uma vez.

Por isso o jogo tem este relógio próprio, que só anda enquanto a partida está rolando.
Tudo que depende de tempo dentro da partida (ataques, invencibilidade, power-ups,
animações) usa agora() daqui.
"""

_tempo = 0


def agora():
    """Milissegundos de partida que já se passaram (sem contar as pausas)."""
    return _tempo


def avancar(milissegundos):
    global _tempo
    _tempo += milissegundos


def zerar():
    global _tempo
    _tempo = 0