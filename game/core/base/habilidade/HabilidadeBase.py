from abc import ABC, abstractmethod


class HabilidadeBase(ABC):
    @property
    @abstractmethod
    def nome(self) -> str:
        pass

    @abstractmethod
    def executar(self, contexto):
        pass