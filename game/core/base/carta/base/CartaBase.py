from abc import ABC
from typing import Iterable


class CartaBase(ABC):
    def __init__(
        self,
        id_carta: str,
        nome: str,
        descricao: str,
        habilidades_associadas: Iterable[str],
        habilidades: dict[str, object],
    ) -> None:
        self.id_carta = id_carta
        self.nome = nome
        self.descricao = descricao
        self.habilidades_associadas = tuple(habilidades_associadas)
        self._habilidades = habilidades

    def usar_habilidade(self, nome_habilidade: str, contexto) -> None:
        if nome_habilidade not in self.habilidades_associadas:
            raise ValueError(
                f"A carta '{self.nome}' não possui a habilidade '{nome_habilidade}'."
            )

        habilidade = self._habilidades.get(nome_habilidade)
        if habilidade is None:
            raise ValueError(
                f"Habilidade '{nome_habilidade}' não encontrada no dicionário."
            )

        habilidade.executar(contexto)