from .EstadoPartida import EstadoPartida
from .Jogador import Jogador
from dataclasses import dataclass, field


@dataclass
class ContextoAcao:
    estado_partida: "EstadoPartida"
    jogador_origem: "Jogador"
    jogador_alvo: "Jogador"
    carta_origem: object | None = None
    pokemon_origem: object | None = None
    pokemon_alvo: object | None = None
    valor: int = 0
    memoria_execucao: dict = field(default_factory=dict)