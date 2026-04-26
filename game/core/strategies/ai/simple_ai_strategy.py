from .ai_strategy import AIStrategy


class SimpleAIStrategy(AIStrategy):
    def escolher_acao(self, logic) -> None:
        if logic.current_turn != "opponent" or logic.winner:
            return

        for i, carta in enumerate(list(logic.opponent_hand)):
            tipo = getattr(carta.tipo, "value", "")
            if tipo not in ("item", "supporter"):
                continue

            if logic.carta_eh_viavel_para_ia(carta, "opponent"):
                logic.apply_opponent_card(i)
                break

        if logic.winner:
            return

        logic.executar_ataque_oponente()