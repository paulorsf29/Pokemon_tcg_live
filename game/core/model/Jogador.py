from .Deck import Deck
from dataclasses import dataclass, field


@dataclass
class Jogador:
    nickname: str
    deck: "Deck"
    mao: list = field(default_factory=list)
    descarte: list = field(default_factory=list)
    banco: list = field(default_factory=list)
    pokemon_ativo: object | None = None
    premios_restantes: int = 6
    premio_extra_ativo: int = 0
    bloqueio_de_premio_ativo: bool = False