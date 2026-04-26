from abc import ABC, abstractmethod


class EfeitoBase(ABC):
    @abstractmethod
    def executar(self, contexto):
        pass