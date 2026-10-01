import json
import os

ARQUIVO_PADRAO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordes.json")


class Recordes:
    """Guarda o maior número de pontos de cada modo (1 ou 2 jogadores) num arquivo JSON.

    Exemplo do arquivo:
        {
          "1": 12340,
          "2": 8650
        }
    """

    def __init__(self, arquivo=ARQUIVO_PADRAO):
        self.arquivo = arquivo
        self.valores = self.carregar()

    def carregar(self):
        try:
            with open(self.arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
            return {modo: int(pontos) for modo, pontos in dados.items()}
        except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError, AttributeError, OSError):
            return {"1": 0, "2": 0}

    def salvar(self):
        try:
            with open(self.arquivo, "w", encoding="utf-8") as f:
                json.dump(self.valores, f, indent=2)
        except OSError:
            pass

    def obter(self, modo):
        return self.valores.get(str(modo), 0)

    def registrar(self, modo, pontos):
        """Salva a pontuação se for recorde. Devolve True quando bateu o recorde."""
        if pontos > self.obter(modo):
            self.valores[str(modo)] = pontos
            self.salvar()
            return True
        return False