from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class EfeitoContexto:
    estado_partida: "EstadoPartida"
    jogador_origem: "Jogador"
    jogador_alvo: "Jogador"
    pokemon_origem: Optional["PokemonEmCampo"] = None
    pokemon_alvo: Optional["PokemonEmCampo"] = None
    valor: int = 0