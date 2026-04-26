from game.core.base.efeito.EfeitoBase import EfeitoBase


class EfeitoCausarDano(EfeitoBase):
    def __init__(self, valor: int, seletor_alvo):
        self.valor = valor
        self.seletor_alvo = seletor_alvo

    def executar(self, contexto):
        alvo = self.seletor_alvo.selecionar(contexto)
        alvo.levar_dano(self.valor)