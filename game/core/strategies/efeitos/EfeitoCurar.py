from game.core.base.efeito.EfeitoBase import EfeitoBase


class EfeitoCurar(EfeitoBase):
    def __init__(self, valor: int, seletor_alvo):
        self.valor = valor
        self.seletor_alvo = seletor_alvo

    def executar(self, contexto):
        alvo = self.seletor_alvo.selecionar(contexto)
        alvo.curar(self.valor)