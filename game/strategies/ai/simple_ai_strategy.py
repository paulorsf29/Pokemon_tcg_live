from .ai_strategy import AIStrategy


class SimpleAIStrategy(AIStrategy):
    """IA simples: prioriza anexar energia se ainda falta, depois usa
    uma carta auxiliar útil e tenta atacar."""

    def escolher_acao(self, logic) -> None:
        if logic.current_turn != "opponent" or logic.winner:
            return

        # 1) Anexa energia se o ativo ainda não tem o necessário
        active = logic.opponent_active
        if active is not None:
            faltam = active.get("attack_required_count", 0) - len(active.get("energies", []))
            if faltam > 0:
                for i, card in enumerate(list(logic.opponent_hand)):
                    if card.get("type") == "energy":
                        if logic.apply_opponent_card(i):
                            break

        if logic.winner:
            return

        # 2) Joga uma carta auxiliar útil (item/supporter)
        for i, card in enumerate(list(logic.opponent_hand)):
            tipo = card.get("type", "")
            if tipo not in ("item", "supporter"):
                continue
            if logic.carta_eh_viavel_para_ia(card, "opponent"):
                logic.apply_opponent_card(i)
                break

        if logic.winner:
            return

        # 3) Tenta atacar (executar_ataque_oponente já checa energia e passa o turno)
        logic.executar_ataque_oponente()
