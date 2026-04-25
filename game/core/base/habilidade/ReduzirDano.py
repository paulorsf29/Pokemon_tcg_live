from typing import final
from .habilidade_base import HabilidadeBase


@final
class ReduzirDano(HabilidadeBase):
    @property
    def nome(self) -> str:
        return "ReduzirDanoProximoTurno"

    def executar(self, contexto) -> None:
        if contexto.pokemon_alvo is None:
            return

        contexto.pokemon_alvo.reducao_dano_proximo_turno += contexto.valor