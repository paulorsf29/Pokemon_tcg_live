from typing import final
from .base.CartaItemBase import CartaItemBase


@final
class CartaItemBuffDano(CartaItemBase):
    def __init__(self, id_carta: str, nome: str, descricao: str, habilidades: dict) -> None:
        super().__init__(
            id_carta=id_carta,
            nome=nome,
            descricao=descricao,
            habilidades_associadas=("AumentarDano",),
            habilidades=habilidades,
        )