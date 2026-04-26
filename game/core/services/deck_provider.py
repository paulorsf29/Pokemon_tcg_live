from abc import ABC, abstractmethod
from pathlib import Path

from game.core.factories.DeckFactory import DeckFactory
from game.core.loaders.CardDefinitionLoader import CardDefinitionLoader
from game.core.loaders.DeckDefinitionLoader import DeckDefinitionLoader


class DeckProvider(ABC):
    @abstractmethod
    def get_deck(self, deck_name: str):
        pass

    @abstractmethod
    def list_decks(self) -> list[str]:
        pass


class JsonDeckProvider(DeckProvider):
    def __init__(self):
        # services/ → core/ → game/
        base_dir = Path(__file__).resolve().parents[2]
        self.cards_dir = base_dir / "data" / "cards"
        self.decks_dir = base_dir / "data" / "decks"

        self._catalogo = CardDefinitionLoader.montar_catalogo(
            str(self.cards_dir / "pokemon.json"),
            str(self.cards_dir / "items.json"),
            str(self.cards_dir / "supporters.json"),
            str(self.cards_dir / "energies.json"),
        )

        self._deck_map = {
            "Deck Pikachu EX": "pikachu_ex.json",
            "Deck Charizard EX": "charizard_ex.json",
            "Deck Chien-Pao": "chien_pao.json",
            "Deck Miraidon": "miraidon.json",
            "Deck Gardevoir": "gardevoir.json",
        }

    def get_deck(self, deck_name: str):
        arquivo = self._deck_map.get(deck_name, "pikachu_ex.json")
        deck_data = DeckDefinitionLoader.carregar(str(self.decks_dir / arquivo))
        return DeckFactory.criar(deck_data, self._catalogo)

    def list_decks(self) -> list[str]:
        return list(self._deck_map.keys())