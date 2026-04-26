from abc import ABC, abstractmethod


class AtaqueBase(ABC):
    @property
    @abstractmethod
    def nome(self) -> str:
        pass

    @abstractmethod
    def pode_usar(self, contexto) -> bool:
        pass

    @abstractmethod
    def usar(self, contexto) -> None:
        pass