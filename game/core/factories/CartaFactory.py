from game.core.enums.TipoCarta import TipoCarta
from game.core.base.carta.pokemon.CartaPokemon import CartaPokemon
from game.core.base.carta.item.CartaItemGenerico import CartaItemGenerico
from game.core.base.carta.apoiador.CartaApoiadorGenerico import CartaApoiadorGenerico
from game.core.base.carta.energia.CartaEnergia import CartaEnergia
from game.core.factories.RegistryFactory import RegistryFactory


class CartaFactory:
    def __new__(cls, *args, **kwargs):
        raise TypeError("CartaFactory não pode ser instanciada.")

    @staticmethod
    def criar(definicao: dict):
        tipo = definicao["type"]
        ataques = [RegistryFactory.criar_ataque(a) for a in definicao.get("attacks", [])]
        habilidades = [RegistryFactory.criar_habilidade(h) for h in definicao.get("abilities", [])]

        if tipo == TipoCarta.POKEMON.value:
            return CartaPokemon(
            id_carta=definicao["id"],
            nome=definicao["name"],
            descricao=definicao.get("description", ""),
            hp=definicao["hp"],
            ataques=ataques,
            habilidades=habilidades,
            state=definicao.get("State", "basic"), 
            image=definicao.get("image", None),
        )

        if tipo == TipoCarta.ITEM.value:
            return CartaItemGenerico(
                id_carta=definicao["id"],
                nome=definicao["name"],
                descricao=definicao.get("description", ""),
                habilidades=habilidades,
            )

        if tipo == TipoCarta.APOIADOR.value:
            return CartaApoiadorGenerico(
                id_carta=definicao["id"],
                nome=definicao["name"],
                descricao=definicao.get("description", ""),
                habilidades=habilidades,
            )

        if tipo == TipoCarta.ENERGIA.value:
            return CartaEnergia(
                id_carta=definicao["id"],
                nome=definicao["name"],
                descricao=definicao.get("description", ""),
                tipo_energia=definicao["energy_type"],
            )

        raise ValueError(f"Tipo de carta não suportado: {tipo}")