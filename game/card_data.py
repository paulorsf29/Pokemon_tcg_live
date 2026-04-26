from game.core.services.deck_provider import JsonDeckProvider

_default_provider = JsonDeckProvider()


def get_deck_by_name(deck_name: str):
    return _default_provider.get_deck(deck_name)


def list_decks():
    return _default_provider.list_decks()