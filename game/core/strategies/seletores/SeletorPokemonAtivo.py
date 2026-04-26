from game.core.base.seletor.SeletorBase import SeletorBase


class SeletorPokemonAtivo(SeletorBase):
    def __init__(self, dono: str):
        self.dono = dono

    def selecionar(self, contexto):
        jogador = contexto.jogador_origem if self.dono == "self" else contexto.jogador_alvo
        return jogador.pokemon_ativo