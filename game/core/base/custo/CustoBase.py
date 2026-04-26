from abc import ABC, abstractmethod


class CustoBase(ABC):
    @abstractmethod
    def pode_pagar(self, contexto) -> bool:
        pass

    @abstractmethod
    def pagar(self, contexto) -> None:
        pass