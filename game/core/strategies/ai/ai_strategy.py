from abc import ABC, abstractmethod


class AIStrategy(ABC):
    @abstractmethod
    def escolher_acao(self, logic) -> None:
        pass