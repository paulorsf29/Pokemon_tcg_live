from typing import final
from .habilidade_base import HabilidadeBase


@final
class CurarPokemonHabilidade(HabilidadeBase):
    @property
    def nome(self) -> str:
        return "CurarPokemon"

    def executar(self, contexto) -> None:
        if contexto.pokemon_alvo is None:
            return

        contexto.pokemon_alvo.curar(contexto.valor)