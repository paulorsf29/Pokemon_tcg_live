from dataclasses import dataclass


@dataclass(slots=True)
class EfeitoContexto:
    jogador_origem: object | None = None
    jogador_alvo: object | None = None
    pokemon_alvo: object | None = None
    carta: object | None = None
    valor: int = 0