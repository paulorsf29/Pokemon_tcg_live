from typing import final
from .carta_apoiador_base import CartaApoiadorBase


@final
class CartaApoiadorReducaoDano(CartaApoiadorBase):
    def __init__(self, id_carta: str, nome: str, descricao: str, habilidades: dict) -> None:
        super().__init__(
            id_carta=id_carta,
            nome=nome,
            descricao=descricao,
            habilidades_associadas=("ReduzirDanoProximoTurno",),
            habilidades=habilidades,
        )