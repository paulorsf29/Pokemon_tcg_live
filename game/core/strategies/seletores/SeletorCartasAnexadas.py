from game.core.base.seletor.SeletorBase import SeletorBase
from game.core.enums.TipoCarta import TipoCarta


class SeletorCartasAnexadas(SeletorBase):
    def __init__(self, dono="self", tipos_aceitos=None):
        self.dono = dono
        self.tipos_aceitos = tipos_aceitos or [TipoCarta.ENERGIA]

    def selecionar(self, contexto):
        pokemon = contexto.pokemon_origem if self.dono == "self" else contexto.pokemon_alvo
        return [c for c in pokemon.energias_anexadas if c.tipo in self.tipos_aceitos]