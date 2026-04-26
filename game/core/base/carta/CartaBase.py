from abc import ABC
from game.core.enums.TipoCarta import TipoCarta


class CartaBase(ABC):
    def __init__(
        self,
        id_carta: str,
        nome: str,
        descricao: str,
        tipo: TipoCarta,
        ataques=None,
        habilidades=None,
    ):
        self.id_carta = id_carta
        self.nome = nome
        self.descricao = descricao
        self.tipo = tipo
        self.ataques = ataques or []
        self.habilidades = habilidades or []
        self.descartada = False
        self.consumida = False
        self.dono = None
        self.zona_atual = None

    def descartar(self, jogador):
        self.zona_atual = "descarte"
        self.descartada = True
        jogador.descarte.append(self)

    def mover_para(self, zona: str):
        self.zona_atual = zona

    def adicionar_ataque(self, ataque):
        self.ataques.append(ataque)

    def adicionar_habilidade(self, habilidade):
        self.habilidades.append(habilidade)