from abc import ABC, abstractmethod


class SeletorBase(ABC):
    @abstractmethod
    def selecionar(self, contexto):
        """
        Retorna um único alvo ou uma coleção, dependendo da estratégia concreta.
        """
        raise NotImplementedError

    def selecionar_varios(self, contexto) -> list:
        """
        Padroniza a saída como lista.
        Se o seletor concreto retornar um único item, ele é embrulhado em lista.
        Se retornar None, devolve lista vazia.
        """
        resultado = self.selecionar(contexto)

        if resultado is None:
            return []

        if isinstance(resultado, list):
            return resultado

        if isinstance(resultado, tuple):
            return list(resultado)

        return [resultado]