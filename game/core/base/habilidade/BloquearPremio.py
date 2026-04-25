from typing import final
from .habilidade_base import HabilidadeBase


@final
class BloquearPremioHabilidade(HabilidadeBase):
    @property
    def nome(self) -> str:
        return "BloquearPremioOponente"

    def executar(self, contexto) -> None:
        contexto.jogador_origem.bloqueia_premio_do_oponente_no_proximo_nocaute = True