from .Jogador import Jogador
from dataclasses import dataclass


@dataclass
class EstadoPartida:
    jogador_1: "Jogador"
    jogador_2: "Jogador"
    turno_atual: int = 1