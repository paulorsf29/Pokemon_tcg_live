import json


class CardDefinitionLoader:
    @staticmethod
    def carregar_arquivo(caminho: str) -> list[dict]:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    @staticmethod
    def montar_catalogo(*arquivos: str) -> dict[str, dict]:
        catalogo = {}

        for caminho in arquivos:
            for carta in CardDefinitionLoader.carregar_arquivo(caminho):
                catalogo[carta["id"]] = carta

        return catalogo