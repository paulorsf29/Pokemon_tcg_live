from game.core.base.carta.CartaBase import CartaBase
from game.core.enums.TipoCarta import TipoCarta


class CartaApoiadorBase(CartaBase):
    def __init__(self, id_carta, nome, descricao, habilidades=None):
        super().__init__(id_carta, nome, descricao, TipoCarta.APOIADOR, [], habilidades)

    def usar(self, contexto):
        for habilidade in self.habilidades:
            habilidade.executar(contexto)
        self.descartar(contexto.jogador_origem)