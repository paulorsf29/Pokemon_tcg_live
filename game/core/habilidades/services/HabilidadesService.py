class HabilidadesService:
    _HABILIDADES = None

    def __new__(cls, *args, **kwargs):
        raise TypeError("HabilidadesService não pode ser instanciada.")

    @staticmethod
    def obter() -> dict[str, object]:
        if HabilidadesService._HABILIDADES is None:
            habilidades = [
                CurarPokemonHabilidade(),
                ComprarPremioExtraHabilidade(),
                AumentarDanoHabilidade(),
                BloquearPremioOponenteHabilidade(),
                ReduzirDanoProximoTurnoHabilidade(),
            ]
            HabilidadesService._HABILIDADES = {
                habilidade.nome: habilidade for habilidade in habilidades
            }

        return HabilidadesService._HABILIDADES