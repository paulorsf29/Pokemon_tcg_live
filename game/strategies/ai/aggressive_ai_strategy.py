from .ai_strategy import AIStrategy


class AggressiveAIStrategy(AIStrategy):
    """IA agressiva: prioriza cartas de dano antes de atacar."""

    def escolher_acao(self, logic) -> None:
        if logic.current_turn != "opponent" or logic.winner:
            return

        for i, card in enumerate(list(logic.opponent_hand)):
            tipo = card.get("type", "")
            if tipo not in ("item", "supporter"):
                continue

            if logic.carta_aumenta_pressao(card):
                logic.apply_opponent_card(i)
                break

        if logic.winner:
            return

        logic.executar_ataque_oponente()
