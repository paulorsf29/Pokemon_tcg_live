from game.core.factories.registries.registries import CUSTO_REGISTRY
from game.core.strategies.custos.CustoEnergiaAnexada import CustoEnergiaAnexada
from game.core.strategies.custos.CustoDescartarSelecionadas import CustoDescartarSelecionadas


def registrar_custos(registry_factory_cls):
    def _qtd(data):
        return data.get("quantity", data.get("quantidade", 0))

    if not CUSTO_REGISTRY.possui("energia_anexada"):
        CUSTO_REGISTRY.registrar(
            "energia_anexada",
            lambda data: CustoEnergiaAnexada(_qtd(data))
        )

    if not CUSTO_REGISTRY.possui("descartar_selecionadas"):
        CUSTO_REGISTRY.registrar(
            "descartar_selecionadas",
            lambda data: CustoDescartarSelecionadas(
                seletor=registry_factory_cls.criar_seletor(data["selector"]),
                quantidade=_qtd(data),
                chave_memoria=data.get("store_as", "cartas_descartadas"),
            )
        )