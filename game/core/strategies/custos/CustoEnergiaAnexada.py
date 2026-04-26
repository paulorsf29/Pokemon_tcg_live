from game.core.base.custo.CustoBase import CustoBase


class CustoEnergiaAnexada(CustoBase):
    def __init__(self, quantidade: int):
        self.quantidade = quantidade

    def pode_pagar(self, contexto) -> bool:
        pokemon = contexto.pokemon_origem
        return pokemon is not None and len(pokemon.energias_anexadas) >= self.quantidade

    def pagar(self, contexto) -> None:
        pass