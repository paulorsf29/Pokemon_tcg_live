from typing import final
from ..habilidade.base.HabilidadeBase import HabilidadeBase


@final
class AumentarDanoHabilidade(HabilidadeBase):
    @property
    def nome(self) -> str:
        return "AumentarDano"

    def executar(self, contexto) -> None:
        if contexto.pokemon_origem is None:
            return

        contexto.pokemon_origem.bonus_dano_no_turno += contexto.valor