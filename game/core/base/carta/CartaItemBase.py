from game.core.base.carta.CartaBase import CartaBase
from game.core.enums.TipoCarta import TipoCarta


class CartaItemBase(CartaBase):
    def __init__(self, id_carta, nome, descricao, habilidades=None):
        super().__init__(id_carta, nome, descricao, TipoCarta.ITEM, [], habilidades)

    def usar(self, contexto):
        for habilidade in self.habilidades:
            habilidade.executar(contexto)
        self.consumir(contexto.jogador_origem)

    def consumir(self, jogador):
        self.consumida = True
        self.descartar(jogador)