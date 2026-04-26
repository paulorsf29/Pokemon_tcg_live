from game.core.base.carta.CartaBase import CartaBase
from game.core.enums.TipoCarta import TipoCarta


class CartaEnergiaBase(CartaBase):
    def __init__(self, id_carta, nome, descricao, tipo_energia):
        super().__init__(id_carta, nome, descricao, TipoCarta.ENERGIA, [], [])
        self.tipo_energia = tipo_energia
        self.anexada = False

    def anexar_em(self, pokemon):
        pokemon.anexar_energia(self)
        self.anexada = True
        self.zona_atual = "pokemon_anexado"