from core.cartas.carta_pokemon import CartaPokemon
from core.cartas.carta_apoiador_cura import CartaApoiadorCura
from core.cartas.carta_apoiador_premio_extra import CartaApoiadorPremioExtra
from core.cartas.carta_item_cura import CartaItemCura
from core.cartas.carta_item_buff_dano import CartaItemBuffDano
from core.cartas.carta_apoiador_bloqueio_premio import CartaApoiadorBloqueioPremio
from core.cartas.carta_apoiador_reducao_dano import CartaApoiadorReducaoDano
from core.services.habilidades_service import HabilidadesService


class CartaFactory:
    def __new__(cls, *args, **kwargs):
        raise TypeError("CartaFactory não pode ser instanciada.")

    @staticmethod
    def criar_pokemon(
        id_carta: str,
        nome: str,
        descricao: str,
        hp: int,
        habilidades_associadas: tuple[str, ...] = (),
    ) -> CartaPokemon:
        return CartaPokemon(
            id_carta=id_carta,
            nome=nome,
            descricao=descricao,
            hp=hp,
            habilidades_associadas=habilidades_associadas,
            habilidades=HabilidadesService.obter(),
        )

    @staticmethod
    def criar_apoiador_cura(id_carta: str, nome: str, descricao: str) -> CartaApoiadorCura:
        return CartaApoiadorCura(id_carta, nome, descricao, HabilidadesService.obter())

    @staticmethod
    def criar_apoiador_premio_extra(id_carta: str, nome: str, descricao: str) -> CartaApoiadorPremioExtra:
        return CartaApoiadorPremioExtra(id_carta, nome, descricao, HabilidadesService.obter())

    @staticmethod
    def criar_item_cura(id_carta: str, nome: str, descricao: str) -> CartaItemCura:
        return CartaItemCura(id_carta, nome, descricao, HabilidadesService.obter())

    @staticmethod
    def criar_item_buff_dano(id_carta: str, nome: str, descricao: str) -> CartaItemBuffDano:
        return CartaItemBuffDano(id_carta, nome, descricao, HabilidadesService.obter())

    @staticmethod
    def criar_apoiador_bloqueio_premio(id_carta: str, nome: str, descricao: str) -> CartaApoiadorBloqueioPremio:
        return CartaApoiadorBloqueioPremio(id_carta, nome, descricao, HabilidadesService.obter())

    @staticmethod
    def criar_apoiador_reducao_dano(id_carta: str, nome: str, descricao: str) -> CartaApoiadorReducaoDano:
        return CartaApoiadorReducaoDano(id_carta, nome, descricao, HabilidadesService.obter())