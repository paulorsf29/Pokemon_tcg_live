from game.core.base.carta.CartaBase import CartaBase
from game.core.enums.TipoCarta import TipoCarta


class CartaPokemonBase(CartaBase):
    def __init__(self, id_carta, nome, descricao, hp, ataques=None, habilidades=None):
        super().__init__(id_carta, nome, descricao, TipoCarta.POKEMON, ataques, habilidades)
        self.hp_maximo = hp
        self.hp_atual = hp
        self.energias_anexadas = []
        self.vivo = True

    def anexar_energia(self, energia):
        self.energias_anexadas.append(energia)

    def levar_dano(self, dano: int):
        self.hp_atual = max(0, self.hp_atual - dano)
        if self.hp_atual == 0:
            self.morrer()

    def curar(self, valor: int):
        self.hp_atual = min(self.hp_maximo, self.hp_atual + valor)

    def morrer(self):
        self.vivo = False

    def esta_nocauteado(self) -> bool:
        return not self.vivo