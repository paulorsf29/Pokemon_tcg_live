from game.core.base.custo.CustoBase import CustoBase


class CustoDescartarSelecionadas(CustoBase):
    def __init__(self, seletor, quantidade: int, chave_memoria="cartas_descartadas"):
        self.seletor = seletor
        self.quantidade = quantidade
        self.chave_memoria = chave_memoria

    def pode_pagar(self, contexto) -> bool:
        selecionadas = self.seletor.selecionar(contexto)
        return len(selecionadas) >= self.quantidade

    def pagar(self, contexto) -> None:
        selecionadas = self.seletor.selecionar(contexto)[:self.quantidade]
        for carta in selecionadas:
            contexto.pokemon_origem.energias_anexadas.remove(carta)
            contexto.jogador_origem.descarte.append(carta)

        contexto.memoria_execucao[self.chave_memoria] = selecionadas