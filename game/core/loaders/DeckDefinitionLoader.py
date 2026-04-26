import json


class DeckDefinitionLoader:
    @staticmethod
    def carregar(caminho: str) -> dict:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)