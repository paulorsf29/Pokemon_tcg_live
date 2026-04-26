from game.core.base.efeito.EfeitoBase import EfeitoBase


class EfeitoPremioExtra(EfeitoBase):
    def __init__(self, quantidade: int):
        self.quantidade = quantidade

    def executar(self, contexto):
        contexto.jogador_origem.premio_extra_ativo += self.quantidade