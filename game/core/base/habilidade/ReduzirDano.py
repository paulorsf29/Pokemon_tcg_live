from typing import final
from ..habilidade.base.HabilidadeBase import HabilidadeBase


@final
class ReduzirDano(HabilidadeBase):
    @property
    def nome(self) -> str:
        return "ReduzirDanoProximoTurno"

    def executar(self, contexto) -> None:
        if contexto.pokemon_alvo is None:
            return

        contexto.pokemon_alvo.reducao_dano_proximo_turno += contexto.valor