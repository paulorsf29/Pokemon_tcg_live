from enum import Enum


class TipoCarta(str, Enum):
    POKEMON = "pokemon"
    ITEM = "item"
    APOIADOR = "supporter"
    ENERGIA = "energy"