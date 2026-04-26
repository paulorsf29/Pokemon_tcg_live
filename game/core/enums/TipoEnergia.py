from enum import Enum


class TipoEnergia(str, Enum):
    ELETRICA = "electric"
    FOGO = "fire"
    AGUA = "water"
    PSIQUICA = "psychic"
    INCOLOR = "colorless"