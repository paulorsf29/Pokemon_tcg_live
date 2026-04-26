from game.core.base.efeito.EfeitoBase import EfeitoBase


class EfeitoDanoPorCartasDescartadas(EfeitoBase):
    def __init__(self, base: int, multiplicador: int, chave_memoria: str, seletor_alvo):
        self.base = base
        self.multiplicador = multiplicador
        self.chave_memoria = chave_memoria
        self.seletor_alvo = seletor_alvo

    def executar(self, contexto):
        descartadas = contexto.memoria_execucao.get(self.chave_memoria, [])
        dano = self.base + (len(descartadas) * self.multiplicador)
        alvo = self.seletor_alvo.selecionar(contexto)
        alvo.levar_dano(dano)