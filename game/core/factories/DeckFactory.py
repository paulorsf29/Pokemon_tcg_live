import json
from game.core.model.Deck import Deck
from game.core.factories.CartaFactory import CartaFactory


class DeckFactory:
    def __new__(cls, *args, **kwargs):
        raise TypeError("DeckFactory não pode ser instanciada.")

    @staticmethod
    def criar(deck_data: dict, catalogo: dict[str, dict]) -> Deck:
        cartas = []

        for item in deck_data["cards"]:
            definicao = catalogo[item["card_id"]]
            for _ in range(item["quantity"]):
                cartas.append(CartaFactory.criar(definicao))

        return Deck(nome=deck_data["name"], cartas=cartas)