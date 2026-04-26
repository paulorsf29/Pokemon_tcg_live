from game.core.base.efeito.EfeitoBase import EfeitoBase


class EfeitoReducaoDano(EfeitoBase):
    def __init__(self, valor: int):
        self.valor = valor

    def executar(self, contexto):
        contexto.memoria_execucao["reducao_dano"] = self.valor