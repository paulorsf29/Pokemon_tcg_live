from typing import final
from ..base.CartaBase import CartaBase


@final
class CartaPokemon(CartaBase):
    def __init__(
        self,
        id_carta: str,
        nome: str,
        descricao: str,
        hp: int,
        habilidades_associadas,
        habilidades,
    ) -> None:
        super().__init__(
            id_carta=id_carta,
            nome=nome,
            descricao=descricao,
            habilidades_associadas=habilidades_associadas,
            habilidades=habilidades,
        )
        self.hp = hp