from game.core.components.ataque.Ataque import Ataque
from game.core.components.habilidade.Habilidade import Habilidade
from game.core.factories.registries import (
    SELETOR_REGISTRY,
    CUSTO_REGISTRY,
    EFEITO_REGISTRY,
)
from game.core.factories.registries.register_seletores import registrar_seletores
from game.core.factories.registries.register_custos import registrar_custos
from game.core.factories.registries.register_efeitos import registrar_efeitos


class RegistryFactory:
    _inicializado = False

    def __new__(cls, *args, **kwargs):
        raise TypeError("RegistryFactory não pode ser instanciada.")

    @staticmethod
    def inicializar():
        if RegistryFactory._inicializado:
            return

        registrar_seletores()
        registrar_custos(RegistryFactory)
        registrar_efeitos(RegistryFactory)

        RegistryFactory._inicializado = True

    @staticmethod
    def criar_seletor(data: dict):
        RegistryFactory.inicializar()
        return SELETOR_REGISTRY.criar(data)

    @staticmethod
    def criar_custo(data: dict):
        RegistryFactory.inicializar()
        return CUSTO_REGISTRY.criar(data)

    @staticmethod
    def criar_efeito(data: dict):
        RegistryFactory.inicializar()
        return EFEITO_REGISTRY.criar(data)

    @staticmethod
    def criar_ataque(data: dict):
        RegistryFactory.inicializar()
        custos = [RegistryFactory.criar_custo(c) for c in data.get("costs", [])]
        efeitos = [RegistryFactory.criar_efeito(e) for e in data.get("effects", [])]
        return Ataque(nome=data["name"], custos=custos, efeitos=efeitos)

    @staticmethod
    def criar_habilidade(data: dict):
        RegistryFactory.inicializar()
        efeitos = [RegistryFactory.criar_efeito(e) for e in data.get("effects", [])]
        return Habilidade(nome=data["name"], efeitos=efeitos)