from game.core.factories.registries.registries import EFEITO_REGISTRY
from game.core.strategies.efeitos.EfeitoCausarDano import EfeitoCausarDano
from game.core.strategies.efeitos.EfeitoCurar import EfeitoCurar
from game.core.strategies.efeitos.EfeitoComprarCartas import EfeitoComprarCartas
from game.core.strategies.efeitos.EfeitoPremioExtra import EfeitoPremioExtra
from game.core.strategies.efeitos.EfeitoReducaoDano import EfeitoReducaoDano
from game.core.strategies.efeitos.EfeitoDanoPorCartasDescartadas import EfeitoDanoPorCartasDescartadas


def _val(data):
    return data.get("value", data.get("valor", 0))


def _qtd(data):
    return data.get("quantity", data.get("quantidade", 0))


def _mult(data):
    return data.get("multiplier", data.get("multiplicador", 0))


def registrar_efeitos(registry_factory_cls):
    if not EFEITO_REGISTRY.possui("causar_dano"):
        EFEITO_REGISTRY.registrar(
            "causar_dano",
            lambda data: EfeitoCausarDano(
                _val(data),
                registry_factory_cls.criar_seletor(data["target"])
            )
        )

    if not EFEITO_REGISTRY.possui("curar"):
        EFEITO_REGISTRY.registrar(
            "curar",
            lambda data: EfeitoCurar(
                _val(data),
                registry_factory_cls.criar_seletor(data["target"])
            )
        )

    if not EFEITO_REGISTRY.possui("comprar_cartas"):
        EFEITO_REGISTRY.registrar(
            "comprar_cartas",
            lambda data: EfeitoComprarCartas(_qtd(data))
        )

    if not EFEITO_REGISTRY.possui("premio_extra"):
        EFEITO_REGISTRY.registrar(
            "premio_extra",
            lambda data: EfeitoPremioExtra(_qtd(data))
        )

    if not EFEITO_REGISTRY.possui("reducao_dano"):
        EFEITO_REGISTRY.registrar(
            "reducao_dano",
            lambda data: EfeitoReducaoDano(_val(data))
        )

    if not EFEITO_REGISTRY.possui("dano_por_descarte"):
        EFEITO_REGISTRY.registrar(
            "dano_por_descarte",
            lambda data: EfeitoDanoPorCartasDescartadas(
                base=data.get("base", 0),
                multiplicador=_mult(data),
                chave_memoria=data["count_from"],
                seletor_alvo=registry_factory_cls.criar_seletor(data["target"]),
            )
        )
