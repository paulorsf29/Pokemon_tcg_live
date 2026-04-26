from game.battle_logic import BattleLogic
from game.core.services.deck_provider import JsonDeckProvider
from game.core.strategies.ai.simple_ai_strategy import SimpleAIStrategy
from game.core.strategies.ai.aggressive_ai_strategy import AggressiveAIStrategy


class BattleLogicFactory:
    _ai_registry = {
        "simple": SimpleAIStrategy,
        "aggressive": AggressiveAIStrategy,
    }

    def __new__(cls, *args, **kwargs):
        raise TypeError("BattleLogicFactory nao pode ser instanciada.")

    @classmethod
    def registrar_ai(cls, nome: str, ai_class: type):
        cls._ai_registry[nome] = ai_class

    @classmethod
    def criar(cls, player_deck_name: str, ai_type: str = "simple") -> BattleLogic:
        ai_class = cls._ai_registry.get(ai_type, SimpleAIStrategy)
        return BattleLogic(
            player_deck_name=player_deck_name,
            deck_provider=JsonDeckProvider(),
            ai_strategy=ai_class(),
        )