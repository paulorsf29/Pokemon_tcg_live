class BloquearPremioOponenteHabilidade:
    def __init__(self):
        self.nome = "bloquear_premio_oponente"
        self.descricao = "Impede que o oponente pegue premio no proximo nocaute."

    def executar(self, contexto):
        alvo = getattr(contexto, "alvo", None)

        if alvo is None:
            return False

        alvo.bloqueia_premio_do_oponente_no_proximo_nocaute = True
        return True