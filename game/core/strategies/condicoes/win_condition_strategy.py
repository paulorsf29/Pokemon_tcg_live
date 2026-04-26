from abc import ABC, abstractmethod


class WinConditionStrategy(ABC):
    @abstractmethod
    def checar(self, logic):
        pass