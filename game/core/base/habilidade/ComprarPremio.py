from typing import final
from ..habilidade.base.HabilidadeBase import HabilidadeBase


@final
class ComprarPremioHabilidade(HabilidadeBase):
    @property
    def nome(self) -> str:
        return "ComprarPremioExtra"

    def executar(self, contexto) -> None:
        contexto.jogador_origem.modificador_premio_extra_ativo = True