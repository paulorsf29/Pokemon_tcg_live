from game.core.base.habilidade.HabilidadeBase import HabilidadeBase


class Habilidade(HabilidadeBase):
    def __init__(self, nome: str, efeitos=None):
        self._nome = nome
        self.efeitos = efeitos or []

    @property
    def nome(self) -> str:
        return self._nome

    def executar(self, contexto):
        for efeito in self.efeitos:
            efeito.executar(contexto)