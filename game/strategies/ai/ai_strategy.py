from abc import ABC, abstractmethod


class AIStrategy(ABC):
    """Estratégia abstrata de IA que opera sobre BattleLogic baseado em dicts."""

    @abstractmethod
    def escolher_acao(self, logic) -> None:
        pass
