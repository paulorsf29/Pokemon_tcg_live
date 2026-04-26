from .ai_strategy import AIStrategy


class SimpleAIStrategy(AIStrategy):
    """IA simples: usa a primeira carta viável e depois ataca."""

    def escolher_acao(self, logic) -> None:
        if logic.current_turn != "opponent" or logic.winner:
            return

        for i, card in enumerate(list(logic.opponent_hand)):
            tipo = card.get("type", "")
            if tipo not in ("item", "supporter"):
                continue

            if logic.carta_eh_viavel_para_ia(card, "opponent"):
                logic.apply_opponent_card(i)
                break

        if logic.winner:
            return

        logic.executar_ataque_oponente()
