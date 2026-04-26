from game.core.factories.registries.registries import SELETOR_REGISTRY
from game.core.strategies.seletores.SeletorPokemonAtivo import SeletorPokemonAtivo
from game.core.strategies.seletores.SeletorCartasAnexadas import SeletorCartasAnexadas


def registrar_seletores():
    if not SELETOR_REGISTRY.possui("pokemon_ativo"):
        SELETOR_REGISTRY.registrar(
            "pokemon_ativo",
            lambda data: SeletorPokemonAtivo(data["owner"])
        )

    if not SELETOR_REGISTRY.possui("cartas_anexadas"):
        SELETOR_REGISTRY.registrar(
            "cartas_anexadas",
            lambda data: SeletorCartasAnexadas(data.get("owner", "self"))
        )