from game.core.base.efeito.EfeitoBase import EfeitoBase


class EfeitoComprarCartas(EfeitoBase):
    def __init__(self, quantidade: int):
        self.quantidade = quantidade

    def executar(self, contexto):
        for _ in range(self.quantidade):
            carta = contexto.jogador_origem.deck.comprar()
            if carta is not None:
                contexto.jogador_origem.mao.append(carta)