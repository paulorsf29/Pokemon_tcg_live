from game.core.base.habilidade.AumentarDano import AumentarDanoHabilidade
from game.core.base.habilidade.CurarPokemon import CurarPokemonHabilidade
from game.core.base.habilidade.BloquearPremioOponente import BloquearPremioOponenteHabilidade
from game.core.base.habilidade.ReduzirDanoProximoTurno import ReduzirDanoProximoTurnoHabilidade


class HabilidadesService:
    _HABILIDADES = None

    def __new__(cls, *args, **kwargs):
        raise TypeError("HabilidadesService não pode ser instanciada.")

    @staticmethod
    def obter() -> dict[str, object]:
        if HabilidadesService._HABILIDADES is None:
            habilidades = [
                CurarPokemonHabilidade(),
                AumentarDanoHabilidade(),
                BloquearPremioOponenteHabilidade(),
                ReduzirDanoProximoTurnoHabilidade(),
            ]

            HabilidadesService._HABILIDADES = {
                habilidade.nome: habilidade for habilidade in habilidades
            }

        return HabilidadesService._HABILIDADES