from game.core.base.ataque.AtaqueBase import AtaqueBase


class Ataque(AtaqueBase):
    def __init__(self, nome: str, custos=None, efeitos=None):
        self._nome = nome
        self.custos = custos or []
        self.efeitos = efeitos or []

    @property
    def nome(self) -> str:
        return self._nome

    def pode_usar(self, contexto) -> bool:
        return all(custo.pode_pagar(contexto) for custo in self.custos)

    def usar(self, contexto) -> None:
        if not self.pode_usar(contexto):
            raise ValueError(f"O ataque {self.nome} não pode ser usado.")

        for custo in self.custos:
            custo.pagar(contexto)

        for efeito in self.efeitos:
            efeito.executar(contexto)