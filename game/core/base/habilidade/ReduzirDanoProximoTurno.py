from typing import final
from game.core.base.habilidade.base.HabilidadeBase import HabilidadeBase


@final
class ReduzirDanoProximoTurnoHabilidade(HabilidadeBase):
    @property
    def nome(self) -> str:
        return "ReduzirDanoProximoTurno"

    def executar(self, contexto) -> None:
        if contexto.jogador_alvo is None:
            return

        contexto.jogador_alvo.reducao_dano_proximo_turno_ativa = True